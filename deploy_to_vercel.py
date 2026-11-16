import os
import hashlib
import json
import urllib.request
import urllib.error
import sys
import io

# Enforce UTF-8 stdout encoding for Windows compatibility
# Removed custom TextIOWrapper wrapping to prevent console stream hangs in headless environments

# Config
def _load_vercel_token():
    for cfg_file in ("config.local.json", "config.json"):
        if os.path.exists(cfg_file):
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    tok = json.load(f).get("vercel_token", "")
                    if tok and not tok.startswith("YOUR_"):
                        return tok
            except Exception:
                pass
    return os.environ.get("VERCEL_TOKEN", "YOUR_VERCEL_TOKEN")

TOKEN = _load_vercel_token()
PROJECT_NAME = "vinaearn-ai"
FILES_TO_DEPLOY = [
    "index.html",
    "dashboard.html",
    "styles.css",
    "global_style.css",
    "checkout_modal.js",
    "app.js",
    "api-portal.js",
    "vercel.json",
    "companies_sample.db",
    "api/search.py",
    "api/company.py",
    "api/ping.py",
    "terms.html",
    "privacy.html",
    "refund.html",
    "ads.txt",
]

headers_auth = {
    "Authorization": f"Bearer {TOKEN}"
}

def get_sha1_and_size(file_path):
    with open(file_path, "rb") as f:
        content = f.read()
        sha1 = hashlib.sha1(content).hexdigest()
        size = len(content)
        return sha1, size, content

