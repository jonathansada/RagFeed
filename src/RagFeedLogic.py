import requests
from datetime import datetime
import re
import json
from src.rssArticlesLoader import RssArticlesLoader
from langchain_core.documents import Document

# Contains the main logic of the app including Sources, Database, Models and VectorStore
class RagFeedLogic:
    def __init__(self, db, vs, model, log, update_feq=12):
        self.db = db
        self.vs = vs
        self.model = model
        self.log= log
        self.update_feq = update_feq

    def getSources(self):
        return self.db.getSources()
    
    def updateSources(self, force=False):
        self.log.info("\nRagFeedLogic.updateArticles()")
        sources = self.getSources()
        updated = []
        for source in sources:
            if self.getHoursLastUpdate(source["last_update"]) > self.update_feq or force==True:
                self.log.debug(f"Updating source {source["title"]}")
                response = requests.get(source["url"])

                if response.status_code == 200:
                    self.updateArticles(source=source, content=response.content)
                    self.db.setSourceLastUpdate(source = source["id"])
                    updated.append(source)
                else:
                    self.log.warning(f"RagFeedLogic.updateSources: Soruce {source["title"]}({source["link"]}) answered with a HTTP Code {response.status_code} and this reason: {response.reason}")

        return updated
    
    def updateArticles(self, source, content):
        self.log.info("\nRagFeedLogic.updateArticles()")
        self.log.debug("Soruce:  " + str(source))
        self.log.debug("Content: " + str(content))

        # I no source is provided update all sources
        rssLoader = RssArticlesLoader()
        articles = rssLoader.loadAsDict(xml = content)

        for article in articles:
            if self.db.getArticleId(link = article["link"], closedb = False) == False:
                self.db.addArticle(source_id = source["id"], article = article, closedb = False)
                self.log.debug("Article added to DB: " + article["link"])
            else:
                self.log.debug("Article already in DB: " + article["link"])
                
        self.db.closeCon()

    def updateVectorStore(self):
        self.log.info("\nRagFeedLogic.updateVectorStore()")
             
        articles = self.db.getArticlesForVectorStore()
        documents = []
        ids = []
        for article in articles:
            page_content = article["title"] + "\n" + article["description"]
            metadata = {}
            metadata["link"] = article["link"]
            metadata["creator"] = article["creator"]
            metadata["date_publication"] = article["creator"]

            documents.append(Document(page_content=page_content, metadata=metadata))
            ids.append(str(article["id"]))
        
        if documents:
            # No chunk documents since they are expected to be small and the ID is provided by DB.
            res = self.vs.add_documents(documents=documents, ids=ids)
            self.log.debug(f"Added {len(documents)} articles to vector store")
            for art_id in res:
                self.db.setArticleInVectorStore(article_id=art_id, closedb=False)
            self.db.closeCon()
    
    def updateTopTopics(self):
        self.log.info("\nRagFeedLogic.updateTopTopics()")

        articles = self.db.getTodayArticles()
        completion, tokBasePrompt, tokInput, tolAnswer = self.model.getTopTopics([{"title": article["title"], "description": article["description"], "categories": article["categories"], "link": article["link"]} for article in articles])
        self.log.debug(completion)
        # Transform completion in the format that will be used 
        toptopics = {}
        
        try: # Just in case answer is not formater properlly
            # Check there is no markdown indicator for json
            completion = completion.strip()
            completion = re.sub(r'^(```json)', '', completion)
            completion = re.sub(r'(```$)', '', completion)
            
            for topic in json.loads(completion):
                rtopic = {}
                freq = 0
                rtopic["title"] = topic["topic"]
                rtopic["summary"] = topic["summary"]
                rarticles = []
                for article in topic["articles"]:
                    url = article
                    if isinstance(article, dict):
                        url = article["url"] if "url" in article.keys() else article["link"] if "link" in article.keys() else url
                    ra = self.db.getArticles(url=url)
                    if ra:
                        rarticles.append(ra[0])
                        freq += 1
                rtopic["articles"] = rarticles
                rtopic["frequency"] = freq
        
                if freq > 0:
                    toptopics[self.hastTagFromText(topic["topic"])] = rtopic
            # Sort by frequency
            toptopics = {k: v for k, v in sorted(toptopics.items(), key=lambda item: item[1]['frequency'], reverse="True")}
            self.log.debug(f"topTopics: {str(toptopics)}")
        except Exception as e:
            self.log.error("\nRagFeedLogic.updateTopTopics()")
            self.log.error("Error:\n" + getattr(e, 'message', str(e)))
            self.log.error("Unable to transform model completion into json:\n" + str(completion))
            toptopics = {}

        # If toptopics is empty this will not be stored in DB
        if toptopics:     
            self.db.setTopicsCache(json.dumps(toptopics), tokBasePrompt, tokInput, tolAnswer)
        else:
            self.log.debug("No top topics to store in DB provided by the model")

    def getTopTopics(self):
        self.log.info("\nRagFeedLogic.getTopTopics()")
        topics = self.db.getTopicsCache()
        if not topics:
            return {}

        return json.loads(topics[0]["completion"])

    def hastTagFromText(self, text):
        s = text.replace("-", " ").replace("_", " ")
        s = s.split()
        if len(text) == 0:
            return text
        return "#"+s[0] + ''.join(i.capitalize() for i in s[1:])

    def askRag(self, search, num_docs=10):
        self.log.info("\nRagFeedLogic.askRag()")

        # Get docs from vectorstore
        docs = self.vs.search(search, k = num_docs)
        
        # Prepare contextx
        context = ""
        for doc in docs:
            context += "\nContent:\n"
            context += doc.page_content + "\n"
            context += str(doc.metadata) +"\n\n"

        # Ask the model to perform the inference
        completion, tokBasePrompt, tokInput, tolAnswer = self.model.summarizeArticles(question=search, context=context)
        self.log.debug(completion)
        try:
            # Check there is no markdown indicator for json
            completion = completion.strip()
            completion = re.sub(r'^(```json)', '', completion)
            completion = re.sub(r'(```$)', '', completion)

            raganswer = json.loads(completion)
            raganswer["title"] = search

            rarticles = []
            for article in raganswer["articles"]:
                url = article
                if isinstance(article, dict):
                    url = article["url"] if "url" in article.keys() else article["link"] if "link" in article.keys() else url
                ra = self.db.getArticles(url=url)
                if ra:
                    rarticles.append(ra[0])
            raganswer["articles"] = rarticles

            self.db.setRagSearchCache(search, json.dumps(raganswer), tokBasePrompt, tokInput, tolAnswer)
        
        except Exception as e:
            raganswer = {}
            self.log.error("\nRagFeedLogic.askRag()")
            self.log.error("Error:" + getattr(e, 'message', str(e)))
            self.log.error("Unable to transform model completion into json:\n" + str(completion))

        return raganswer  

    def getRagSearches(self, search=False):
        self.log.info("\nRagFeedLogic.getRagSearches()")
        searches = self.db.getRagSearchCache(search)
        if not searches:
            return []

        return [json.loads(search["completion"]) for search in searches]

    def updateRagSearches(self, num_docs=10):
        ragsearches = self.getRagSearches()
        for rsearch in ragsearches:
            self.askRag(rsearch["title"], num_docs=num_docs)
    
    def getHoursLastUpdate(self, last_update:datetime):
        return (datetime.now() - last_update).total_seconds() // 3600

    def getFileName(self, title):
        title = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
        title = re.sub(r'\s{2,}', ' ', title)
        title = re.sub(r'\s', '_', title)
        return title.lower() + ".xml"




