import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from playwright.sync_api import sync_playwright


BASE_URL = "https://www.blogto.com/events/"
resp = requests.get(BASE_URL)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(BASE_URL, timeout=60000)
    page.wait_for_selector(".event-info-box", timeout=10000)  # Wait until events load

    html = page.content()
    browser.close()

soup = BeautifulSoup(html, "html.parser")

events = []

# Select each event card
for card in soup.select("div.event-info-box")[:10]:
    try:
        title_tag = card.select_one(".event-info-box-title-link")
        title = title_tag.get_text(strip=True)
        link = title_tag['href']
        if not link.startswith("http"):
            link = "https://www.blogto.com" + link

        img_tag = card.select_one("img.event-info-box-image")
        img_url = img_tag["src"] if img_tag else ""

        desc_tag = card.select_one("p.event-info-box-description")
        description = desc_tag.get_text(separator=" ", strip=True) if desc_tag else ""
        if len(description) > 100:
            description = description[:97] + "..."

        venue_tag = card.select_one("div.event-info-box-venue span")
        venue = venue_tag.get_text(strip=True) if venue_tag else "TBD"

        date_tag = card.select_one("div.event-info-box-date")
        date = date_tag.get_text(strip=True) if date_tag else "TBD"

        events.append((img_url, title, link, date, venue, description))
    except Exception as e:
        print("Skipping an event due to error:", e)


table_header = "| Image | Event | Date | Location | Description |\n|-------|-------|------|----------|-------------|"

rows = []
for img, title, link, date, venue, desc in events:
    markdown_img = f"![]({img})" if img else ""
    markdown_link = f"[{title}]({link})"
    rows.append(f"| {markdown_img} | {markdown_link} | {date} | {venue} | {desc} |")

table_content = table_header + "\n" + "\n".join(rows)

# Inject into README.md
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "<!-- START:events -->\n"
end_marker = "<!-- END:events -->"

start = content.find(start_marker) + len(start_marker)
end = content.find(end_marker)

updated = content[:start] + "\n" + table_content + "\n" + content[end:]

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated)