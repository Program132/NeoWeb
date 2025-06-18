import sqlite3

def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS pages
                 (
                     url
                     TEXT
                     PRIMARY
                     KEY,
                     title
                     TEXT,
                     content
                     TEXT,
                     links
                     TEXT
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS index_inverted
    (
        word
        TEXT,
        url
        TEXT,
        tf
        REAL,
        PRIMARY
        KEY
                 (
        word,
        url
                 )
        )''')

    c.execute('''CREATE TABLE IF NOT EXISTS pagerank
                 (
                     url
                     TEXT
                     PRIMARY
                     KEY,
                     rank
                     REAL
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS queue
                 (
                     url
                     TEXT
                     PRIMARY
                     KEY
                 )''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()