from source.hybrid_rag_agents import sql_input_agent, sql_output_agent
from source.helper_functions import query_sql_agents

practice_queries = ['What are the top 5 ski resorts in the United States with the highest max elevation?',
                    'What are the top 5 ski resorts in the Canada with the highest vertical drop?',
                    'What are the top 5 ski resorts in the United Kingdom with the most lifts?',
                    'What are the top 5 ski resorts in the Europe with the most downhill distance?',
                    'What are the top 5 ski resorts in the United States with the most nordic distance?']

responses = query_sql_agents(queries=practice_queries,
                             input_agent=sql_input_agent,
                             output_agent=sql_output_agent,
                             print_response=True)

