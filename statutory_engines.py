# -*- coding: utf-8 -*-
"""
2026 Vietnamese Statutory FinTech Engines & Shared Layout Shell.
Provides deterministic calculation engines and clean client-side HTML shell rendering.
"""

HKD_INDUSTRIES = {
    "group1": {
        "name": "Nhóm 1: Phân phối, cung cấp hàng hóa (Bán buôn, bán lẻ, tạp hóa, thời trang, TMĐT)",
        "vat_rate": 0.01,
        "pit_rate": 0.005,
    },
    "group2": {
        "name": "Nhóm 2: Dịch vụ, xây dựng không bao thầu nguyên vật liệu (Spa, tư vấn, thiết kế, lưu trú)",
        "vat_rate": 0.05,
        "pit_rate": 0.02,
    },
    "group3": {
        "name": "Nhóm 3: Sản xuất, vận tải, dịch vụ có gắn với hàng hóa, ăn uống (Nhà hàng, quán cafe, gia công)",
        "vat_rate": 0.03,
        "pit_rate": 0.015,
    },
    "group4": {
        "name": "Nhóm 4: Hoạt động kinh doanh khác",
        "vat_rate": 0.02,
        "pit_rate": 0.01,
    },
    "group5": {
        "name": "Nhóm 5: Cho thuê tài sản (Cho thuê nhà, mặt bằng, phương tiện)",
        "vat_rate": 0.05,
        "pit_rate": 0.05,
    },
}

REGION_MIN_WAGES_2026 = {
    "1": 5310000,
    "2": 4730000,
    "3": 4140000,
    "4": 3700000,
}

BASE_SALARIES_2026 = {
    "h2_2026": 2530000,  # From 01/07/2026 per Decree 161/2026/ND-CP
    "h1_2026": 2340000,  # H1 2026
}


def calculate_hkd_tax_2026(revenue, expenses, industry_key="group1", ecom_pct=0.0):
    """
    Calculates 2026 Household Business (Ho Kinh Doanh) VAT, PIT, License Fee,
    and platform-withheld breakdown per Decree 68/2026/ND-CP, Circular 18/2026/TT-BTC,
    Decree 141/2026/ND-CP, and Resolution 198/2025/QH15.
    """
    revenue = max(0.0, float(revenue))
    expenses = max(0.0, float(expenses))
    ecom_pct = min(100.0, max(0.0, float(ecom_pct)))

    ind = HKD_INDUSTRIES.get(industry_key, HKD_INDUSTRIES["group1"])
    vat_rate = ind["vat_rate"]
    pit_rate = ind["pit_rate"]
    license_fee = 0  # Abolished from 01/01/2026 under Resolution 198/2025/QH15

    platform_revenue = revenue * (ecom_pct / 100.0)
    direct_revenue = revenue - platform_revenue

    if revenue <= 1000000000:
        tier = "Tier 1"
        vat = 0
        pit_method1 = 0
        pit_method2 = None
        pit_optimal = 0
        recommended_method = "exempt"
        withheld_at_source = round(platform_revenue * (vat_rate + pit_rate)) if platform_revenue > 0 else 0
        self_declared_due = 0
    elif revenue <= 3000000000:
        tier = "Tier 2"
        vat = round(revenue * vat_rate)
        pit_method1 = round((revenue - 1000000000) * pit_rate)
        pit_method2 = round(max(0.0, revenue - expenses) * 0.15)
        if pit_method1 <= pit_method2:
            pit_optimal = pit_method1
            recommended_method = "method1_revenue"
        else:
            pit_optimal = pit_method2
            recommended_method = "method2_profit"
        withheld_at_source = round(platform_revenue * (vat_rate + pit_rate))
        self_declared_due = max(0, (vat + pit_optimal) - withheld_at_source)
    elif revenue <= 50000000000:
        tier = "Tier 3"
        vat = round(revenue * vat_rate)
        pit_method1 = None
        pit_method2 = round(max(0.0, revenue - expenses) * 0.17)
        pit_optimal = pit_method2
        recommended_method = "mandatory_profit_17"
        withheld_at_source = round(platform_revenue * (vat_rate + pit_rate))
        self_declared_due = max(0, (vat + pit_optimal) - withheld_at_source)
    else:
        tier = "Tier 4"
        vat = round(revenue * vat_rate)
        pit_method1 = None
        pit_method2 = round(max(0.0, revenue - expenses) * 0.20)
        pit_optimal = pit_method2
        recommended_method = "mandatory_profit_20"
        withheld_at_source = round(platform_revenue * (vat_rate + pit_rate))
        self_declared_due = max(0, (vat + pit_optimal) - withheld_at_source)

    return {
        "tier": tier,
        "revenue": round(revenue),
        "expenses": round(expenses),
        "license_fee": license_fee,
        "vat_rate": vat_rate,
        "pit_rate": pit_rate,
        "vat": vat,
        "pit_method1": pit_method1,
        "pit_method2": pit_method2,
        "pit_optimal": pit_optimal,
        "recommended_method": recommended_method,
        "total_tax": vat + pit_optimal,
        "platform_revenue": round(platform_revenue),
        "direct_revenue": round(direct_revenue),
        "withheld_at_source": withheld_at_source,
        "self_declared_due": self_declared_due,
    }


