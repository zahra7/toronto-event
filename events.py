from bs4 import BeautifulSoup
import feedparser
import html

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
    paragraphs = []
    for p in soup.find_all('p'):
        raw = p.get_text().strip()
        if raw:
            clean = html.unescape(raw.replace('\n', ' ').replace('\r', ' ').strip())
            paragraphs.append(clean)

    description = " ".join(paragraphs)

    # Description
    if len(description) > 120:
        description = description[:117].rstrip() + "..."

    # Location (from any <p> that looks like an address)
    location = "TBD"
    for para in paragraphs:
        if (
            any(word in para.lower() for word in ['street', 'avenue', 'road', 'place', 'toronto']) and
            len(para.split()) < 15
        ):
            location = para
            break

    event_id = title.lower().replace(" ", "-").replace(":", "").replace("!", "").replace("’", "").replace("'", "")
    row = f"| [{title}]({link}) | {date} | {location} | {description} [read more](#{event_id}) |"
    table_rows.append(row)

    full_descriptions.append((event_id, title, "\n".join(paragraphs)))

# Inject into README.md
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "<!-- START:events -->"
end_marker = "\n<!-- END:events -->\n"

start = content.find(start_marker) + len(start_marker)
end = content.find(end_marker)

updated = content[:start] + "\n" + table_header + "\n" + "\n".join(table_rows) + "\n" + content[end:]

# Add full description section
full_desc_md = "\n\n## 📄 Full Descriptions\n"
for event_id, title, full_desc in full_descriptions:
    full_desc_md += f"\n### {title}\n<a name=\"{event_id}\"></a>\n{full_desc}\n\n---\n"

updated += "\n" + full_desc_md

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated)
