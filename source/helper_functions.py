from pathlib import Path
from pandas import read_csv,DataFrame
from sqlalchemy import create_engine
import os
from agno.document.base import Document
from agno.agent import Agent
import re
import string
from typing import Optional

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

def query_sql_agents(queries:list,
                     input_agent:Agent,
                     output_agent:Agent,
                     max_number_attempts:int=3,
                     sql_output_agent_response:Optional[dict] = None,
                     print_response:bool = False,
                     print_progess:bool=False) -> list:
    """
    Function to run a list of queries through the sql_input_agent and sql_output_agent.

    Parameters:
        queries (list): A list of queries to run through the agents.
        input_agent(Agno.Agent): The agent responsible for processing the input queries.
        output_agent(Agno.Agent): The agent responsible for generating the SQL queries and processing the output.
        max_number_attempts (int): The maximum number of attempts to run the agents. Default is 3.
        sql_output_agent_response (optional[dict]): The response from the sql_input_agent. Default is None. If dict is provided, it is
               used to pass a incorrect response from the sql_output_agent into the query_sql_agents function for another attempt.The 
               dictionary keys are:
                1.user_query(str): The original user query.
                2.sql_query(str or None): The SQL query generated by the sql_input_agent in its previous attempt, if available.
                2.response_text(str or None): The previous response from the sql_output_agent, if available.
                3.attempts(int): The number of attempts made to generate a response, if available.
                4.error(bool): Indicates if an error occurred during the previous attempt, if available.
        print_response (bool): Whether to print the queries and responses. Default is False.
        print_progress (bool): Whether to print the messages outlining the progress of the agents. Default is False.
        
    Returns:
        results(list(dict)): A list of results from the sql_output_agent where each query result is a list element in the form of the
                 sql_output_agent_response dictionary.
    """
    results = []
    for user_query in queries:
        # building the sql_input_agent's query - if applicable using the previous sql_output_agent's response
        if print_progess: print(f"Building sql_input_agent's query from user query")
        sql_input_agent_query = build_sql_input_agent_query(user_query,sql_output_agent_response)

        # run the sql_input_agent
        if print_progess: print(f"Running sql_input_agent with user query.")
        sql_input_agent_response = input_agent.run(sql_input_agent_query)

        # extracting keywords from the sql_input_agent's response
        if print_progess: print(f"Extracting keywords from sql_input_agent's response.")
        keywords:dict = sql_input_agent_response.content.model_dump()

        # build the sql query for the sql_output_agent
        if print_progess: print(f"Building SQL query from keywords.")
        sql_query:str = build_sql_query(keywords)
        sql_output_agent_query = str({'user_query': user_query, 'sql_query': sql_query})

        # run the sql_output_agent
        if print_progess: print(f"Running sql_output_agent with SQL query.")
        sql_output_agent_response = output_agent.run(sql_output_agent_query)
        
        # converting sql_output_agent's response into a dictionary
        if print_progess: print(f"Extracting SQL data from sql_output_agent's response.")
        sql_output_agent_response:dict = sql_output_agent_response.content.model_dump()

        # check if the sql_output_agent's response contains an error
        if print_progess: print(f"Checking if sql_output_agent's response contains an error.")
        if sql_output_agent_response['error'] == True:
            # rerun the query_sql_agents function for another attempt
            sql_output_agent_response['attempts'] += 1
            while sql_output_agent_response['attempts'] < max_number_attempts:
                result = query_sql_agents(queries = [sql_input_agent_query],
                                          input_agent=input_agent,
                                          output_agent=output_agent,
                                          max_number_attempts=1,
                                          sql_output_agent_response=sql_output_agent_response['sql_query'],
                                          print_response=print_response,
                                          print_progess=print_progess)

        # print final response to user_query 
        if print_progess: print('Printing response to user query.')
        results.append(result)
        if print_response:
            print(f"User Query: {sql_output_agent_response['user_query']}\n")
            print(f"SQL Query: {sql_output_agent_response['sql_query']}\n")
            print(f"Response: {sql_output_agent_response['response_text']}\n")
            print("\n")
    return results

def build_sql_input_agent_query(user_query:str,sql_input_agent_respone:Optional[dict] = None) -> str:
    """
    Build the input query for the sql_input_agent. This function takes the user query and the previous response from the sql_input_agent 
    (if available) and builds the input query for the sql_input_agent. It returns a string representation of the input query which 
    is a dictionary with the following keys:
    - user_query(str): The original user query.
    - response_text(str or None): The previous response from the sql_output_agent, if available.
    - sql_query(str or None): The SQL query generated by the sql_input_agent in its previous attempt, if available.
    - attempts(int or None): The number of attempts made to generate a response, if available.
    - error(bool or None): Indicates if an error occurred during the previous attempt, if available.

    Parameters:
        user_query (str): The original user query.
        sql_input_agent_respone (optional[dict]): The response from the sql_input_agent. Default is None. If dict is provided, it is
               used to pass a incorrect response from the sql_output_agent into the build_input_query function for another attempt.
    
    Returns:
        input_query (str): The input query for the sql_input_agent as a string representation of a dictionary.
    """
    #building sql_input_agent's query when a previous attempt has already been made
    if sql_input_agent_respone:
        sql_input_agent_respone['user_query'] = user_query
        input_query =  str(sql_input_agent_respone)
    #building sql_input_agent's first query when no previous attempt has been made
    else:
        input_query = str({'user_query': user_query,'sql_query':None,'response_text': None, 'attempts': 0, 'error': False})
    return input_query

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
