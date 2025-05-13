# grant_scraper.py
import requests
from bs4 import BeautifulSoup
import datetime

# Target URL (you can add more later)
URL = "https://www.energy.gov/bil/ev-charging-programs"
KEYWORDS = ["EV charging", "rural", "infrastructure", "NEVI", "funding"]

# Fetch the webpage
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all links
links = soup.find_all('a')

# Store matches
matches = []
for link in links:
    text = link.get_text().strip()
    href = link.get('href')
    if any(kw.lower() in text.lower() for kw in KEYWORDS):
        matches.append(f"{text} - {href}")

# Save results to a file
now = datetime.datetime.now().strftime("%Y-%m-%d")
with open(f"grant_results_{now}.txt", "w") as f:
    if matches:
        f.write("\n".join(matches))
    else:
        f.write("No matches found.")

print("Scraping complete. Results saved.")
