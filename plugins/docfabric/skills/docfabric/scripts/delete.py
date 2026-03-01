#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["requests"]
# ///
"""Delete a document from DocFabric.

Removes a document and its converted content from DocFabric via the REST API.

Requirements:
    DOCFABRIC_URL   Environment variable pointing to the DocFabric server.
                    Example: export DOCFABRIC_URL=http://localhost:8000
"""

import argparse
import os
import sys

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete a document from DocFabric")
    parser.add_argument("document_id", help="UUID of the document to delete")
    args = parser.parse_args()

    base_url = os.environ.get("DOCFABRIC_URL")
    if not base_url:
        print("Error: DOCFABRIC_URL environment variable is not set", file=sys.stderr)
        sys.exit(1)

    url = f"{base_url.rstrip('/')}/api/documents/{args.document_id}"
    response = requests.delete(url)

    if response.status_code == 404:
        print(f"Error: document not found: {args.document_id}", file=sys.stderr)
        sys.exit(1)

    if not response.ok:
        print(
            f"Error: deletion failed ({response.status_code}): {response.text}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"{args.document_id}: deleted")


if __name__ == "__main__":
    main()
