import os
import sys
import re
import requests
from requests.auth import HTTPBasicAuth

# Try to load local credentials if the .env file exists
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val.replace('"', '').replace("'", "")

def markdown_to_html(text):
    # Ultra-lightweight converter for basic headers, lists, and tables
    html = text
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.M)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.M)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.M)
    html = re.sub(r'^\* (.*?)$', r'<li>\1</li>', html, flags=re.M)
    # Strip newlines — content is already block-level HTML; newlines produce spurious <br/> gaps
    html = re.sub(r'\n+', '', html)
    return f"<div>{html}</div>"

def publish_markdown_to_confluence(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {file_path}")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    front_matter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not front_matter_match:
        print("❌ Error: Missing routing slip.")
        return False
    
    metadata_text = front_matter_match.group(1)
    body_markdown = content[front_matter_match.end():]

    space_id = re.search(r'confluence_space:\s*["\'](.*?)["\']', metadata_text).group(1)
    parent_name = re.search(r'confluence_parent_page:\s*["\'](.*?)["\']', metadata_text).group(1)
    page_title = re.search(r'confluence_title:\s*["\'](.*?)["\']', metadata_text).group(1)

    url = os.getenv("CONFLUENCE_URL")
    email = os.getenv("CONFLUENCE_EMAIL")
    token = os.getenv("CONFLUENCE_API_TOKEN")

    if not url or "YOUR-COMPANY" in url:
        print("🔒 [Simulation Mode Active] Setup your actual .env file credentials to push live.")
        return True

    print(f"🚀 Connecting live to {url}...")
    auth = HTTPBasicAuth(email, token)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    # 1. Fetch the Parent Page ID dynamically using its title
    search_url = f"{url}/wiki/rest/api/content?title={parent_name}&spaceKey={space_id}"
    response = requests.get(search_url, auth=auth, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to query Confluence space. Status: {response.status_code}")
        return False
    
    results = response.json().get("results", [])
    if not results:
        print(f"❌ Could not find parent page titled '{parent_name}' in space {space_id}")
        return False
    parent_id = results[0]["id"]

    # 2. Build the live XHTML payload
    html_body = markdown_to_html(body_markdown)

    # 3. Check if a page with this title already exists (create vs update)
    import urllib.parse
    check_url = f"{url}/wiki/rest/api/content?title={urllib.parse.quote(page_title)}&spaceKey={space_id}&expand=version"
    check_response = requests.get(check_url, auth=auth, headers=headers)
    existing = check_response.json().get("results", []) if check_response.status_code == 200 else []

    if existing:
        page_id = existing[0]["id"]
        version = existing[0]["version"]["number"] + 1
        payload = {
            "type": "page",
            "title": page_title,
            "version": {"number": version},
            "space": {"key": space_id},
            "ancestors": [{"id": parent_id}],
            "body": {"storage": {"value": html_body, "representation": "storage"}},
        }
        response = requests.put(f"{url}/wiki/rest/api/content/{page_id}", json=payload, auth=auth, headers=headers)
        action = "updated"
    else:
        payload = {
            "type": "page",
            "title": page_title,
            "space": {"key": space_id},
            "ancestors": [{"id": parent_id}],
            "body": {"storage": {"value": html_body, "representation": "storage"}},
        }
        response = requests.post(f"{url}/wiki/rest/api/content", json=payload, auth=auth, headers=headers)
        page_id = response.json().get("id") if response.status_code in [200, 201] else None
        action = "created"

    if response.status_code in [200, 201]:
        print(f"🎉 Page {action} under '{parent_name}'")
        print(f"🔗 View: {url}/wiki/spaces/{space_id}/pages/{page_id}")
        return True
    else:
        print(f"❌ Failed to {action} page. Server response: {response.text}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    success = publish_markdown_to_confluence(sys.argv[1])
    sys.exit(0 if success else 1)
