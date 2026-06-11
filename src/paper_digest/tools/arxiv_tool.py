import time
import random
import arxiv
from datetime import datetime, timedelta
from paper_digest.graph.state import Paper

CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.IR", "cs.MA", "cs.NE", "cs.RO", "stat.ML"]


def safe_fetch(client, search, max_retries: int = 5) -> list:
    """Fetch with exponential backoff + jitter on 429."""
    for attempt in range(max_retries):
        try:
            return list(client.results(search))
        except arxiv.HTTPError as e:
            if "429" in str(e):
                wait = 2 ** attempt + random.uniform(0, 1)
                print(f"Rate limited. Waiting {wait:.1f}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                raise  # non-429 errors bubble up immediately
    raise RuntimeError("arXiv rate limit exceeded after max retries")


def fetch_papers(
    categories: list[str] = CATEGORIES,
    max_results: int = 20,
    days_back: int = 7,
) -> list[Paper]:

    query = " OR ".join(f"cat:{cat}" for cat in categories)

    client = arxiv.Client(
        page_size=10,
        delay_seconds=1,
        num_retries=1,        # we handle retries ourselves in safe_fetch
    )

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    cutoff_date = datetime.now() - timedelta(days=days_back)

    results = safe_fetch(client, search)

    papers = []
    for result in results:
        published = result.published.replace(tzinfo=None)
        if published < cutoff_date:
            continue

        papers.append(Paper(
            id=result.entry_id.split("/abs/")[-1],
            title=result.title.strip(),
            abstract=result.summary.strip(),
            authors=[a.name for a in result.authors],
            published=result.published.strftime("%Y-%m-%d"),
            url=result.entry_id,
        ))

    return papers
