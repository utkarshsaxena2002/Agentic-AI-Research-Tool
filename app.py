import os
import streamlit as st

# Bridge Streamlit Cloud secrets into env vars so agents.py/tools.py's
# os.getenv() calls work identically locally (.env) and when deployed.
if hasattr(st, "secrets"):
    try:
        for k, v in st.secrets.items():
            os.environ[k] = str(v)
    except Exception:
        pass

from graph import stream_research

st.set_page_config(page_title="AI Research Agent", page_icon="🔎", layout="wide")

st.title("🔎 AI Research Agent")
st.caption("Multi-agent pipeline: search → scrape → write → critique → revise (LangGraph)")

with st.sidebar:
    st.header("Settings")
    max_revisions = st.slider("Max revisions", 0, 5, 2)
    score_threshold = st.slider("Score needed to stop", 1, 10, 8)
    st.divider()
    st.caption("Stack: LangChain · LangGraph · Tavily · BeautifulSoup")

topic = st.text_input(
    "Research topic",
    placeholder="e.g. Impact of quantum computing on modern cryptography",
)
run_button = st.button("Run Research", type="primary", use_container_width=True)

if run_button and topic.strip():
    status = st.status("Starting pipeline...", expanded=True)
    search_slot = st.empty()
    scrape_slot = st.empty()
    report_slot = st.empty()
    feedback_slot = st.empty()

    seen_search = seen_scrape = False
    score_history = []
    final_state = None

    for state in stream_research(topic, max_revisions=max_revisions, score_threshold=score_threshold):
        final_state = state

        if state.get("search_results") and not seen_search:
            status.update(label="Searching the web...")
            with search_slot.expander("🔍 Search results", expanded=False):
                st.text(state["search_results"])
            seen_search = True

        if state.get("scraped_content") and not seen_scrape:
            status.update(label="Reading source page...")
            with scrape_slot.expander("📄 Scraped content", expanded=False):
                st.text(state["scraped_content"][:2000])
            seen_scrape = True

        if state.get("report"):
            status.update(label=f"Drafting report (revision {state['revision_count']})...")
            with report_slot.container():
                st.subheader(f"📝 Report — revision {state['revision_count']}")
                st.markdown(state["report"])

        if state.get("feedback"):
            status.update(label=f"Critic scored it {state['score']}/10")
            with feedback_slot.container():
                st.subheader(f"🧐 Critic feedback — score {state['score']}/10")
                st.markdown(state["feedback"])
            score_history.append(state["score"])

    status.update(label="Done", state="complete")

    if final_state:
        st.divider()
        if len(score_history) > 1:
            st.subheader("📊 Score across revisions")
            st.line_chart(score_history)

        st.download_button(
            "⬇️ Download final report (.md)",
            data=final_state["report"],
            file_name=f"{topic.strip().replace(' ', '_')}_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

elif run_button:
    st.warning("Enter a topic first.")