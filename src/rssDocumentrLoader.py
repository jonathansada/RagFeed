from langchain_core.documents import Document
from bs4 import BeautifulSoup

class RssDocumentLoader:
    def load(self, xml_file):
        with open(xml_file) as f:
            soup = BeautifulSoup(f, 'xml')

        docs = []         
        for item in soup.find_all('item'):
            metadata = {}
            metadata["url"] = item.link.text
            if item.creator:
                metadata["creator"] = item.creator.text
            if item.pubDate:
                metadata["publication"] = item.pubDate.text
            if item.category:
                metadata["categories"] = ", ".join([cat.text for cat in item.find_all('category')])
            if item.credit:
                metadata["credit"] = item.credit.text

            docs.append(Document(
                page_content=f"{item.title.text}\n{"\n".join([desc.text for desc in item.find_all('description')])}",
                metadata=metadata
            ))
        return docs