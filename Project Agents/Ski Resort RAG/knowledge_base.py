from pathlib import Path
from agno.knowledge.csv import CSVKnowledgeBase
from agno.vectordb.pgvector import PgVector

#setting configuration settings for vector database
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
csv_path = Path(r'Data\ski_areas.csv')

kb = CSVKnowledgeBase(
    path=csv_path,
    vector_db=PgVector(
        table_name="ski_areas",
        db_url=db_url),
    num_documents=1,
)

# Load once without recreating
kb.load(recreate=False)