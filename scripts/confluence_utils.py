#!/usr/bin/env python3
"""
Shared Confluence read/write utilities.
Used by: contact_pipeline.py, weekly_review.py, new-contact
"""

import os
import re
import sys
import urllib.parse
import requests
from requests.auth import HTTPBasicAuth


def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key] = val.strip("\"'")


def get_credentials():
    load_env()
    url   = os.getenv("CONFLUENCE_URL", "")
    email = os.getenv("CONFLUENCE_EMAIL", "")
    token = os.getenv("CONFLUENCE_API_TOKEN", "")
    if not url or not email or not token:
        print("❌ Missing Confluence credentials in .env")
        sys.exit(1)
    return url, email, token, HTTPBasicAuth(email, token)


def find_page_by_title(url, auth, space, title):
    """Returns the first page dict (id, title, body.storage) matching title in space, or None."""
    encoded = urllib.parse.quote(title)
    resp = requests.get(
        f"{url}/wiki/rest/api/content?title={encoded}&spaceKey={space}&expand=body.storage,version,ancestors",
        auth=auth,
        headers={"Accept": "application/json"},
        timeout=30,
    )
    if resp.status_code != 200:
        return None
    results = resp.json().get("results", [])
    return results[0] if results else None


def search_pages_by_title(url, auth, space, title):
    """Returns all pages with exact title match in space."""
    encoded = urllib.parse.quote(title)
    resp = requests.get(
        f"{url}/wiki/rest/api/content?title={encoded}&spaceKey={space}&expand=body.storage,version,ancestors",
        auth=auth,
        headers={"Accept": "application/json"},
        timeout=30,
    )
    if resp.status_code != 200:
        return []
    return resp.json().get("results", [])


def search_pages_by_title_contains(url, auth, space, keyword):
    """Returns all pages whose title contains keyword (CQL ~ operator)."""
    cql = f'title ~ "{keyword}" AND space = "{space}" AND type = page'
    encoded = urllib.parse.quote(cql)
    resp = requests.get(
        f"{url}/wiki/rest/api/content/search?cql={encoded}&expand=body.storage,version,ancestors&limit=50",
        auth=auth,
        headers={"Accept": "application/json"},
        timeout=30,
    )
    if resp.status_code != 200:
        return []
    return resp.json().get("results", [])


def html_to_text(html):
    """Strip Confluence storage format XML/HTML to readable plain text."""
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_space_homepage(url, auth, space):
    """Returns the homepage page dict (id, title) for a space, or None."""
    resp = requests.get(
        f"{url}/wiki/rest/api/space/{space}?expand=homepage",
        auth=auth,
        headers={"Accept": "application/json"},
        timeout=30,
    )
    if resp.status_code == 200:
        return resp.json().get("homepage")
    return None


def create_or_update_page(url, auth, space, parent_id, title, body_html):
    """Create page if it doesn't exist; update (increment version) if it does. Returns page URL or None."""
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    encoded = urllib.parse.quote(title)
    resp = requests.get(
        f"{url}/wiki/rest/api/content?title={encoded}&spaceKey={space}&expand=version",
        auth=auth, headers=headers, timeout=30,
    )
    results = resp.json().get("results", []) if resp.status_code == 200 else []

    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space},
        "ancestors": [{"id": parent_id}],
        "body": {"storage": {"value": body_html, "representation": "storage"}},
    }

    if results:
        page_id = results[0]["id"]
        version = results[0]["version"]["number"] + 1
        payload["version"] = {"number": version}
        r = requests.put(
            f"{url}/wiki/rest/api/content/{page_id}",
            json=payload, auth=auth, headers=headers, timeout=30,
        )
        if r.status_code in (200, 201):
            return f"{url}/wiki/spaces/{space}/pages/{page_id}"
        print(f"❌ Update failed: {r.text}")
        return None
    else:
        r = requests.post(
            f"{url}/wiki/rest/api/content",
            json=payload, auth=auth, headers=headers, timeout=30,
        )
        if r.status_code in (200, 201):
            page_id = r.json().get("id")
            return f"{url}/wiki/spaces/{space}/pages/{page_id}"
        print(f"❌ Create failed: {r.text}")
        return None
