from source.hybrid_rag_agents import sql_input_agent, sql_output_agent
from source.helper_functions import query_sql_agents

practice_queries = ['What is the elevation of breckonridge and vail Ski resorts?']

responses = query_sql_agents(queries=practice_queries,
                             input_agent=sql_input_agent,
                             output_agent=sql_output_agent,
                             print_response=True,
                             print_progess=True,)

