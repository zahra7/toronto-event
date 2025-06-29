from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
from html import unescape

BASE_URL = "https://www.blogto.com"
EVENT_URL = BASE_URL + "/events/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(EVENT_URL, timeout=60000)
    page.wait_for_selector(".event-info-box", timeout=10000)  # Wait until events load

    html = page.content()
    browser.close()

soup = BeautifulSoup(html, "html.parser")

events = []

def clean_md_cell(text):
    if not text:
        return ""
    # Remove newlines and tabs, replace with space
    text = re.sub(r'[\r\n\t]+', ' ', text)
    # Replace pipe chars with similar safe char (e.g. │ or just space)
    text = text.replace('|', '│')
    # Normalize multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Select each event card
for card in soup.select("div.event-info-box")[:25]:
    try:
        title_tag = card.select_one(".event-info-box-title-link")
        title = title_tag.get_text(strip=True)
        link = title_tag['href']
        if not link.startswith("http"):
            link = BASE_URL + link

        img_tag = card.select_one("img.event-info-box-image")
        img_url = img_tag["src"] if img_tag else ""

        desc_tag = card.select_one("p.event-info-box-description")
        desc_tag = card.select_one("p.event-info-box-description")
        if desc_tag:
            # Join all text parts, unescape HTML entities
            raw_desc = " ".join(desc_tag.stripped_strings)
            raw_desc = unescape(raw_desc)

            # Remove excessive whitespace and control characters
            description = re.sub(r"[\r\n]+", " ", raw_desc)              # remove line breaks
            description = re.sub(r"\s+", " ", description).strip()       # normalize spacing

            # Optional: truncate if too long
            if len(description) > 100:
                description = description[:97] + "..."
        else:
            description = ""

        venue_tag = card.select_one("div.event-info-box-venue span")
        venue = venue_tag.get_text(strip=True) if venue_tag else "TBD"

        date_tag = card.select_one("div.event-info-box-date")
        date = date_tag.get_text(strip=True) if date_tag else "TBD"

        events.append((img_url, title, link, date, venue, description))
    except Exception as e:
        print("Skipping an event due to error:", e)


table_header = "|                | Event | Date | Location | Description |\n|----------------|-------|------|----------|-------------|"

rows = []
for img, title, link, date, venue, desc in events:
    markdown_img = f'<img src="{img}" width="120"/>' if img else ""
    markdown_link = f"[{clean_md_cell(title)}]({link})"
    clean_date = clean_md_cell(date)
    clean_venue = clean_md_cell(venue)
    clean_desc = clean_md_cell(desc)
    rows.append(f"| {markdown_img} | {markdown_link} | {clean_date} | {clean_venue} | {clean_desc} |")

table_content = table_header + "\n" + "\n".join(rows)

# Inject into index.md
with open("docs/index.md", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "<!-- START:events -->\n"
end_marker = "\n<!-- END:events -->"

start = content.find(start_marker) + len(start_marker)
end = content.find(end_marker)

updated = content[:start] + "\n" + table_content + "\n" + content[end:]

with open("docs/index.md", "w", encoding="utf-8") as f:
    f.write(updated)