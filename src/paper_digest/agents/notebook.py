# src/paper_digest/agents/notebook.py
import json
from paper_digest.graph.state import Paper
from paper_digest.llm import call_llm

SYSTEM_PROMPT = """You are an expert AI research tutor helping a Senior Software Engineer 
transition into AI Engineering. Your job is to make research papers easy to understand 
and actionable.

When given a paper, generate structured study notes in this EXACT JSON format:
{
  "tldr": "One sentence summary of the paper (max 30 words)",
  "problem": "What problem does this paper solve? (2-3 sentences)",
  "solution": "What is the proposed solution or contribution? (2-3 sentences)",
  "key_concepts": [
    {"term": "concept name", "definition": "plain english definition"}
  ],
  "practical_relevance": "How is this relevant to building RAG pipelines, LLM agents, or AI systems? (2-3 sentences)",
  "further_reading": ["related topic 1", "related topic 2"]
}

Respond with ONLY the JSON object. No markdown, no explanation, no backticks.
"""


def generate_notes(paper: Paper) -> Paper:
    """Generate structured study notes for a single paper."""

    prompt = f"""Generate study notes for this paper:

Title: {paper.title}
Authors: {', '.join(paper.authors[:3])}
Abstract: {paper.abstract}
"""

    response = call_llm("notebook", prompt=prompt, system=SYSTEM_PROMPT)

    try:
        notes = json.loads(response.strip())
        # store as formatted string on the paper
        paper.notes = json.dumps(notes, indent=2)
    except json.JSONDecodeError:
        # if JSON parsing fails, store raw response
        paper.notes = response

    return paper


def generate_notes_for_papers(papers: list[Paper]) -> list[Paper]:
    """Generate study notes for all selected papers."""
    return [generate_notes(p) for p in papers]