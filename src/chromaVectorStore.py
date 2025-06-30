from langchain_chroma import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata

class ChromaVectorStore():
    def __init__(self, embeddings, collection_name, persist_directory, log):
        self.log = log
        self.log.info("\nChromaVectorStore.__init__()")
        self.vectorstore = Chroma(collection_name=collection_name, embedding_function=embeddings, persist_directory=persist_directory)

    def document_preprocess(self, document):
        self.log.info("\nChromaVectorStore.document_preprocess()")
        self.log.debug("Document: " + str(document))

        return filter_complex_metadata(document)

    def add_documents(self, documents, ids):
        self.log.info("\nChromaVectorStore.add_documents()")
        self.log.debug("Documents: " + str(documents))
        
        # Rudimentary way to avoid duplications
        repeated_ids = self.vectorstore.get(ids)["ids"]
        if repeated_ids:
            self.log.debug("deleting documents with ids: " + str(repeated_ids))
            self.vectorstore.delete(ids=repeated_ids)

        result = self.vectorstore.add_documents(documents=documents, ids = ids)
        self.log.debug("Documents added to vectorstore: " + str(result))

        return result

    def search(self, term, k=1):
        self.log.info("\nChromaVectorStore.search()")
        self.log.debug("Term: " + str(term))
        self.log.debug("k: " + str(k))

        return self.vectorstore.similarity_search(term, k=k) 

    def searchMetadata(self, term, k=1):
        return self.vectorstore.metadata_search(term, k=k) 