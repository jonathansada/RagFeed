from langchain_ollama import OllamaEmbeddings, ChatOllama

class OllamaModel():
    embeddings = None
    char = None
    def __init__(self, llm_model, embeddings_model, url, log):
        self.log = log
        self.log.debug("OllamaModel.__init__()")
        self.chat = ChatOllama(model = llm_model, temperature =  0.8, max_tokens = 10000, top_p = 0.3, frequency_penalty = 0.4, presence_penalt = 0.95)
        self.embeddings = OllamaEmbeddings(model=embeddings_model, base_url=url)


