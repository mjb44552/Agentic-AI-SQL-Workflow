from agent_instance import agent
from agno.agent import Agent
from typing import Optional,List

def run_RAG_agent(agent:Agent,queries: List,recreate:bool = False) -> None:
    if recreate:
        agent.knowledge.load(recreate=True)

    if queries != None:
        for query in queries:
            agent.print_response(query, stream=False)
    else:
        print("No queries provided.")
    return 

    
run_RAG_agent(agent,queries=[
    "Create a list of 5 USA Ski Resorts with the highest max elevation in the country, show descending order of their elevation.",
    "Create a list of 5 USA Ski Resorts with the highest max elevation in the country, show descending order of their elevation. "],
    recreate=False)


