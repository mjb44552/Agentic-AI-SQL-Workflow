from .data_processing import resort_traits_data
from .helper_functions import get_db_credentials, get_input_sql_agent_documents
from agno.knowledge.document import DocumentKnowledgeBase,Document
from agno.vectordb.pgvector import PgVector

def build_input_sql_agent_knowledge_base(dtype_dict:dict,database_name:str,debug_mode:bool = False) -> DocumentKnowledgeBase:

    #accessing database credentials 
    if debug_mode: print('getting database credentials')
    vctdb_credentials:dict = get_db_credentials(database_name=database_name)

    #get list of documents for knowledge base
    if debug_mode: print('building documents list for sql_input_agent knowledge base')
    documents:list = get_input_sql_agent_documents(data = resort_traits_data,dtype_dict=dtype_dict,debug_mode=debug_mode)

    #initialising pgvector knowledge base
    if debug_mode: print('initialising pgvector knowledge base for sql_input_agent')
    knowledge_base = DocumentKnowledgeBase(
        documents=documents,
        vector_db=PgVector(
            table_name="unique_values",
            db_url = f"postgresql://{vctdb_credentials['user']}:{vctdb_credentials['password']}@{vctdb_credentials['host']}:{vctdb_credentials['port']}/{vctdb_credentials['database']}",
        )
    )

    return knowledge_base, vctdb_credentials





