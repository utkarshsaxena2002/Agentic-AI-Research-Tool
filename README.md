<<<<<<< HEAD
# 🔎 Agentic AI Research Tool

> A self-improving AI research assistant built with **LangGraph**, **LangChain**, and **OpenRouter** that searches the web, reads reliable sources, writes professional research reports, critiques its own output, and automatically revises until a desired quality score is achieved.

---

## 🚀 Overview

This project demonstrates an **Agentic AI workflow** where multiple specialized AI agents collaborate to produce high-quality research reports.

Instead of relying on a single prompt, the system follows an iterative reasoning process:



🔍 Autonomous web search using Tavily
📄 Automatic webpage scraping and content extraction
🤖 Multi-agent architecture using LangGraph
✍️ AI-generated structured research reports
🧐 Critic agent for quality evaluation
🔄 Automatic iterative revisions until quality threshold
📈 Live workflow visualization in Streamlit
📥 Download reports as Markdown
⚙️ Adjustable revision count and quality threshold



```

                ┌───────────────┐
                │ User Request  │
                └──────┬────────┘
                       │
               Search Agent
                       │
                       ▼
               Reader Agent
                       │
                       ▼
               Writer Agent
                       │
                       ▼
               Critic Agent
                       │
          Score ≥ Threshold?
              │           │
             Yes          No
              │           │
              ▼           ▼
        Final Report   Revise Agent
                          │
                          └───────┐
                                  │
                                  ▼
                             Writer Agent
=======
# Agentic-AI-Research-Tool
An Agentic AI Research Tool powered by LangGraph that autonomously searches the web, analyzes sources, writes research reports, critiques its own work, and iteratively improves the output using multi-agent collaboration.
>>>>>>> e650130ba6a4e9eda6353c4e3d71d744f0ac3cae
