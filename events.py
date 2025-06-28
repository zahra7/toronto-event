# update_readme.py

import feedparser

RSS_URL = "https://feeds.feedburner.com/torontoevents"
MAX_ITEMS = 5

feed = feedparser.parse(RSS_URL)

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "<!-- START:events -->"
end_marker = "<!-- END:events -->"

events_md = "\n".join(
    [f"{i+1}. [{entry.title}]({entry.link}) — {entry.published[:10]}" for i, entry in enumerate(feed.entries[:MAX_ITEMS])]
)

# Replace content between markers
start = content.find(start_marker) + len(start_marker)
end = content.find(end_marker)
new_content = content[:start] + "\n" + events_md + "\n" + content[end:]

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_content)
