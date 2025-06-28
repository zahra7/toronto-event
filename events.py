import feedparser
import re

RSS_URL = "https://feeds.feedburner.com/torontoevents"
MAX_ITEMS = 20

feed = feedparser.parse(RSS_URL)

table_header = "| Event | Date | Location |\n|-------|------|----------|"
table_rows = []

for entry in feed.entries[:MAX_ITEMS]:
    title = entry.title
    link = entry.link
    date = entry.published[:16]  # E.g., "Thu, 24 Nov 2016"
    
    # Try to extract a location from the description using regex
    desc = entry.description.replace('\n', ' ')
    match = re.search(r'(?:Theatre,|at|in)\s+([A-Z][^<]+)', desc)
    location = match.group(1).strip() if match else "TBD"
    
    row = f"| [{title}]({link}) | {date} | {location} |"
    table_rows.append(row)

new_table = table_header + "\n" + "\n".join(table_rows)

# Read README.md
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the block between markers
start_marker = "<!-- START:events -->"
end_marker = "<!-- END:events -->"

start = content.find(start_marker) + len(start_marker)
end = content.find(end_marker)

updated = content[:start] + "\n" + new_table + "\n" + content[end:]

# Write updated README
with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated)