def upload_file(sha1, content):
    url = "https://api.vercel.com/v2/now/files"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "x-vercel-digest": sha1,
        "Content-Type": "application/octet-stream"
    }
    
    req = urllib.request.Request(url, data=content, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            print(f"File with SHA1 {sha1} uploaded successfully (Status: {res.status}).")
    except urllib.error.HTTPError as e:
        # 200 OK has empty body, but some HTTP errors might occur if unauthorized or bad request
        print(f"Upload error for {sha1}: {e.code} - {e.read().decode('utf-8')}")
        raise

def create_deployment(files_meta):
    url = "https://api.vercel.com/v13/deployments"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": PROJECT_NAME,
        "files": files_meta,
        "target": "production",
        "projectSettings": {
            "framework": None
        }
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            result = json.loads(res.read().decode("utf-8"))
            print("\nDeployment Created successfully!")
            print(f"Project URL: https://{result['url']}")
            print(f"Inspector URL: {result['inspectorUrl']}")
            return result["url"]
    except urllib.error.HTTPError as e:
        print(f"Deployment error: {e.code} - {e.read().decode('utf-8')}")
        raise

def acquire_lock():
    lock_path = "deploy.lock"
    for _ in range(30): # Wait up to 150 seconds
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            print("Acquired deployment lock.")
            return True
        except FileExistsError:
            print("Deployment lock is held by another process. Waiting 5 seconds...")
            import time
            time.sleep(5)
    print("Warning: Could not acquire deployment lock after timeout. Proceeding anyway.")
    return False

def release_lock():
    lock_path = "deploy.lock"
    try:
        if os.path.exists(lock_path):
            os.remove(lock_path)
            print("Released deployment lock.")
    except Exception as e:
        print(f"Error releasing lock: {e}")

def main():
    print("Starting Vercel direct deployment...")
    acquire_lock()
    
    # Step 0: Temporarily swap index.html with vinaearn_index.html
    has_original = os.path.exists("index.html")
    index_bak = "index.html.bak"
    index_temp = "vinaearn_index.html"
    
    if has_original:
        if os.path.exists(index_bak):
            os.remove(index_bak)
        os.rename("index.html", index_bak)
        
    import shutil
    if os.path.exists(index_temp):
        shutil.copy(index_temp, "index.html")
        print("Temporarily copied vinaearn_index.html to index.html for deployment.")
        
    try:
        # Dynamically inject the active tunnel URL into app.js from config.json
        try:
            config_path = "config.json"
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                api_url = config.get("api_url", "")
                import re
                match = re.match(r'(https?://[a-zA-Z0-9\.\-_]+)', api_url)
                if match:
                    tunnel_url = match.group(1)
                    print(f"Extracted active tunnel URL: {tunnel_url}")
                    
                    app_path = "app.js"
                    if os.path.exists(app_path):
                        with open(app_path, "r", encoding="utf-8") as f:
                            app_content = f.read()
                        
                        # Replace the ACTIVE_TUNNEL_URL constant (new pattern)
                        updated_content = re.sub(
                            r"const ACTIVE_TUNNEL_URL\s*=\s*[\"']https?://[^\"']*[\"']\s*;",
                            f'const ACTIVE_TUNNEL_URL = "{tunnel_url}";',
                            app_content
                        )
                        # Also support old localApiUrl pattern (legacy fallback)
                        updated_content = re.sub(
                            r"localApiUrl\s*=\s*[\"']https?://[^\"']*(?:serveousercontent\.com|lhr\.life)[\"']\s*;",
                            f'localApiUrl = "{tunnel_url}";',
                            updated_content
                        )

                        
                        with open(app_path, "w", encoding="utf-8") as f:
                            f.write(updated_content)
                        print(f"Updated app.js with the active tunnel URL: {tunnel_url}")
                    
                    # Dynamically inject the active bank settings into api-portal.js
                    api_portal_path = "api-portal.js"
                    if os.path.exists(api_portal_path):
                        with open(api_portal_path, "r", encoding="utf-8") as f:
                            api_portal_content = f.read()
                        
                        bank_name = config.get("bank_name", "Techcombank")
                        bank_id = config.get("bank_id", "TCB")
                        if bank_id == "TCB" and "vietcom" in bank_name.lower():
                            bank_id = "VCB"
                        
                        bank_acc = config.get("bank_account", "")
                        bank_holder = config.get("bank_account_holder", "")
                        
                        updated_portal = re.sub(
                            r'bankName:\s*["\'][^"\']*["\']',
                            f'bankName: "{bank_name}"',
                            api_portal_content
                        )
                        updated_portal = re.sub(
                            r'bankId:\s*["\'][^"\']*["\']',
                            f'bankId: "{bank_id}"',
                            updated_portal
                        )
                        updated_portal = re.sub(
                            r'accountNumber:\s*["\'][^"\']*["\']',
                            f'accountNumber: "{bank_acc}"',
                            updated_portal
                        )
                        updated_portal = re.sub(
                            r'accountName:\s*["\'][^"\']*["\']',
                            f'accountName: "{bank_holder}"',
                            updated_portal
                        )
                        
                        with open(api_portal_path, "w", encoding="utf-8") as f:
                            f.write(updated_portal)
                        print(f"Updated api-portal.js with dynamic bank settings: {bank_name}, {bank_acc}")
        except Exception as e:
            print(f"Warning: Failed to inject configs: {e}")

        files_meta = []
        
        for file_path in FILES_TO_DEPLOY:
            if not os.path.exists(file_path):
                print(f"Error: File {file_path} not found.")
                return
                
            sha1, size, content = get_sha1_and_size(file_path)
            print(f"Processing {file_path} (Size: {size} bytes, SHA1: {sha1})")
            
            # Step 1: Upload File
            upload_file(sha1, content)
            
            # Add to meta
            files_meta.append({
                "file": file_path,
                "sha": sha1,
                "size": size
            })
            
        # Step 2: Create Deployment
        create_deployment(files_meta)
    finally:
        # Restore original index.html
        if os.path.exists("index.html"):
            os.remove("index.html")
        if has_original and os.path.exists(index_bak):
            os.rename(index_bak, "index.html")
            print("Restored original index.html.")
        release_lock()

if __name__ == "__main__":
    main()

