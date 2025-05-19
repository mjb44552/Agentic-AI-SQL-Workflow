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

def binarise_bool_values(data:pd.DataFrame,columns:list) -> pd.DataFrame:
    """
    Clean the boolean values in the dataframe.

    Parameters:
        data (pd.DataFrame): The dataframe to be cleaned.
        columns (list): The list of columns to be cleaned.

    Returns:
        pd.DataFrame: The cleaned dataframe.
    """
    for col in columns:
        #set yes values to 1
        yes_mask = data[col].str.lower() == 'yes'
        data.loc[yes_mask, col] = 1
        #set no values to 0
        no_mask = data[col].str.lower() == 'no'
        data.loc[no_mask, col] = 0
    return data

country_continent_data = pd.read_csv(filepath_or_buffer = country_continent_path,usecols = ['Country','Continent'])
country_continent_data.columns = ['continent','country']

resort_website_data = pd.read_csv(filepath_or_buffer = resort_path,usecols = ['name','websites'])
resort_traits_data = read_data(resort_path,resort_use_cols)

# adding continent data to the resort traits data
resort_traits_data['country'] = resort_traits_data['country'].str.strip()
resort_traits_data['country'] = resort_traits_data['country'].str.lower()
resort_traits_data['name'] = resort_traits_data['name'].str.strip()
resort_traits_data['name'] = resort_traits_data['name'].str.lower()
resort_traits_data['lift_count'] = resort_traits_data['lift_count'].astype('Int64')
country_continent_data['country'] = country_continent_data['country'].str.strip()
country_continent_data['country'] = country_continent_data['country'].str.lower()
country_continent_data['continent'] = country_continent_data['continent'].str.strip()
country_continent_data['continent'] = country_continent_data['continent'].str.lower()

resort_traits_data = pd.merge(resort_traits_data, country_continent_data,on='country', how='inner')

resort_traits_data = binarise_bool_values(data = resort_traits_data,columns = ['has_downhill','has_nordic'])

#filtering data 
#remove ski resorts that are not operational
is_operational_mask = resort_traits_data['status'] == 'operating'
resort_traits_data = resort_traits_data[is_operational_mask]
print(resort_traits_data.shape)

#remove ski resorts that do not have downhill skiing
has_downhill_mask = resort_traits_data['has_downhill'] == 1
resort_traits_data = resort_traits_data[has_downhill_mask]
print(resort_traits_data.shape)

#remove ski resorts that don't have ski lifts
has_valid_ski_lift_entry_mask = pd.notna(resort_traits_data['lift_count'])
has_non_zero_ski_lift_count_mask = resort_traits_data['lift_count'] > 0
resort_traits_data = resort_traits_data[has_valid_ski_lift_entry_mask & has_non_zero_ski_lift_count_mask]
print(resort_traits_data.shape)

#remove ski resorts that don't have a valid name
has_valid_name_mask = resort_traits_data['name'].str.strip() != ''
resort_traits_data = resort_traits_data[has_valid_name_mask]

resort_traits_data.reset_index(drop=True,inplace=True)

print(resort_traits_data[['has_downhill','has_nordic','downhill_distance_km',
            'nordic_distance_km','vertical_m','min_elevation_m']].head(5))







