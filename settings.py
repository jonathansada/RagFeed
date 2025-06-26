# Feeds
feeds_path = "./data/feeds"

# Databases
vector_store_engine = "chroma"
chromadb_collection = "RagFeed"
chromadb_path = "./data/chroma/ragfeed"

database_engine = "sqlite"
sqlite_path = "./data/sqlite/ragfeed.db"

# Models
model_source = "ollama"
ollama_url = "http://localhost:11434/"
ollama_llm = ""
ollama_embeddings = "snowflake-arctic-embed2"