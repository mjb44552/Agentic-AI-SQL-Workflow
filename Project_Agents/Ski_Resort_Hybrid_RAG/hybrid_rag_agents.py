from agno.agent import Agent,RunResponse
from agno.models.openai import OpenAIChat
from agno.knowledge.document import DocumentKnowledgeBase,Document
from agno.vectordb.pgvector import PgVector

from pydantic import BaseModel

from helper_functions import get_db_credentials,create_or_update_db_table,build_sql_query,get_unique_values_dict,to_documents

from sql_toolkit import sql_toolkit

from sqlalchemy import VARCHAR, BOOLEAN, FLOAT, INTEGER

from data_processing import resort_traits_data 

print('getting database credentials')
db_user, db_password, db_host, db_port, db_name = get_db_credentials(database_name="RESORT_TRAITS")
vctdb_user, vctdb_password, vctdb_host, vctdb_port, vctdb_name = get_db_credentials(database_name="VCT")
print(get_db_credentials(database_name="VCT"))

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

print('updating database table with resort traits data')
create_or_update_db_table(db_user=db_user,
          db_password=db_password,
          db_host=db_host,
          db_port=db_port,
          db_name=db_name,
          data=resort_traits_data,
          dtype_dict=dtype_dict,
          table_name="ski_resorts")

#build document for agno schema 
schema_doc = Document(
    name="schema",
    content= ", ".join(list(dtype_dict.keys())),
    meta_data={
        "description": "This document contains the schema of the ski resorts database as a list of column names.",
    }
)

print('building list of documents for sql_input_agent knowledge base')
unique_values:dict = get_unique_values_dict(columns=['country','continent'], data=resort_traits_data)
documents:list = to_documents(dict=unique_values)

#adding schema docs to documents list 
documents.append(schema_doc)
print(documents)

print('building pgvector knowledge base for sql_input_agent')
knowledge_base = DocumentKnowledgeBase(
    documents=documents,
    vector_db=PgVector(
        table_name="unique_values",
        db_url = f"postgresql://{vctdb_user}:{vctdb_password}@{vctdb_host}:{vctdb_port}/{vctdb_name}",
    ),
)

#load databse
print('loading empty document knowledge base')
knowledge_base.load(recreate=True)

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
user_question = "What are the top 5 ski resorts in the United States with the highest max elevation?"
input_response:RunResponse = sql_input_agent.run(user_question)

print('processing sql_input_agent response')
keywords:dict = input_response.content.model_dump()
sql_query:str = build_sql_query(keywords)

print('running sql_output_agent')
output_query = user_question + '\n' + sql_query
print(output_query)
output_response:RunResponse = sql_output_agent.run(output_query)
print(output_response.content)




print('running sql_input_agent')
user_question = "What are the 20 ski resorts in the United States with the lowest max elevation return in ascending order?"
input_response:RunResponse = sql_input_agent.run(user_question)

print('processing sql_input_agent response')
keywords:dict = input_response.content.model_dump()
sql_query:str = build_sql_query(keywords)

print('running sql_output_agent')
output_query = user_question + '\n' + sql_query
print(output_query)
output_response:RunResponse = sql_output_agent.run(output_query)
print(output_response.content)




print('running sql_input_agent')
user_question = "Return 5 french ski resorts with more than 3 ski lifts and tell me the number of ski lifts at each resort."
input_response:RunResponse = sql_input_agent.run(user_question)

print('processing sql_input_agent response')
keywords:dict = input_response.content.model_dump()
sql_query:str = build_sql_query(keywords)

print('running sql_output_agent')
output_query = user_question + '\n' + sql_query
print(output_query)
output_response:RunResponse = sql_output_agent.run(output_query)
print(output_response.content)