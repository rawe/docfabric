#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["requests"]
# ///
"""Upload a document to DocFabric.

Sends a local file to the DocFabric REST API for ingestion and
AI-optimized access.

Requirements:
    DOCFABRIC_URL   Environment variable pointing to the DocFabric server.
                    Example: export DOCFABRIC_URL=http://localhost:8000

Supported formats: PDF, DOCX, PPTX, HTML, CSV, images.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload a document to DocFabric")
    parser.add_argument("file", type=Path, help="path to the file to upload")
    parser.add_argument(
        "--metadata",
        action="append",
        metavar="KEY=VALUE",
        help="metadata key=value pair (repeatable)",
    )
    args = parser.parse_args()

    base_url = os.environ.get("DOCFABRIC_URL")
    if not base_url:
        print("Error: DOCFABRIC_URL environment variable is not set", file=sys.stderr)
        sys.exit(1)

    file_path: Path = args.file
    if not file_path.is_file():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    metadata = {}
    if args.metadata:
        for item in args.metadata:
            if "=" not in item:
                print(
                    f"Error: invalid metadata format: {item} (expected KEY=VALUE)",
                    file=sys.stderr,
                )
                sys.exit(1)
            key, value = item.split("=", 1)
            metadata[key] = value

    url = f"{base_url.rstrip('/')}/api/documents"
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f)}
        data = {}
        if metadata:
            data["metadata"] = json.dumps(metadata)
        response = requests.post(url, files=files, data=data)

    if not response.ok:
        print(
            f"Error: upload failed ({response.status_code}): {response.text}",
            file=sys.stderr,
        )
        sys.exit(1)

    result = response.json()
    print(f"{result['filename']}: {result['id']}")


if __name__ == "__main__":
    main()
