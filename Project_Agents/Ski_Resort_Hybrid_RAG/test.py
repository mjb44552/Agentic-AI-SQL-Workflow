from data_processing import resort_traits_data 
from hybrid_rag_agents import dtype_dict
from sqlalchemy import VARCHAR

unique_values = {}
for key,value in dtype_dict.items():
    if value == VARCHAR:
        unique_values[key] = resort_traits_data[key].unique().tolist() 


