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
            "lift_count": INTEGER,
            }

#vctdb credentials is a dictionary with the keys: user, password, host, port, database
knowledge_base, vctdb_credentials = build_input_sql_agent_knowledge_base(new_data=resort_traits_data,
                                                                        dtype_dict=dtype_dict,
                                                                        database_name="VCTDB",
                                                                        columns=['country','continent'],
                                                                        debug_mode=False)

#db credentials is a dictionary with the keys: user, password, host, port, database
db_credentials = build_output_sql_agent_database(dtype_dict=dtype_dict, 
                                                  database_name="DB",
                                                  table_name= 'ski_resorts',
                                                  new_data=resort_traits_data, 
                                                  debug_mode=False)

#defining the sql_input_agent
sql_input_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    response_model=sql_input_agent_response_model,
    knowledge=knowledge_base,
    add_references=True,        #always pull information from vector database and add to user query
    search_knowledge=False,     #enable agentic rag
    show_tool_calls=False,
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
        Your response should use the sql_output response model. This means you are only returning the expressions associated with each keyword in a standard SQL query. If a keyword
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
    tools= [sql_toolkit(
        db_user= db_credentials['user'],
        db_password= db_credentials['password'],
        db_host= db_credentials['host'],
        db_port= db_credentials['port'],
        db_name= db_credentials['database'],
        dtype_dict=dtype_dict,
        table_name="ski_resorts")],
    debug_mode=False,
    goal= """
        To use the sql_toolkit to run SQL queries on a postgres database and then summarise the results in a human-readable format. 
    """,
    instructions="""
        You are an AI agent that runs the user's SQL query with your sql_toolkit to retrieve data from a postgres database.
        You then summarise the results in a human-readable format. The user's query will provide a question and the sql query.
        Summarise your results in a way that answer the user's question. If the query returns no results, you should
        return a message saying that no results were found and explain where the error occured.
    """,
    markdown=True)



