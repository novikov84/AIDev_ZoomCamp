"""
Quick manual test for fetch_markdown tool.
Run with: uv run python test.py --url https://example.com
"""

import argparse

from main import fetch_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch markdown via Jina reader.")
    parser.add_argument(
        "--url",
        default="https://example.com",
        help="URL to fetch (default: https://example.com)",
    )
    args = parser.parse_args()

    content = fetch_markdown(args.url)
    print("Fetched markdown preview (first 500 chars):")
    print(content[:])
    
    print("Length is ", len(content))


if __name__ == "__main__":
    main()
