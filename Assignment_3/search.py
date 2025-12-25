"""
Index markdown docs from fastmcp zip archives and search them with minsearch.
Run: uv run python search.py
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from typing import Iterable, List, Tuple

import requests
from minsearch import Index

BASE_DIR = Path(__file__).parent
ZIP_URL = "https://github.com/jlowin/fastmcp/archive/refs/heads/main.zip"
ZIP_NAME = "fastmcp-main.zip"


def ensure_zip(url: str = ZIP_URL, filename: str = ZIP_NAME) -> Path:
    """Download the target zip if it's not already present."""
    target = BASE_DIR / filename
    if target.exists():
        return target

    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    with target.open("wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return target


def strip_root(path_str: str) -> str:
    """Remove the first path component from a zip entry."""
    parts = Path(path_str).parts
    if len(parts) <= 1:
        return path_str
    return Path(*parts[1:]).as_posix()


def iter_markdown_from_zip(zip_path: Path) -> Iterable[Tuple[str, str]]:
    """Yield (relative_path, text) for .md/.mdx files inside a zip."""
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            if not info.filename.lower().endswith((".md", ".mdx")):
                continue
            with zf.open(info) as f:
                text = f.read().decode("utf-8", errors="ignore")
            yield strip_root(info.filename), text


def load_documents() -> List[dict]:
    """Collect documents from all zip files in BASE_DIR."""
    docs: List[dict] = []
    for zip_path in BASE_DIR.glob("*.zip"):
        for rel_path, text in iter_markdown_from_zip(zip_path):
            docs.append({"filename": rel_path, "content": text})
    return docs


def build_index(docs: List[dict]) -> Index:
    """Build a minsearch index over markdown content."""
    index = Index(text_fields=["content"], keyword_fields=["filename"])
    index.fit(docs)
    return index


def search(index: Index, query: str, top_k: int = 5) -> List[dict]:
    """Search the index and return top_k results."""
    return index.search(query=query, num_results=top_k)


def main() -> None:
    parser = argparse.ArgumentParser(description="Index and search markdown docs from fastmcp zip archives.")
    parser.add_argument("--query", default="getting started", help="Search query (default: 'getting started')")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return (default: 5)")
    args = parser.parse_args()

    ensure_zip()
    docs = load_documents()
    index = build_index(docs)
    results = search(index, args.query, top_k=args.top_k)
    print(f"Top results for {args.query!r}:")
    for i, doc in enumerate(results, start=1):
        print(f"{i}. {doc['filename']}")


if __name__ == "__main__":
    main()
