#!/usr/bin/env python3
"""
Web Crawler pour le TP1 - Indexation Web ENSAI 2026
Ce crawler explore un site web en priorisant les pages produits.
"""

import json
import time
import urllib.parse
import urllib.robotparser
from collections import deque
from typing import Dict, List, Set, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from bs4 import BeautifulSoup


class RobotsChecker:
    """Classe pour vérifier et respecter les règles du robots.txt"""
    
    def __init__(self):
        self._parsers = {}  # Cache des robots.txt par domaine
    
    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """
        Vérifie si l'URL peut être crawlée selon robots.txt
        
        Args:
            url: L'URL à vérifier
            user_agent: Le user agent du crawler
            
        Returns:
            True si le crawl est autorisé, False sinon
        """
        parsed_url = urllib.parse.urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"
        
        # Vérifier le cache
        if base_url not in self._parsers:
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
                self._parsers[base_url] = parser
            except Exception as e:
                print(f"⚠️  Impossible de lire robots.txt pour {base_url}: {e}")
                # Si on ne peut pas lire robots.txt, on autorise par défaut
                return True
        
        return self._parsers[base_url].can_fetch(user_agent, url)


def fetch_page(url: str, timeout: int = 10) -> Optional[str]:
    """
    Récupère le contenu HTML d'une page web
    
    Args:
        url: L'URL de la page à récupérer
        timeout: Temps maximum d'attente en secondes
        
    Returns:
        Le contenu HTML de la page ou None en cas d'erreur
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (ENSAI Web Crawler TP1/1.0; Educational purpose)'
        }
        req = Request(url, headers=headers)
        
        with urlopen(req, timeout=timeout) as response:
            # Vérifier le type de contenu
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                print(f"⚠️  Contenu non-HTML ignoré: {url} ({content_type})")
                return None
            
            return response.read().decode('utf-8', errors='ignore')
    
    except HTTPError as e:
        print(f"❌ Erreur HTTP {e.code} pour {url}")
        return None
    except URLError as e:
        print(f"❌ Erreur URL pour {url}: {e.reason}")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue pour {url}: {e}")
        return None


def extract_title(soup: BeautifulSoup) -> str:
    """
    Extrait le titre de la page
    
    Args:
        soup: Objet BeautifulSoup de la page
        
    Returns:
        Le titre de la page ou chaîne vide
    """
    # Chercher d'abord dans <h3 class="product-title">
    product_title = soup.find('h3', class_='product-title')
    if product_title:
        return product_title.get_text(strip=True)
    
    # Sinon dans <title> en nettoyant le préfixe
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)
        
        # Enlever le préfixe "web-scraping.dev product "
        if title.startswith('web-scraping.dev product '):
            title = title.replace('web-scraping.dev product ', '', 1)
        # Enlever aussi juste "web-scraping.dev "
        elif title.startswith('web-scraping.dev '):
            title = title.replace('web-scraping.dev ', '', 1)
        return title
    
    # Chercher un h1 comme fallback
    h1_tag = soup.find('h1')
    if h1_tag:
        return h1_tag.get_text(strip=True)
    
    return ""


def extract_description(soup: BeautifulSoup) -> str:
    """
    Extrait la description (premier paragraphe significatif)
    
    Args:
        soup: Objet BeautifulSoup de la page
        
    Returns:
        La description ou chaîne vide
    """
    # Chercher dans la zone de contenu produit
    product_desc = soup.find('p', class_='card-description')
    if product_desc:
        return product_desc.get_text(strip=True)
    
    # Chercher dans les paragraphes de la zone de contenu principal
    content_areas = soup.find_all(['div'], class_=lambda x: x and ('content' in x.lower() or 'description' in x.lower()))
    
    for area in content_areas:
        paragraphs = area.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Prendre le premier paragraphe significatif (plus de 20 caractères)
            if len(text) > 20:
                return text
    
    # Fallback: chercher tous les paragraphes
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 20:
            return text
    
    return ""


def extract_product_features(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extrait les caractéristiques produit depuis le tableau HTML
    
    Structure HTML du site :
    <table class="table-product">
      <tr class="feature">
        <td class="feature-label">material</td>
        <td class="feature-value">Premium quality chocolate</td>
      </tr>
    </table>
    
    Args:
        soup: Objet BeautifulSoup de la page
        
    Returns:
        Dictionnaire des caractéristiques produit
    """
    features = {}
    
    # Chercher les lignes de features dans le tableau
    feature_rows = soup.find_all('tr', class_='feature')
    
    for row in feature_rows:
        label_td = row.find('td', class_='feature-label')
        value_td = row.find('td', class_='feature-value')
        
        if label_td and value_td:
            key = label_td.get_text(strip=True).lower()
            value = value_td.get_text(strip=True)
            if key and value:
                features[key] = value
    
    return features


def extract_product_reviews(soup: BeautifulSoup) -> List[Dict]:
    """
    Extrait les avis produits
    
    Structure HTML du site :
    <div class="review review-chocolate-candy-box-1">
      <span>2022-07-22</span>
      <svg>...</svg> (5 étoiles)
      <p>Absolutely delicious! The orange flavor is my favorite.</p>
    </div>
    
    Args:
        soup: Objet BeautifulSoup de la page
        
    Returns:
        Liste des avis produits
    """
    reviews = []
    
    # Chercher les conteneurs d'avis avec class="review"
    review_containers = soup.find_all('div', class_='review')
    
    for container in review_containers:
        review = {}
        
        # Extraire la date (dans <span>)
        date_span = container.find('span')
        if date_span:
            review['date'] = date_span.get_text(strip=True)
        
        # Extraire l'ID depuis les classes du div
        classes = container.get('class', [])
        for cls in classes:
            if cls.startswith('review-') and cls != 'review':
                review['id'] = cls
                break
        
        # Extraire le rating (nombre d'étoiles SVG)
        stars = container.find_all('svg')
        if stars:
            review['rating'] = len(stars)
        
        # Extraire le texte (dans <p>)
        text_p = container.find('p')
        if text_p:
            review['text'] = text_p.get_text(strip=True)
        
        if review:  # Ajouter seulement si on a trouvé des données
            reviews.append(review)
    
    return reviews


