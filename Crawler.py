import json
from urllib.parse import urljoin, urlparse, urlunparse
import requests
from bs4 import BeautifulSoup
from Database import DatabaseManager


class Crawler:
    def __init__(self, start_url, database="neoweb.db"):
        self.currentURL = start_url
        self.needToStop = False
        self.database_path = database
        self.links = []
        self.db = DatabaseManager(self.database_path)

    @staticmethod
    def get_page_from_url(url, timeout=5):
        try:
            return requests.get(url, timeout=timeout)
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération de l'URL {url}: {e}")
            return None

    @staticmethod
    def get_title_from_page(page):
        soup = BeautifulSoup(page.text, 'html.parser')
        title = soup.find('title')
        return title.text if title else "Title not found"

    @staticmethod
    def get_subtitles_from_page(page):
        soup = BeautifulSoup(page.text, 'html.parser')
        subtitles = soup.find_all('h1')
        return [subtitle.text for subtitle in subtitles] if subtitles else ["Subtitles not found"]

    @staticmethod
    def get_metadata_from_page(page):
        soup = BeautifulSoup(page.text, 'html.parser')
        meta_tags = soup.find_all('meta')
        metadata = {}
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content

        return metadata if metadata else {"Metadata not found": "No meta tags found"}

    @staticmethod
    def get_text_from_page(page):
        soup = BeautifulSoup(page.text, 'html.parser')
        text = soup.get_text()
        return text.strip() if text else "Text not found"

    @staticmethod
    def get_all_href_from_page(page, base_url):
        soup = BeautifulSoup(page.text, 'html.parser')
        hrefs = soup.find_all('a', href=True)
        valid_hrefs = []
        for href in hrefs:
            link = href['href']
            absolute_link = urljoin(base_url, link)
            if absolute_link.startswith('http'):
                valid_hrefs.append(absolute_link)
        return valid_hrefs if valid_hrefs else ["No valid links found"]

    def get_base_url(self):
        parsed_url = urlparse(self.currentURL)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url

    def get_robots_txt(self):
        base_url = self.get_base_url()
        robots_url = urljoin(base_url, "/robots.txt")
        try:
            response = requests.get(robots_url)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Erreur lors de la récupération du fichier robots.txt de {base_url}: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération du fichier robots.txt: {e}")
            return None

    def get_robots_txt_urls(self):
        robots_txt = self.get_robots_txt()
        if not robots_txt: return []
        urls = []
        for line in robots_txt.splitlines():
            if self.needToStop: break

            line = line.strip()
            if line.lower().startswith("allow") or line.lower().startswith("disallow"):
                if self.needToStop: break

                parts = line.split()
                if len(parts) > 1:
                    urls.append(parts[1])
        return urls

    @staticmethod
    def clean_url(url):
        parsed_url = urlparse(url)
        cleaned_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            '',
            '',
            ''
        ))
        return cleaned_url

    def add_url_to_pending_table(self, url):
        data = {
            "url": f"{url}",
            "status": "pending"
        }
        self.db.connect()

        query = "INSERT OR IGNORE INTO pending (url, status) VALUES (?, ?)" # évite les doublons
        self.db.execute_query(query, (url, "pending"))

        self.db.close()
        print(f"URL ajoutée à la table 'pending': {url}")

    def update_url_status(self, status):
        self.db = DatabaseManager(self.database_path)
        self.db.connect()

        query = f"UPDATE pending SET status = ? WHERE url = ?"
        self.db.execute_query(query, (status, self.currentURL))

        self.db.close()

    def reload_links_from_db(self):
        self.db.connect()

        query = "SELECT url FROM pending WHERE status = 'pending' LIMIT 50"
        result = self.db.execute_query(query)
        print(f"URLs récupérées depuis la base de données: {result}")

        self.links = [url[0] for url in result if url[0] not in self.links]

        self.db.close()

    def url_in_web_pages(self):
        self.db.connect()
        query = "SELECT 1 FROM web_pages WHERE url = ?"
        result = self.db.execute_query(query, (self.currentURL,))
        self.db.close()
        return len(result) > 0

    def remove_url_from_pending(self):
        self.db.connect()
        query = "DELETE FROM pending WHERE url = ?"
        self.db.execute_query(query, (self.currentURL,))
        self.db.close()
        print(f"URL supprimée de la table 'pending': {self.currentURL}")

    def crawl_current(self):
        if len(self.links) < 5:
            self.reload_links_from_db()

        if not self.links:
            print("Aucune URL à crawler.")
            return

        if self.url_in_web_pages(): return

        self.currentURL = self.links.pop(0)
        page = self.get_page_from_url(self.currentURL)
        if not page:
            print(f"Impossible de récupérer la page {self.currentURL}. Passage à la suivante.")
            self.remove_url_from_pending()
            return

        self.update_url_status("crawling")

        all_hrefs = self.get_all_href_from_page(page, self.get_base_url())
        all_hrefs_not_allowed = self.get_robots_txt_urls()

        title = self.get_title_from_page(page)
        subtitles = self.get_subtitles_from_page(page)
        metadata = self.get_metadata_from_page(page)
        text = self.get_text_from_page(page)
        links_href = []

        for href in all_hrefs:
            if self.needToStop: break
            if href not in all_hrefs_not_allowed:
                if self.needToStop: break
                cleaned = self.clean_url(href)
                links_href.append(cleaned)
                self.add_url_to_pending_table(cleaned)
                self.reload_links_from_db()

        self.update_url_status("done")

        data = {
            "url": self.currentURL,
            "title": title,
            "subtitles": subtitles,
            "metadata": json.dumps(metadata),
            "text": text,
            "links": links_href,
        }

        for key, value in data.items():
            if isinstance(value, list):
                data[key] = ', '.join(value)

        self.remove_url_from_pending()

        self.db.connect()
        self.db.add_entry("web_pages", data)
        self.db.close()

    def crawl(self):
        self.add_url_to_pending_table(self.currentURL)

        self.crawl_current()

        for l in self.links:
            if self.needToStop: break
            self.currentURL = l
            self.crawl_current()

    def handle_stop_signal(self):
        print("Arrêt du processus de crawl...")
        self.needToStop = True
        if self.db:
            self.db.close()
        print("Processus arrêté proprement.")