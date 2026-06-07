# src/paper_digest/graph/state.py
from typing import Optional, TypedDict
from pydantic import BaseModel, Field


class Paper(BaseModel):
    id: str                             # arXiv ID e.g. "2401.12345"
    title: str
    abstract: str
    authors: list[str]
    published: str                      # "2024-01-15"
    url: str
    score: Optional[float] = None       # filled by ranker
    notes: Optional[str] = None         # filled by notebook agent
    quiz: Optional[str] = None          # filled by quiz agent
    summary: Optional[str] = None       # filled by notifier

    model_config = {"arbitrary_types_allowed": True}


class PipelineState(TypedDict):
    raw_papers: list[Paper]         # fetcher output
    ranked_papers: list[Paper]      # ranker output
    selected_papers: list[Paper]    # curator output
    enriched_papers: list[Paper]    # notebook + quiz output
    run_date: str
    errors: list[str]