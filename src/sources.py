import requests
from datetime import datetime
import re

from src.rssArticlesLoader import RssArticlesLoader

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Manages the source and the storage of the information
class Sources:
    def __init__(self, db, vs, log, update_feq=12):
        self.db = db
        self.vs = vs
        self.log= log
        self.update_feq = update_feq

    def getSources(self):
        return self.db.getSources()
    
    def updateSources(self):
        self.log.info("\nSources.updateArticles()")
        sources = self.getSources()
        updated = []
        for source in sources:
            if self.getHoursLastUpdate(source["last_update"]) > self.update_feq:
                self.log.debug(f"Updating source {source["title"]}")
                response = requests.get(source["url"])

                if response.status_code == 200:
                    self.updateArticles(source=source, content=response.content)
                    self.db.setSourceLastUpdate(source = source["id"])
                    updated.append(source)
                else:
                    self.log.warning(f"Soruce {source["title"]}({source["link"]}) answered with a HTTP Code {response.status_code} and this reason: {response.reason}")

        return updated
    
    def updateArticles(self, source, content):
        self.log.info("\nSources.updateArticles()")
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
        self.log.info("\nSources.updateVectorStore()")
             
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

    def getHoursLastUpdate(self, last_update:datetime):
        return (datetime.now() - last_update).total_seconds() // 3600

    def getFileName(self, title):
        title = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
        title = re.sub(r'\s{2,}', ' ', title)
        title = re.sub(r'\s', '_', title)
        return title.lower() + ".xml"




