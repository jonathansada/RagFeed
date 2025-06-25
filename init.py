## APP INIT
# Import Settings
from settings import *

# Get Sources
from src.sources import Sources
sources = Sources()

# Ollama
if model_source == "ollama":
    from src.ollamaModel import OllamaModel
    model = OllamaModel(llm_model = ollama_llm, embeddings_model = ollama_embeddings, url = ollama_url)
else:
    raise NotImplementedError(f"model_source '{model_source}' is not implemented")

# Prepare ChromaDB
if vector_db == "chroma":
    from src.chromaVectorStore import ChromaVectorStore
    vectorstore = ChromaVectorStore(embeddings=model.getEmbeddings(), collection_name=chromadb_collection, persist_directory=chromadb_path)
else:
    raise NotImplementedError(f"vector_db '{vector_db}' is not implemented")