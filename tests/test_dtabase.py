# tests/test_database.py
from paper_digest.storage.database import (
    init_db,
    save_papers,
    get_seen_ids,
    get_all_papers,
)
from paper_digest.tools.arxiv_tool import fetch_papers
from paper_digest.agents.ranker import rank_papers
from paper_digest.agents.curator import curate_papers
from paper_digest.agents.notebook import generate_notes_for_papers
from paper_digest.agents.quiz import generate_quizzes

# setup
init_db()
print("Database initialized")

# run pipeline
papers  = fetch_papers(max_results=10, days_back=7)
ranked  = rank_papers(papers)
selected = curate_papers(ranked)
enriched = generate_notes_for_papers(selected)
quizzed  = generate_quizzes(enriched)

# save to DB
save_papers(quizzed)
print(f"Saved {len(quizzed)} papers to database")

# verify seen_ids
seen = get_seen_ids()
print(f"Seen IDs in DB: {seen}")

# verify retrieval
all_papers = get_all_papers()
print(f"Total papers in DB: {len(all_papers)}")
for p in all_papers:
    print(f"  [{p.score}] {p.title}")