from agno.agent import Agent
from knowledge_base import kb
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o",temperature=0.4),
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
        2. Do not use other tools or sources of information to answer the users query.

    Specific Instructions:
        1.If the knowledge base does not contain information relevent to the users 
        query, inform the user that you are unable to provide information. 
        2. In your response, when describing the source of your information,say the source 
        of the information is 'ski_areas.csv'.
    """,
    add_references=True,
    search_knowledge=True,
    markdown=True,
)


