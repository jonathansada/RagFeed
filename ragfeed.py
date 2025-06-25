from init import *

# Update Sources
#sources.updateArticles()

# Load XML into VectorStore
import os
from langchain_community.document_loaders.xml import UnstructuredXMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

for file in os.listdir(feeds_path):
    xmlLoader = UnstructuredXMLLoader(file_path = feeds_path + "/" + file, mode = "elements")
    docs = vectorstore.document_preprocess(xmlLoader.load())
    chunks = text_splitter.split_documents(docs)
    vectorstore.add_documents(documents=chunks)