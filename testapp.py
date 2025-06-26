from RagFeed import RagFeed
app = RagFeed()

#app.updateVectorStore()

result = app.searchRelated("Spain")
print(result)