from langchain_ollama import OllamaEmbeddings

class OllamaModel():
    def __init__(self, llm_model, embeddings_model, url):
        #self.llm = 
        self.embeddings = OllamaEmbeddings(model=embeddings_model, base_url=url)

    def getEmbeddings(self):
        return self.embeddings
