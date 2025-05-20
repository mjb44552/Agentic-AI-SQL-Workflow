from pathlib import Path
from agno.knowledge.csv import CSVKnowledgeBase
from agno.vectordb.pgvector import PgVector

#setting configuration settings for vector database
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

csv_path = Path(r'Project_Agents\Ski_Resort_RAG\clean_data\resort_traits.csv')

#defining knowledge base
kb = CSVKnowledgeBase(
    path=csv_path,
    vector_db=PgVector(
        table_name="ski_areas",
        db_url=db_url,
        search_type='vector'),
    num_documents=5,
)

print('Knowledge base created')

#loading knowledge base
kb.load(recreate=False)

print('Knowledge base loaded')


