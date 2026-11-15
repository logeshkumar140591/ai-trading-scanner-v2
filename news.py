import urllib.parse, urllib.request, xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

def fetch_news(symbols):
    rows=[]
    for sym in symbols:
        company=sym.replace(".NS","").replace(".BO","")
        url="https://news.google.com/rss/search?q="+urllib.parse.quote(company+" NSE stock")+"&hl=en-IN&gl=IN&ceid=IN:en"
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req,timeout=8) as r: root=ET.fromstring(r.read())
            for item in root.findall(".//item")[:3]:
                rows.append({"Symbol":sym,"Headline":item.findtext("title"),"Published":item.findtext("pubDate"),"Source":item.findtext("source"),"Link":item.findtext("link")})
        except Exception:
            continue
    return pd.DataFrame(rows)
