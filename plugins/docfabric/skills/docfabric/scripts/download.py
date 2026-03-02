#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["requests"]
# ///
"""Download a document from DocFabric.

Retrieves the original file or its markdown representation and writes it
to a local path.

Environment:
    DOCFABRIC_URL   DocFabric server URL (default: http://localhost:8000)
"""

import argparse
import os
import sys
from pathlib import Path

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a document from DocFabric")
    parser.add_argument("document_id", help="UUID of the document to download")
    parser.add_argument("output", type=Path, help="local file path to write to")
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="download the markdown representation instead of the original file",
    )
    args = parser.parse_args()

    base_url = os.environ.get("DOCFABRIC_URL")
    if not base_url:
        print("Error: DOCFABRIC_URL environment variable is not set", file=sys.stderr)
        sys.exit(1)

    output_path: Path = args.output
    if output_path.exists():
        print(f"Error: output path already exists: {output_path}", file=sys.stderr)
        sys.exit(1)

    parent = output_path.parent
    if not parent.exists():
        print(f"Error: parent directory does not exist: {parent}", file=sys.stderr)
        sys.exit(1)

    base = base_url.rstrip("/")

    if args.markdown:
        url = f"{base}/api/documents/{args.document_id}/content"
        response = requests.get(url)
    else:
        url = f"{base}/api/documents/{args.document_id}/original"
        response = requests.get(url)

    if response.status_code == 404:
        print(f"Error: document not found: {args.document_id}", file=sys.stderr)
        sys.exit(1)

    if not response.ok:
        print(
            f"Error: download failed ({response.status_code}): {response.text}",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.markdown:
        content = response.json()["content"]
        output_path.write_text(content, encoding="utf-8")
    else:
        output_path.write_bytes(response.content)

    print(f"{args.document_id}: saved to {output_path}")


if __name__ == "__main__":
    main()
