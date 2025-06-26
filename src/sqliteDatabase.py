import sqlite3 
from datetime import datetime

class SqliteDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.con = False
        self.cur = False

    def openCon(self):
        if self.con == False:
            self.con = sqlite3.connect(self.db_path)
            self.cur = self.con.cursor()
    
    def closeCon(self):
        if self.con != False:
            self.con.close()
            self.con = False
            self.cur = False

    def getSources(self):
        self.openCon()
        self.cur.execute("SELECT id, title, url, last_update FROM sources")
        rows = self.cur.fetchall()
        self.closeCon()

        return [{"id": row[0], "title": row[1], "url": row[2], "last_update": self.dbDateToTimestamp(int(row[3]))} for row in rows]

    def setSourceLastUpdate(self, source:int, last_update:datetime = datetime.now()):
        self.openCon()
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


