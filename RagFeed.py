import os
import pathlib
import logging

from langchain_community.document_loaders.xml import UnstructuredXMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import Settings
from settings import *

# This class controls the logic of the app and its used by the clients
class RagFeed:
    # Initializes application based on the settings
    def __init__(self):
        # Logger
        logging.basicConfig(filename='./log/ragfeed.log', encoding='utf-8', level=logging.DEBUG)
        self.log = logging

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
            self.vectorstore = ChromaVectorStore(embeddings=self.model.getEmbeddings(), collection_name=chromadb_collection, persist_directory=chromadb_path, log=self.log)
        else:
            error = f"database_engine '{vector_db}' is not implemented"
            self.log.error(error)
            raise NotImplementedError(error)

        # Get Sources
        from src.sources import Sources
        self.sources = Sources(db = self.database, log=self.log, update_feq = feeds_update_freq)

        self.updateVectorStore()
    
    # Reads the RSS stored in the feeds folder and update vectorstore
    def updateVectorStore(self):
        # Load XML into VectorStore
        self.log.debug("RagFeed.updateVectorStore()")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        for file in os.listdir(feeds_path):
            if pathlib.Path(file).suffix.lower() == ".xml":
                self.log.debug(f"Adding file {file} in vector store")
                xmlLoader = UnstructuredXMLLoader(file_path = feeds_path + "/" + file, mode = "elements")
                docs = self.vectorstore.document_preprocess(xmlLoader.load())
                chunks = text_splitter.split_documents(docs)
                self.vectorstore.add_documents(documents=chunks)
                self.log.debug(f"Added {len(chunks)} chunks")

    # Updates the rss and 
    def updateSources(self):
        self.log.debug("RagFeed.updateSources()")
        if self.sources.updateArticles() > 0:
            self.updateVectorStore()

    def searchRelated(self, search, num_docs=10):
        self.log.debug("RagFeed.searchRelated()")
        return self.vectorstore.search(search, k = num_docs) 