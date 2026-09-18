from langgraph.graph import StateGraph, START, END
from backend.app.graph.state import ResearchState
from backend.app.graph.nodes import (
    search_node,
    source_selection_node,
    scrape_node,
    synthesize_node,
    write_node,
    critique_node,
    should_revise_router,
    revision_node,
    finalize_node,
)


def create_research_graph():
    workflow = StateGraph(ResearchState)

    # Add Nodes
    workflow.add_node("search", search_node)
    workflow.add_node("select_sources", source_selection_node)
    workflow.add_node("scrape", scrape_node)
    workflow.add_node("synthesize", synthesize_node)
    workflow.add_node("write", write_node)
    workflow.add_node("critique", critique_node)
    workflow.add_node("revise", revision_node)
    workflow.add_node("finalize", finalize_node)

    # Linear Edges
    workflow.add_edge(START, "search")
    workflow.add_edge("search", "select_sources")
    workflow.add_edge("select_sources", "scrape")
    workflow.add_edge("scrape", "synthesize")
    workflow.add_edge("synthesize", "write")
    workflow.add_edge("write", "critique")

    # Conditional Branching Quality Gate & Revision Loop
    workflow.add_conditional_edges(
        "critique",
        should_revise_router,
        {
            "revise": "revise",
            "finalize": "finalize",
        },
    )

    # Loop back from revise to critique
    workflow.add_edge("revise", "critique")

    # End
    workflow.add_edge("finalize", END)

    return workflow.compile()


research_graph = create_research_graph()
