# Interact with the input/output application through running the query_sql_agents function.
#
# The query_sql_agents function has the following parameters and returns:
# Parameters:
#     input_agent(Agno.Agent): The agent responsible for processing the input queries.
#     output_agent(Agno.Agent): The agent responsible for generating the SQL queries and processing the output.
#     max_number_attempts (int): The maximum number of attempts to run the agents. Default is 3.
#     print_response (bool): Whether to print the queries and responses. Default is False.
#     print_progress (bool): Whether to print the messages outlining the progress of the agents. Default is False.

# Returns:
#     results(list(dict)): A list of results from the sql_output_agent where each query result is a list element 
#        in the form of the sql_output_agent_response dictionary.

#The input/output application utalises two Agno Agentic AI Agents. These are:
#   1. sql_input_agent: This agent is responsible for processing the input queries and generating the SQL queries.
#   2. sql_output_agent: This agent is responsible for generating the SQL queries and processing the output.

from source.hybrid_rag_agents import sql_input_agent, sql_output_agent
from source.query_agents import query_sql_agents

practice_queries = ['What is the elevation of breckenridge?',
                    'What is the average number of chairlifts at ski resorts in Canada?,'
                    'What ski resort in Italy has the largest elevation range?',
                    'How many ski resorts are in France and the United States?',]

responses = query_sql_agents(queries=practice_queries,
                             input_agent=sql_input_agent,
                             output_agent=sql_output_agent,
                             max_number_attempts=2,
                             print_response=True,
                             print_progess=True)

print(responses)