import os
import pathlib
import logging

from src.rssDocumentrLoader import RssDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import Settings
from settings import *

# This class controls the logic of the app and its used by the clients
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

        # Get Sources
        from src.sources import Sources
        self.sources = Sources(db = self.database, log=self.log, update_feq = feeds_update_freq)
        
        # Update sources 
        #self.updateVectorStore()
    
    # Reads the RSS stored in the feeds folder and update vectorstore
    def updateVectorStore(self):
        # Load XML into VectorStore
        self.log.info("RagFeed.updateVectorStore()")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        rssLoader = RssDocumentLoader()
        for file in os.listdir(feeds_path):
            if pathlib.Path(file).suffix.lower() == ".xml":
                self.log.debug(f"Adding file {file} in vector store")
                docs = rssLoader.load(xml_file = feeds_path + "/" + file)
                chunks = text_splitter.split_documents(docs)
                #self.vectorstore.add_documents(documents=chunks)
                self.log.debug(f"Added {len(chunks)} chunks")

    # Updates the rss and 
    def updateSources(self):
        self.log.info("RagFeed.updateSources()")
        if self.sources.updateArticles() > 0:
            self.updateVectorStore()

    def askRag(self, search, num_docs=10):
        self.log.info("RagFeed.askRag()")

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

    def getTopTopics(self):
        self.log.info("RagFeed.getTopTopics()")
        
        docs = []    
        from bs4 import BeautifulSoup
        for file in os.listdir(feeds_path):
            if pathlib.Path(file).suffix.lower() == ".xml":
                with open(feeds_path + "/" + file) as f:
                    soup = BeautifulSoup(f, 'xml')
                
                for item in soup.find_all('item'):
                    docs.append({"title": item.title.text, "link": item.link.text})

        return self.model.getTopTopics(docs)
