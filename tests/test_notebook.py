# tests/test_notebook.py
import json
from paper_digest.tools.arxiv_tool import fetch_papers
from paper_digest.agents.ranker import rank_papers
from paper_digest.agents.curator import curate_papers
from paper_digest.agents.notebook import generate_notes_for_papers

papers = fetch_papers(max_results=10, days_back=7)
ranked = rank_papers(papers)
selected = curate_papers(ranked)
enriched = generate_notes_for_papers(selected)

for p in enriched:
    print(f"\n{'='*60}")
    print(f"PAPER: {p.title}")
    print(f"SCORE: {p.score}")
    print(f"\nNOTES:")
    try:
        notes = json.loads(p.notes)
        print(f"  TL;DR: {notes['tldr']}")
        print(f"  Problem: {notes['problem']}")
        print(f"  Solution: {notes['solution']}")
        print(f"  Relevance: {notes['practical_relevance']}")
        print(f"  Key concepts:")
        for kc in notes['key_concepts']:
            print(f"    - {kc['term']}: {kc['definition']}")
    except Exception:
        print(p.notes)