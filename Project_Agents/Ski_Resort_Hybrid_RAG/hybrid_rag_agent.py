
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from pydantic import BaseModel

from agno.knowledge.json import JSONKnowledgeBase
from agno.vectordb.pgvector import PgVector

# Create a knowledge base for the sql schema stored in JSON format

sql_schema = JSONKnowledgeBase(
    path="data/json",
    vector_db=PgVector(
        table_name="sql_schema",
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
    ),
)
# Load the knowledge base: Comment after first run as the knowledge base is already loaded
sql_schema.load(upsert=True)

class sql_query_expressions(BaseModel):
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
    knowledge = sql_schema,
    response_model=sql_query_expressions,
    goal= """
        To generate a SQL query for a postgres database containing the traits and chatacteristics of ski resorts. 
    """,
    instructions="""
        You are an AI agent that generates SQL queries for a postgres database containing the traits and characteristics of ski resorts.
        Your response should extract information to answer the question in the user's query. Your response should use the sql_query_expressions
        response model. This means you are only returning the expressions associated with each keyword in a standard SQL query. If a keyword
        isn't required for the query, you should return an empty string for that keyword. Use your knowledge base to get and understand
        the database's schema. 
        """
    markdown=True)

