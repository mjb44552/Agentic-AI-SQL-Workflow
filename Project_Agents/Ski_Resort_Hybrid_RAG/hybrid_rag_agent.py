
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from pydantic import BaseModel

class sql_query_variables(BaseModel):
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
    

# Create our News Reporter with a fun personality
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    agent_id="Sandy Rivers from HIMYM",
    response_model=sql_query_variables,
    goal= """
        To generate a SQL query for a postgres database containing the traits and chatacteristics of ski resorts. 
    """,
    instructions="""
        You are an AI agent that generates SQL queries for a postgres database containing the traits and characteristics of ski resorts.
        Your response should extract from the database information required to answer the question outlined in the users query. 
        """
    markdown=True)

