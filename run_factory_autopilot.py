import time
import json
import os
import re
import sqlite3
from datetime import datetime

# Import all sub-agents
from agent_niche_finder import run_niche_discovery
from agent_code_generator import generate_tool
from agent_seo_writer import generate_seo_article
from agent_deployer import run_deployment

# Config & Paths
WORKSPACE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(WORKSPACE, "config.json")
NICHE_FILE = os.path.join(WORKSPACE, "niche_opportunities.json")
DEPLOYED_LOG = os.path.join(WORKSPACE, "deployed_tools.json")
ANALYTICS_LOG = os.path.join(WORKSPACE, "analytics.json")
DB_PATH = os.path.join(WORKSPACE, "payments.db")

# How many new tools the agent will build per cycle
TOOLS_PER_CYCLE = 3

# Interval between full cycles (5 minutes)
CYCLE_INTERVAL_SECONDS = 5 * 60


def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = {"INFO": "✅", "WARN": "⚠️", "ERROR": "❌", "MONEY": "💰"}.get(level, "ℹ️")
    print(f"[{timestamp}] {prefix}  {msg}")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_deployed_tools():
    if os.path.exists(DEPLOYED_LOG):
        with open(DEPLOYED_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_deployed_tools(tools):
    seen_slugs = set()
    deduplicated = []
    for tool in reversed(tools):
        slug = tool.get("slug", "").strip()
        if slug and slug not in seen_slugs:
            seen_slugs.add(slug)
            deduplicated.append(tool)
    deduplicated.reverse()
    with open(DEPLOYED_LOG, "w", encoding="utf-8") as f:
        json.dump(deduplicated, f, ensure_ascii=False, indent=2)

def fetch_revenue_stats():
    """
    Reads the SQLite payments DB and calculates cumulative revenue.
    """
    if not os.path.exists(DB_PATH):
        return {"total_transactions": 0, "total_revenue_vnd": 0}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(amount) FROM payments WHERE status = 'completed'")
    row = cursor.fetchone()
    conn.close()
    
    count = row[0] or 0
    total = row[1] or 0
    return {"total_transactions": count, "total_revenue_vnd": total}

def update_analytics(deployed_tools, revenue):
    """
    Saves analytics data to a log file for review.
    """
    analytics = {
        "last_updated": datetime.now().isoformat(),
        "total_tools_deployed": len(deployed_tools),
        "total_transactions": revenue["total_transactions"],
        "total_revenue_vnd": revenue["total_revenue_vnd"],
        "formatted_revenue": f"{revenue['total_revenue_vnd']:,.0f} VND",
        "tools": deployed_tools
    }
    with open(ANALYTICS_LOG, "w", encoding="utf-8") as f:
        json.dump(analytics, f, ensure_ascii=False, indent=2)
    return analytics

def print_dashboard(analytics):
    """
    Prints a clean revenue dashboard to the terminal.
    """
    rev = analytics["total_revenue_vnd"]
    target = 100_000_000  # 100M VND monthly target
    progress_pct = min(100, (rev / target) * 100) if target > 0 else 0
    bar_len = 30
    filled = int(bar_len * progress_pct / 100)
    bar = "█" * filled + "░" * (bar_len - filled)

    print("\n" + "=" * 60)
    print("  🏭  VINA AUTO-FACTORY  |  REVENUE DASHBOARD")
    print("=" * 60)
    print(f"  🛠️   Tools Live on Google :  {analytics['total_tools_deployed']}")
    print(f"  💳  Total Transactions   :  {analytics['total_transactions']}")
    print(f"  💰  Total Revenue        :  {analytics['formatted_revenue']}")
    print(f"\n  📈  Monthly Target (100M VND)")
    print(f"  [{bar}] {progress_pct:.1f}%")
    print("=" * 60 + "\n")

def run_factory_cycle(deployed_tools):
    """
    Executes one full factory cycle:
    1. Discover new keyword niches
    2. Generate tools for the best new niches
    3. Write SEO content for each tool
    4. Deploy everything to Vercel
    """
    log("Starting new factory cycle...")

    # Step 1: Niche Discovery
    log("Phase 1/4: Running Niche Finder Agent...")
    try:
        niches = run_niche_discovery()
    except Exception as e:
        log(f"Niche finder failed: {e}", "ERROR")
        return deployed_tools

    # Filter out already-deployed keywords
    already_deployed_keywords = {t["keyword"].lower().strip() for t in deployed_tools}
    new_niches = [n for n in niches if n["keyword"].lower().strip() not in already_deployed_keywords]

    if not new_niches:
        log("No new niche opportunities found this cycle. Will retry next cycle.", "WARN")
        return deployed_tools

    # Pick the top N niches for this cycle
    selected_niches = new_niches[:TOOLS_PER_CYCLE]
    log(f"Phase 1 Complete: Selected {len(selected_niches)} new niches to build.")

    newly_built = []

    for niche in selected_niches:
        kw = niche["keyword"]
        log(f"Phase 2/4: Generating code for → '{kw}'")
        try:
            slug = generate_tool(kw)
        except Exception as e:
            log(f"Code generation failed for '{kw}': {e}", "ERROR")
            continue

        log(f"Phase 3/4: Writing SEO content for → '{kw}'")
        try:
            generate_seo_article(slug, kw)
        except Exception as e:
            log(f"SEO writer failed for '{kw}': {e}", "WARN")
            # Non-critical — proceed even if SEO content fails

        newly_built.append({
            "keyword": kw,
            "slug": slug,
            "deployed_at": datetime.now().isoformat(),
            "estimated_volume": niche.get("estimated_monthly_volume", 0),
            "niche_score": niche.get("score", 0)
        })

    if not newly_built:
        log("No new tools were built this cycle.", "WARN")
        return deployed_tools

    # Step 4: Deploy entire site to Vercel
    log(f"Phase 4/4: Deploying {len(newly_built)} new tool(s) to Vercel...")
    try:
        deployment_url = run_deployment()
        if deployment_url:
            log(f"Deployment successful! Live at: https://{deployment_url}", "MONEY")
            for tool in newly_built:
                tool["url"] = f"https://{deployment_url}/{tool['slug']}"
        else:
            log("Deployment skipped (check Vercel token in config.json).", "WARN")
    except Exception as e:
        log(f"Deployment failed: {e}", "ERROR")

    # Update deployed tools list
    deployed_tools.extend(newly_built)
    save_deployed_tools(deployed_tools)
    deployed_tools = load_deployed_tools()
    log(f"Cycle complete. Total tools live: {len(deployed_tools)}")
    return deployed_tools


def main():
    log("=" * 50)
    log("VINA AUTO-FACTORY DAEMON STARTING UP")
    log(f"Building {TOOLS_PER_CYCLE} tools per cycle, every {CYCLE_INTERVAL_SECONDS // 3600} hours")
    log("=" * 50)

    config = load_config()

    # Basic config check
    missing = []
    if not config.get("bank_account") or config.get("bank_account", "").startswith("YOUR_"):
        missing.append("bank_account (your Techcombank account number)")
    if not config.get("bank_account_holder") or config.get("bank_account_holder", "").startswith("YOUR_"):
        missing.append("bank_account_holder (your full name)")
    if not config.get("vercel_token") or config.get("vercel_token", "").startswith("YOUR_"):
        missing.append("vercel_token")

    if missing:
        log("⚠️  Config incomplete. Please fill in config.json before running:", "WARN")
        for m in missing:
            log(f"   → {m}", "WARN")
        log("Entering SIMULATION MODE — no real deployments will be made.", "WARN")

    deployed_tools = load_deployed_tools()
    log(f"Loaded {len(deployed_tools)} previously deployed tools from history.")

    # Main autopilot loop
    cycle_count = 0
    while True:
        cycle_count += 1
        log(f"--- CYCLE #{cycle_count} BEGIN ---")

        deployed_tools = run_factory_cycle(deployed_tools)

        # Analytics & Dashboard
        revenue = fetch_revenue_stats()
        analytics = update_analytics(deployed_tools, revenue)
        print_dashboard(analytics)

        log(f"Next cycle in {CYCLE_INTERVAL_SECONDS // 3600} hours. Daemon sleeping...")
        time.sleep(CYCLE_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
