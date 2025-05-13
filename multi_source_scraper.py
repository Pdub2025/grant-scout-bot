# multi_source_scraper.py
import requests
from bs4 import BeautifulSoup
import datetime
import os
from urllib.parse import urljoin
from collections import defaultdict
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# Load Google credentials from environment
creds_json = os.environ.get("GOOGLE_SHEETS_CREDS")
if creds_json is None:
    raise ValueError("Missing GOOGLE_SHEETS_CREDS environment variable.")
creds_dict = json.loads(creds_json)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)

# Open the target Google Sheet
sheet = gc.open("EV Grant Scouting Results").sheet1
sheet.clear()
sheet.append_row(["Date", "Source", "Priority", "Title", "URL"])

# Define grant source URLs
SOURCES = {
    "DOE BIL EV Charging Programs": "https://www.energy.gov/bil/ev-charging-programs",
    "Grants.gov Search - EV": "https://www.grants.gov/search-results.html?keywords=EV%20charging",
    "USDOT EV Infrastructure": "https://www.transportation.gov/rural/ev-toolkit",
    "USDA Rural Development": "https://www.rd.usda.gov/programs-services/electric-programs",
    "FHWA NEVI Program": "https://www.fhwa.dot.gov/environment/alternative_fuel_corridors/ev/"
}

KEYWORDS = ["EV charging", "rural", "infrastructure", "NEVI", "funding"]
PRIORITY_TERMS = ["rural", "NEVI", "deadline", "now open", "application"]

results = []
summary = defaultdict(int)
priority_count = 0
now = datetime.datetime.now().strftime("%Y-%m-%d")

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
                is_priority = any(term in text.lower() for term in PRIORITY_TERMS)
                priority_flag = "⭐" if is_priority else ""

                results.append(f"[{source_name}] {priority_flag} {text} - {full_link}")
                summary[source_name] += 1
                if is_priority:
                    priority_count += 1

                sheet.append_row([now, source_name, priority_flag, text, full_link])

    except Exception as e:
        results.append(f"[{source_name}] ERROR: {str(e)}")

# Print summary
print(f"Scraping complete. {len(results)} items found across sources.\n")
print("--- SUMMARY ---")
for source, count in summary.items():
    print(f"{source}: {count} match(es)")
print(f"\nPriority items flagged: {priority_count}\n")

print("--- GRANT RESULTS ---\n" + "\n".join(results))
