from agno.agent import Agent,RunResponse
from agno.models.openai import OpenAIChat

from pydantic import BaseModel

from helper_functions import get_db_credentials,create_or_update_db_table,build_sql_query

from sql_toolkit import sql_toolkit

from sqlalchemy import VARCHAR, BOOLEAN, FLOAT, INTEGER

from data_processing import resort_traits_data 

print('getting database credentials')
db_user, db_password, db_host, db_port, db_name = get_db_credentials(database_name="RESORT_TRAITS")

dtype_dict={"name": VARCHAR,
            "country": VARCHAR,
            "status": VARCHAR,
            "has_downhill": BOOLEAN,
            "has_nordic": BOOLEAN,
            "downhill_distance_km": FLOAT,
            "nordic_distance_km": FLOAT,
            "vertical_m": FLOAT,
            "min_elevation_m": FLOAT,
            "max_elevation_m": FLOAT,
            "lift_count": INTEGER,
            'continent': VARCHAR}

print('updating database table with resort traits data')
create_or_update_db_table(db_user=db_user,
          db_password=db_password,
          db_host=db_host,
          db_port=db_port,
          db_name=db_name,
          data=resort_traits_data,
          dtype_dict=dtype_dict,
          table_name="ski_resorts")

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

print('defining sql_input_agent')
sql_input_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    response_model=sql_output,
    markdown=True,
    goal= """
        To generate a SQL query for a postgres database containing the traits and chatacteristics of ski resorts. 
    """,
    instructions=f"""
        You are an AI agent that generates SQL queries for a postgres database containing the traits and characteristics of ski resorts.
        Your response should extract information to answer the question in the user's query. Your response should use the sql_output
        response model. This means you are only returning the expressions associated with each keyword in a standard SQL query. If a keyword
        isn't required for the query, you should return an empty string for that keyword. Use your knowledge base to get and understand
        the database's schema. Here is the schema of the database: 
        {dtype_dict} 
    """
)

print('defining sql_output_agent')
#instantiate the hybrid rag agent with the sql_toolkit
sql_output_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    show_tool_calls=True,
    tools= [sql_toolkit(
        db_user=db_user,
        db_password=db_password,
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
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

print('running sql_input_agent')
user_question = "What are the top 5 ski resorts in the united states with the highest max elevation?"
input_response:RunResponse = sql_input_agent.run(user_question)

print('processing sql_input_agent response')
keywords:dict = input_response.content.model_dump()
sql_query:str = build_sql_query(keywords)

print('running sql_output_agent')
output_query = user_question + '\n' + sql_query
print(output_query)
output_response:RunResponse = sql_output_agent.run(output_query)
print(output_response.content)
