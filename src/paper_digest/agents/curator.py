# src/paper_digest/agents/curator.py
from paper_digest.graph.state import Paper


MIN_SCORE = 5.0       # ranker uses 5.0 when JSON parse fails; 6.0 filtered everything out
TOP_N = 3             # pick top N papers per day


def curate_papers(
    ranked_papers: list[Paper],
    seen_ids: set[str] = None,
    min_score: float = MIN_SCORE,
    top_n: int = TOP_N,
) -> list[Paper]:
    """
    From ranked papers:
    1. Filter out already seen papers
    2. Filter out low scoring papers
    3. Return top N
    """

    seen_ids = seen_ids or set()

    filtered = [
        p for p in ranked_papers
        if (p.score or 0) >= min_score
        and p.id not in seen_ids
    ]

    return filtered[:top_n]