def _pit_2026_from_tntt(tntt):
    if tntt <= 0:
        return 0
    if tntt <= 10000000:
        tax = tntt * 0.05
    elif tntt <= 30000000:
        tax = tntt * 0.10 - 500000
    elif tntt <= 60000000:
        tax = tntt * 0.20 - 3500000
    elif tntt <= 100000000:
        tax = tntt * 0.30 - 9500000
    else:
        tax = tntt * 0.35 - 14500000
    return round(max(0.0, tax))


def _pit_2025_from_tntt(tntt):
    if tntt <= 0:
        return 0
    if tntt <= 5000000:
        tax = tntt * 0.05
    elif tntt <= 10000000:
        tax = tntt * 0.10 - 250000
    elif tntt <= 18000000:
        tax = tntt * 0.15 - 750000
    elif tntt <= 32000000:
        tax = tntt * 0.20 - 1650000
    elif tntt <= 52000000:
        tax = tntt * 0.25 - 3250000
    elif tntt <= 80000000:
        tax = tntt * 0.30 - 5850000
    else:
        tax = tntt * 0.35 - 9850000
    return round(max(0.0, tax))


def _compute_insurance(gross, ins_base_custom=None, region="1", period="h2_2026"):
    ins_salary = float(gross) if ins_base_custom is None else max(0.0, float(ins_base_custom))
    base_salary = BASE_SALARIES_2026.get(period, 2530000)
    min_wage = REGION_MIN_WAGES_2026.get(str(region), 5310000)

    cap_bhxh_bhyt = 20 * base_salary
    cap_bhtn = 20 * min_wage

    bhxh_base = min(ins_salary, cap_bhxh_bhyt)
    bhtn_base = min(ins_salary, cap_bhtn)

    bhxh = round(bhxh_base * 0.08)
    bhyt = round(bhxh_base * 0.015)
    bhtn = round(bhtn_base * 0.01)
    total_ins = bhxh + bhyt + bhtn
    return {
        "bhxh": bhxh,
        "bhyt": bhyt,
        "bhtn": bhtn,
        "total_insurance": total_ins,
        "cap_bhxh_bhyt": cap_bhxh_bhyt,
        "cap_bhtn": cap_bhtn,
    }


def calculate_pit_2026(
    income,
    mode="gross-to-net",
    dependents=0,
    region="1",
    period="h2_2026",
    ins_base_custom=None,
    med_edu_monthly=0,
):
    """
    Calculates 2026 Gross/Net salary and 5-bracket PIT per Law No. 109/2025/QH15,
    Resolution 110/2025/UBTVQH15, Decree 253/2026/ND-CP, Decree 293/2025/ND-CP,
    and Decree 161/2026/ND-CP, along with side-by-side 2025 7-bracket comparison.
    """
    income = max(0.0, float(income))
    dependents = max(0, int(dependents))
    med_edu_cap = round((23000000 + 24000000) / 12)
    med_edu = min(max(0.0, float(med_edu_monthly)), med_edu_cap)

    def eval_from_gross(gross_val):
        ins = _compute_insurance(gross_val, ins_base_custom, region, period)
        total_ins = ins["total_insurance"]

        personal_2026 = 15500000
        dependent_2026 = 6200000 * dependents
        tntt_2026 = max(0.0, gross_val - total_ins - personal_2026 - dependent_2026 - med_edu)
        pit_2026 = _pit_2026_from_tntt(tntt_2026)
        net_2026 = round(gross_val - total_ins - pit_2026)

        personal_2025 = 11000000
        dependent_2025 = 4400000 * dependents
        tntt_2025 = max(0.0, gross_val - total_ins - personal_2025 - dependent_2025)
        pit_2025 = _pit_2025_from_tntt(tntt_2025)
        net_2025 = round(gross_val - total_ins - pit_2025)

        return {
            "gross": round(gross_val),
            "net": net_2026,
            "net_2025": net_2025,
            **ins,
            "personal_deduction_2026": personal_2026,
            "dependent_deduction_2026": dependent_2026,
            "med_edu_deduction": round(med_edu),
            "tntt_2026": round(tntt_2026),
            "pit_2026": pit_2026,
            "tntt_2025": round(tntt_2025),
            "pit_2025": pit_2025,
            "monthly_tax_saved": pit_2025 - pit_2026,
            "annual_tax_saved": (pit_2025 - pit_2026) * 12,
        }

    if mode == "net-to-gross":
        target_net = income
        low = target_net
        high = max(target_net * 2.2 + 50000000, 100000000)
        for _ in range(80):
            mid = (low + high) / 2.0
            res = eval_from_gross(mid)
            if res["net"] < target_net:
                low = mid
            else:
                high = mid
        gross_est = round((low + high) / 2.0)
        # Fine-tune within +-3 VND for exact integer net match
        best = eval_from_gross(gross_est)
        for delta in (-2, -1, 0, 1, 2):
            cand = eval_from_gross(max(0, gross_est + delta))
            if abs(cand["net"] - target_net) < abs(best["net"] - target_net):
                best = cand
        return best

    return eval_from_gross(income)


