# tests/test_ranker.py
from paper_digest.tools.arxiv_tool import fetch_papers
from paper_digest.agents.ranker import rank_papers

papers = fetch_papers(max_results=5, days_back=7)
ranked = rank_papers(papers)

for p in ranked:
    print(f"[{p.score}] {p.title}")