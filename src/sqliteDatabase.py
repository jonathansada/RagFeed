import sqlite3 
from datetime import datetime, timedelta

class SqliteDatabase:
    def __init__(self, db_path, log):
        self.db_path = db_path
        self.log = log
        self.con = False
        self.cur = False

    def openCon(self):
        if self.con == False:
            self.log.info(f"\nSqliteDatabase.openCon({self.db_path})")
            self.con = sqlite3.connect(self.db_path)
            self.cur = self.con.cursor()
    
    def closeCon(self):
        if self.con != False:
            self.log.info(f"\nSqliteDatabase.closeCon()")
            self.con.close()
            self.con = False
            self.cur = False

    def getSources(self):
        self.log.info(f"\nSqliteDatabase.getSources()")
        
        self.openCon()
        self.cur.execute("SELECT id, title, url, last_update FROM sources")
        rows = self.cur.fetchall()
        self.closeCon()

        result = [{"id": row[0], "title": row[1], "url": row[2], "last_update": self.dbDateToTimestamp(int(row[3]))} for row in rows]
        self.log.debug(f"SqliteDatabase.getSources: {result}")

        return result

    def setSourceLastUpdate(self, source:int, last_update:datetime = datetime.now(), closedb = True):
        self.log.info(f"\nSqliteDatabase.setSourceLastUpdate()")
        self.log.debug(f"source={source}\nlast_update={datetime}")

        self.openCon()
        result = self.cur.execute("UPDATE sources SET last_update=? WHERE id=?", [self.timestampToDbData(last_update), source])
        self.log.debug(f"result: {str(result)}")
        self.con.commit()
        if closedb:
            self.closeCon()

    def addArticle(self, source_id, article, closedb = True):
        self.log.info(f"\nSqliteDatabase.addArticle()")
        self.log.debug(f"source_id: {str(source_id)}")
        self.log.debug(f"article: {str(article)}")

        self.openCon()
        self.cur.execute("INSERT INTO articles (id_source, title, description, link, creator, pub_date, categories, media_url, media_medium, media_height, media_credit, media_description, in_vectorstore) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)", 
                        [source_id, 
                        article["title"], 
                        article["description"], 
                        article["link"], 
                        article["creator"] if article["creator"] else "NULL", 
                        self.timestampToDbData(article["pub_date"]), 
                        ", ".join(article["categories"]) if article["categories"] else "NULL", 
                        article["media_url"] if article["media_url"] else "NULL", 
                        article["media_medium"] if article["media_medium"] else "NULL",  
                        article["media_height"] if article["media_height"] else "NULL", 
                        article["media_credit"] if article["media_credit"] else "NULL", 
                        article["media_description"] if article["media_description"] else "NULL"])

        row_id = self.cur.lastrowid
        self.con.commit()
        if closedb:
            self.closeCon()
        self.log.debug(f"article inserted with id: {str(row_id)}")
        return row_id
    
    def getArticleId(self, link, closedb = True):
        self.log.info(f"\nSqliteDatabase.getArticleId()")
        self.log.debug(f"link: {link}")

        self.openCon()
        self.cur.execute("SELECT id FROM articles WHERE link=?", [link])
        rows = self.cur.fetchall()

        if closedb:
            self.closeCon()

        self.log.debug(f"result: {str(rows)}")
        return rows[0][0] if rows else False

    def getArticlesForVectorStore(self):
        self.log.info(f"\nSqliteDatabase.getSources()")
        
        self.openCon()
        self.cur.execute("SELECT * FROM articles WHERE in_vectorstore = 0")
        cols = self.cur.description
        rows = self.cur.fetchall()
        self.closeCon()

        result = self.rowsToDict(rows, cols)
        self.log.debug(f"result: {str(result)}")
        
        return result
    
    def setArticleInVectorStore(self, article_id, closedb = True):
        self.log.info(f"\nSqliteDatabase.setArticleInVectorStore()")
        
        self.openCon()
        result = self.cur.execute("UPDATE articles SET in_vectorstore=1 WHERE id=?", [article_id])
        self.log.debug(f"result: {str(result)}")
        self.con.commit()
        if closedb:
            self.closeCon()

    def getArticles(self, url=False):
        self.log.info(f"\nSqliteDatabase.getArticles()")
        self.log.debug(f"url: {url}")

        sql = "SELECT * FROM articles "
        params = []
        if url != False:
            sql += " WHERE link = ? "
            params.append(url)
        sql += " ORDER BY pub_date DESC"

        self.openCon()
        result = self.cur.execute(sql, params)
        cols = self.cur.description
        rows = self.cur.fetchall()
        self.closeCon()

        result = self.rowsToDict(rows, cols)
        self.log.debug(f"result: {str(result)}")
        
        return result

    def getTodayArticles(self):
        self.log.info(f"\nSqliteDatabase.getTodayArticles()")

        self.openCon()
        result = self.cur.execute("SELECT * FROM articles WHERE pub_date>=? ORDER BY pub_date DESC", [self.timestampToDbData(datetime.now() + timedelta(hours=-24))])
        cols = self.cur.description
        rows = self.cur.fetchall()
        self.closeCon()

        result = self.rowsToDict(rows, cols)
        self.log.debug(f"result: {str(result)}")
        
        return result

    def setTopicsCache(self, completion, numTokensPrompt, numTokensInput, numTokensCompletion):
        self.log.info(f"\nSqliteDatabase.setTopicsCache()")
        self.log.debug(f"completion={completion}, numTokensPrompt={numTokensPrompt}, numTokensInput={numTokensInput}, numTokensCompletion={numTokensCompletion}")

        self.openCon()
        self.cur.execute("INSERT INTO topics_cache (completion, num_tokens_prompt, num_tokens_input, num_tokens_completition, date_completition) values (?, ?, ?, ?, ?)",
                         [completion, numTokensPrompt, numTokensInput, numTokensCompletion, self.timestampToDbData(datetime.now())])
        self.con.commit()
        self.closeCon()

    def getTopicsCache(self):
        self.log.info(f"\nSqliteDatabase.getTopicsCache()")

        self.openCon()
        result = self.cur.execute("SELECT * FROM topics_cache ORDER BY date_completition DESC LIMIT 1")
        cols = self.cur.description
        rows = self.cur.fetchall()
        self.closeCon()

        result = self.rowsToDict(rows, cols)
        self.log.debug(f"result: {str(result)}")
        
        return result

    def setRagSearchCache(self, search, completion, numTokensPrompt, numTokensInput, numTokensCompletion):
        self.log.info(f"\nSqliteDatabase.setRagSearchCache()")
        self.log.debug(f"search={search}, completion={completion}, numTokensPrompt={numTokensPrompt}, numTokensInput={numTokensInput}, numTokensCompletion={numTokensCompletion}")

        self.openCon()
        result = self.cur.execute("SELECT * FROM ragsearch_cache WHERE search=?", [search])
        rows = self.cur.fetchall()
        if not rows:
            sql = "INSERT INTO ragsearch_cache (completion, num_tokens_prompt, num_tokens_input, num_tokens_completition, date_completition, search) values (?, ?, ?, ?, ?, ?)"
        else:
            sql = "UPDATE ragsearch_cache SET completion = ?, num_tokens_prompt = ? , num_tokens_input = ?, num_tokens_completition = ?, date_completition = ? WHERE search = ?"
        self.cur.execute(sql, [completion, numTokensPrompt, numTokensInput, numTokensCompletion, self.timestampToDbData(datetime.now()), search])
        self.con.commit()
        self.closeCon()

    def getRagSearchCache(self, search = False):
        self.log.info(f"\nSqliteDatabase.setRagSearchCache()")
        self.log.debug(f"search={str(search)}")

        sql = "SELECT * FROM ragsearch_cache "
        params = []
        if search:
            sql += " WHERE search = ? "
            params.append(search)
        sql += " ORDER BY date_completition DESC"

        self.openCon()
        result = self.cur.execute(sql, params)
        cols = self.cur.description
        rows = self.cur.fetchall()
        self.closeCon()

        result = self.rowsToDict(rows, cols)
        self.log.debug(f"result: {str(result)}")
        
        return result

    def delRagSearch(self, search):
        self.log.info(f"\nSqliteDatabase.delRagSearch()")
        self.log.debug(f"search={str(search)}")

        sql = "DELETE FROM ragsearch_cache  WHERE search = ? "

        self.openCon()
        result = self.cur.execute(sql, [search])
        self.con.commit()
        self.closeCon()

    def dbDateToTimestamp(self, timestamp:int):
        return datetime.fromtimestamp(timestamp)

    def timestampToDbData(self, date:datetime):
        return int(date.timestamp())

    def rowsToDict(self, rows, cols):
        cols = [col[0] for col in cols]
        return [dict(zip(cols, row)) for row in rows]

