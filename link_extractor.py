import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from typing import List, Dict, Set, Optional
import re
from fake_useragent import UserAgent
from config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkExtractor:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.session = requests.Session()
        self.ua = UserAgent()
        self.visited_urls: Set[str] = set()
        self.found_links: Set[str] = set()
        self.found_forms: List[Dict] = []
        
        # Set headers
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def is_internal_url(self, url: str) -> bool:
        """Check if URL belongs to the same domain"""
        try:
            parsed = urlparse(url)
            return parsed.netloc == self.domain or parsed.netloc == ''
        except:
            return False
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and sorting query parameters"""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        sorted_query = '&'.join([f"{k}={v[0]}" for k, v in sorted(query_params.items())])
        
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if sorted_query:
            normalized += f"?{sorted_query}"
        
        return normalized
    
    def extract_links_from_page(self, url: str) -> List[str]:
        """Extract all internal links from a single page"""
        try:
            response = self.session.get(url, timeout=config.request_timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            # Extract links from various HTML elements
            for tag in soup.find_all(['a', 'link', 'area']):
                href = tag.get('href')
                if href:
                    absolute_url = urljoin(url, href)
                    if self.is_internal_url(absolute_url):
                        normalized = self.normalize_url(absolute_url)
                        links.append(normalized)
            
            # Extract JavaScript-based links
            for script in soup.find_all('script'):
                if script.string:
                    # Look for URLs in JavaScript
                    js_urls = re.findall(r'["\']([^"\']*(?:\.html|\.php|\.asp|\.jsp|/[^"\']*?))["\']', script.string)
                    for js_url in js_urls:
                        if js_url.startswith('/') or js_url.startswith('http'):
                            absolute_url = urljoin(url, js_url)
                            if self.is_internal_url(absolute_url):
                                normalized = self.normalize_url(absolute_url)
                                links.append(normalized)
            
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {str(e)}")
            return []
    
    def extract_forms_from_page(self, url: str) -> List[Dict]:
        """Extract all forms from a single page"""
        try:
            response = self.session.get(url, timeout=config.request_timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            forms = []
            
            for form in soup.find_all('form'):
                form_data = {
                    'url': url,
                    'action': urljoin(url, form.get('action', '')),
                    'method': form.get('method', 'GET').upper(),
                    'inputs': [],
                    'has_file_upload': False
                }
                
                # Extract input fields
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    input_data = {
                        'name': input_tag.get('name', ''),
                        'type': input_tag.get('type', 'text'),
                        'value': input_tag.get('value', ''),
                        'required': input_tag.has_attr('required'),
                        'placeholder': input_tag.get('placeholder', '')
                    }
                    
                    if input_data['type'] == 'file':
                        form_data['has_file_upload'] = True
                    
                    if input_data['name']:  # Only add inputs with names
                        form_data['inputs'].append(input_data)
                
                forms.append(form_data)
            
            return forms
            
        except Exception as e:
            logger.error(f"Error extracting forms from {url}: {str(e)}")
            return []
    
    def crawl_website(self, max_depth: int = None) -> Dict:
        """Crawl website to extract all internal links and forms"""
        if max_depth is None:
            max_depth = config.max_depth
            
        urls_to_visit = [(self.base_url, 0)]
        
        while urls_to_visit:
            current_url, depth = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls or depth > max_depth:
                continue
                
            logger.info(f"Crawling: {current_url} (depth: {depth})")
            self.visited_urls.add(current_url)
            
            # Extract links
            page_links = self.extract_links_from_page(current_url)
            for link in page_links:
                if link not in self.visited_urls and link not in self.found_links:
                    self.found_links.add(link)
                    if depth < max_depth:
                        urls_to_visit.append((link, depth + 1))
            
            # Extract forms
            page_forms = self.extract_forms_from_page(current_url)
            self.found_forms.extend(page_forms)
        
        return {
            'base_url': self.base_url,
            'total_links': len(self.found_links),
            'total_forms': len(self.found_forms),
            'links': list(self.found_links),
            'forms': self.found_forms,
            'visited_pages': len(self.visited_urls)
        }
    
    def get_interesting_endpoints(self) -> List[Dict]:
        """Get potentially interesting endpoints for vulnerability testing"""
        interesting = []
        
        # Look for admin/login pages
        admin_patterns = [
            r'admin', r'login', r'auth', r'dashboard', r'panel',
            r'manage', r'control', r'config', r'settings'
        ]
        
        for link in self.found_links:
            for pattern in admin_patterns:
                if re.search(pattern, link, re.IGNORECASE):
                    interesting.append({
                        'url': link,
                        'type': 'admin_endpoint',
                        'reason': f'Contains "{pattern}" pattern'
                    })
                    break
        
        # Look for API endpoints
        api_patterns = [r'api/', r'/v\d+/', r'rest/', r'graphql', r'json']
        
        for link in self.found_links:
            for pattern in api_patterns:
                if re.search(pattern, link, re.IGNORECASE):
                    interesting.append({
                        'url': link,
                        'type': 'api_endpoint',
                        'reason': f'Contains API pattern "{pattern}"'
                    })
                    break
        
        # Look for file uploads
        for form in self.found_forms:
            if form['has_file_upload']:
                interesting.append({
                    'url': form['url'],
                    'type': 'file_upload',
                    'reason': 'Contains file upload functionality',
                    'form_data': form
                })
        
        return interesting