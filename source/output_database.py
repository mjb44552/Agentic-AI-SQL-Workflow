
from pandas import DataFrame
from source.helper_functions import get_db_credentials, load_db_table

def update_output_sql_agent_database(dtype_dict:dict, database_name:str, new_data:DataFrame,debug_mode:bool=False) -> None:
    """
    Update the database with the resort traits data.

    Parameters:
        dtype_dict (dict): Dictionary mapping column names to SQLAlchemy types.
        database_name (str): Name of the database to update.
        new_data (pd.DataFrame): DataFrame containing the new data to be loaded into the database.
        debug_mode (bool): If True, print debug information.
    """
    #accessing postgres sql database credentials
    if debug_mode:
        print('getting database credentials')
    db_user, db_password, db_host, db_port, db_name = get_db_credentials(database_name=database_name)
    db_credentials = {
        'user': db_user,
        'password': db_password,
        'host': db_host,
        'port': db_port,
        'database': db_name
    }

    #reloading the table in the database with the new resort traits data
    if debug_mode:
        print('updating database table with resort traits data')
    load_db_table(db_user=db_user,
            db_password=db_password,
            db_host=db_host,
            db_port=db_port,
            db_name=db_name,
            data=new_data,
            dtype_dict=dtype_dict,
            table_name="ski_resorts")
    return db_credentials
    