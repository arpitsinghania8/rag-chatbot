import requests
from bs4 import BeautifulSoup
import json
import os
import time
import urllib3
import ssl
import certifi
import xmltodict
from urllib.parse import urljoin

# Disable SSL warnings
urllib3.disable_warnings()

SITEMAP_URL = "https://www.angelone.in/sitemap.xml"
SUPPORT_BASE_URL = "https://www.angelone.in/support"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
}

def get_article_links_from_sitemap():
    print("Fetching sitemap...")
    try:
        session = requests.Session()
        resp = session.get(SITEMAP_URL, headers=HEADERS, verify=False)
        
        if resp.status_code != 200:
            print(f"Failed to fetch sitemap. Status code: {resp.status_code}")
            return crawl_support_pages()

        # Try parsing as XML using xmltodict
        try:
            sitemap = xmltodict.parse(resp.content)
            urls = []
            
            # Debug the sitemap structure
            print("Sitemap structure:", json.dumps(sitemap, indent=2))
            
            # Handle nested sitemaps
            if 'sitemapindex' in sitemap:
                print("Found sitemapindex")
                sitemaps = sitemap['sitemapindex']['sitemap']
                # Handle both single and multiple sitemaps
                if isinstance(sitemaps, dict):
                    sitemaps = [sitemaps]
                    
                for sitemap_entry in sitemaps:
                    try:
                        sub_resp = session.get(sitemap_entry['loc'], headers=HEADERS, verify=False)
                        sub_sitemap = xmltodict.parse(sub_resp.content)
                        if 'urlset' in sub_sitemap:
                            urls_in_set = sub_sitemap['urlset']['url']
                            # Handle both single and multiple URLs
                            if isinstance(urls_in_set, dict):
                                urls_in_set = [urls_in_set]
                            
                            for url in urls_in_set:
                                if '/support/article/' in url['loc']:
                                    urls.append(url['loc'])
                    except Exception as e:
                        print(f"Error processing sub-sitemap: {e}")
                        continue
                        
            # Handle direct URL list
            elif 'urlset' in sitemap:
                print("Found urlset")
                urls_in_set = sitemap['urlset']['url']
                # Handle both single and multiple URLs
                if isinstance(urls_in_set, dict):
                    urls_in_set = [urls_in_set]
                    
                for url in urls_in_set:
                    if '/support/article/' in url['loc']:
                        urls.append(url['loc'])
                        
            if urls:
                print(f"Found {len(urls)} article links in sitemap.")
                return urls
                
        except Exception as e:
            print(f"XML parsing failed: {e}, trying HTML parsing...")
            import traceback
            print("Full error:", traceback.format_exc())
    except Exception as e:
        print(f"Sitemap fetch failed: {e}")
        import traceback
        print("Full error:", traceback.format_exc())

    return crawl_support_pages()

def crawl_support_pages():
    """Fallback method to directly crawl the support pages"""
    print("Falling back to direct support page crawling...")
    urls = []
    try:
        resp = requests.get(
            SUPPORT_BASE_URL, 
            headers=HEADERS,
            verify=False
        )
        
        if resp.status_code != 200:
            print(f"Failed to fetch support page. Status code: {resp.status_code}")
            print("Response content:", resp.text[:500])  # Print first 500 chars of response
            return []
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Try different selectors to find links
        for link in soup.find_all(['a', 'link'], href=True):
            href = link['href']
            if isinstance(href, str) and '/support/article/' in href:
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('//'):
                    full_url = f"https:{href}"
                else:
                    full_url = urljoin(SUPPORT_BASE_URL, href)
                urls.append(full_url)
                
        urls = list(set(urls))  # Remove duplicates
        print(f"Found {len(urls)} article links from direct crawling.")
        
        if not urls:
            print("No links found in HTML. Page content sample:", soup.text[:500])
        
    except Exception as e:
        print(f"Error crawling support pages: {e}")
        import traceback
        print("Full error:", traceback.format_exc())
    
    return urls

def extract_text_from_page(url):
    try:
        print(f"Scraping: {url}")
        r = requests.get(url, headers=HEADERS, verify=False)
        if r.status_code != 200:
            print(f"Failed to fetch {url}. Status code: {r.status_code}")
            return None
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Try to find the main content area
        content_selectors = [
            "main",
            "article",
            ".article-content",
            "#content",
            ".content"
        ]
        
        content = None
        for selector in content_selectors:
            if selector.startswith('.'):
                element = soup.find(class_=selector[1:])
            elif selector.startswith('#'):
                element = soup.find(id=selector[1:])
            else:
                element = soup.find(selector)
                
            if element:
                content = element
                break
        
        if not content:
            content = soup.body if soup.body else soup

        # Remove unwanted elements
        for unwanted in content.find_all(['script', 'style', 'nav', 'header', 'footer']):
            unwanted.decompose()

        text = content.get_text(separator="\n").strip()
        return {"url": url, "content": text}
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    os.makedirs("data/raw_html", exist_ok=True)
    links = get_article_links_from_sitemap()
    
    if not links:
        print("No links found. Please check the website structure or network connection.")
        return
        
    docs = []
    
    for link in links:
        doc = extract_text_from_page(link)
        if doc:
            docs.append(doc)
        time.sleep(1)  # Increased delay to be more polite

    with open("data/raw_html/angelone_docs.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraped and saved {len(docs)} pages.")

if __name__ == "__main__":
    main()
