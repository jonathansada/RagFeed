from RagFeed import RagFeed
app = RagFeed()

#app.updateVectorStore()

result = app.askRag("What are the latest advances on AI?", 10)
#result = app.getTopTopics()
print(result)
"""
for topic in result["topics"]:
    print(topic.summary)
    for article in topic.articles:
        print("-", article.article, "-", article.url)
"""