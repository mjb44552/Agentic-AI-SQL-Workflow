from agent_instance import resort_agent
from agno.agent import Agent
from typing import List

def run_RAG_agent(agent:Agent,queries: List,recreate:bool = False) -> None:
    if recreate:
        agent.knowledge.load(recreate=True)

    if queries != None:
        for query in queries:
            agent.print_response(query, stream=False)
    else:
        print("No queries provided.")
    return 

    
# run_RAG_agent(resort_agent,queries=[
#     "Create a list of 5 USA Ski Resorts with the highest max elevation in the country, show descending order of their elevation.",
#     "Create a list of 5 USA Ski Resorts with the highest max elevation in the country, show descending order of their elevation.",
#     "Create a list of 5 USA Ski Resorts with the highest max elevation in the country, show descending order of their elevation.",
#     "Create a list of 5 USA Ski Resorts with the highest max elevation in the country, show descending order of their elevation.",
#     "Create a list of 5 USA Ski Resorts with the lowest max elevation in the country, show descending order of their elevation."],
#     recreate=False)

resort_agent.cli_app(markdown=True)

