"""
Web scraper to collect URLs related to IU South Bend
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def scrape_iu_southbend_urls():
    """Scrape URLs from IU South Bend website"""

    # Starting URLs including faculty and department pages
    seed_urls = [
        "https://www.iusb.edu",
        "https://www.iusb.edu/academics/index.html",
        "https://www.iusb.edu/about/index.html",
        # College and School pages
        "https://arts.iusb.edu/",
        "https://education.iusb.edu/",
        "https://business.iusb.edu/",
        "https://nursing.iusb.edu/",
        "https://science.iusb.edu/",
        "https://liberal-arts.iusb.edu/",
        # Faculty directories
        "https://www.iusb.edu/computer-science/",
        "https://www.iusb.edu/mathematics/",
        "https://cs.iusb.edu/",
        "https://math.iusb.edu/",
        # Specific department pages
        "https://academics.iusb.edu/",
        "https://students.iusb.edu/",
        "https://library.iusb.edu/",
    ]

    visited_urls = set()
    collected_urls = set()
    urls_to_visit = seed_urls.copy()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    max_pages = 150  # Increased limit for more coverage
    pages_scraped = 0

    print(f"Starting to scrape IU South Bend URLs from {len(seed_urls)} seed URLs")
    print("-" * 50)

    while urls_to_visit and pages_scraped < max_pages:
        current_url = urls_to_visit.pop(0)

        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)

        try:
            response = requests.get(current_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links on the page
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)

                # Parse the URL
                parsed = urlparse(full_url)

                # Only collect URLs related to IU South Bend
                if 'iusb.edu' in parsed.netloc or 'southbend' in parsed.netloc.lower():
                    # Clean URL (remove fragments)
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    if parsed.query:
                        clean_url += f"?{parsed.query}"

                    collected_urls.add(clean_url)

                    # Add to visit queue if it's an iusb.edu page
                    if 'iusb.edu' in parsed.netloc and clean_url not in visited_urls:
                        urls_to_visit.append(clean_url)

            pages_scraped += 1
            print(f"Scraped page {pages_scraped}: {current_url[:60]}...")

            # Be respectful - add delay between requests
            time.sleep(0.5)

        except requests.RequestException as e:
            print(f"Error scraping {current_url}: {e}")
            continue

    return sorted(collected_urls)

def save_urls_to_file(urls, filename):
    """Save collected URLs to a file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# IU South Bend URLs\n")
        f.write(f"# Total URLs collected: {len(urls)}\n")
        f.write("# " + "=" * 50 + "\n\n")

        for url in urls:
            f.write(url + "\n")

    print(f"\nSaved {len(urls)} URLs to {filename}")

def main():
    output_file = "iu_southbend_urls.txt"

    print("IU South Bend URL Scraper")
    print("=" * 50)

    urls = scrape_iu_southbend_urls()

    print(f"\nTotal unique URLs collected: {len(urls)}")

    save_urls_to_file(urls, output_file)

    print(f"\nDone! Check '{output_file}' for the results.")

if __name__ == "__main__":
    main()
