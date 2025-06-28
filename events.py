from bs4 import BeautifulSoup
import feedparser

RSS_URL = "https://feeds.feedburner.com/torontoevents"
MAX_ITEMS = 30

feed = feedparser.parse(RSS_URL)

table_header = "\n| Event | Date | Location | Description |\n|-------|------|----------|-------------|"
table_rows = []
full_descriptions = []

for entry in feed.entries[:MAX_ITEMS]:
    title = entry.title
    link = entry.link
    date = entry.published[:16]

    # Parse HTML description
    soup = BeautifulSoup(entry.description, 'html.parser')
    paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]

    # Description
    description = paragraphs[0] if paragraphs else "No description available"
    truncated = (description[:47] + "...") if len(description) > 50 else description

    # Location (from any <p> that looks like an address)
    location = "TBD"
    for para in paragraphs:
        if (
            any(word in para.lower() for word in ['street', 'avenue', 'road', 'place', 'toronto']) and
            len(para.split()) < 15
        ):
            location = para
            break

    row = f"| [{title}]({link}) | {date} | {location} | {truncated} |"
    table_rows.append(row)

# Inject into README.md
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "<!-- START:events -->"
end_marker = "\n<!-- END:events -->\n"

start = content.find(start_marker) + len(start_marker)
end = content.find(end_marker)

updated = content[:start] + "\n" + table_header + "\n" + "\n".join(table_rows) + "\n" + content[end:]

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated)
