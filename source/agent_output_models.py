from pydantic import BaseModel

class sql_input_agent_response_model(BaseModel):
    """
    Class outlining the response for the sql_input_agent.
    This class defines the structure of the expressions the AI 
    agent will generate for each keyword in the sql query.
    """
    SELECT: str
    FROM: str
    WHERE: str
    HAVING: str
    GROUPBY: str
    ORDERBY: str
    LIMIT: str

class sql_output_agent_response_model(BaseModel):
    """
    This class defines the structure of the response from the sql_output_agent.

    It inclides:
    - response: The human-readable summary of the SQL query results or if there is an error, an explanation of the error.
    - attempts: The number of attempts the agent made to generate a response.
    - error: A boolean indicating if an error occurred during the process.
    """
    response: str
    attempts: int
    error:bool