# RagFeed
## About RagFeed
RagFeed is a feed reader powered by RAG and LLM models.

The main feature is to provide an overview of the most relevant topics on the articles from the RSS sources provided by the user and allow him/her to ask questions to its feed to dive into the topics. 

Other posible features (future) is to allow the user to rate specific articles in grade of interest so the app could filter the most relevant topics based on preferences and create a custom feed, similar to the one provided by social networks but based on the user provided RSS sources.

## How to run
1. Clone repository
2. Enter in directory
    `cd RagFeed`
2. Install depencies 
    `pip install -r requirements.txt`
3. Create SQLite Database
    `sqlite3 ./data/sqlite/ragfeed.db < ./db/ragfeed_schema.sql`
3. Run App
    `python -m streamlit run slapp.py`
4. Access through the provided url