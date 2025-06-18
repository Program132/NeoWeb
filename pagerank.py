import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def setup_out_links():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS out_links")
    cur.execute("CREATE TABLE IF NOT EXISTS out_links (src TEXT, dst TEXT, PRIMARY KEY (src, dst))")

    cur.execute("SELECT url, links FROM pages")
    for url, links in cur.fetchall():
        for dst in links.split('\n'):
            cur.execute("INSERT OR IGNORE INTO out_links (src, dst) VALUES (?, ?)", (url, dst))

    conn.commit()
    conn.close()


def compute_pagerank(iterations=10, d=0.85):
    logging.info("Preparing graph...")
    setup_out_links()

    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT src FROM out_links")
    urls = [row[0] for row in cur.fetchall()]
    N = len(urls)
    logging.info(f"{N} pages found.")

    rank = {url: 1.0 / N for url in urls}

    for i in range(iterations):
        logging.info(f"Iteration {i+1}/{iterations}")
        new_rank = {}
        for url in urls:
            new_rank[url] = (1 - d) / N

        for url in urls:
            cur.execute("SELECT dst FROM out_links WHERE src=?", (url,))
            out_links = [row[0] for row in cur.fetchall()]
            if not out_links:
                continue
            share = rank[url] / len(out_links)
            for dst in out_links:
                if dst not in new_rank:
                    new_rank[dst] = (1 - d) / N
                new_rank[dst] += d * share

        rank = new_rank

    for url, score in rank.items():
        cur.execute("REPLACE INTO pagerank (url, rank) VALUES (?, ?)", (url, score))

    conn.commit()
    conn.close()
    logging.info("PageRank computation completed.")

if __name__ == "__main__":
    compute_pagerank()
