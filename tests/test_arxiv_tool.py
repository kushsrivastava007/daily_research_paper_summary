# tests/test_arxiv_tool.py
from paper_digest.tools.arxiv_tool import fetch_papers

papers = fetch_papers(max_results=5, days_back=7)

for p in papers:
    print(f"[{p.published}] {p.title}")
    print(f"  Authors: {', '.join(p.authors[:2])}")
    print(f"  URL: {p.url}")
    print()

print(f"Total fetched: {len(papers)}")