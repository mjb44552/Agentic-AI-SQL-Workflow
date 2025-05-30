from pathlib import Path
from pandas import read_csv,DataFrame
from sqlalchemy import create_engine
import os
from agno.document.base import Document
from agno.agent import Agent
import re
import string

def read_data(path:Path,custom_usecols:list) -> DataFrame:
    """
    Load the data from the csv file and return a pandas dataframe.

    Parameters:
        path (Path): The path to the csv file.
        custom_usecols (list): The list of columns to be used from the csv file.

    Returns:
        pd.DataFrame: The loaded data as a pandas dataframe.
    """
    try:
        data = read_csv(filepath_or_buffer = path,usecols = custom_usecols)
        return data
    except FileNotFoundError:
        print(f"File not found: {path}")
        return None

def clean_bool_values(data:DataFrame,columns:list) -> DataFrame:
    """
    Clean the boolean values in the dataframe.

    Parameters:
        data (pd.DataFrame): The dataframe to be cleaned.
        columns (list): The list of columns to be cleaned.

    Returns:
        pd.DataFrame: The cleaned dataframe.
    """
    for col in columns:
        #set yes values to True
        yes_mask = data[col].str.lower() == 'yes'
        data.loc[yes_mask, col] = True
        #set no values to False
        no_mask = data[col].str.lower() == 'no'
        data.loc[no_mask, col] = False
        #set NaN values to False
        nan_mask = data[col].isna()
        data.loc[nan_mask, col] = False
    return data

def clean_string_values(data: DataFrame, columns: list) -> DataFrame:
    """
    Clean the string values in the dataframe.

    This involves:
    - Stripping whitespace from the beginning and end of the string.
    - Converting the string to lowercase.
    - Removing spaces from the string.
    - Removing all punctuation symbols from the string.

    Parameters:
        data (pd.DataFrame): The dataframe to be cleaned.
        columns (list): The list of columns to be cleaned.

    Returns:
        pd.DataFrame: The cleaned dataframe.
    """
    # Create a regular expression pattern to match any punctuation character.
    punctuation_pattern = re.compile(f"[{re.escape(string.punctuation)}]")

    for col in columns:
        # Ensure the column is of string type to apply string methods
        data[col] = data[col].astype(str)
        data[col] = data[col].str.strip()
        data[col] = data[col].str.lower()
        data[col] = data[col].str.replace(' ', '')
        # Add punctuation removal
        data[col] = data[col].str.replace(punctuation_pattern, '', regex=True)
    return data

def get_db_credentials(database_name)-> dict:
    """
    Get the database credentials from environment variables.

    Parameters:
        database_name (str): The name of the database which in the .env file is the prefix for the environment variable (i.e. abcd_DB_USER).

    Returns:
        db_credentials(dict): The databse credentials stored in a dictionary.
    """
    try:
        db_credentials = {
            'user': os.getenv(f"{database_name}_USER"),
            'password': os.getenv(f"{database_name}_PASSWORD"),
            'host': os.getenv(f"{database_name}_HOST"),
            'port': os.getenv(f"{database_name}_PORT"),
            'database': os.getenv(f"{database_name}_NAME")
        }

        # Check if all required environment variables are set
        for db_credential in db_credentials.values():
            if db_credential is None:
                raise ValueError(f"Database credentials are incorrect")
        
        return db_credentials
    except Exception as e:
        print(f"Error getting database credentials: {e}")
        return None
    
def load_db_table(db_credentials:dict,data:DataFrame,dtype_dict:dict,table_name:str) -> None:
    """
    Update the database with the new data.

    Parameters:
        db_credentials (dict): Dictionary containing the database credentials.
        data (pd.DataFrame): Data to be used for updating the database.
        dtype_dict (dict): Dictionary mapping column names to SQLAlchemy types.
    """
    try:
        connection_string = f"postgresql+psycopg2://{db_credentials['user']}:{db_credentials['password']}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['database']}"
        engine =  create_engine(connection_string)
        data.to_sql(name=table_name, con=engine, if_exists='replace', index=False, dtype= dtype_dict)
    except Exception as e:
        print(f"Error executing query: {e}")

