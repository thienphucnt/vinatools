# VinaTools — Vietnamese FinTech, LegalTech & Business Registry Suite (2026)

A deterministic, static-first Vietnamese LegalTech, FinTech, and Business Registry web platform (`vinatools.vercel.app`) deployed on Vercel with Python serverless endpoints and pure ES6 client-side calculation engines. All 12 flagship tools run 100% locally in the browser (zero server persistence of user inputs, compliant with Personal Data Protection Law No. 91/2025/QH15), with instant free CSV (UTF-8 BOM), Microsoft Word (`.doc`), and Decree 30/2020/NĐ-CP A4 Print/PDF exports.

## Architecture Overview

- **Modular Static Generator Pipeline**:
  - `statutory_engines.py`: Pure Python reference implementations for 2026 Vietnamese statutory tax, payroll, social insurance, and e-commerce calculations, plus the shared ad-free HTML page shell (`render_tool_shell`).
  - `fintech_builders.py`: Deterministic ES6 client-side builders for the 7 FinTech, Data, and Registry tools synchronized with `statutory_engines.py`.
  - `legal_builders.py`: Multi-step wizard builders (`#user-recipient` ASCII IDs, dynamic `.form-step` `validateStep(step)`) rendering live A4 previews compliant with **Decree 30/2020/NĐ-CP Appendix I** (`Times New Roman`, `13pt`, `@page { size: A4 portrait; margin: 20mm 15mm 20mm 30mm; }`).
  - `agent_code_generator.py`: Curated dispatcher mapping the 12 flagship slugs/keywords (`deployed_tools.json`) to their deterministic builders and rejecting unsupported/placebo slugs with `ValueError`.
  - `agent_seo_writer.py`: Category-aware statutory legal basis, usage steps, and JSON-LD `FAQPage` injector.
  - `generate_niche_portal.py` & `generate_sitemap.py`: Builds `index.html` and `sitemap.xml` directly without temporary index swap files; developer API documentation lives at `/api-docs.html`.
- **VietRegistry Serverless API (`vercel.json` -> `api/*.py`)**:
  - `GET /api/company?tax_code=...` (`api/company.py`): Business tax code (MST) detail lookup sourced from public registry records.
  - `GET /api/search?q=...` (`api/search.py`): Business registry search across Vietnamese provinces.
  - `GET /api/ping` (`api/ping.py`): Health-check endpoint.
  - Configured with `cleanUrls: true` in `vercel.json`.

## Curated 12 Flagship Tools

### FinTech, Statutory Tax & Data Utilities (`tien-ich`)
1. `/cong-cu-tinh-thue-ho-kinh-doanh` — **2026 Household Business Tax & Compliance Simulator**: Implements the 4 revenue tiers, 1 billion VND exemption threshold, Method 1 (excess revenue over 1B) vs Method 2 (15%/17%/20% profit), license fee abolition, and e-commerce withholding per **Decree 68/2026/NĐ-CP**, **Decree 141/2026/NĐ-CP**, **Circular 18/2026/TT-BTC**, and **Resolution 198/2025/QH15**.
2. `/cong-cu-tinh-luong-gross-net-tncn-2026` — **2026 Gross ↔ Net & 5-Bracket PIT Calculator**: Bidirectional converter implementing the 15.5M VND personal / 6.2M VND dependent deductions and 5 progressive tax brackets under **Law No. 109/2025/QH15**, **Resolution 110/2025/UBTVQH15**, **Decree 253/2026/NĐ-CP**, **Decree 293/2025/NĐ-CP**, and **Decree 161/2026/NĐ-CP**, alongside a side-by-side 2025 7-bracket tax savings comparison.
3. `/cong-cu-tinh-phi-san-tmdt` — **2026 Shopee & TikTok Shop Seller Fee & Break-Even ROAS Calculator**: Models payment/transaction fees, commission/fixed tiers, Voucher/Content Xtra caps, PiShip, 1.5% Article 11 Decree 68/2026 platform tax withholding, Net Payout, and Break-Even ROAS.
4. `/cong-cu-doc-so-thanh-chu` — **Vietnamese Accounting Number-to-Words Converter**: Deterministic reader supporting up to 999,999,999,999,999 with standard `lẻ/linh`, `mốt`, `tư`, `lăm` rules.
5. `/cong-cu-tach-va-chuan-hoa-dia-chi` — **Vietnamese Address Parser & Normalizer**: Bulk multi-line parser extracting House/Street, Ward/Commune, District, and Province/City with UTF-8 BOM CSV export.
6. `/cong-cu-tinh-lai-gop` — **Compound Interest & Cashflow Schedule Simulator**: Periodic contribution growth schedule with instant CSV export.
7. `/tra-cuu-ma-so-thue-doanh-nghiep` — **VietRegistry MST Enterprise Lookup UI**: Live frontend connected to `/api/company` and `/api/search` with CSV export.

