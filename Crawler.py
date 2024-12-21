from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from JsonDatabase import JsonDatabase


class Crawler:
    def __init__(self, start_url, max_iteration=None):
        self.currentURL = start_url
        self.database_data = "data.json"
        self.database_pending = "queue.json"
        self.max_iteration = max_iteration
        self.needToStop = False

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

    def add_pending_url(self):
        db = JsonDatabase(self.database_pending)
        existing_record = db.get_record(self.currentURL)
        if existing_record: return
        record_data = {"status": "pending"}
        db.add_record(self.currentURL, record_data)
        print(f"URL '{self.currentURL}' ajoutée à la file d'attente avec le statut 'pending' pour récupérer les URLs.")

    def conclude_for_url(self):
        db = JsonDatabase(self.database_pending)
        existing_record = db.get_record(self.currentURL)
        if existing_record:
            db.delete_record(self.currentURL)
            print(f"URL '{self.currentURL}' : fini.")

    def add_data_to_db(self):
        db = JsonDatabase(self.database_data)
        existing_record = db.get_record(self.currentURL)
        if existing_record: return
        page = self.get_page_from_url(self.currentURL)
        if page is None:
            print(f"Impossible de récupérer les données pour l'URL '{self.currentURL}'.")
            return

        title = self.get_title_from_page(page)
        subtitles = self.get_subtitles_from_page(page)
        metadata = self.get_metadata_from_page(page)
        text_from_page = self.get_text_from_page(page)
        links = self.get_all_href_from_page(page, self.currentURL)

        record_data = {
            "title": title,
            "subtitles": subtitles,
            "text": text_from_page,
            "href": links,
            "metadata": metadata
        }
        db.add_record(self.currentURL, record_data)
        print(f"URL '{self.currentURL}' : données sauvegardées.")

    def crawl_one(self, url):
        self.currentURL = url
        self.add_pending_url()
        self.add_data_to_db()
        self.conclude_for_url()

    def crawl(self):
        not_allowed_href = self.get_robots_txt_urls()

        self.crawl_one(self.currentURL)

        db = JsonDatabase(self.database_data)
        links = db.get_record(self.currentURL)["href"]

        disallowed_links = []
        for l in not_allowed_href:
            if self.needToStop: break

            disallowed_links.append(str(self.get_base_url() + l))

        allowed_links = [l for l in links if l not in disallowed_links]

        iteration_limit = self.max_iteration or len(allowed_links)

        for i, link in enumerate(allowed_links):
            if self.needToStop: break

            if i >= iteration_limit:
                break
            print(f"--------------- Analyse : {link} ---------------")
            self.crawl_one(link)

    def handle_stop_signal(self):
        self.needToStop = True