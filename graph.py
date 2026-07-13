import re
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from agents import build_search_agent, build_reader_agent, writer_chain, revise_chain, critic_chain


class ResearchState(TypedDict):
    topic: str
    search_results: str
    scraped_content: str
    report: str
    feedback: str
    score: int
    revision_count: int
    max_revisions: int
    score_threshold: int
    history: List[dict]


def extract_score(feedback: str) -> int:
    """Pulls the numeric score out of the critic's 'Score: X/10' line."""
    match = re.search(r"Score:\s*(\d+)\s*/\s*10", feedback)
    return int(match.group(1)) if match else 0


def search_node(state: ResearchState) -> ResearchState:
    agent = build_search_agent()
    result = agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {state['topic']}")]
    })
    state["search_results"] = result["messages"][-1].content
    return state


def scrape_node(state: ResearchState) -> ResearchState:
    agent = build_reader_agent()
    snippet = state["search_results"][:1000]
    result = agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{state['topic']}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{snippet}"
        )]
    })
    state["scraped_content"] = result["messages"][-1].content
    return state


def write_node(state: ResearchState) -> ResearchState:
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    if state["revision_count"] == 0:
        state["report"] = writer_chain.invoke({
            "topic": state["topic"],
            "research": research_combined,
        })
    else:

        state["report"] = revise_chain.invoke({
            "topic": state["topic"],
            "research": research_combined,
            "previous_report": state["report"],
            "feedback": state["feedback"],
        })
    return state


def critique_node(state: ResearchState) -> ResearchState:
    feedback = critic_chain.invoke({"report": state["report"]})
    state["feedback"] = feedback
    state["score"] = extract_score(feedback)
    state["history"].append({
        "revision": state["revision_count"],
        "report": state["report"],
        "feedback": feedback,
        "score": state["score"],
    })
    return state


def route_after_critique(state: ResearchState) -> str:
    """The decision point. This is what makes it agentic instead of a fixed chain."""
    if state["score"] >= state["score_threshold"]:
        return "end"
    if state["revision_count"] >= state["max_revisions"]:
        return "end"
    return "revise"


def increment_revision(state: ResearchState) -> ResearchState:
    state["revision_count"] += 1
    return state


def build_research_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("search", search_node)
    graph.add_node("scrape", scrape_node)
    graph.add_node("write", write_node)
    graph.add_node("critique", critique_node)
    graph.add_node("increment", increment_revision)

    graph.add_edge(START, "search")
    graph.add_edge("search", "scrape")
    graph.add_edge("scrape", "write")
    graph.add_edge("write", "critique")

    graph.add_conditional_edges(
        "critique",
        route_after_critique,
        {"end": END, "revise": "increment"},
    )
    graph.add_edge("increment", "write") 

    return graph.compile()


def run_research(topic: str, max_revisions: int = 2, score_threshold: int = 8) -> ResearchState:
    """Run to completion, return final state only."""
    app = build_research_graph()
    initial_state: ResearchState = {
        "topic": topic, "search_results": "", "scraped_content": "",
        "report": "", "feedback": "", "score": 0,
        "revision_count": 0, "max_revisions": max_revisions,
        "score_threshold": score_threshold, "history": [],
    }
    return app.invoke(initial_state)


def stream_research(topic: str, max_revisions: int = 2, score_threshold: int = 8):
    """Generator yielding state after every node runs — used for the live UI."""
    app = build_research_graph()
    initial_state: ResearchState = {
        "topic": topic, "search_results": "", "scraped_content": "",
        "report": "", "feedback": "", "score": 0,
        "revision_count": 0, "max_revisions": max_revisions,
        "score_threshold": score_threshold, "history": [],
    }
    for step_state in app.stream(initial_state, stream_mode="values"):
        yield step_state


if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    final = run_research(topic)
    print(f"\nFinal score: {final['score']}/10 after {final['revision_count']} revision(s)")
    print(final["report"])