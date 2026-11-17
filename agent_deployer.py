import os
import hashlib
import json
import urllib.request
import urllib.error
import shutil
import sys

# Force UTF-8 output on Windows
# Removed reconfigure block to prevent console stream hangs in headless environments

# Custom logging to file to bypass Windows background stdout buffering
import builtins
original_print = builtins.print
def log_to_file(*args, **kwargs):
  original_print(*args, **kwargs)
  try:
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deploy_debug.log")
    with open(log_file, "a", encoding="utf-8") as f:
      original_print(*args, file=f, **kwargs)
  except:
    pass
print = log_to_file

# Config & Paths
WORKSPACE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(WORKSPACE, "config.json")
TEMPLATES_DIR = os.path.join(WORKSPACE, "templates")

# Excluded folders during scanning
EXCLUDE_DIRS = {".git", ".gemini", "templates", "__pycache__"}

def load_config():
  if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
      return json.load(f)
  return {}

def copy_static_assets():
  """
  Copies global style and script templates to the root directory
  so they can be uploaded at the root path of the deployment.
  Dynamically injects the current active api_url from config.json.
  """
  import re
  config = load_config()
  api_url = config.get("api_url", "/api/check-payment")
  
  src_css = os.path.join(TEMPLATES_DIR, "global_style.css")
  dest_css = os.path.join(WORKSPACE, "global_style.css")
  
  src_js = os.path.join(TEMPLATES_DIR, "checkout_modal.js")
  dest_js = os.path.join(WORKSPACE, "checkout_modal.js")
  
  if os.path.exists(src_css):
    shutil.copy(src_css, dest_css)
  if os.path.exists(src_js):
    with open(src_js, "r", encoding="utf-8") as f:
      content = f.read()
    
    # Dynamically inject the active api_url into the central config object
    updated_content = re.sub(
      r'apiEndpoint:\s*["\'][^"\']*["\']',
      f'apiEndpoint: "{api_url}"',
      content
    )
    
    with open(dest_js, "w", encoding="utf-8") as f:
      f.write(updated_content)
  print(f"Static templates copied to workspace root. Active API Endpoint injected: {api_url}")

def get_sha1_and_size(file_path):
  with open(file_path, "rb") as f:
    content = f.read()
    sha1 = hashlib.sha1(content).hexdigest()
    size = len(content)
    return sha1, size, content

def upload_file(sha1, content, token):
  url = "https://api.vercel.com/v2/now/files"
  headers = {
    "Authorization": f"Bearer {token}",
    "x-vercel-digest": sha1,
    "Content-Type": "application/octet-stream"
  }
  
  req = urllib.request.Request(url, data=content, headers=headers, method="POST")
  try:
    with urllib.request.urlopen(req, timeout=15) as res:
      return res.status
  except urllib.error.HTTPError as e:
    print(f"Vercel file upload error for SHA1 {sha1}: {e.code} - {e.read().decode('utf-8')}")
    raise

def create_vercel_deployment(files_meta, project_name, token):
  url = "https://api.vercel.com/v13/deployments"
  headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
  }
  
  payload = {
    "name": project_name,
    "files": files_meta,
    "target": "production",
    "projectSettings": {
      "framework": None
    }
  }
  
  data = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(url, data=data, headers=headers, method="POST")
  
  with urllib.request.urlopen(req, timeout=15) as res:
    result = json.loads(res.read().decode("utf-8"))
    print(f"\nVercel Deployment Created: https://{result['url']}")
    return result["url"]

