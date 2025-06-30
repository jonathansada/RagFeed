CREATE TABLE "sources" (
	"id"	INTEGER NOT NULL,
	"title"	TEXT NOT NULL,
	"url"	TEXT NOT NULL UNIQUE,
	"last_update"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
)

CREATE TABLE "articles" (
	"id"	INTEGER NOT NULL,
	"id_source"	INTEGER NOT NULL,
	"title"	TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	"link"	TEXT NOT NULL UNIQUE,
	"creator"	TEXT,
	"pub_date"	INTEGER NOT NULL,
	"categories"	TEXT,
	"media_url"	TEXT,
	"media_medium"	TEXT,
	"media_height"	TEXT,
	"media_credit"	TEXT,
	"media_description"	TEXT,
	"in_vectorstore"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("id_source") REFERENCES ""
)

CREATE TABLE "topics_cache" (
	"completition"	TEXT,
	"num_tokens_prompt"	INTEGER,
	"num_tokens_input"	INTEGER,
	"num_tokens_completition"	INTEGER,
	"date_completition"	INTEGER
)