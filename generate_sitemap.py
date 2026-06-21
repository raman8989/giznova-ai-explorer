import pandas as pd

df = pd.read_csv("devices_master.csv")

urls = [
    "https://ai.giznova.in/",
    "https://ai.giznova.in/compare",
    "https://ai.giznova.in/top-ai-devices",
    "https://ai.giznova.in/top-ai-phones",
    "https://ai.giznova.in/top-ai-tablets",
    "https://ai.giznova.in/top-ai-pcs",
    "https://ai.giznova.in/methodology",

    "https://ai.giznova.in/platform/apple-intelligence",
    "https://ai.giznova.in/platform/galaxy-ai",
    "https://ai.giznova.in/platform/gemini-nano",
    "https://ai.giznova.in/platform/copilot-plus"
]

for device in df["device"]:
    slug = device.lower().replace(" ", "-")
    urls.append(f"https://ai.giznova.in/device/{slug}")

xml = ['<?xml version="1.0" encoding="UTF-8"?>']
xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

for url in urls:
    xml.append("<url>")
    xml.append(f"<loc>{url}</loc>")
    xml.append("</url>")

xml.append("</urlset>")

with open("static/sitemap.xml", "w", encoding="utf-8") as f:
    f.write("\n".join(xml))

print(f"Generated sitemap with {len(urls)} URLs")