# tests/test_curator.py
from paper_digest.tools.arxiv_tool import fetch_papers
from paper_digest.agents.ranker import rank_papers
from paper_digest.agents.curator import curate_papers

papers = fetch_papers(max_results=10, days_back=7)
ranked = rank_papers(papers)
selected = curate_papers(ranked)

print(f"Fetched:  {len(papers)}")
print(f"Ranked:   {len(ranked)}")
print(f"Selected: {len(selected)}\n")

for p in selected:
    print(f"[{p.score}] {p.title}")
    print(f"  {p.url}\n")