import requests
class Sources:
    def __init__(self):
        self.sources = [{"title": "Wired", "file": "wired.xml", "url": "https://www.wired.com/feed/rss"},
                        {"title": "The New York Times", "file": "the_new_yourk_times.xml", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"}]

    def getSources(self):
        return self.sources
    
    def updateArticles(self):
        for source in self.sources:
            response = requests.get(source["url"])
            with open(f'./data/feeds/{source["file"]}', 'wb') as file:
                file.write(response.content)



