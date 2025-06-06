from agno.agent import Agent
from agno.models.openai import OpenAIChat
from.agent_output_models import sql_input_agent_response_model, sql_output_agent_response_model
from .sql_toolkit import sql_toolkit
from sqlalchemy import VARCHAR, FLOAT, INTEGER
from .input_knowledgebase import build_input_sql_agent_knowledge_base
from .output_database import build_output_sql_agent_database
from .data_processing import resort_traits_data

dtype_dict={"name": VARCHAR,
            "country": VARCHAR,
            'continent': VARCHAR,
            "downhill_distance_km": FLOAT,
            "nordic_distance_km": FLOAT,
            "vertical_m": FLOAT,
            "min_elevation_m": FLOAT,
            "max_elevation_m": FLOAT,
            "lift_count": INTEGER}

#vctdb credentials is a dictionary with the keys: user, password, host, port, database
knowledge_base, vctdb_credentials = build_input_sql_agent_knowledge_base(new_data=resort_traits_data,
                                                                        dtype_dict=dtype_dict,
                                                                        database_name="VCTDB",
                                                                        columns=['country','continent'],
                                                                        debug_mode=False)

#db credentials is a dictionary with the keys: user, password, host, port, database
db_table_name = 'ski_resorts'
db_credentials = build_output_sql_agent_database(dtype_dict=dtype_dict, 
                                                  database_name="DB",
                                                  table_name= db_table_name,
                                                  new_data=resort_traits_data, 
                                                  debug_mode=False)

#defining the sql_input_agent
sql_input_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    response_model=sql_input_agent_response_model,
    knowledge=knowledge_base,
    add_references=True,        #always pull information from vector database and add to user query
    markdown=True,
    debug_mode=False,
    goal= """
        To generate a SQL query for a postgres database containing the traits and chatacteristics of ski resorts. 
    """,
    instructions=[
        """
        You are an AI agent that generates SQL queries for a postgres database containing the traits and characteristics of ski resorts.
        Your response should extract information to answer the question in the user's query.
        """,
        """
        You will receive your input as a JSON string. This JSON will contain two fields:
          - 'user_query': The user's original request in natural language.
          - 'sql_queries': A list of previous SQL queries that have been attempted and failed. If this list is empty, it's the first attempt.
        """,
        """
        Generate your sql query based off the question in the 'user_query' key of the input dictionary and recognise that the 'sql_queries' key
        may contain a list of previous attempts at generating a correct sql query. Therefor, if there are previous sql_queries 
        make your new sql query slightly different (but still consistent with the database schema in your knowledge base).
        """,
        """ 
        Your response must always the sql_output response model. This means you are only returning the expressions associated with each keyword in a standard SQL query. If a keyword
        isn't required for the query, you should return an empty string for that keyword.
        """,
        """ 
        Use your knowledge base to understand the schema of the database tables ensure you use the correct column names when 
        building your query.
        """,
        """
        The user's query will reference specific countries, continents, names or traits of ski resorts. When using
        these references utalise your knowledge base to find the correct syntax to use in the SQL query. For example, 
        the 'UK' should be referenced as 'united kingdom' in the SQL query.
        """,
        """
        Columns with data types VARCHAR have been preprocessed. This involved removing all spaces from the string, converting the 
        string to lowercase, removing all punctuation characters.
        """,
        """
        Be aware that the name of ski resorts in the database may not match the name in the user's query exactly. For example, The 
        user may input 'Copper' but the database stores 'Copper Mountain'. Search if the users ski resort name is a substring of the name 
        in the database.
        """
    ]
)

#instantiate the hybrid rag agent with the sql_toolkit
sql_output_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    show_tool_calls=False,
    response_model=sql_output_agent_response_model,
    tools= [sql_toolkit(
        db_user= db_credentials['user'],
        db_password= db_credentials['password'],
        db_host= db_credentials['host'],
        db_port= db_credentials['port'],
        db_name= db_credentials['database'],
        dtype_dict=dtype_dict,
        table_name=db_table_name)],
    debug_mode=False,
    goal= """
        To use the sql_toolkit to run SQL queries on a postgres database and then summarise the results in a human-readable format. 
    """,
    instructions=["""
        You are an AI agent that runs the inputted sql_query with your sql_toolkit to retrieve data from a postgres database.
        You then summarise the results in a human-readable format. 
        """,
        """
        Your input is a string representation of a Python dictionary. The keys to this dictionary are:
        - user_query(str): The user's question which the sql query will answer.
        - sql_query(str): The SQL query generated by the sql_input_agent.
        """,
        """
        Your response must use the sql_output response model. This means you are returning the following:
        - user_query: The user's question you were inputted.
        - sql_query: The SQL query you were inputted.
        - response_text: A human-readable summary of the SQL query results. 
        - error: A boolean indicating if an error occurred during the process.
        """,
        """
        If after using your sql_toolkit you don't get all the information required to fully and completely anser the user's query,
        you must set the 'error' key to True. 
        """,
        """
        If after using your sql_toolkit you don't get all the information required to fully and completely anser the user's query,
        you must set 'response_text' key to a string that explains the error and what information is missing.
        """],
    markdown=True)



