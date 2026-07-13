from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_tool
import os
from dotenv import load_dotenv

load_dotenv()

# ---- Model Setup ----
required_env = ["model_name", "url", "OPENROUTER_API_KEY"]
missing = [v for v in required_env if not os.getenv(v)]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {missing}")

llm = ChatOpenAI(
    model=os.getenv("model_name"),
    base_url=os.getenv("url"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


# ---- Search Agent ----
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
    )


# ---- Reader Agent ----
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_tool],
    )


# ---- Writer Chain ----
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful responses."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}
Research Gathered:
{research}

Structure the report as:
    - Introduction
    - Key Findings (minimum 3 well-explained points)
    - Conclusion
    - Sources (list all URLs found in research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# ---- Critic Chain ----
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- .....

Areas to Improve:
- .....
- .....

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()


# ---- Revision Chain (used when critic score is below threshold) ----
revise_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer revising a report based on critic feedback. "
               "Address every point raised, do not ignore any of them."),
    ("human", """Topic: {topic}

Original Research:
{research}

Previous Report Draft:
{previous_report}

Critic Feedback:
{feedback}

Rewrite the report addressing every point in "Areas to Improve". Keep the same structure:
    - Introduction
    - Key Findings (minimum 3 well-explained points)
    - Conclusion
    - Sources (list all URLs found in research)

Be detailed, factual, and professional."""),
])

revise_chain = revise_prompt | llm | StrOutputParser()