def build_sql_query(keyword_dict:dict) -> str:
    """
    Build a SQL query from the keywords dictionary.

    Parameters:
        keywords (dict): The dictionary containing the keywords for the SQL query.

    Returns:
        str: The SQL query as a string.
    """
    sql_query = ""
    
    #iteratively build sql query
    for keyword in ['SELECT','FROM','WHERE','HAVING','GROUPBY','ORDERBY','LIMIT']:
        if keyword_dict[keyword] != '':
            sql_query = f"{sql_query} {str(keyword)} {str(keyword_dict[keyword])} "

    #format sql query 
    sql_query = sql_query.strip()
    sql_query = sql_query + ';'
    sql_query = sql_query.replace('  ', ' ')
    sql_query = sql_query.replace('ORDERBY', 'ORDER BY')
    sql_query = sql_query.replace('GROUPBY', 'GROUP BY')

    return sql_query

def get_unique_values_dict(columns:list, data:DataFrame) -> dict:
    """
    Takes a dictionary of column names and their SQLAlchemy types, and returns a dictionary with each 
    VARCHAR column name as the key and a list of unique values from that column in the DataFrame.

    Parameters:
        columns (list): A list of column names. 
        data (Dataframe): A Pandas DataFrame. 

    Returns:
        dict: A dictionary where keys are column names and values are lists of unique values.
    """
    unique_values_dict = {}
    for column in columns:
        unique_values_dict[column] = data[column].unique().tolist()
    return unique_values_dict

def to_documents(dict: dict) -> list:
    """
    Converts a dictionary of into a list of Agno Document objects. The key is used as the name of the document,
    and the values are the contents of the document.

    Parameters:
        unique_values_dict (dict): A dictionary where keys are column names and values are lists of unique values.

    Returns:
        list: A list of Document objects, each containing the unique values for a specific column.
    """
    documents = []
    for key, values in dict.items():
        content = f"Unique values for {key}: {', '.join(map(str, values))}"
        documents.append(Document(name=key + ' column',content=content, ))
    return documents

def query_sql_agents(queries:list,input_agent:Agent,output_agent:Agent,print_response:bool = False) -> list:
    """
    Function to run a list of queries through the sql_input_agent and sql_output_agent.

    Parameters:
        queries (list): A list of queries to run through the agents.
        input_agent(Agno.Agent): The agent responsible for processing the input queries.
        output_agent(Agno.Agent): The agent responsible for generating the SQL queries and processing the output.
        print_queries (bool): Whether to print the queries and responses. Default is False.
        
    Returns:
        results(list): A list of results from the sql_output_agent for each query.
    """
    results = []
    for query in queries:
        input_response = input_agent.run(query)
        keywords:dict = input_response.content.model_dump()
        sql_query:str = build_sql_query(keywords)
        output_query = query + '\n' + sql_query
        output_response = output_agent.run(output_query)
        results.append(output_response.content)
        if print_response:
            print(f"Query: {query}\n")
            print(f"SQL Query: {sql_query}\n")
            print(f"Response: {output_response.content}\n")
            print("\n")
    return results

def NaN_to_zero(data:DataFrame,columns:list) -> DataFrame:
    """
    Convert NaN values in specified columns of a DataFrame to zero.

    Parameters:
        data (pd.DataFrame): The DataFrame to be processed.
        columns (list): The list of columns in which NaN values should be replaced with zero.

    Returns:
        pd.DataFrame: The DataFrame with NaN values replaced by zero in the specified columns.
    """
    for col in columns:
        data[col] = data[col].fillna(0)
    return data

def get_input_sql_agent_documents(data:DataFrame,dtype_dict:dict,debug_mode:bool = False) -> list:
    """
    Build a list of documents for the sql_input_agent knowledge base.
    
    Parameters:
        data (pd.DataFrame): The DataFrame containing the data in the sql_input_agent's knowledge base.
        dtype_dict (dict): Dictionary mapping column names to SQLAlchemy types.
        debug_mode (bool): If True, print debug information.
    """
    #build document for agno schema
    if debug_mode: print('building schema document for sql_input_agent knowledge base')
    schema_doc = Document(
        name="schema",
        content= ", ".join(list(dtype_dict.keys())),
        meta_data={
            "description": "This document contains the schema of the ski resorts database as a list of column names.",
        }
    )

    #building documents containing unique values in database
    if debug_mode: print('building list of documents for sql_input_agent knowledge base')
    unique_values:dict = get_unique_values_dict(columns=['country','continent'], data=data)
    documents:list = to_documents(dict=unique_values)

    #adding schema docs to documents list 
    documents.append(schema_doc)

    return documents