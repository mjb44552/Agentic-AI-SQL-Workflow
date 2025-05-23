from pathlib import Path
from pandas import read_csv,DataFrame
from sqlalchemy import create_engine
import os
import json

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

def clean_string_values(data:DataFrame,columns:list) -> DataFrame:
    """
    Clean the string values in the dataframe.

    Parameters:
        data (pd.DataFrame): The dataframe to be cleaned.
        columns (list): The list of columns to be cleaned.

    Returns:
        pd.DataFrame: The cleaned dataframe.
    """
    for col in columns:
        data[col] = data[col].str.strip()
        data[col] = data[col].str.lower()
    return data

def get_db_credentials(database_name)-> tuple:
    """
    Get the database credentials from environment variables.

    Parameters:
        database_name (str): The name of the database which in the .env file is the prefix for the environment variable (i.e. abcd_DB_USER).

    Returns:
        db_credentials(tuple): The database credentials as a tuple.
    """
    try:
        #access environment variables
        db_user = os.getenv(f"{database_name}_DB_USER")
        db_password = os.getenv(f"{database_name}_DB_PASSWORD")
        db_host = os.getenv(f"{database_name}_DB_HOST")
        db_port = os.getenv(f"{database_name}_DB_PORT")
        db_name = os.getenv(f"{database_name}_DB_NAME")

        # Check if all required environment variables are set
        for db_credential in [db_user, db_password, db_host, db_port, db_name]:
            if db_credential is None:
                raise ValueError(f"Database credentials are incorrect")
        
        #return the database credentials if there are no errors
        db_credentials = (db_user, db_password, db_host, db_port, db_name)
        return db_credentials
    except Exception as e:
        print(f"Error getting database credentials: {e}")
        return None
    
def create_or_update_db_table(db_user:str,db_password:str,db_host:str,db_port:str,db_name:str,data:DataFrame,dtype_dict:dict,table_name:str) -> None:
    """
    Update the database with the new data.

    Parameters:
        db_user (str): Database username.
        db_password (str): Database password.
        db_host (str): Database host.
        db_port (str): Database port.
        db_name (str): Database name.
        data (pd.DataFrame): Data to be used for updating the database.
        dtype_dict (dict): Dictionary mapping column names to SQLAlchemy types.
    """
    try:
        connection_string = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine =  create_engine(connection_string)
        data.to_sql(name=table_name, con=engine, if_exists='replace', index=False, dtype= dtype_dict)
    except Exception as e:
        print(f"Error executing query: {e}")