def calculate_ecommerce_fees_2026(
    platform="shopee",
    selling_price=250000,
    cogs=120000,
    ops=15000,
    buyer_shipping=0,
    shop_voucher=0,
    pay_fee_pct=6.0,
    fixed_fee_pct=3.5,
    infra_fee=3000,
    voucher_xtra=False,
    content_xtra=False,
    piship=False,
    tax_withholding=False,
    affiliate_pct=0.0,
    tiktok_trans_pct=6.0,
    tiktok_comm_pct=14.0,
    tiktok_flat_fee=3000,
):
    """
    Calculates 2026 Shopee & TikTok Shop seller fee breakdown, net payout,
    net profit, margin %, and Break-Even ROAS.
    """
    price = max(0.0, float(selling_price))
    cogs = max(0.0, float(cogs))
    ops = max(0.0, float(ops))
    buyer_shipping = max(0.0, float(buyer_shipping))
    shop_voucher = max(0.0, float(shop_voucher))

    item_net = max(0.0, price - shop_voucher)
    trans_base = max(0.0, price + buyer_shipping - shop_voucher)

    if platform == "shopee":
        transaction_fee = round(trans_base * (float(pay_fee_pct) / 100.0))
        fixed_fee = round(item_net * (float(fixed_fee_pct) / 100.0))
        infra = round(max(0.0, float(infra_fee)))
        vx_fee = round(min(item_net * 0.055, 50000)) if voucher_xtra else 0
        cx_fee = round(min(item_net * 0.0295, 50000)) if content_xtra else 0
        ps_fee = 2700 if piship else 0
        platform_fee = transaction_fee + fixed_fee + infra + vx_fee + cx_fee + ps_fee
    else:
        transaction_fee = round(trans_base * (float(tiktok_trans_pct) / 100.0))
        fixed_fee = round(item_net * (float(tiktok_comm_pct) / 100.0))
        infra = round(max(0.0, float(tiktok_flat_fee)))
        vx_fee = 0
        cx_fee = 0
        ps_fee = 0
        platform_fee = transaction_fee + fixed_fee + infra

    tax_withheld = round(item_net * 0.015) if tax_withholding else 0
    affiliate_fee = round(item_net * (max(0.0, float(affiliate_pct)) / 100.0))
    net_payout = round(item_net - platform_fee - tax_withheld)
    profit_before_ads = round(net_payout - cogs - ops)
    net_profit = round(profit_before_ads - affiliate_fee)
    margin_pct = (net_profit / item_net * 100.0) if item_net > 0 else 0.0
    break_even_roas = (item_net / profit_before_ads) if profit_before_ads > 0 else None

    return {
        "platform": platform,
        "item_net": round(item_net),
        "transaction_fee": transaction_fee,
        "fixed_fee": fixed_fee,
        "infra_fee": infra,
        "voucher_xtra_fee": vx_fee,
        "content_xtra_fee": cx_fee,
        "piship_fee": ps_fee,
        "platform_fee": platform_fee,
        "tax_withheld": tax_withheld,
        "affiliate_fee": affiliate_fee,
        "net_payout": net_payout,
        "profit_before_ads": profit_before_ads,
        "net_profit": net_profit,
        "margin_pct": round(margin_pct, 2),
        "break_even_roas": round(break_even_roas, 2) if break_even_roas is not None else None,
    }


