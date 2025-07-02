from langchain_core.documents import Document
from bs4 import BeautifulSoup
from datetime import datetime

class RssArticlesLoader:
    def loadAsDict(self, xml):
        soup = BeautifulSoup(xml, 'xml')
        articles = []  
        for item in soup.find_all('item'):
            article = {}
            article["title"] = item.title.text
            article["description"] = item.description.text
            article["link"] = item.link.text
            article["creator"] = item.find('dc:creator').text if item.find('dc:creator') else False
            if item.pubDate:
                try:
                    if item.pubDate.text[27] in ["+", "-"]:
                        # TimeZone Defined as UTC Offset
                        article["pub_date"] = datetime.strptime(item.pubDate.text,'%a, %d %b %Y %H:%M:%S %z')
                    else:
                        # TimeZone Defined by Zone Name
                        article["pub_date"] = datetime.strptime(item.pubDate.text,'%a, %d %b %Y %H:%M:%S %Z')
                except:
                    # In case any of both formats for timezone works
                    article["pub_date"] = datetime.strptime(item.pubDate.text[:24],'%a, %d %b %Y %H:%M:%S')
            else:
                article["pub_date"] = datetime.now() 
            article["categories"] = self.cleanCategories(item.find_all('category')) if item.category else []
            article["media_url"] = item.find('media:content').attrs["url"] if item.find('media:content', url=True) else False
            article["media_medium"] = item.find('media:content').attrs["medium"] if item.find('media:content', medium=True) else False
            article["media_height"] = item.find('media:content').attrs["height"] if item.find('media:content', media_height=True) else False
            article["media_credit"] = item.find('media:credit').text if item.find('media:credit') else False
            if item.find('media:thumbnail') and article["media_url"]==False:
                article["media_url"] = item.find('media:thumbnail').attrs["url"] if item.find('media:thumbnail', url=True) else False
                article["media_height"] = item.find('media:thumbnail').attrs["height"] if item.find('media:thumbnail', height=True) else False
            article["media_description"] = item.find('media:description').text if item.find('media:description') else False
            if item.find('media:keywords'):
                article["media_description"] = article["media_description"] + " " + item.find('media:keywords').text if article["media_description"] else item.find('media:keywords').text
            articles.append(article)
        
        return articles

    def cleanCategories(self, categories):
        result = []
        for category in categories:
            result += category.text.split(" / ")
        return set(result)
