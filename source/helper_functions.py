from pathlib import Path
from pandas import read_csv,DataFrame
from sqlalchemy import create_engine
import os
from agno.document.base import Document
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
        database_name (str):  Database name in .env file. This value is the prefix for the environment variable (i.e. abcd_USER).

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

def get_input_sql_agent_documents(data:DataFrame,columns:list,dtype_dict:dict,debug_mode:bool = False) -> list:
    """
    Build a list of documents for the sql_input_agent knowledge base.

    The purpose of the knowledge base is to provide the sql_input_agent with the necessary information to generate SQL queries.
    Specifically, it helps the agent add syntactically correct SQL expressions to the query it generates. For example, with this
    knowledge base the agent knows that in the column, 'country' the 'United States' is referred to as 'united states' in the database.
    
    Parameters:
        data (pd.DataFrame): The DataFrame containing the data in the sql_input_agent's knowledge base.
        columns (list): The list of columns in the data parameter which will have it's unique values stored in the knowledge base.
        dtype_dict (dict): Dictionary mapping column names to SQLAlchemy types.
        debug_mode (bool): If True, print debug information.

    Returns:
        documents(list): A list of Document objects containing the schema and unique values from the DataFrame.
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

    #storing the unique values of each column in the data to a dictionary
    unique_values_dict = {}
    for column in columns:
        unique_values_dict[column] = data[column].unique().tolist()

    #converting the unique values of each column stored in a dictionary to a list of documents
    documents:list = to_documents(dict=unique_values_dict)

    #adding schema docs to documents list 
    documents.append(schema_doc)

    return documents