def scan_files_to_deploy():
  """
  Scans workspace recursively for all files that need deployment.
  Returns relative file paths.
  """
  files_list = []
  
  # Core root pages
  core_files = [
    "index.html", "api-docs.html", "dashboard.html",
    "global_style.css", "styles.css", "checkout_modal.js", "app.js", "api-portal.js",
    "robots.txt", "sitemap.xml", "terms.html", "privacy.html", "refund.html",
    "ads.txt", "sw.js", "og-image.png", "vercel.json", "manifest.json",
    "offline.html", "about.html", "contact.html", "logo.png"
  ]
  for f in core_files:
    path = os.path.join(WORKSPACE, f)
    if os.path.exists(path):
      files_list.append(f)
      
  # Auto-include any google verification files at the root
  for f in os.listdir(WORKSPACE):
    if f.startswith("google") and f.endswith(".html"):
      files_list.append(f)
      
  # Scan subfolders for tool files (like index.html in slug directories)
  for root, dirs, files in os.walk(WORKSPACE):
    # Prune excluded directories
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    
    # Avoid root directory as we handled core files above
    if root == WORKSPACE:
      continue
      
    for file in files:
      # We deploy HTML files, scripts, assets in subdirectories
      if file.endswith((".html", ".css", ".js", ".png", ".jpg", ".svg", ".json", ".py")):
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, WORKSPACE)
        files_list.append(rel_path.replace("\\", "/"))
        
  return files_list

def acquire_lock():
  lock_path = os.path.join(WORKSPACE, "deploy.lock")
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
  lock_path = os.path.join(WORKSPACE, "deploy.lock")
  try:
    if os.path.exists(lock_path):
      os.remove(lock_path)
      print("Released deployment lock.")
  except Exception as e:
    print(f"Error releasing lock: {e}")

def run_deployment():
  print("run_deployment() function started...")
  acquire_lock()

  config = load_config()
  token = config.get("vercel_token", "")
  project_name = config.get("vercel_project_name", "vinaearn-ai")
  
  if not token or token.startswith("YOUR_"):
    print("Error: Vercel Token is missing in config.json. Deployment cancelled.")
    return None
    
  # Step 1: Copy templates to root
  copy_static_assets()
  
  # Step 2: Generate up-to-date directory index.html and sitemap.xml
  try:
    from generate_niche_portal import generate_index
    generate_index()
  except Exception as e:
    print(f"Error generating niche portal index: {e}")

  try:
    from generate_sitemap import generate_sitemap
    generate_sitemap()
  except Exception as e:
    print(f"Error generating sitemap.xml: {e}")

  deployment_url = None
  try:
    # Scan files directly from workspace
    files_to_deploy = scan_files_to_deploy()
    print(f"Scanned {len(files_to_deploy)} files for deployment.")
    
    files_meta = []
    sha_to_content = {}
    
    for rel_path in files_to_deploy:
      abs_path = os.path.join(WORKSPACE, rel_path)
      sha1, size, content = get_sha1_and_size(abs_path)
      files_meta.append({
        "file": rel_path,
        "sha": sha1,
        "size": size
      })
      sha_to_content[sha1] = (rel_path, content)
      
    # Try deploying directly
    print("Attempting to create Vercel deployment...")
    try:
      deployment_url = create_vercel_deployment(files_meta, project_name, token)
    except urllib.error.HTTPError as e:
      if e.code == 400:
        err_body = e.read().decode("utf-8")
        try:
          err_data = json.loads(err_body)
          if err_data.get("error", {}).get("code") == "missing_files":
            missing_shas = err_data["error"].get("missing", [])
            print(f"Vercel reports {len(missing_shas)} files are missing. Uploading only the missing files...")
            
            for sha in missing_shas:
              if sha in sha_to_content:
                rel_path, content = sha_to_content[sha]
                print(f"Uploading missing file: {rel_path} (SHA1: {sha})...")
                upload_file(sha, content, token)
              else:
                print(f"Error: Missing file with SHA1 {sha} not found in scan!")
                
            # Retry deployment
            print("Retrying Vercel deployment after uploading missing files...")
            deployment_url = create_vercel_deployment(files_meta, project_name, token)
          else:
            print(f"Vercel deployment failed with 400 error: {err_body}")
            raise
        except Exception as ex:
          print(f"Failed to process deployment error: {ex}. Original error: {err_body}")
          raise
      else:
        print(f"Vercel deployment failed with HTTP error {e.code} - {e.read().decode('utf-8')}")
        raise
  finally:
    release_lock()
      
  return deployment_url

if __name__ == "__main__":
  print("agent_deployer.py main block entered...")
  run_deployment()
