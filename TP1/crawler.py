"""
Web Crawler for TP1
This crawler explores a website by prioritizing product pages.
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
    """Class to verify and respect robots.txt rules"""
    
    def __init__(self):
        self._parsers = {}  
    
    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """
        Check if URL can be crawled according to robots.txt
        
        Args:
            url: URL to verify
            user_agent: Crawler's user agent
            
        Returns:
            True if crawling is allowed, False otherwise
        """
        parsed_url = urllib.parse.urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"
        
        # Check cache
        if base_url not in self._parsers:
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
                self._parsers[base_url] = parser
            except Exception as e:
                print(f"Unable to read robots.txt for {base_url}: {e}")
                # Allow by default if error
                return True
        
        return self._parsers[base_url].can_fetch(user_agent, url)


def fetch_page(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetch HTML content of a web page
    
    Args:
        url: URL of the page to fetch
        timeout: Maximum wait time in seconds
        
    Returns:
        HTML content of the page or None on error
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (ENSAI Web Crawler TP1/1.0; Educational purpose)'
        }
        req = Request(url, headers=headers)
        
        with urlopen(req, timeout=timeout) as response:
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                print(f"Non-HTML content ignored: {url} ({content_type})")
                return None
            
            return response.read().decode('utf-8', errors='ignore')
    
    except HTTPError as e:
        print(f"HTTP Error {e.code} for {url}")
        return None
    except URLError as e:
        print(f"URL Error for {url}: {e.reason}")
        return None
    except Exception as e:
        print(f"Unexpected error for {url}: {e}")
        return None


def extract_title(soup: BeautifulSoup) -> str:
    """
    Extract page title
    
    Args:
        soup: BeautifulSoup object of the page
        
    Returns:
        Page title or empty string
    """
    # Search in <h3 class="product-title">
    product_title = soup.find('h3', class_='product-title')
    if product_title:
        return product_title.get_text(strip=True)
    
    # Search in <title> with selective prefix cleaning
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)
        
        # Clean only if it's NOT "page X"
        if 'page' not in title.lower():
            if title.startswith('web-scraping.dev product '):
                title = title.replace('web-scraping.dev product ', '', 1)
            elif title.startswith('web-scraping.dev '):
                title = title.replace('web-scraping.dev ', '', 1)
        
        return title
    
    # Search in <h1> as fallback
    h1_tag = soup.find('h1')
    if h1_tag:
        return h1_tag.get_text(strip=True)
    
    return ""


def extract_description(soup: BeautifulSoup) -> str:
    """
    Extract description (first significant paragraph)
    
    Args:
        soup: BeautifulSoup object of the page
        
    Returns:
        Description or empty string
    """
    # Search in product content area
    product_desc = soup.find('p', class_='card-description')
    if product_desc:
        return product_desc.get_text(strip=True)
    
    # Search in main content areas
    content_areas = soup.find_all(['div'], class_=lambda x: x and ('content' in x.lower() or 'description' in x.lower()))
    
    for area in content_areas:
        paragraphs = area.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Select first significant paragraph
            if len(text) > 20:
                return text
    
    # Fallback: search in all paragraphs
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 20:
            return text
    
    return ""


def extract_product_features(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extract product features from HTML table
    
    Args:
        soup: BeautifulSoup object of the page
        
    Returns:
        Dictionary of product features
    """
    features = {}
    
    # Search for feature rows in table
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
    Extract product reviews
    
    Args:
        soup: BeautifulSoup object of the page
        
    Returns:
        List of product reviews
    """
    reviews = []
    
    # Method 1: Extract from JSON script (for dynamic content)
    reviews_script = soup.find('script', id='reviews-data')
    if reviews_script and reviews_script.string:
        try:
            reviews = json.loads(reviews_script.string)
            return reviews
        except json.JSONDecodeError:
            pass
    
    # Method 2: Fallback - extract from rendered HTML (if JavaScript executed)
    review_containers = soup.find_all('div', class_='review')
    
    for container in review_containers:
        review = {}
        
        # Extract date
        date_span = container.find('span')
        if date_span:
            review['date'] = date_span.get_text(strip=True)
        
        # Extract ID from CSS classes
        classes = container.get('class', [])
        for cls in classes:
            if cls.startswith('review-') and cls != 'review':
                # Clean "review-" prefix
                review['id'] = cls.replace('review-', '', 1)
                break
        
        # Extract rating (number of star SVGs)
        stars = container.find_all('svg')
        if stars:
            review['rating'] = len(stars)
        
        # Extract text
        text_p = container.find('p')
        if text_p:
            review['text'] = text_p.get_text(strip=True)
        
        # Add only if data was found
        if review:
            reviews.append(review)
    
    return reviews


def extract_links(soup: BeautifulSoup, base_url: str, current_url: str) -> List[str]:
    """
    Extract all links from page and normalize them
    
    Args:
        soup: BeautifulSoup object of the page
        base_url: Base URL of the site
        current_url: URL of current page
        
    Returns:
        List of unique absolute URLs
    """
    links = []
    seen = set()
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        
        # Resolve relative URLs
        absolute_url = urllib.parse.urljoin(current_url, href)
        
        # Clean URL (remove fragments)
        parsed = urllib.parse.urlparse(absolute_url)
        clean_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''
        ))
        
        # Check domain
        if clean_url.startswith(base_url) and clean_url not in seen:
            links.append(clean_url)
            seen.add(clean_url)
    
    return links


class WebCrawler:
    """Web crawler with priority for product pages"""
    
    def __init__(self, start_url: str, max_pages: int = 50, delay: float = 1.0):
        """
        Initialize crawler
        
        Args:
            start_url: Starting URL
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests (politeness)
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.delay = delay
        
        # Extract base URL
        parsed = urllib.parse.urlparse(start_url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Priority queue
        # Priority 0 = product pages (crawl first)
        # Priority 1 = other pages
        self.to_visit = deque()
        self.to_visit.append((1, start_url))
        
        # Set of already visited URLs
        self.visited: Set[str] = set()
        
        # List of results
        self.results: List[Dict] = []
        
        # Robots.txt checker instance
        self.robots_checker = RobotsChecker()
    
    def is_product_url(self, url: str) -> bool:
        """
        Determine if URL is a product page
        
        Args:
            url: URL to check
            
        Returns:
            True if it's a product page
        """
        return 'product' in url.lower()
    
    def add_urls_to_queue(self, urls: List[str]):
        """
        Add URLs to queue with priority
        
        Args:
            urls: List of URLs to add
        """
        for url in urls:
            if url not in self.visited and url not in [u for _, u in self.to_visit]:
                priority = 0 if self.is_product_url(url) else 1
                self.to_visit.append((priority, url))
    
    def crawl(self):
        """Start crawling"""
        print(f"Starting crawler from {self.start_url}")
        print(f"Target: {self.max_pages} pages maximum")
        print(f"Delay between requests: {self.delay}s\n")
        
        while self.to_visit and len(self.visited) < self.max_pages:
            # Sort by priority before popping
            self.to_visit = deque(sorted(self.to_visit, key=lambda x: x[0]))
            
            priority, url = self.to_visit.popleft()
            
            if url in self.visited:
                continue
            
            # Check robots.txt
            if not self.robots_checker.can_fetch(url):
                print(f"Blocked by robots.txt: {url}")
                continue
            
            # Mark as visited
            self.visited.add(url)
            
            # Priority indicator
            priority_icon = "[PROD]" if priority == 0 else "[PAGE]"
            print(f"{priority_icon} [{len(self.visited)}/{self.max_pages}] Crawling: {url}")
            
            # Fetch page
            html = fetch_page(url)
            if not html:
                continue
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract data
            page_data = {
                'url': url,
                'title': extract_title(soup),
                'description': extract_description(soup),
                'product_features': extract_product_features(soup),
                'links': extract_links(soup, self.base_url, url),
                'product_reviews': extract_product_reviews(soup)
            }
            
            self.results.append(page_data)
            
            # Add new links to queue
            self.add_urls_to_queue(page_data['links'])
            
            # Respect politeness delay
            if len(self.visited) < self.max_pages:
                time.sleep(self.delay)
        
        print(f"\nCrawling complete!")
        print(f"{len(self.results)} pages crawled")
    
    def save_results(self, output_file: str):
        """
        Save results in JSONL format
        
        Args:
            output_file: Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in self.results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        print(f"Results saved to: {output_file}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Web Crawler for TP1 - Web Indexing ENSAI 2026'
    )
    parser.add_argument(
        '--url',
        type=str,
        default='https://web-scraping.dev/products',
        help='Starting URL (default: https://web-scraping.dev/products)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=50,
        help='Maximum number of pages to crawl (default: 50)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay in seconds between requests (default: 1.0)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output/crawled_pages.jsonl',
        help='Output file (default: output/crawled_pages.jsonl)'
    )
    
    args = parser.parse_args()
    
    # Create crawler
    crawler = WebCrawler(
        start_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay
    )
    
    # Start crawling
    crawler.crawl()
    
    # Save results
    crawler.save_results(args.output)


if __name__ == '__main__':
    main()