### LegalTech Contracts & Administrative Petitions (`hop-dong`, `don-tu`)
8. `/mau-hop-dong-lao-dong-2026` — **Labor Contract Wizard (Điều 1–9)**: Collects and renders all 10 mandatory statutory items per **Article 21 Labor Code 2019** and **Circular 10/2020/TT-BLĐTBXH**, with real-time regional minimum wage validation against **Decree 293/2025/NĐ-CP**.
9. `/bien-ban-ban-giao-tai-san` — **Asset & Equipment Handover Protocol**: Dynamic multi-row asset inventory table with automatic quantity and valuation totals.
10. `/mau-don-xin-viec` — **Job Application & Cover Letter Wizard**: Compliant with **Labor Code 2019** and **Decree 30/2020/NĐ-CP**.
11. `/mau-don-xin-nghi-phep-cong-ty` — **Leave Request & Task Handover Wizard**: References **Article 113 / Article 115 Labor Code 2019** with supervisor and handover signature blocks.
12. `/mau-don-xin-tam-tru` — **CT01 Residency Change Declaration**: Compliant with **Residence Law 2020** and **Circular 66/2023/TT-BCA**, including homeowner consent section.

## Security & Configuration Notes

- Live secrets are excluded from source control. `config.json` holds neutral environment-backed defaults (`"api_url": "/api"`, `"bank_account": "REDACTED_SET_IN_ENV"`). Put private local deployment credentials in git-ignored `config.local.json` or environment variables (`VERCEL_TOKEN`, `API_SECRET_KEY`).
- `api/company.py` and `api/search.py` read `API_SECRET_KEY` strictly from the environment (returning `False` on `verify_api_key` when unconfigured), enforce per-IP sliding-window rate limiting (`60` requests / `60` seconds returning HTTP `429`), and do not trust spoofable `Referer`/`Origin` headers.
- `app.js` `verifyPasscode` fails closed (`return false;` on fetch/network errors), and `payment_webhook.py` `/api/recover` omits `"mock_otp"` unless test mode (`TESTING`) is explicitly enabled.

## Development, Build & Test Verification

Regenerate all 12 static tool pages, the main portal index (`index.html`), and `sitemap.xml`:

```bash
python regenerate_all_tools.py
python generate_niche_portal.py
python generate_sitemap.py
```

Run the full automated test suite (SQLite/HTTP backend endpoints, API/console security checks, Node.js syntax & `validateStep()` DOM verification across all legal wizards, PII hygiene scan, and exact mathematical verification for the 2026 HKD Tax, 5-Bracket PIT, and Shopee/TikTok calculators):

```bash
python run_tests.py
```

## Repomix Export

Repository context packaging is configured via `repomix.config.json` and `.repomixignore`, including all core platform source files, serverless API routes, tests, and the 12 curated tool directories while excluding binary databases (`*.db`), build/deployment logs (`*.log`), local secret overrides (`config.local.json`), and previous `repomix-output.*` bundles:

```bash
npx repomix
```
