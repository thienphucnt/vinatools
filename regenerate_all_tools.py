# -*- coding: utf-8 -*-
import json
import os
import sys

# Force UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
DEPLOYED_LOG = os.path.join(WORKSPACE, "deployed_tools.json")

# Import the generation engine
from agent_code_generator import generate_tool
from agent_seo_writer import generate_seo_article

def main():
    if not os.path.exists(DEPLOYED_LOG):
        print("Error: deployed_tools.json not found!")
        return
        
    with open(DEPLOYED_LOG, "r", encoding="utf-8") as f:
        tools = json.load(f)
        
    print(f"Loaded {len(tools)} tool entries from history.")
    
    # Group by keyword to avoid duplicate generations
    unique_keywords = sorted(list(set(t["keyword"] for t in tools)))
    print(f"Found {len(unique_keywords)} unique tool keywords to regenerate.")
    
    success_count = 0
    for idx, kw in enumerate(unique_keywords):
        print(f"[{idx+1}/{len(unique_keywords)}] Regenerating tool page for: '{kw}'...")
        try:
            slug = generate_tool(kw)
            generate_seo_article(slug, kw)
            print(f"   -> Success! Generated in: /{slug}")
            success_count += 1
        except Exception as e:
            print(f"   -> Error: {e}")
            
    print(f"\nRegeneration complete. Successfully updated {success_count} / {len(unique_keywords)} pages.")

if __name__ == "__main__":
    main()
