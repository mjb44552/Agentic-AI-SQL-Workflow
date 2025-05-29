from pathlib import Path
import pandas as pd
from source.helper_functions import read_data, clean_string_values, clean_bool_values,NaN_to_zero

resort_path = Path(r'data\ski_areas.csv')
country_continent_path = Path(r'data\country_continent.csv')

resort_use_cols = ['name','country','status','has_downhill','has_nordic','downhill_distance_km',
            'nordic_distance_km','vertical_m','min_elevation_m','max_elevation_m',
            'lift_count']

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

#convert cells with NaN in numerical columns to 0 
resort_traits_data = NaN_to_zero(data=resort_traits_data, columns=['downhill_distance_km', 'nordic_distance_km', 'vertical_m', 'min_elevation_m', 'max_elevation_m'])

resort_traits_data.reset_index(drop=True,inplace=True)

