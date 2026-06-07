# tests/test_quiz.py
import json
from paper_digest.tools.arxiv_tool import fetch_papers
from paper_digest.agents.ranker import rank_papers
from paper_digest.agents.curator import curate_papers
from paper_digest.agents.notebook import generate_notes_for_papers
from paper_digest.agents.quiz import generate_quizzes

papers = fetch_papers(max_results=10, days_back=7)
ranked = rank_papers(papers)
selected = curate_papers(ranked)
enriched = generate_notes_for_papers(selected)
quizzed = generate_quizzes(enriched)

for p in quizzed:
    print(f"\n{'='*60}")
    print(f"PAPER: {p.title}")
    print(f"\nQUIZ:")
    try:
        quiz = json.loads(p.quiz)
        for i, q in enumerate(quiz["questions"], 1):
            print(f"\n  Q{i}: {q['question']}")
            for opt in q["options"]:
                print(f"    {opt}")
            print(f"  Answer: {q['answer']}")
            print(f"  Why: {q['explanation']}")
    except Exception:
        print(p.quiz)