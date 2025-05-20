from pathlib import Path
import pandas as pd

resort_path = Path(r'Data\ski_areas.csv')
country_continent_path = Path(r'Data\country_continent.csv')

resort_use_cols = ['name','country','status','has_downhill','has_nordic','downhill_distance_km',
            'nordic_distance_km','vertical_m','min_elevation_m','max_elevation_m',
            'lift_count']

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
        print(f"Data loaded from {path}")
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

#read and set columns for country_continent data
country_continent_data = pd.read_csv(filepath_or_buffer = country_continent_path,usecols = ['Country','Continent'])
country_continent_data.columns = ['continent','country']

#read resort website data 
resort_website_data = pd.read_csv(filepath_or_buffer = resort_path,usecols = ['name','websites'])

#read resort traits data
resort_traits_data = read_data(resort_path,resort_use_cols)

#clean string type columna in resort_traits_data
resort_traits_data = clean_string_values(data = resort_traits_data,columns = ['country','name'])
resort_traits_data = clean_bool_values(data = resort_traits_data,columns = ['has_downhill','has_nordic'])
resort_traits_data['lift_count'] = resort_traits_data['lift_count'].astype('Int64')

#clean strings in country_continent data
country_continent_data = clean_string_values(data = country_continent_data,columns = ['country','continent'])

resort_traits_data = pd.merge(resort_traits_data, country_continent_data,on='country', how='inner')


#filtering data 
#remove ski resorts that are not operational
is_operational_mask = resort_traits_data['status'] == 'operating'
resort_traits_data = resort_traits_data[is_operational_mask]

#remove ski resorts that do not have downhill skiing
has_downhill_mask = resort_traits_data['has_downhill'] == 1
resort_traits_data = resort_traits_data[has_downhill_mask]

#remove ski resorts that don't have ski lifts
has_valid_ski_lift_entry_mask = pd.notna(resort_traits_data['lift_count'])
has_non_zero_ski_lift_count_mask = resort_traits_data['lift_count'] > 0
resort_traits_data = resort_traits_data[has_valid_ski_lift_entry_mask & has_non_zero_ski_lift_count_mask]

#remove ski resorts that don't have a valid name
has_valid_name_mask = resort_traits_data['name'] != ''
resort_traits_data = resort_traits_data[has_valid_name_mask]

resort_traits_data.reset_index(drop=True,inplace=True)

resort_traits_data.to_csv(r'Project Agents\Ski Resort RAG\clean_data\resort_traits.csv',index=False)
resort_website_data.to_csv(r'Project Agents\Ski Resort RAG\clean_data\resort_websites.csv', index=False)







