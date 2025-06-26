import os
import pathlib
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from bs4 import BeautifulSoup

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
        self.log.debug("RagFeed.updateVectorStore()")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        for file in os.listdir(feeds_path):
            if pathlib.Path(file).suffix.lower() == ".xml":
                self.log.debug(f"Adding file {file} in vector store")
                docs = self.rssLoader(xml_file = feeds_path + "/" + file)
                chunks = text_splitter.split_documents(docs)
                self.vectorstore.add_documents(documents=chunks)
                self.log.debug(f"Added {len(chunks)} chunks")

    def rssLoader(self, xml_file):
        with open(xml_file) as f:
            soup = BeautifulSoup(f, 'xml')

        docs = []         
        for item in soup.find_all('item'):
            metadata = {}
            metadata["url"] = item.link.text
            if item.creator:
                metadata["creator"] = item.creator.text
            if item.pubDate:
                metadata["publication"] = item.pubDate.text
            if item.category:
                metadata["categories"] = ", ".join([cat.text for cat in item.find_all('category')])
            if item.credit:
                metadata["credit"] = item.credit.text

            docs.append(Document(
                page_content=f"{item.title.text}\n{"\n".join([desc.text for desc in item.find_all('description')])}",
                metadata=metadata
            ))
        return docs

    # Updates the rss and 
    def updateSources(self):
        self.log.debug("RagFeed.updateSources()")
        if self.sources.updateArticles() > 0:
            self.updateVectorStore()

    def searchRelated(self, search, num_docs=10):
        self.log.debug("RagFeed.searchRelated()")
        #return self.vectorstore.search(search, k = num_docs) 

        messages = [('user', self.get_prompt(search, self.vectorstore.search(search, k = num_docs)))]
        completion = self.model.chat.invoke(messages)

        return completion.content

    def get_prompt(self, question, docs):
        context = ""
        for doc in docs:
            context += "\nContent:\n"
            context += doc.page_content + "\n"
            context += str(doc.metadata) +"\n\n"

        return f"""## SYSTEM ROLE
                You are a chatbot designed to summarize and classify articles comming from RSS sources.
                Your answers must be based exclusively on provided content.

                ## USER QUESTION
                The user has asked:
                "{question}"

                ## CONTEXT
                Here is the relevant content from the RSS Sources:
                '''
                {context}
                '''

                ## GUIDELINES
                1. **Accuracy**:
                - Only use the content in the `CONTEXT` section to answer.
                - If the answer cannot be found, explicitly state: "The provided context does not contain this information."

                2. **Transparency**:
                - Reference the articles title and url (in context) when providing information.
                - Do not speculate or provide opinions.

                3. **Clarity**:
                - Use simple, professional, and concise language.
                - Format your response in Markdown for readability.

                ## TASK
                1. Provide a summary of the relevant information in context related to user's question.
                2. Point the user to relevant parts of the articles in context.
                3. Provide the response in the following format:

                ## RESPONSE FORMAT
                '''
                # [Headline sumarizing the topic]
                [Brief summary of the events, clear text, use bulletpoints when possible]

                **Source**:
                • [[Title]([url])]
                '''
                """