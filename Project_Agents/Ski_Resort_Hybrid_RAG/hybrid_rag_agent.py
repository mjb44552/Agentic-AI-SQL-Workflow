from agno.agent import Agent
from agno.models.openai import OpenAIChat

from pydantic import BaseModel

from agno.knowledge.json import JSONKnowledgeBase
from agno.vectordb.pgvector import PgVector

from helper_functions import get_db_credentials,create_or_update_db_table,write_json_to_file

from sql_toolkit import sql_toolkit

from sqlalchemy import VARCHAR, BOOLEAN, FLOAT, INTEGER

from data_processing import resort_traits_data 

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
            "lift_count": INTEGER}

create_or_update_db_table(db_user=db_user,
          db_password=db_password,
          db_host=db_host,
          db_port=db_port,
          db_name=db_name,
          data=resort_traits_data,
          dtype_dict=dtype_dict,
          table_name="ski_resorts")

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

#instantiate the hybrid rag agent with the sql_toolkit
sql_output_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    response_model=sql_output,
    tools= [sql_toolkit(
        db_user=db_user,
        db_password=db_password,
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
        dtype_dict=dtype_dict,
        table_name="ski_resorts")],
    goal= """
        To generate a SQL query for a postgres database containing the traits and chatacteristics of ski resorts. 
    """,
    instructions="""
        You are an AI agent that generates SQL queries for a postgres database containing the traits and characteristics of ski resorts.
        Your response should extract information to answer the question in the user's query. Your response should use the sql_output
        response model. This means you are only returning the expressions associated with each keyword in a standard SQL query. If a keyword
        isn't required for the query, you should return an empty string for that keyword. Use your knowledge base to get and understand
        the database's schema. 
    """,
    markdown=True)

