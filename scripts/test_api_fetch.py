#!/usr/bin/env python3
"""Proof-of-concept: fetch iiko docs article via ClickHelp helper API."""

import json
import urllib.request

SLUG = "avtorizatsiya"
URL = f"https://ru.iiko.help/helper/articles/api-documentations/{SLUG}/"

payload = json.dumps({
    "curUrl": f"https://ru.iiko.help/articles/#!api-documentations/{SLUG}",
    "articleChangedFromTabName": None,
    "articleChangedRefEntityId": None,
}).encode("utf-8")

req = urllib.request.Request(
    URL,
    data=payload,
    headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://ru.iiko.help/articles/",
    },
    method="POST",
)

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8-sig"))

print("=== API Response Structure ===")
print(f"internalId:       {data['internalId']}")
print(f"externalId:       {data['externalId']}")
print(f"projectExternalId:{data['projectExternalId']}")
print(f"title:            {data['title']}")
print(f"viewFrameHtml:    {len(data.get('viewFrameHtml', ''))} chars")
print(f"timeToRead:       {data.get('timeToRead')}")
print(f"Keys:             {list(data.keys())[:10]}...")
print()
print("=== SUCCESS: Article fetched without browser! ===")
