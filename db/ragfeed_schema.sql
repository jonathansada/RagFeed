CREATE TABLE "sources" (
	"id"	INTEGER,
	"title"	TEXT,
	"url"	TEXT UNIQUE,
	"last_update"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
)