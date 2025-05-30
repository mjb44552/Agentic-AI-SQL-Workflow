
from pandas import DataFrame
from .helper_functions import get_db_credentials, load_db_table

def build_output_sql_agent_database(dtype_dict:dict, database_name:str,table_name:str,new_data:DataFrame,debug_mode:bool=False) -> dict:
    """
    Update the database with the new data.
    This function automatically drops exsisting tables in the database and creates a new table with the new data.
    It uses the provided dtype_dict to define the data types of the columns in the new table.

    Parameters:
        dtype_dict (dict): Dictionary mapping column names to SQLAlchemy types.
        database_name (str): Database name in .env file. This value is the prefix for the environment variable (i.e. abcd_USER).
        table_name (str): Name of the table to be updated in the database. This table will be dropped and recreated with the new 
                          data or if it doesn't exist it will be created with the new data.
        new_data (pd.DataFrame): DataFrame containing the new data to be loaded into the database.
        debug_mode (bool): If True, print debug information.

    Returns:
        db_credentials(dict): Database credentials used to connect to the database. The keys are: user, password, host, port, database.
    """
    #accessing postgres sql database credentials
    if debug_mode:print('getting database credentials')
    db_credentials = get_db_credentials(database_name=database_name)

    #reloading the table in the database with the new resort traits data
    if debug_mode:print('updating database table with resort traits data')
    load_db_table(db_credentials=db_credentials,data=new_data,dtype_dict=dtype_dict,table_name=table_name)
    
    return db_credentials
    