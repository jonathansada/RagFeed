import requests
from datetime import datetime
import re

class Sources:
    def __init__(self, db, log, update_feq=12):
        self.db = db
        self.log= log
        self.update_feq = update_feq

    def getSources(self):
        return self.db.getSources()
    
    def updateArticles(self):
        self.log.debug("Sources.updateArticles()")
        sources = self.getSources()
        updated = 0
        for source in sources:
            if self.getHoursLastUpdate(source["last_update"]) > self.update_feq:
                self.log.debug(f"Updating source {source["title"]}")
                response = requests.get(source["url"])
                with open(f'./data/feeds/{self.getFileName(source["title"])}', 'wb') as file:
                    file.write(response.content)
                self.db.setSourceLastUpdate(source = source["id"])
                updated += 1
        return updated

    def getHoursLastUpdate(self, last_update:datetime):
        return (datetime.now() - last_update).total_seconds() // 3600

    def getFileName(self, title):
        title = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
        title = re.sub(r'\s{2,}', ' ', title)
        title = re.sub(r'\s', '_', title)
        return title.lower() + ".xml"


