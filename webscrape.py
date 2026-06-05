import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse
from collections import deque

BASE_URL = "https://sece.ac.in"

visited = set()
queue = deque([BASE_URL])

data = []

MAX_PAGES = 100

while queue and len(visited) < MAX_PAGES:
    url = queue.popleft()

    if url in visited:
        continue

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if response.status_code != 200:
            continue

        visited.add(url)

        soup = BeautifulSoup(response.text, "lxml")

        title = soup.title.text.strip() if soup.title else ""

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        data.append({
            "url": url,
            "title": title,
            "content": text
        })

        print(f"Scraped: {url}")

        for link in soup.find_all("a", href=True):

            full_url = urljoin(url, link["href"])

            if urlparse(full_url).netloc == urlparse(BASE_URL).netloc:
                if full_url not in visited:
                    queue.append(full_url)

    except Exception as e:
        print(e)

df = pd.DataFrame(data)

df.to_csv("college_website_data.csv", index=False)

print(f"Saved {len(df)} pages")