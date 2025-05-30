from .data_processing import resort_traits_data
from .helper_functions import get_db_credentials, get_input_sql_agent_documents
from agno.knowledge.document import DocumentKnowledgeBase,Document
from agno.vectordb.pgvector import PgVector
from typing import Tuple, List

def build_input_sql_agent_knowledge_base(dtype_dict:dict,database_name:str,columns:List[str],debug_mode:bool = False) -> Tuple[DocumentKnowledgeBase, dict]:
    """
    This function builds the knowledge base for the sql_input_agent.
    The purpose of the knowledge base is to provide the sql_input_agent with the necessary information to generate SQL queries.
    Specifically, it helps the agent add syntactically correct SQL expressions to the query it generates. For example, with this
    knowledge base the agent knows that in the column, 'country' the 'United States' is referred to as 'united states' in the database.

    It uses the data which will be loaded into the sql_output_agent's database and creates two types of documents which are:
    1. Documents containing the unique values for each column in the columns parameter. 
    2. A document containing the schema of the database table.

    Parameters:
        dtype_dict (dict): Dictionary mapping column names to SQLAlchemy types.
        database_name (str): Database name in .env file. This value is the prefix for the environment variable (i.e. abcd_USER).
        columns (List[str]): List of columns whose unique values will be used to create documents for the knowledge base.
        debug_mode (bool): If True, print debug information.

    Returns:
        knowledge_base (DocumentKnowledgeBase): The knowledge base for the sql_input_agent.
        vctdb_credentials (dict): Database credentials used to connect to the vector database. 
                                  The keys are: user, password, host, port, database.
    """
    #accessing database credentials 
    if debug_mode: print('getting database credentials')
    vctdb_credentials:dict = get_db_credentials(database_name=database_name)

    #get list of documents for knowledge base
    if debug_mode: print('building documents list for sql_input_agent knowledge base')
    documents:list = get_input_sql_agent_documents(data = resort_traits_data,
                                                   columns=columns,
                                                   dtype_dict=dtype_dict,
                                                   debug_mode=debug_mode)

    #initialising pgvector knowledge base
    if debug_mode: print('initialising pgvector knowledge base for sql_input_agent')
    knowledge_base = DocumentKnowledgeBase(
        documents=documents,
        vector_db=PgVector(
            table_name="unique_values",
            db_url = f"postgresql://{vctdb_credentials['user']}:{vctdb_credentials['password']}@{vctdb_credentials['host']}:{vctdb_credentials['port']}/{vctdb_credentials['database']}",
        )
    )
    #load databse
    knowledge_base.load(recreate=True)

    return knowledge_base, vctdb_credentials





