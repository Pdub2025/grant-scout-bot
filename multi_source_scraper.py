# multi_source_scraper.py
import requests
from bs4 import BeautifulSoup
import datetime
import os
from urllib.parse import urljoin

# Define grant source URLs
SOURCES = {
    "DOE BIL EV Charging Programs": "https://www.energy.gov/bil/ev-charging-programs",
    "Grants.gov Search - EV": "https://www.grants.gov/search-results.html?keywords=EV%20charging",
    "USDOT EV Infrastructure": "https://www.transportation.gov/rural/ev-toolkit",
    "USDA Rural Development": "https://www.rd.usda.gov/programs-services/electric-programs",
    "FHWA NEVI Program": "https://www.fhwa.dot.gov/environment/alternative_fuel_corridors/ev/"
}

KEYWORDS = ["EV charging", "rural", "infrastructure", "NEVI", "funding"]

results = []

for source_name, base_url in SOURCES.items():
    try:
        response = requests.get(base_url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        for link in links:
            text = link.get_text().strip()
            href = link.get('href')

            # Skip empty, javascript, or anchor-only links
            if not href or href.startswith("#") or href.lower().startswith("javascript"):
                continue

            if any(kw.lower() in text.lower() for kw in KEYWORDS):
                full_link = urljoin(base_url, href)
                results.append(f"[{source_name}] {text} - {full_link}")

    except Exception as e:
        results.append(f"[{source_name}] ERROR: {str(e)}")

# Always write results
now = datetime.datetime.now().strftime("%Y-%m-%d")
filename = f"multi_grant_results_{now}.txt"

with open(filename, "w", encoding="utf-8") as f:
    if results:
        f.write("\n".join(results))
    else:
        f.write("No matches found.")

# Print summary
print(f"Scraping complete. {len(results)} items found across sources.")
print("\n--- GRANT RESULTS ---\n" + "\n".join(results))
