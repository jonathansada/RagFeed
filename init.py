## APP INIT
# Import Settings
from settings import *

# Initialize DB
if database_engine == "sqlite":
    from src.sqliteDatabase import SqliteDatabase
    database = SqliteDatabase(sqlite_path)
else:
    raise NotImplementedError(f"database_engine '{database_engine}' is not implemented")

# Ollama
if model_source == "ollama":
    from src.ollamaModel import OllamaModel
    model = OllamaModel(llm_model = ollama_llm, embeddings_model = ollama_embeddings, url = ollama_url)
else:
    raise NotImplementedError(f"model_source '{model_source}' is not implemented")

# Prepare ChromaDB
if vector_store_engine == "chroma":
    from src.chromaVectorStore import ChromaVectorStore
    vectorstore = ChromaVectorStore(embeddings=model.getEmbeddings(), collection_name=chromadb_collection, persist_directory=chromadb_path)
else:
    raise NotImplementedError(f"database_engine '{vector_db}' is not implemented")

# Get Sources
from src.sources import Sources
sources = Sources(db = database)
sources.updateArticles()