def render_tool_shell(
    keyword,
    slug,
    category_label,
    page_title,
    meta_desc,
    meta_keywords,
    subtitle,
    tool_html,
    tool_js,
    extra_head="",
    body_class="bg-slate-950 text-white min-h-screen",
    container_class="layout-container max-w-7xl mx-auto",
    nav_badge="100% Client-Side",
):
    """
    Renders a clean, ad-free, paywall-free VinaTools page shell with JSON-LD metadata
    and Decree 91/2025/QH15 compliance footer.
    """
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>

  <meta name="description" content="{meta_desc}">
  <meta name="keywords" content="{meta_keywords}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://vinatools.vercel.app/{slug}">

  <link rel="preconnect" href="https://cdnjs.cloudflare.com">

  <meta property="og:type" content="website">
  <meta property="og:title" content="{page_title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:url" content="https://vinatools.vercel.app/{slug}">
  <meta property="og:site_name" content="VinaTools">
  <meta property="og:image" content="https://vinatools.vercel.app/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "SoftwareApplication",
        "name": "{keyword}",
        "operatingSystem": "All",
        "applicationCategory": "BusinessApplication",
        "offers": {{
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "VND"
        }}
      }},
      {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{
            "@type": "ListItem",
            "position": 1,
            "name": "VinaTools",
            "item": "https://vinatools.vercel.app"
          }},
          {{
            "@type": "ListItem",
            "position": 2,
            "name": "{category_label}",
            "item": "https://vinatools.vercel.app"
          }},
          {{
            "@type": "ListItem",
            "position": 3,
            "name": "{keyword}",
            "item": "https://vinatools.vercel.app/{slug}"
          }}
        ]
      }}
    ]
  }}
  </script>

  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="/global_style.css">
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#0a0c10">
  <script>
    if ('serviceWorker' in navigator) {{
      window.addEventListener('load', () => {{
        navigator.serviceWorker.register('/sw.js').catch(() => {{}});
      }});
    }}
  </script>
  {extra_head}
</head>
<body class="{body_class}">
  <div class="{container_class}">
    <nav class="portal-nav no-print" style="display: flex; justify-content: space-between; align-items: center; padding: 20px 16px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 30px; flex-wrap: wrap; gap: 12px;">
      <a href="/" class="portal-logo" style="display: flex; align-items: center; gap: 10px; font-size: 1.4rem; font-weight: 800; color: #fff; text-decoration: none;">
        <i class="fa-solid fa-toolbox" style="color: #00a8ff;"></i> VinaTools
      </a>
      <div class="nav-links" style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
        <a href="/?filter=tien-ich" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500;"><i class="fa-solid fa-calculator" style="color: #ec4899; margin-right: 4px;"></i> FinTech &amp; Thuế</a>
        <a href="/?filter=hop-dong" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500;"><i class="fa-solid fa-file-contract" style="color: #8b5cf6; margin-right: 4px;"></i> Hợp đồng</a>
        <a href="/?filter=don-tu" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500;"><i class="fa-solid fa-file-lines" style="color: #00a8ff; margin-right: 4px;"></i> Đơn từ</a>
        <a href="/api-docs.html" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500;"><i class="fa-solid fa-code" style="color: #10b981; margin-right: 4px;"></i> VietRegistry API</a>
      </div>
      <div id="user-nav-status" style="font-size: 0.85rem; color: #10b981; display: flex; align-items: center; gap: 8px; font-weight: 600;">
        <i class="fa-solid fa-shield-halved"></i> {nav_badge}
      </div>
    </nav>

    <header class="tool-header no-print" style="text-align: center; margin-bottom: 32px; padding: 0 16px;">
      <h1 style="font-size: clamp(1.75rem, 3.5vw, 2.5rem); margin-bottom: 12px;">{keyword}</h1>
      <p style="color: var(--text-secondary); max-width: 780px; margin: 0 auto; font-size: 0.98rem;">{subtitle}</p>
    </header>

    {tool_html}

    <footer class="tool-footer no-print" style="margin-top: 50px; padding: 25px 16px; border-top: 1px solid var(--border-glass); font-size: 0.8rem; color: var(--text-muted); text-align: center; display: flex; flex-direction: column; align-items: center; gap: 12px;">
      <p>&copy; 2026 VinaTools. Toàn bộ biểu mẫu &amp; công cụ tính toán chạy hoàn toàn miễn phí trên trình duyệt (client-side), tuân thủ Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15.</p>
      <p style="display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
        <a href="/" style="color: var(--text-secondary); text-decoration: none;">Trang chủ</a>
        <a href="/api-docs.html" style="color: var(--text-secondary); text-decoration: none;">VietRegistry API</a>
        <a href="/terms.html" style="color: var(--text-secondary); text-decoration: none;">Điều khoản</a>
        <a href="/privacy.html" style="color: var(--text-secondary); text-decoration: none;">Bảo mật</a>
        <a href="/about.html" style="color: var(--text-secondary); text-decoration: none;">Giới thiệu</a>
        <a href="/contact.html" style="color: var(--text-secondary); text-decoration: none;">Liên hệ</a>
      </p>
    </footer>
  </div>

  <script>
    {tool_js}
  </script>
</body>
</html>
"""
