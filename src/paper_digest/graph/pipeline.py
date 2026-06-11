# src/paper_digest/graph/pipeline.py
from datetime import datetime
from langgraph.graph import StateGraph, END

from paper_digest.graph.state import PipelineState
from paper_digest.tools.arxiv_tool import fetch_papers
from paper_digest.agents.ranker import rank_papers
from paper_digest.agents.curator import curate_papers
from paper_digest.agents.notebook import generate_notes_for_papers
from paper_digest.agents.quiz import generate_quizzes
from paper_digest.storage.database import (
    init_db,
    get_seen_ids,
    save_papers,
    mark_as_seen,
)


# ── Nodes ─────────────────────────────────────────────────────
# Each node receives the full state, does one job, returns updated state

def fetcher_node(state: PipelineState) -> PipelineState:
    """Fetch latest papers from arXiv."""
    print("📡 Fetching papers from arXiv...")
    try:
        categories = state.get("categories") or None
        papers = fetch_papers(categories=categories, max_results=10, days_back=7) if categories else fetch_papers(max_results=10, days_back=7)
        print(f"   Fetched {len(papers)} papers (categories: {categories or 'default'})")
        return {**state, "raw_papers": papers}
    except Exception as e:
        print(f"   Error: {e}")
        return {**state, "errors": state["errors"] + [f"fetcher: {e}"]}


def ranker_node(state: PipelineState) -> PipelineState:
    """Score each paper for relevance."""
    print("⭐ Ranking papers...")
    try:
        ranked = rank_papers(state["raw_papers"])
        print(f"   Ranked {len(ranked)} papers")
        for p in ranked[:3]:
            print(f"   [{p.score}] {p.title[:60]}...")
        return {**state, "ranked_papers": ranked}
    except Exception as e:
        print(f"   Error: {e}")
        return {**state, "errors": state["errors"] + [f"ranker: {e}"]}


def curator_node(state: PipelineState) -> PipelineState:
    """Pick top papers, skip already seen ones."""
    print("🎯 Curating papers...")
    try:
        seen_ids = get_seen_ids()           # load from SQLite
        selected = curate_papers(
            state["ranked_papers"],
            seen_ids=seen_ids,
        )
        print(f"   Selected {len(selected)} papers")
        return {**state, "selected_papers": selected}
    except Exception as e:
        print(f"   Error: {e}")
        return {**state, "errors": state["errors"] + [f"curator: {e}"]}


def notebook_node(state: PipelineState) -> PipelineState:
    """Generate study notes for each selected paper."""
    print("📓 Generating study notes...")
    try:
        enriched = generate_notes_for_papers(state["selected_papers"])
        print(f"   Generated notes for {len(enriched)} papers")
        return {**state, "enriched_papers": enriched}
    except Exception as e:
        print(f"   Error: {e}")
        return {**state, "errors": state["errors"] + [f"notebook: {e}"]}


def quiz_node(state: PipelineState) -> PipelineState:
    """Generate quiz questions for each paper."""
    print("❓ Generating quizzes...")
    try:
        quizzed = generate_quizzes(state["enriched_papers"])
        print(f"   Generated quizzes for {len(quizzed)} papers")
        return {**state, "enriched_papers": quizzed}
    except Exception as e:
        print(f"   Error: {e}")
        return {**state, "errors": state["errors"] + [f"quiz: {e}"]}


def storage_node(state: PipelineState) -> PipelineState:
    """Persist enriched papers to SQLite."""
    print("💾 Saving to database...")
    try:
        save_papers(state["enriched_papers"])
        mark_as_seen([p.id for p in state["enriched_papers"]])
        print(f"   Saved {len(state['enriched_papers'])} papers")
        return state
    except Exception as e:
        print(f"   Error: {e}")
        return {**state, "errors": state["errors"] + [f"storage: {e}"]}


# ── Conditional edges ─────────────────────────────────────────
# These decide whether to continue or stop early

def should_continue_after_fetch(state: PipelineState) -> str:
    if not state.get("raw_papers"):
        print("   No papers fetched, stopping.")
        return "end"
    return "continue"


def should_continue_after_curate(state: PipelineState) -> str:
    if not state.get("selected_papers"):
        print("   No papers selected, stopping.")
        return "end"
    return "continue"


# ── Graph builder ─────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(PipelineState)

    # register nodes
    graph.add_node("fetcher",  fetcher_node)
    graph.add_node("ranker",   ranker_node)
    graph.add_node("curator",  curator_node)
    graph.add_node("notebook", notebook_node)
    graph.add_node("quiz",     quiz_node)
    graph.add_node("storage",  storage_node)

    # entry point
    graph.set_entry_point("fetcher")

    # edges — with conditional checks
    graph.add_conditional_edges(
        "fetcher",
        should_continue_after_fetch,
        {"continue": "ranker", "end": END}
    )
    graph.add_edge("ranker",   "curator")
    graph.add_conditional_edges(
        "curator",
        should_continue_after_curate,
        {"continue": "notebook", "end": END}
    )
    graph.add_edge("notebook", "quiz")
    graph.add_edge("quiz",     "storage")
    graph.add_edge("storage",  END)

    return graph.compile()


# ── Entry point ───────────────────────────────────────────────

def run_pipeline(categories: list[str] = None) -> PipelineState:
    init_db()

    initial_state: PipelineState = {
        "raw_papers":      [],
        "ranked_papers":   [],
        "selected_papers": [],
        "enriched_papers": [],
        "run_date":        datetime.now().strftime("%Y-%m-%d"),
        "errors":          [],
        "categories":      categories or [],
    }

    print(f"\n🚀 Starting pipeline — {initial_state['run_date']}\n")
    graph = build_graph()
    final_state = graph.invoke(initial_state)

    print(f"\n✅ Pipeline complete")
    print(f"   Papers enriched: {len(final_state['enriched_papers'])}")
    if final_state["errors"]:
        print(f"   Errors: {final_state['errors']}")

    return final_state


if __name__ == "__main__":
    run_pipeline()