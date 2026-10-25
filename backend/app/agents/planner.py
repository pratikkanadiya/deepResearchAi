from typing import List

from pydantic import BaseModel, Field
from app.services.model import get_llm
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv


load_dotenv()

class ResearchPlan(BaseModel):
    topic: str = Field(
        description="The original research topic."
    )

    objective: str = Field(
        description="The main objective of the research."
    )

    research_questions: List[str] = Field(
        description="Important questions that the research should answer."
    )

    subtopics: List[str] = Field(
        description="Major subtopics that should be investigated."
    )

    search_queries: List[str] = Field(
        description="Search queries that research agents can use."
    )

    source_types: List[str] = Field(
        description="Useful source categories for this research."
    )

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert research planning agent.

Your job is to transform a user's research topic into
a comprehensive and logically organized research plan.

The plan will later be used by multiple research agents,
including:

1. Web Research Agent
2. Academic Research Agent
3. News Research Agent

Requirements:

- Understand the user's topic.
- Identify the main research objective.
- Break the topic into meaningful subtopics.
- Create research questions that the final report should answer.
- Generate useful and diverse search queries.
- Identify appropriate source categories.
- Avoid redundant questions and queries.
- Do not answer the research topic yourself.
- Only create the research plan.

The research plan should be practical for autonomous
multi-agent research.
"""
        ),
        (
            "human",
            """
Create a research plan for:

{topic}
"""
        ),
    ]
)


def create_research_plan(topic: str) -> ResearchPlan:

    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    structured_planner = get_llm().with_structured_output(
        ResearchPlan,
        method="json_schema",
        strict=False,
    )
    planner_chain = planner_prompt | structured_planner

    result = planner_chain.invoke(
        {
            "topic": topic.strip()
        }
    )

    return result


if __name__ == "__main__":

    topic = input(
        "Enter research topic: "
    )

    plan = create_research_plan(topic)

    print("\n" + "=" * 60)
    print("RESEARCH PLAN")
    print("=" * 60)

    print("\nTopic:")
    print(plan.topic)

    print("\nObjective:")
    print(plan.objective)

    print("\nResearch Questions:")

    for i, question in enumerate(
        plan.research_questions,
        start=1
    ):
        print(f"{i}. {question}")

    print("\nSubtopics:")

    for i, subtopic in enumerate(
        plan.subtopics,
        start=1
    ):
        print(f"{i}. {subtopic}")

    print("\nSearch Queries:")

    for i, query in enumerate(
        plan.search_queries,
        start=1
    ):
        print(f"{i}. {query}")

    print("\nSource Types:")

    for source in plan.source_types:
        print(f"- {source}")


