from agno.agent import Agent
from knowledge_base import kb
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o",temperature=0.7),
    knowledge=kb,
    goal=""" 
    Your goal is to provide the user with helpful and accurate information about 
    the ski resorts.
    """,
    instructions= """
    General Instrunctions:
        1. Use the knowledge base to give the user specific facts,figures and statistics about the ski resorts
        they enquire about.
        2. Do not use other tools or sources of information to answer the users query.

    Specific Instructions:
        1.If the knowledge base does not contain information relevent to the users 
        query, inform the user that you are unable to provide information. 
        2. In your response, when describing the source of your information,say the source 
        of the information is 'ski_areas.csv'.
    """,
    # 3 types of RAG implentations 
    add_references=True,        #always pull information from vector database and add to user query
    search_knowledge=False,     #at the agents discretion, pull information from the vector database and add to user query
    read_chat_history=False,    #always pull information from the vector database storing the chat history
    markdown=True,
    debug_mode=True             #prints the RAG augmented query  
)

print("Agent instance created")


