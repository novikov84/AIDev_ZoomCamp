# Assignment 3 – MCP Server + Doc Search

Small FastMCP server exposing:
- `add(a, b)`: simple addition tool
- `fetch_markdown(url)`: fetch page markdown via Jina reader (`https://r.jina.ai/<url>`)
- `doc_search(query, top_k)`: searches the fastmcp docs (.md/.mdx) indexed locally with minsearch; downloads the repo zip on first use

## Run the server
```bash
cd Assignment_3
uv run python main.py          # stdio transport (default)
# or HTTP:
# uv run python -c "from main import mcp; mcp.run(transport='http', host='127.0.0.1', port=8765)"
```

## Manual search script
```bash
uv run python search.py --query "quickstart" --top-k 5
```

## Notes
- Dependencies: see `pyproject.toml` / `uv.lock` (includes `fastmcp`, `requests`, `minsearch`).
- The docs zip `fastmcp-main.zip` is cached in this folder; reused on subsequent runs.
