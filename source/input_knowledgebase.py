from source.data_processing import resort_traits_data
from source.helper_functions import get_db_credentials,get_unique_values_dict,to_documents
from agno.knowledge.document import DocumentKnowledgeBase,Document
from agno.vectordb.pgvector import PgVector

def build_input_sql_agent_knowledge_base(dtype_dict:dict,database_name:str,debug_mode:bool = False) -> DocumentKnowledgeBase:

    #accessing database credentials 
    if debug_mode: 
        print('getting database credentials')

    vctdb_user, vctdb_password, vctdb_host, vctdb_port, vctdb_name = get_db_credentials(database_name=database_name)
    vctdb_credentials ={'user': vctdb_user,
                        'password': vctdb_password,
                        'host': vctdb_host,
                        'port': vctdb_port,
                        'database': vctdb_name}

    #build document for agno schema
    if debug_mode: 
        print('building schema document for sql_input_agent knowledge base')

    schema_doc = Document(
        name="schema",
        content= ", ".join(list(dtype_dict.keys())),
        meta_data={
            "description": "This document contains the schema of the ski resorts database as a list of column names.",
        }
    )

    #building documents for sql_input_agent knowledgebase based of unique values in the resort traits data
    if debug_mode: 
        print('building list of documents for sql_input_agent knowledge base')

    unique_values:dict = get_unique_values_dict(columns=['country','continent'], data=resort_traits_data)
    documents:list = to_documents(dict=unique_values)

    #adding schema docs to documents list 
    documents.append(schema_doc)

    #initialising pgvector knowledge base
    if debug_mode: 
        print('initialising pgvector knowledge base for sql_input_agent')

    knowledge_base = DocumentKnowledgeBase(
        documents=documents,
        vector_db=PgVector(
            table_name="unique_values",
            db_url = f"postgresql://{vctdb_user}:{vctdb_password}@{vctdb_host}:{vctdb_port}/{vctdb_name}",
        ),
    )

    return knowledge_base, vctdb_credentials




