# src/paper_digest/agents/quiz.py
import json
from paper_digest.graph.state import Paper
from paper_digest.llm import call_llm

SYSTEM_PROMPT = """You are an expert AI research tutor. Your job is to test understanding 
of research papers through well-crafted questions.

Given a paper, generate a quiz in this EXACT JSON format:
{
  "questions": [
    {
      "question": "question text",
      "options": ["A) option", "B) option", "C) option", "D) option"],
      "answer": "A",
      "explanation": "why this is correct (1-2 sentences)"
    }
  ]
}

Rules:
- Generate exactly 3 questions
- Increase difficulty: question 1 is easy, question 2 is medium, question 3 is hard
- Questions must test actual understanding, not just memory
- Wrong options must be plausible, not obviously wrong
- Each option MUST start with a letter and parenthesis: "A) ...", "B) ...", "C) ...", "D) ..."
- The "answer" field MUST be a single uppercase letter: "A", "B", "C", or "D"
- Respond with ONLY the JSON object. No markdown, no backticks.
"""


def generate_quiz(paper: Paper) -> Paper:
    """Generate a quiz for a single paper."""

    prompt = f"""Generate a quiz for this paper:

Title: {paper.title}
Abstract: {paper.abstract}
Notes: {paper.notes or ''}
"""

    response = call_llm("quiz", prompt=prompt, system=SYSTEM_PROMPT)

    try:
        quiz = json.loads(response.strip())
        paper.quiz = json.dumps(quiz, indent=2)
    except json.JSONDecodeError:
        paper.quiz = response

    return paper


def generate_quizzes(papers: list[Paper]) -> list[Paper]:
    """Generate quizzes for all enriched papers."""
    return [generate_quiz(p) for p in papers]