import subprocess
import time
import re
import json
import os
import urllib.request
import sys
import threading

# Force UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(WORKSPACE, "config.json")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def run_deployer():
    print("Running deployer to update Vercel...")
    try:
        import importlib
        import agent_deployer
        importlib.reload(agent_deployer)
        agent_deployer.run_deployment()
    except Exception as e:
        print(f"Error running in-process agent_deployer: {e}")

def health_check(url):
    test_url = f"{url}?memo=VE_HEALTH_CHECK"
    try:
        req = urllib.request.Request(test_url, method="GET")
        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("status") == "pending"
    except Exception as e:
        print(f"Health check failed for {url}: {e}")
    return False

def consume_stream(stream):
    """
    Continually reads and discards output from a stream to prevent pipe blocking.
    """
    try:
        for line in stream:
            pass
    except Exception:
        pass

def start_tunnel():
    # Primary: localhost.run
    # Fallback: serveo.net
    tunnel_services = [
        {
            "cmd": ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=3", "-o", "ConnectTimeout=10", "-o", "ConnectionAttempts=1", "-R", "80:127.0.0.1:8085", "nokey@localhost.run"],
            "pattern": r"([a-zA-Z0-9\.\-_]+\.lhr\.life)"
        },
        {
            "cmd": ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=3", "-o", "ConnectTimeout=10", "-o", "ConnectionAttempts=1", "-R", "80:127.0.0.1:8085", "serveo.net"],
            "pattern": r"Forwarding HTTP traffic from (https://[a-zA-Z0-9\.\-_]+)"
        }
    ]
    
    for svc in tunnel_services:
        print(f"Attempting to start tunnel using: {' '.join(svc['cmd'])}")
        # Start SSH subprocess with close_fds=True to prevent handle leak
        proc = subprocess.Popen(
            svc["cmd"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            bufsize=1,
            close_fds=True
        )
        
        # Parse stdout line-by-line looking for the tunnel URL
        url = None
        start_time = time.time()
        while time.time() - start_time < 20: # Wait up to 20 seconds for URL
            line = proc.stdout.readline()
            if not line:
                break
            print(f"[SSH OUTPUT] {line.strip()}")
            match = re.search(svc["pattern"], line)
            if match:
                url = match.group(1)
                # If localhost.run pattern was matched, format it as https://
                if "lhr.life" in url and not url.startswith("http"):
                    url = f"https://{url}"
                break
        
        if url:
            print(f"Successfully established tunnel! URL: {url}")
            # Start a background daemon thread to consume any future stdout from SSH
            # to prevent pipe buffer lockups
            t = threading.Thread(target=consume_stream, args=(proc.stdout,), daemon=True)
            t.start()
            return proc, url
        else:
            print("Failed to get URL from this service, killing process...")
            proc.terminate()
            proc.wait()
            
    return None, None

def main():
    print("Starting Tunnel Manager...")
    
    while True:
        # Kill any existing ssh processes to clear ports on Windows
        subprocess.run("taskkill /F /IM ssh.exe 2>nul", shell=True)
        
        proc, url = start_tunnel()
        if not proc or not url:
            print("Failed to start any tunnel service. Retrying in 10 seconds...")
            time.sleep(10)
            continue
            
        # Update config.json
        should_redeploy = True
        try:
            config = load_config()
            last_url = config.get("last_deployed_url", "")
            if last_url == url:
                print(f"Tunnel URL has not changed ({url}). Skipping Vercel redeployment to avoid rate limits!")
                should_redeploy = False
            else:
                config["api_url"] = f"{url}/api/check-payment"
                config["last_deployed_url"] = url
                save_config(config)
                print(f"Updated config.json with new api_url: {config['api_url']}")
        except Exception as e:
            print(f"Error updating config.json: {e}")
            proc.terminate()
            proc.wait()
            time.sleep(10)
            continue
            
        # Redeploy to Vercel
        if should_redeploy:
            try:
                run_deployer()
                import importlib
                import deploy_to_vercel
                importlib.reload(deploy_to_vercel)
                deploy_to_vercel.main()
            except Exception as e:
                print(f"Error running deployer: {e}")
            
        # Monitor Loop
        consecutive_failures = 0
        while True:
            # Check if subprocess is still alive
            if proc.poll() is not None:
                print("SSH tunnel process terminated unexpectedly!")
                break
                
            # Perform health check
            if health_check(f"{url}/api/check-payment"):
                consecutive_failures = 0
                print(f"Health check OK: {url}")
            else:
                consecutive_failures += 1
                print(f"Health check failed ({consecutive_failures}/3): {url}")
                
            if consecutive_failures >= 3:
                print("Tunnel health checks failed 3 times. Re-establishing tunnel...")
                break
                
            # Sleep 60 seconds before next health check
            time.sleep(60)
            
        # Clean up
        print("Cleaning up tunnel process...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Tunnel closed. Retrying loop in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    main()
