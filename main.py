from source.hybrid_rag_agents import sql_input_agent, sql_output_agent
from source.query_agents import query_sql_agents

practice_queries = ['What is the of breckonridge and cooooper Ski resorts in Canada?']

responses = query_sql_agents(queries=practice_queries,
                             input_agent=sql_input_agent,
                             output_agent=sql_output_agent,
                             max_number_attempts=4,
                             print_response=True,
                             print_progess=True)

print(responses)

