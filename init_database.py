from Database import DatabaseManager

def database_config():
    db = DatabaseManager("neoweb.db")
    db.connect()
    table_name = "web_pages"
    columns = {
        "url": "TEXT PRIMARY KEY",
        "links": "TEXT",
        "title": "TEXT",
        "subtitles": "TEXT",
        "metadata": "TEXT",
        "text": "TEXT"
    }
    db.create_table(table_name, columns)
    table_name = "pending"
    columns = {
        "url": "TEXT PRIMARY KEY",
        "status": "TEXT",
    }
    db.create_table(table_name, columns)
    table_name = "pending_indexer"
    columns = {
        "url": "TEXT PRIMARY KEY",
        "status": "TEXT",
    }
    db.create_table(table_name, columns)
    table_name = "occurrences"
    columns = {
        "word": "TEXT",
        "list_urls": "TEXT",
    }
    db.create_table(table_name, columns)
    db.close()
database_config()