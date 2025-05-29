from agno.agent import Agent
from agno.models.openai import OpenAIChat
from pydantic import BaseModel
from source.helper_functions import query_sql_agents
from source.sql_toolkit import sql_toolkit
from sqlalchemy import VARCHAR, BOOLEAN, FLOAT, INTEGER
from source.input_knowledge_base import build_input_sql_agent_knowledge_base
from source.output_knowledge_base import update_output_sql_agent_database
from source.data_processing import resort_traits_data

dtype_dict={"name": VARCHAR,
            "country": VARCHAR,
            "has_nordic": BOOLEAN,
            "downhill_distance_km": FLOAT,
            "nordic_distance_km": FLOAT,
            "vertical_m": FLOAT,
            "min_elevation_m": FLOAT,
            "max_elevation_m": FLOAT,
            "lift_count": INTEGER,
            'continent': VARCHAR}

#vctdb credentials is a dictionary with the keys: user, password, host, port, database
knowledge_base, vctdb_credentials= build_input_sql_agent_knowledge_base(dtype_dict=dtype_dict,database_name="VCT",debug_mode=False)

db_credentials = update_output_sql_agent_database(dtype_dict=dtype_dict, database_name="Resort_Traits", new_data=resort_traits_data, debug_mode=False)

print('defining sql_output response model for sql_input_agent')
#create output model for AI Agent 
class sql_output(BaseModel):
    """
    Class to hold the variables for the SQL query.
    """
    SELECT: str
    FROM: str
    WHERE: str
    HAVING: str
    GROUPBY: str
    ORDERBY: str
    LIMIT: str

#load databse
print('loading empty document knowledge base')
knowledge_base.load(recreate=True)

print('defining sql_input_agent')
sql_input_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    response_model=sql_output,
    knowledge=knowledge_base,
    add_references=True,        #always pull information from vector database and add to user query
    search_knowledge=False,     #enable agentic rag
    show_tool_calls=True,
    markdown=True,
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
        """
    ]
)

print('defining sql_output_agent')
#instantiate the hybrid rag agent with the sql_toolkit
sql_output_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    show_tool_calls=True,
    tools= [sql_toolkit(
        db_user= db_credentials['user'],
        db_password= db_credentials['password'],
        db_host= db_credentials['host'],
        db_port= db_credentials['port'],
        db_name= db_credentials['database'],
        dtype_dict=dtype_dict,
        table_name="ski_resorts")],
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



