# src/paper_digest/agents/ranker.py
import json
import time
from paper_digest.graph.state import Paper
from paper_digest.llm import call_llm

# Map arXiv category codes to human-readable research area descriptions
CATEGORY_LABELS = {
    "cs.AI": "Artificial Intelligence",
    "cs.LG": "Machine Learning",
    "cs.CL": "Natural Language Processing / Computational Linguistics",
    "cs.CV": "Computer Vision",
    "cs.IR": "Information Retrieval",
    "cs.MA": "Multiagent Systems",
    "cs.NE": "Neural and Evolutionary Computing",
    "cs.RO": "Robotics",
    "stat.ML": "Statistical Machine Learning",
}


# AI-focused categories get a richer, practitioner-oriented prompt
AI_CATEGORIES = {"cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.IR", "cs.MA", "cs.NE", "stat.ML"}


def build_system_prompt(categories: list[str] | None = None) -> str:
    """Build a scoring prompt that reflects the user's selected categories."""
    if categories:
        interest_lines = []
        for cat in categories:
            label = CATEGORY_LABELS.get(cat, cat)
            interest_lines.append(f"- {label} ({cat})")
        interests = "\n".join(interest_lines)
    else:
        interests = (
            "- Artificial Intelligence (cs.AI)\n"
            "- Machine Learning (cs.LG)\n"
            "- Natural Language Processing (cs.CL)"
        )

    # Check if the user's categories are AI/ML focused
    cats_set = set(categories or [])
    is_ai_focused = bool(cats_set & AI_CATEGORIES)

    if is_ai_focused:
        domain_guidance = """
Additional context — the user is an AI/ML practitioner. Prioritize papers that are:
- Practical and applicable: RAG pipelines, LLM agents, agentic workflows, fine-tuning techniques
- Framework/tooling oriented: LangChain, LangGraph, vLLM, orchestration patterns
- Systems-level: MLOps, LLM serving, observability, evaluation, guardrails
- Applied over theoretical: real-world benchmarks, deployment insights, engineering trade-offs
- Novel architectures or techniques with clear practical impact

Deprioritize papers that are purely mathematical proofs or narrow domain theory 
with no engineering relevance."""
    else:
        domain_guidance = """
Focus on papers that present novel results, practical methods, or significant 
advances in the user's selected fields. Prioritize applied work and clear 
contributions over incremental or narrow theoretical results."""

    return f"""You are an expert research paper evaluator. Your job is to score 
research papers by how relevant they are to the user's selected research interests.

The user is interested in these research areas:
{interests}
{domain_guidance}

Score each paper from 1-10 where:
10 = directly relevant, immediately applicable or groundbreaking
7-9 = highly relevant, worth reading today
4-6 = moderately relevant, useful background
1-3 = not relevant to the user's interests

You must respond with ONLY a JSON object, no explanation, no markdown:
{{"score": 8, "reason": "one sentence why"}}
"""


def rank_paper(paper: Paper, system_prompt: str) -> Paper:
    """Score a single paper for relevance. Returns paper with score filled in."""

    prompt = f"""Score this paper:

Title: {paper.title}
Abstract: {paper.abstract[:500]}
"""

    response = call_llm("ranker", prompt=prompt, system=system_prompt)

    try:
        data = json.loads(response.strip())
        paper.score = float(data["score"])
    except (json.JSONDecodeError, KeyError, ValueError):
        paper.score = 5.0

    return paper


def rank_papers(papers: list[Paper], categories: list[str] | None = None) -> list[Paper]:
    """Score all papers and return sorted by score descending."""

    system_prompt = build_system_prompt(categories)

    ranked = []
    for i, p in enumerate(papers):
        ranked.append(rank_paper(p, system_prompt))
        if i < len(papers) - 1:
            time.sleep(2)
    ranked.sort(key=lambda p: p.score or 0, reverse=True)
    return ranked