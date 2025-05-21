from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, Engine

def read_data(path:Path,custom_usecols:list) -> pd.DataFrame:
    """
    Load the data from the csv file and return a pandas dataframe.

    Parameters:
        path (Path): The path to the csv file.
        custom_usecols (list): The list of columns to be used from the csv file.

    Returns:
        pd.DataFrame: The loaded data as a pandas dataframe.
    """
    try:
        data = pd.read_csv(filepath_or_buffer = path,usecols = custom_usecols)
        return data
    except FileNotFoundError:
        print(f"File not found: {path}")
        return None

def clean_bool_values(data:pd.DataFrame,columns:list) -> pd.DataFrame:
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

def clean_string_values(data:pd.DataFrame,columns:list) -> pd.DataFrame:
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

def resort_traits_to_sql(data:pd.DataFrame,
                         engine:Engine,
                         table_name:str,
                         custom_dtype_dict:dict) -> None:
    """
    Load the dataframe to a sql database.

    Parameters:
        data (pd.DataFrame): The dataframe to be loaded.
        engine (Engine): The sql alchemy engine.
        table_name (str): The name of the table in the database.
    """
    try:
        data.to_sql(name=table_name, 
                    con=engine, 
                    if_exists='replace', 
                    index=False,
                    dtype= custom_dtype_dict)
        print(f"Data loaded to {table_name} table in the database.")
    except Exception as e:
        print(f"Error loading data to SQL: {e}")