import zapzap.model.database as db


def tableSettings() -> str:
    return """
            CREATE TABLE IF NOT EXISTS "Settings" (
                "id"	INTEGER,
                "name"	TEXT NOT NULL,
                "start"	INTEGER DEFAULT 1,
                "image" BLOB,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
            """
