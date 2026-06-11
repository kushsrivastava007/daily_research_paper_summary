# src/paper_digest/agents/notebook.py
import json
import re
from paper_digest.graph.state import Paper
from paper_digest.llm import call_llm
from paper_digest.agents.ranker import CATEGORY_LABELS, AI_CATEGORIES


def build_notebook_prompt(categories: list[str] | None = None) -> str:
    """Build a notes prompt that adapts to user's research interests."""
    cats_set = set(categories or [])
    is_ai_focused = bool(cats_set & AI_CATEGORIES)

    if is_ai_focused:
        relevance_field = '"practical_relevance": "How is this relevant to AI engineering, agentic AI, generative AI, or production ML systems? Mention connections to LLM agents, RAG, fine-tuning, model serving, or emerging AI tooling where applicable. (2-3 sentences)"'
    elif categories:
        labels = [CATEGORY_LABELS.get(c, c) for c in categories]
        areas = ", ".join(labels[:5])
        relevance_field = f'"practical_relevance": "How is this relevant to practitioners in {areas}? (2-3 sentences)"'
    else:
        relevance_field = '"practical_relevance": "Why does this paper matter and how could it be applied? (2-3 sentences)"'

    return f"""You are an expert research tutor. Your job is to make research papers 
easy to understand and actionable.

When given a paper, generate structured study notes in this EXACT JSON format:
{{
  "tldr": "One sentence summary of the paper (max 30 words)",
  "problem": "What problem does this paper solve? (2-3 sentences)",
  "solution": "What is the proposed solution or contribution? (2-3 sentences)",
  "key_concepts": [
    {{"term": "concept name", "definition": "plain english definition"}}
  ],
  {relevance_field},
  "further_reading": ["related topic 1", "related topic 2"]
}}

Respond with ONLY the JSON object. No markdown, no explanation, no backticks.
"""


def generate_notes(paper: Paper, system_prompt: str) -> Paper:
    """Generate structured study notes for a single paper."""

    prompt = f"""Generate study notes for this paper:

Title: {paper.title}
Authors: {', '.join(paper.authors[:3])}
Abstract: {paper.abstract}
"""

    response = call_llm("notebook", prompt=prompt, system=system_prompt)

    try:
        notes = json.loads(response.strip())
        paper.notes = json.dumps(notes, indent=2)
    except json.JSONDecodeError:
        # LLM may wrap JSON in markdown code fences — strip them
        cleaned = re.sub(r'^```(?:json)?\s*', '', response.strip())
        cleaned = re.sub(r'\s*```$', '', cleaned)
        try:
            notes = json.loads(cleaned.strip())
            paper.notes = json.dumps(notes, indent=2)
        except json.JSONDecodeError:
            paper.notes = response

    return paper


def generate_notes_for_papers(papers: list[Paper], categories: list[str] | None = None) -> list[Paper]:
    """Generate study notes for all selected papers."""
    system_prompt = build_notebook_prompt(categories)
    return [generate_notes(p, system_prompt) for p in papers]