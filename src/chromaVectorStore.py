from langchain_chroma import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata

class ChromaVectorStore():
    def __init__(self, embeddings, collection_name, persist_directory, log):
        self.log = log
        self.log.info("ChromaVectorStore.__init__()")
        self.vectorstore = Chroma(collection_name=collection_name, embedding_function=embeddings, persist_directory=persist_directory)

    def document_preprocess(self, document):
        self.log.info("ChromaVectorStore.document_preprocess()")
        self.log.debug("Document: " + str(document))

        return filter_complex_metadata(document)

    def add_documents(self, documents):
        self.log.info("ChromaVectorStore.add_documents()")
        self.log.debug("Documents: " + str(documents))

        self.vectorstore.add_documents(documents=documents)

    def search(self, term, k=1):
        self.log.info("ChromaVectorStore.search()")
        self.log.debug("Term: " + str(term))
        self.log.debug("k: " + str(k))

        return self.vectorstore.similarity_search(term, k=k) 

    def searchMetadata(self, term, k=1):
        return self.vectorstore.metadata_search(term, k=k) 