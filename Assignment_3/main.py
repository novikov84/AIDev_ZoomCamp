import requests
from fastmcp import FastMCP

from search import build_index, ensure_zip, load_documents, search as search_docs

mcp = FastMCP("Demo 🚀")

_doc_index = None

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


def fetch_markdown(url: str) -> str:
    """Fetch page content as markdown via Jina reader."""
    cleaned_url = url.strip()
    jina_prefix = "https://r.jina.ai/"
    if not cleaned_url.startswith(jina_prefix):
        if not cleaned_url.startswith(("http://", "https://")):
            cleaned_url = f"https://{cleaned_url}"
        cleaned_url = f"{jina_prefix}{cleaned_url}"

    response = requests.get(cleaned_url, timeout=20)
    response.raise_for_status()
    return response.text


mcp.tool(fetch_markdown)


def _get_doc_index():
    global _doc_index
    if _doc_index is None:
        ensure_zip()
        docs = load_documents()
        _doc_index = build_index(docs)
    return _doc_index


@mcp.tool
def doc_search(query: str, top_k: int = 5) -> list[dict]:
    """Search the fastmcp markdown docs and return top matches."""
    index = _get_doc_index()
    results = search_docs(index, query, top_k=top_k)
    return [
        {"filename": r["filename"], "preview": r["content"][:500]}
        for r in results
    ]


if __name__ == "__main__":
    mcp.run()