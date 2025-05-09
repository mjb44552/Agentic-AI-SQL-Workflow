from agno.agent import Agent
from knowledge_base import kb
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=kb,
    add_references=True,
    search_knowledge=False,
    markdown=True,
)
