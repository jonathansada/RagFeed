import logging

# Import Settings
from settings import *

# Get RagFeedLogic
from src.RagFeedLogic import RagFeedLogic

# This class is the main controller of the app 
# Initializes everything the app needs to work and contains the endpoint for the clients
# To keep it clean, logic is stored in src.RagFeedLogic
class RagFeed:
    # Initializes application based on the settings
    def __init__(self):
        # Logger
        self.log = logging.getLogger(logger_path)
        self.log.setLevel(logger_level)
        self.log.addHandler(logging.FileHandler(logger_path, 'w'))

        # Initialize DB
        if database_engine == "sqlite":
            from src.sqliteDatabase import SqliteDatabase
            self.database = SqliteDatabase(sqlite_path, log=self.log)
        else:
            error = f"database_engine '{database_engine}' is not implemented"
            self.log.error(error)
            raise NotImplementedError(error)

        # Ollama
        if model_source == "ollama":
            from src.ollamaModel import OllamaModel
            self.model = OllamaModel(llm_model = ollama_llm, embeddings_model = ollama_embeddings, url = ollama_url, log = self.log)
        else:
            error = f"model_source '{model_source}' is not implemented"
            self.log.error(error)
            raise NotImplementedError(error)

        # Prepare ChromaDB
        if vector_store_engine == "chroma":
            from src.chromaVectorStore import ChromaVectorStore
            self.vectorstore = ChromaVectorStore(embeddings=self.model.embeddings, collection_name=chromadb_collection, persist_directory=chromadb_path, log=self.log)
        else:
            error = f"database_engine '{vector_db}' is not implemented"
            self.log.error(error)
            raise NotImplementedError(error)

        # Init RagFeedLogic
        self.ragfeedlogic = RagFeedLogic(db = self.database, vs = self.vectorstore, model=self.model, log=self.log, update_feq = feeds_update_freq)
        
        # Update sources 
        self.updateSources()

    # Updates the rss and 
    def updateSources(self):
        self.log.info("\nRagFeed.updateSources()")
        sourcesUpdated = self.ragfeedlogic.updateSources()
        if sourcesUpdated:
            self.ragfeedlogic.updateVectorStore()

    def askRag(self, search, num_docs=10):
        self.log.info("\nRagFeed.askRag()")

        # Get docs from vectorstore
        docs = self.vectorstore.search(search, k = num_docs)
        
        # Prepare contextx
        context = ""
        for doc in docs:
            context += "\nContent:\n"
            context += doc.page_content + "\n"
            context += str(doc.metadata) +"\n\n"

        # Ask the model to perform the inference
        result = self.model.summarizeArticles(question=search, context=context)

        return result  

    # TODO: Call it autmatically after updateSources() in an async way or through a cron
    def updateTopTopics(self):
        self.ragfeedlogic.updateTopTopics()

    def getTopTopics(self):
        self.log.info("\nRagFeed.getTopTopics()")
        return  self.ragfeedlogic.getTopTopics()

    def getSources(self):
        self.log.info("\nRagFeed.getSources()")
        return self.database.getSources()

    def getArticles(self):
        self.log.info("\nRagFeed.getArticles()")
        return self.database.getArticles()
