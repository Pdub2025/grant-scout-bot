# grant_scraper.py
import requests
from bs4 import BeautifulSoup
import datetime
import os

# Target URL
URL = "https://www.energy.gov/bil/ev-charging-programs"
KEYWORDS = ["EV charging", "rural", "infrastructure", "NEVI", "funding"]

# Fetch and parse page
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')
links = soup.find_all('a')

# Search for keyword matches
matches = []
for link in links:
    text = link.get_text().strip()
    href = link.get('href')
    if any(kw.lower() in text.lower() for kw in KEYWORDS):
        matches.append(f"{text} - {href}")

# Always create the output file
now = datetime.datetime.now().strftime("%Y-%m-%d")
filename = f"grant_results_{now}.txt"
with open(filename, "w") as f:
    if matches:
        f.write("\n".join(matches))
    else:
        f.write("No matches found.")

print(f"Scraping complete. Saved {len(matches)} matches to {filename}")
print("Current directory contents:", os.listdir())
print("\n--- GRANT RESULTS ---\n" + "\n".join(matches))
