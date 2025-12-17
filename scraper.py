import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import re


class AllHackathonsScraper:
    """Scraper for allhackathons.com website"""

    def __init__(self, base_url: str = "https://allhackathons.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch a page and return BeautifulSoup object"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                print(f"Error fetching {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None
        return None

    def extract_hackathon_cards(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract hackathon cards from a listing page"""
        hackathons = []
        cards = soup.find_all('div', class_='row align-items-center bg-white mb-4 py-5 px-4')

        for card in cards:
            try:
                hackathon = {}

                # Extract title and URL
                title_link = card.find('a', class_='h5 text-darkblue d-block mt-3')
                if title_link:
                    hackathon['title'] = title_link.text.strip()
                    hackathon['detail_url'] = self.base_url + title_link.get('href', '')

                # Extract image
                img = card.find('img', class_='img-fluid')
                if img:
                    hackathon['image_url'] = self.base_url + img.get('src', '')

                # Extract location badge
                badge = card.find('span', class_='badge bg-success')
                if badge:
                    hackathon['location_type'] = badge.text.strip()

                # Extract dates
                date_p = card.find_all('p')
                if len(date_p) > 0:
                    hackathon['dates'] = date_p[0].text.strip()

                # Extract status
                status_div = card.find('div', string=re.compile('Upcoming|Open|Ended'))
                if status_div:
                    hackathon['status'] = status_div.text.strip()

                # Extract description
                desc_p = card.find('p', class_='text-muted mt-2 mb-0')
                if desc_p:
                    hackathon['short_description'] = desc_p.text.strip()

                # Extract themes
                themes_div = card.find('div', class_='font-size-sm text-muted mt-3')
                if themes_div:
                    theme_links = themes_div.find_all('a')
                    hackathon['themes'] = [link.text.strip() for link in theme_links]

                    # Extract location from the same div
                    location_text = themes_div.get_text()
                    # Remove theme text and extract location
                    for link in theme_links:
                        location_text = location_text.replace(link.text, '')
                    location_text = location_text.replace('·', '').strip()
                    if location_text:
                        hackathon['location'] = location_text

                hackathons.append(hackathon)
            except Exception as e:
                print(f"Error extracting hackathon card: {e}")
                continue

        return hackathons

    def extract_hackathon_details(self, url: str) -> Dict:
        """Extract detailed information from a hackathon detail page"""
        soup = self.get_page(url)
        if not soup:
            return {}

        details = {}

        try:
            # Extract description
            desc_card = soup.find('div', class_='card-body')
            if desc_card:
                desc_content = desc_card.find('div', class_='text-muted lh-lg')
                if desc_content:
                    # Get all paragraphs
                    paragraphs = desc_content.find_all('p')
                    details['full_description'] = '\n\n'.join([p.text.strip() for p in paragraphs])

            # Extract event dates
            dates_card = soup.find('h5', string=re.compile('Event Dates'))
            if dates_card:
                dates_body = dates_card.find_next('div')
                if dates_body:
                    date_fw = dates_body.find('div', class_='fw-medium')
                    date_small = dates_body.find('small', class_='text-muted')
                    if date_fw:
                        details['start_date'] = date_fw.text.strip()
                    if date_small:
                        details['end_date'] = date_small.text.replace('to', '').strip()

            # Extract location
            location_card = soup.find('h5', string=re.compile('Location'))
            if location_card:
                location_body = location_card.find_next('div', class_='text-muted')
                if location_body:
                    location_p = location_body.find('p')
                    if location_p:
                        details['location'] = location_p.text.strip()

            # Extract organizer
            org_card = soup.find('h5', string=re.compile('Organizer'))
            if org_card:
                org_body = org_card.find_next('div', class_='text-muted')
                if org_body:
                    org_p = org_body.find('p')
                    if org_p:
                        details['organizer'] = org_p.text.strip()

            # Extract prizes
            prizes_card = soup.find('h5', string=re.compile('Prizes'))
            if prizes_card:
                prizes_body = prizes_card.find_next('div', class_='text-muted')
                if prizes_body:
                    prizes_p = prizes_body.find('p')
                    if prizes_p:
                        details['prizes'] = prizes_p.text.strip()

            # Extract website link
            website_card = soup.find('h5', string=re.compile('Website'))
            if website_card:
                website_body = website_card.find_next('div', class_='text-muted')
                if website_body:
                    website_link = website_body.find('a')
                    if website_link:
                        details['website'] = website_link.get('href', '')

        except Exception as e:
            print(f"Error extracting details from {url}: {e}")

        return details

    def get_total_pages(self, theme_url: str) -> int:
        """Determine the total number of pages for a theme"""
        soup = self.get_page(theme_url)
        if not soup:
            return 1

        pagination = soup.find('div', class_='pagination')
        if not pagination:
            return 1

        page_links = pagination.find_all('a', class_='endless_page_link')
        max_page = 1

        for link in page_links:
            try:
                page_num = int(link.text.strip())
                max_page = max(max_page, page_num)
            except ValueError:
                continue

        return max_page

    def scrape_theme(self, theme: str = "remote", save_file: str = None) -> List[Dict]:
        """
        Scrape all hackathons for a specific theme

        Args:
            theme: The theme to scrape (e.g., 'remote', 'ai', 'blockchain')
            save_file: Optional file path to save results as JSON

        Returns:
            List of hackathon dictionaries with full details
        """
        theme_url = f"{self.base_url}/themes/{theme}/"
        print(f"Starting scrape for theme: {theme}")
        print(f"Base URL: {theme_url}")

        # Get total pages
        total_pages = self.get_total_pages(theme_url)
        print(f"Found {total_pages} pages to scrape")

        all_hackathons = []

        # Scrape each page
        for page in range(1, total_pages + 1):
            if page == 1:
                page_url = theme_url
            else:
                page_url = f"{theme_url}?page={page}"

            print(f"\nScraping page {page}/{total_pages}: {page_url}")
            soup = self.get_page(page_url)

            if not soup:
                print(f"Failed to fetch page {page}")
                continue

            # Extract hackathon cards from this page
            hackathons = self.extract_hackathon_cards(soup)
            print(f"Found {len(hackathons)} hackathons on page {page}")

            # Get detailed information for each hackathon
            for idx, hackathon in enumerate(hackathons, 1):
                print(f"  Fetching details for hackathon {idx}/{len(hackathons)}: {hackathon.get('title', 'Unknown')}")

                if 'detail_url' in hackathon:
                    details = self.extract_hackathon_details(hackathon['detail_url'])
                    hackathon.update(details)

                all_hackathons.append(hackathon)

                # Be polite - add a small delay between requests
                time.sleep(1)

            # Delay between pages
            time.sleep(2)

        print(f"\n{'='*60}")
        print(f"Scraping complete! Total hackathons found: {len(all_hackathons)}")
        print(f"{'='*60}")

        # Save to file if specified
        if save_file:
            self.save_to_json(all_hackathons, save_file)

        return all_hackathons

    def scrape_all_themes(self, save_file: str = None) -> Dict[str, List[Dict]]:
        """Scrape hackathons from all available themes"""
        # Common themes based on the HTML
        themes = [
            'ai', 'api', 'art', 'ar-vr', 'audio', 'beginner', 'big-data',
            'blockchain', 'databases', 'design', 'devops', 'education',
            'energy', 'enterprise', 'fintech', 'friendly', 'games', 'health',
            'industry', 'iot', 'low-no-code', 'machine-learning', 'media',
            'metaverse', 'mobile', 'nft', 'non-profit', 'quantum', 'retail',
            'robotics', 'science', 'security', 'social', 'transport', 'video',
            'wearables', 'web', 'remote'
        ]

        all_themes_data = {}

        for theme in themes:
            print(f"\n{'='*60}")
            print(f"Scraping theme: {theme}")
            print(f"{'='*60}")

            hackathons = self.scrape_theme(theme)
            all_themes_data[theme] = hackathons

            # Longer delay between themes
            time.sleep(5)

        # Save to file if specified
        if save_file:
            self.save_to_json(all_themes_data, save_file)

        return all_themes_data

    def save_to_json(self, data: any, filename: str):
        """Save data to a JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\nData saved to {filename}")
        except Exception as e:
            print(f"Error saving to {filename}: {e}")


def main():
    """Main function to run the scraper"""
    scraper = AllHackathonsScraper()

    # Option 1: Scrape only remote hackathons
    print("Scraping remote hackathons...")
    remote_hackathons = scraper.scrape_theme(
        theme="remote",
        save_file="remote_hackathons.json"
    )

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total hackathons scraped: {len(remote_hackathons)}")

    if remote_hackathons:
        print(f"\nSample hackathon:")
        print(json.dumps(remote_hackathons[0], indent=2))

    # Option 2: Uncomment to scrape all themes (this will take a long time)
    # print("\n\nScraping ALL themes...")
    # all_data = scraper.scrape_all_themes(save_file="all_hackathons.json")


if __name__ == "__main__":
    main()
