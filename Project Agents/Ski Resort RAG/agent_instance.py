from agno.agent import Agent
from knowledge_base import kb
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=kb,
    goal=""" 
    Your goal is to provide the user with helpful and accurate information about 
    the ski resorts they enquire about.
    """,
    instructions= """
    General Instrunctions:
        1. Use the knowledge base to enhance your response by 
        giving the user specific facts,figures and statistics about the ski resorts
        they enquire about.

    Specific Instructions:
        1.If the knowledge base does not contain information relevent to the users 
        query, inform the user that you are unable to provide information. 
    """,
    add_references=True,
    search_knowledge=False,
    markdown=True,
)
