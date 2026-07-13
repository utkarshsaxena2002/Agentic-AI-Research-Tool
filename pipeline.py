import json
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


def run_research_pipeline(topic: str) -> dict:
    state = {"topic": topic}

    # ---- Step 1: Search Agent ----
    print("\n" + "=" * 50)
    print("Step 1 - Search agent is working ...")
    print("=" * 50)

    try:
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        state["search_results"] = search_result["messages"][-1].content
        print("\nSearch Result:\n", state["search_results"])
    except Exception as e:
        print(f"Search agent failed: {e}")
        state["search_results"] = ""

    # ---- Step 2: Reader Agent ----
    print("\n" + "=" * 50)
    print("Step 2 - Reader agent is scraping ...")
    print("=" * 50)

    try:
        reader_agent = build_reader_agent()
        search_snippet = state["search_results"][:1000]
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{search_snippet}"
            )]
        })
        state["scraped_content"] = reader_result["messages"][-1].content
        print("\nScraped Content:\n", state["scraped_content"])
    except Exception as e:
        print(f"Reader agent failed: {e}")
        state["scraped_content"] = ""

    # ---- Step 3: Writer Chain ----
    print("\n" + "=" * 50)
    print("Step 3 - Writer is drafting a report...")
    print("=" * 50)

    # BUG FIX: this previously used search_results twice and never
    # included the scraped content the reader agent actually produced.
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    try:
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined,
        })
        print("\nFinal Report:\n", state["report"])
    except Exception as e:
        print(f"Writer chain failed: {e}")
        state["report"] = ""

    # ---- Step 4: Critic Chain ----
    print("\n" + "=" * 50)
    print("Step 4 - Critic is reviewing the report ...")
    print("=" * 50)

    try:
        state["feedback"] = critic_chain.invoke({
            "report": state["report"]
        })
        print("\nCritic Feedback:\n", state["feedback"])
    except Exception as e:
        print(f"Critic chain failed: {e}")
        state["feedback"] = ""

    # Save the full run so a crash downstream never loses your work
    try:
        with open("last_run.json", "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Could not save run to file: {e}")

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)