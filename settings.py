# Logger
logger_path = "./log/ragfeed.log"
logger_level = 10# https://docs.python.org/3/library/logging.html#logging-levels

# Feeds
feeds_update_freq = 12 # hours

# Databases
vector_store_engine = "chroma"
chromadb_collection = "RagFeed"
chromadb_path = "./data/chroma/ragfeed"

database_engine = "sqlite"
sqlite_path = "./data/sqlite/ragfeed.db"

# Models
model_source = "ollama"
ollama_url = "http://localhost:11434/"
ollama_llm = "llama3.2:3b"
ollama_embeddings = "snowflake-arctic-embed2"