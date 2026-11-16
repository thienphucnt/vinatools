# VinaTools & VinaEarn AI

Automated Vietnamese legal/financial web tools portal, SEO tool factory, VietQR/Casso payment gateway, and VietRegistry API console (`vinaearn-ai` / `vinatools.vercel.app`).

## Core Architecture

- **Autopilot Tool Factory**:
  - `run_factory_autopilot.py`: Orchestrates cyclic discovery, generation, SEO writing, and deployment.
  - `agent_niche_finder.py`: Discovers Vietnamese tool/template opportunities into `niche_opportunities.json`.
  - `agent_code_generator.py`: Generates client-side HTML/JS tools and legal document builders into slug directories (`deployed_tools.json`).
  - `agent_seo_writer.py`: Generates structured Vietnamese SEO guides and metadata per tool category.
  - `agent_deployer.py` / `deploy_to_vercel.py`: Syncs assets (`templates/global_style.css`, `templates/checkout_modal.js`), regenerates the portal index (`generate_niche_portal.py`) and sitemap (`generate_sitemap.py`), and deploys via Vercel REST API.
- **Featured Client-Side Tool — 2026 Household Business Tax & Compliance Simulator**:
  - `cong-cu-tinh-thue-ho-kinh-doanh/index.html`: 100% client-side React + Tailwind CSS simulator for Vietnamese Household Businesses (*Hộ Kinh Doanh*) under 2026 standards (Decree 141/2026/NĐ-CP), calculating VAT/PIT across 5 industry categories, checking the 1B VND e-invoicing & accounting threshold, and providing an A4 print/PDF report view.
- **Payment Gateway, Admin Console & Registry API**:
  - `payment_webhook.py`: Local HTTP/SQLite server (`payments.db`) handling Casso payment verification, VIP token signing, AdSense OAuth/live reporting, and admin endpoints.
  - `tunnel_manager.py`: Manages public tunnel exposure for `payment_webhook.py`.
  - `dashboard.html`, `app.js`, `api-portal.js`, `checkout_modal.js`: Registry API admin console and VietQR checkout modal integration.
  - `api/search.py`, `api/company.py`, `api/ping.py`, `vercel.json`: Serverless Python API routes backed by `companies_sample.db`.
  - `run_tests.py`: Automated test suite covering webhook, auth, and API endpoints.

## Configuration & Secrets

Live credentials are intentionally redacted in `config.json`. Copy `config.json` to `config.local.json` (git-ignored) or set `VERCEL_TOKEN` in your environment before running deployment scripts locally.

## Gemini Deep Research / Repomix Usage

This repository includes `repomix.config.json` and `.repomixignore` so both `repomix.com` (via `https://github.com/thienphucnt/vinatools`) and local `npx repomix` exclude repetitive auto-generated static HTML tool folders, logs, and binary databases while keeping the full platform engine, API routes, frontend console, and 4 representative tool directories (`cong-cu-tinh-thue-ho-kinh-doanh`, `cong-cu-tinh-phi-san-tmdt`, `mau-hop-dong-lao-dong-2026`, `mau-don-xin-viec`).
