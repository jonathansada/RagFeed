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
        self.log.info("\n\n===================== RagFit Init ===================== \n")

        # Initialize DB
        if database_engine == "sqlite":
            from src.sqliteDatabase import SqliteDatabase
            self.database = SqliteDatabase(sqlite_path, log=self.log)
        else:
            error = f"RagFeed.__init__: database_engine '{database_engine}' is not implemented"
            self.log.error(error)
            raise NotImplementedError(error)

        # Ollama
        if model_source == "ollama":
            from src.ollamaModel import OllamaModel
            self.model = OllamaModel(llm_model = ollama_llm, embeddings_model = ollama_embeddings, url = ollama_url, log = self.log)
        else:
            error = f"RagFeed.__init__: model_source '{model_source}' is not implemented"
            self.log.error(error)
            raise NotImplementedError(error)

        # Prepare ChromaDB
        if vector_store_engine == "chroma":
            from src.chromaVectorStore import ChromaVectorStore
            self.vectorstore = ChromaVectorStore(embeddings=self.model.embeddings, collection_name=chromadb_collection, persist_directory=chromadb_path, log=self.log)
        else:
            error = f"RagFeed.__init__: database_engine '{vector_db}' is not implemented"
            self.log.error(error)
            raise NotImplementedError(error)

        # Init RagFeedLogic
        self.ragfeedlogic = RagFeedLogic(db = self.database, vs = self.vectorstore, model=self.model, log=self.log, update_feq = feeds_update_freq)
        
        # Update sources 
        self.updateSources()

    # Updates the rss and vectorstore
    # TODO Integrate this code in the cron
    def updateSources(self, force=False):
        self.log.info("\nRagFeed.updateSources()")
        sourcesUpdated = self.ragfeedlogic.updateSources(force)
        if sourcesUpdated:
            self.ragfeedlogic.updateVectorStore()
            return True
        return False

    # TODO It would be nice to be able to run this async and not need a specific cron process running apart
    def cronJob(self, force=False):
        # Update sources 
        try:
            if self.updateSources(force) or force==True:
                # Update Top Topics
                self.ragfeedlogic.updateTopTopics()
                # Update Saved Searches
                self.ragfeedlogic.updateRagSearches(num_docs=50) # Take more docs during cron work for more content.
            return "OK"
        except Exception as e:
            self.log.error("RagFeed.cronJob" + getattr(e, 'message', str(e)))
            return "KO"
            
    def askRag(self, search):
        self.log.info("\nRagFeed.askRag()")
        return self.ragfeedlogic.askRag(search, num_docs=10) # Do not take much docs for a Fast Inference

    def getRagSearches(self, search=False):
        self.log.info("\nRagFeed.getRagSearches()")
        return self.ragfeedlogic.getRagSearches()

    def delRagSearch(self, search):
        self.log.info("\nRagFeed.delRagSearches()")
        return self.database.delRagSearch(search)

    def getTopTopics(self):
        self.log.info("\nRagFeed.getTopTopics()")
        return  self.ragfeedlogic.getTopTopics()

    def getSources(self):
        self.log.info("\nRagFeed.getSources()")
        return self.database.getSources()

    def getArticles(self):
        self.log.info("\nRagFeed.getArticles()")
        return self.database.getArticles()
