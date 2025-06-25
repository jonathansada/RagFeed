from langchain_chroma import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata

class ChromaVectorStore():
    def __init__(self, embeddings, collection_name, persist_directory):
        self.vectorstore = Chroma(collection_name=collection_name, embedding_function=embeddings, persist_directory=persist_directory)

    def document_preprocess(self, document):
        return filter_complex_metadata(document)

    def add_documents(self, documents):
        self.vectorstore.add_documents(documents=documents)

    def search(self, term, k=1):
        return self.vectorstore.similarity_search(term, k=k) 