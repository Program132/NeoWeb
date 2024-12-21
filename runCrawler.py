from Crawler import Crawler

url = "https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Accueil_principal"

crawler = Crawler(start_url=url)
crawler.crawl()