def extract_links(soup: BeautifulSoup, base_url: str, current_url: str) -> List[str]:
    """
    Extrait tous les liens de la page et les normalise
    
    Args:
        soup: Objet BeautifulSoup de la page
        base_url: URL de base du site
        current_url: URL de la page actuelle
        
    Returns:
        Liste des URLs absolues uniques
    """
    links = []
    seen = set()
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        
        # Résoudre les URLs relatives
        absolute_url = urllib.parse.urljoin(current_url, href)
        
        # Nettoyer l'URL (supprimer les fragments)
        parsed = urllib.parse.urlparse(absolute_url)
        clean_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''  # Pas de fragment
        ))
        
        # Vérifier que c'est le même domaine
        if clean_url.startswith(base_url) and clean_url not in seen:
            links.append(clean_url)
            seen.add(clean_url)
    
    return links


class WebCrawler:
    """Crawler web avec priorité pour les pages produits"""
    
    def __init__(self, start_url: str, max_pages: int = 50, delay: float = 1.0):
        """
        Initialise le crawler
        
        Args:
            start_url: URL de départ
            max_pages: Nombre maximum de pages à crawler
            delay: Délai entre deux requêtes (politesse)
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.delay = delay
        
        # Extraire l'URL de base
        parsed = urllib.parse.urlparse(start_url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # File d'attente avec priorité : (priorité, url)
        # Priorité 0 = pages produit (à crawler en premier)
        # Priorité 1 = autres pages
        self.to_visit = deque()
        self.to_visit.append((1, start_url))  # URL de départ
        
        # URLs déjà visitées
        self.visited: Set[str] = set()
        
        # Résultats
        self.results: List[Dict] = []
        
        # Checker robots.txt
        self.robots_checker = RobotsChecker()
    
    def is_product_url(self, url: str) -> bool:
        """
        Détermine si une URL est une page produit
        
        Args:
            url: L'URL à vérifier
            
        Returns:
            True si c'est une page produit
        """
        return 'product' in url.lower()
    
    def add_urls_to_queue(self, urls: List[str]):
        """
        Ajoute des URLs à la file d'attente avec priorité
        
        Args:
            urls: Liste des URLs à ajouter
        """
        for url in urls:
            if url not in self.visited and url not in [u for _, u in self.to_visit]:
                priority = 0 if self.is_product_url(url) else 1
                self.to_visit.append((priority, url))
    
    def crawl(self):
        """Lance le crawling"""
        print(f"🚀 Démarrage du crawler depuis {self.start_url}")
        print(f"📊 Objectif: {self.max_pages} pages maximum")
        print(f"⏱️  Délai entre requêtes: {self.delay}s\n")
        
        while self.to_visit and len(self.visited) < self.max_pages:
            # Trier par priorité avant de dépiler
            self.to_visit = deque(sorted(self.to_visit, key=lambda x: x[0]))
            
            priority, url = self.to_visit.popleft()
            
            if url in self.visited:
                continue
            
            # Vérifier robots.txt
            if not self.robots_checker.can_fetch(url):
                print(f"🚫 Bloqué par robots.txt: {url}")
                continue
            
            # Marquer comme visité
            self.visited.add(url)
            
            # Indicateur de priorité
            priority_icon = "⭐" if priority == 0 else "  "
            print(f"{priority_icon} [{len(self.visited)}/{self.max_pages}] Crawling: {url}")
            
            # Récupérer la page
            html = fetch_page(url)
            if not html:
                continue
            
            # Parser le HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extraire les données
            page_data = {
                'url': url,
                'title': extract_title(soup),
                'description': extract_description(soup),
                'product_features': extract_product_features(soup),
                'links': extract_links(soup, self.base_url, url),
                'product_reviews': extract_product_reviews(soup)
            }
            
            self.results.append(page_data)
            
            # Ajouter les nouveaux liens à la file
            self.add_urls_to_queue(page_data['links'])
            
            # Respecter le délai (politesse)
            if len(self.visited) < self.max_pages:
                time.sleep(self.delay)
        
        print(f"\n✅ Crawling terminé!")
        print(f"📄 {len(self.results)} pages crawlées")
    
    def save_results(self, output_file: str):
        """
        Sauvegarde les résultats en JSONL
        
        Args:
            output_file: Chemin du fichier de sortie
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in self.results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        print(f"💾 Résultats sauvegardés dans: {output_file}")


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Web Crawler pour le TP1 - Indexation Web ENSAI 2026'
    )
    parser.add_argument(
        '--url',
        type=str,
        default='https://web-scraping.dev/products',
        help='URL de départ (défaut: https://web-scraping.dev/products)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=50,
        help='Nombre maximum de pages à crawler (défaut: 50)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Délai en secondes entre deux requêtes (défaut: 1.0)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='results/crawled_pages.jsonl',
        help='Fichier de sortie (défaut: results/crawled_pages.jsonl)'
    )
    
    args = parser.parse_args()
    
    # Créer le crawler
    crawler = WebCrawler(
        start_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay
    )
    
    # Lancer le crawling
    crawler.crawl()
    
    # Sauvegarder les résultats
    crawler.save_results(args.output)


if __name__ == '__main__':
    main()