from langchain_ollama import OllamaEmbeddings

class OllamaModel():
    def __init__(self, llm_model, embeddings_model, url, log):
        self.log = log
        self.log.debug("OllamaModel.__init__()")
        #self.llm = 
        self.embeddings = OllamaEmbeddings(model=embeddings_model, base_url=url)

    def getEmbeddings(self):
        self.log.debug("OllamaModel.getEmbeddings()")
        return self.embeddings
