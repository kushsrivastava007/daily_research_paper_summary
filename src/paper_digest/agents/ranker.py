# src/paper_digest/agents/ranker.py
import json
import time
from paper_digest.graph.state import Paper
from paper_digest.llm import call_llm

SYSTEM_PROMPT = """You are an expert AI researcher helping a Senior Software Engineer 
transition into AI Engineering. Your job is to score research papers by relevance.

The engineer is interested in:
- RAG pipelines and retrieval systems
- LLM agents and agentic workflows  
- LangGraph and orchestration frameworks
- FastAPI and backend systems
- MLOps and LLM observability
- Practical, applied AI engineering (not pure theory)

Score each paper from 1-10 where:
10 = directly relevant, immediately applicable
7-9 = highly relevant, worth reading today
4-6 = moderately relevant, useful background
1-3 = not relevant (pure theory, unrelated domain)

You must respond with ONLY a JSON object, no explanation, no markdown:
{"score": 8, "reason": "one sentence why"}
"""


def rank_paper(paper: Paper) -> Paper:
    """Score a single paper for relevance. Returns paper with score filled in."""

    prompt = f"""Score this paper:

Title: {paper.title}
Abstract: {paper.abstract[:500]}
"""

    response = call_llm("ranker", prompt=prompt, system=SYSTEM_PROMPT)

    try:
        # parse the JSON response
        data = json.loads(response.strip())
        paper.score = float(data["score"])
    except (json.JSONDecodeError, KeyError, ValueError):
        # if LLM returns bad JSON, default to middle score
        paper.score = 5.0

    return paper


def rank_papers(papers: list[Paper]) -> list[Paper]:
    """Score all papers and return sorted by score descending."""

    ranked = []
    for i, p in enumerate(papers):
        ranked.append(rank_paper(p))
        if i < len(papers) - 1:
            time.sleep(2)  # avoid Groq TPM rate limits
    ranked.sort(key=lambda p: p.score or 0, reverse=True)
    return ranked