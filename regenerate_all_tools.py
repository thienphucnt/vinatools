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

from agent_code_generator import generate_tool
from agent_seo_writer import generate_seo_article


def main():
    if not os.path.exists(DEPLOYED_LOG):
        print("Error: deployed_tools.json not found!")
        sys.exit(1)

    with open(DEPLOYED_LOG, "r", encoding="utf-8") as f:
        tools = json.load(f)

    print(f"Loaded {len(tools)} flagship tool entries from deployed_tools.json.")

    success_count = 0
    errors = []
    for idx, t in enumerate(tools):
        kw = t["keyword"]
        target_slug = t.get("slug")
        print(f"[{idx + 1}/{len(tools)}] Regenerating '{kw}' -> /{target_slug}...")
        try:
            slug = generate_tool(kw, slug=target_slug)
            generate_seo_article(slug, kw)
            print(f"   -> Success! Generated in: /{slug}")
            success_count += 1
        except Exception as e:
            print(f"   -> Error: {e}")
            errors.append((kw, str(e)))

    print(f"\nRegeneration complete. Successfully updated {success_count} / {len(tools)} pages.")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
