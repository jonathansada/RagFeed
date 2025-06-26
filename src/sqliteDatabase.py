import sqlite3 
from datetime import datetime

class SqliteDatabase:
    def __init__(self, db_path, log):
        self.db_path = db_path
        self.log = log
        self.con = False
        self.cur = False

    def openCon(self):
        if self.con == False:
            self.log.debug(f"SqliteDatabase.openCon({self.db_path})")
            self.con = sqlite3.connect(self.db_path)
            self.cur = self.con.cursor()
    
    def closeCon(self):
        if self.con != False:
            self.log.debug(f"SqliteDatabase.closeCon()")
            self.con.close()
            self.con = False
            self.cur = False

    def getSources(self):
        self.openCon()
        self.cur.execute("SELECT id, title, url, last_update FROM sources")
        rows = self.cur.fetchall()
        self.closeCon()

        result = [{"id": row[0], "title": row[1], "url": row[2], "last_update": self.dbDateToTimestamp(int(row[3]))} for row in rows]
        self.log.debug(f"SqliteDatabase.getSources: {result}")

        return result

    def setSourceLastUpdate(self, source:int, last_update:datetime = datetime.now()):
        self.openCon()
        self.log.debug(f"SqliteDatabase.setSourceLastUpdate(source={source}, last_update={datetime})")
        result = self.cur.execute("UPDATE sources SET last_update=? WHERE id=?", (self.timestampToDbData(last_update), source))
        self.con.commit()
        self.closeCon()

    def dbDateToTimestamp(self, timestamp:int):
        return datetime.fromtimestamp(timestamp)

    def timestampToDbData(self, date:datetime):
        print(date)
        print(date.timestamp())
        print(int(date.timestamp()))
        return int(date.timestamp())


