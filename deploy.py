import hashlib, requests, json, base64

TOKEN = "cfut_UI7BFd7iudQGwaY71cM5kBTPRI2LXJD58e5ZVkeD60d06d94"
ACCOUNT_ID = "b951b64381068ace9ae0cf1835f7207e"
PROJECT = "latencygrid"
CF_BASE = "https://api.cloudflare.com/client/v4"
auth = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

files_to_upload = {
    "/index.html": ("/Users/henrychen/.openclaw/workspace/latencygrid-site/index.html", "text/html; charset=utf-8"),
    "/styles.css": ("/Users/henrychen/.openclaw/workspace/latencygrid-site/styles.css", "text/css; charset=utf-8"),
    "/sitemap.xml": ("/Users/henrychen/.openclaw/workspace/latencygrid-site/sitemap.xml", "application/xml"),
    "/robots.txt": ("/Users/henrychen/.openclaw/workspace/latencygrid-site/robots.txt", "text/plain"),
}

file_data = {}
for path, (fpath, ct) in files_to_upload.items():
    with open(fpath, "rb") as f:
        b = f.read()
    h = hashlib.sha256(b).hexdigest()
    file_data[path] = {"hash": h, "bytes": b, "content_type": ct}

jwt = requests.get(f"{CF_BASE}/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT}/upload-token",
    headers=auth).json()["result"]["jwt"]
jwt_h = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}

upload_payload = [
    {"key": v["hash"], "value": base64.b64encode(v["bytes"]).decode(),
     "metadata": {"contentType": v["content_type"]}, "base64": True}
    for v in file_data.values()
]
up = requests.post("https://api.cloudflare.com/client/v4/pages/assets/upload",
    headers=jwt_h, json=upload_payload)
print("Upload:", up.json().get("result", {}).get("successful_key_count"), "files")

manifest = {path: v["hash"] for path, v in file_data.items()}
files = [("manifest", (None, json.dumps(manifest), "application/json"))]
deploy = requests.post(f"{CF_BASE}/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT}/deployments",
    headers={"Authorization": f"Bearer {TOKEN}"}, files=files)
data = deploy.json()
print("Deploy:", data.get("success"), "URL:", data.get("result", {}).get("url"))
