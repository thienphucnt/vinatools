# -*- coding: utf-8 -*-
"""
VinaTools Modular Code Generator & Dispatcher.
Routes the 12 curated flagship LegalTech, FinTech, Data, and Registry tools
to deterministic builders without any fake dropzones, countdown gates, or PII.
"""

import json
import os
import re
import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(WORKSPACE, "config.json")
DEPLOYED_PATH = os.path.join(WORKSPACE, "deployed_tools.json")

from statutory_engines import (
    calculate_hkd_tax_2026,
    calculate_pit_2026,
    calculate_ecommerce_fees_2026,
)
from fintech_builders import (
    build_hkd_tax_simulator,
    build_pit_gross_net_simulator,
    build_ecommerce_calculator,
    build_number_to_words,
    build_address_parser,
    build_compound_interest_calculator,
    build_tax_code_lookup,
)
from legal_builders import build_legal_document_wizard


BUILDER_MAP = {
    "cong-cu-tinh-thue-ho-kinh-doanh": build_hkd_tax_simulator,
    "cong-cu-tinh-luong-gross-net-tncn-2026": build_pit_gross_net_simulator,
    "cong-cu-tinh-phi-san-tmdt": build_ecommerce_calculator,
    "cong-cu-doc-so-thanh-chu": build_number_to_words,
    "cong-cu-tach-va-chuan-hoa-dia-chi": build_address_parser,
    "cong-cu-tinh-lai-gop": build_compound_interest_calculator,
    "tra-cuu-ma-so-thue-doanh-nghiep": build_tax_code_lookup,
    "mau-hop-dong-lao-dong-2026": build_legal_document_wizard,
    "bien-ban-ban-giao-tai-san": build_legal_document_wizard,
    "mau-don-xin-viec": build_legal_document_wizard,
    "mau-don-xin-nghi-phep-cong-ty": build_legal_document_wizard,
    "mau-don-xin-tam-tru": build_legal_document_wizard,
}


def load_config():
    """Load platform configuration without leaking secrets into static outputs."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def slugify(text):
    """Convert Vietnamese text into a canonical ASCII URL slug."""
    text = text.lower().strip()
    maps = {
        "[àáảãạăằắẳẵặâầấẩẫậ]": "a",
        "[èéẻẽẹêềếểễệ]": "e",
        "[ìíỉĩị]": "i",
        "[òóỏõọôồốổỗộơờớởỡợ]": "o",
        "[ùúủũụưừứửữự]": "u",
        "[ỳýỷỹỵ]": "y",
        "đ": "d",
    }
    for pattern, repl in maps.items():
        text = re.sub(pattern, repl, text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text.strip("-")


def resolve_canonical_slug(niche_keyword, slug=None):
    """Resolve an input keyword or slug to one of the 12 supported flagship slugs."""
    if slug:
        candidate = slug.strip().lower()
        if candidate in BUILDER_MAP:
            return candidate
        raise ValueError(f"Unsupported tool slug: '{slug}'. Only curated flagship tools are supported.")

    kw_lower = niche_keyword.lower().strip()

    # Exact manifest lookup first
    if os.path.exists(DEPLOYED_PATH):
        try:
            with open(DEPLOYED_PATH, "r", encoding="utf-8") as f:
                for entry in json.load(f):
                    if entry.get("keyword", "").lower().strip() == kw_lower:
                        mapped = entry.get("slug", "").strip().lower()
                        if mapped in BUILDER_MAP:
                            return mapped
        except (OSError, json.JSONDecodeError):
            pass

    raw_slug = slugify(niche_keyword)
    if raw_slug in BUILDER_MAP:
        return raw_slug

    # Deterministic keyword pattern fallback for CLI / autopilot calls
    keyword_routes = [
        (("thuế hộ kinh doanh", "hộ kinh doanh"), "cong-cu-tinh-thue-ho-kinh-doanh"),
        (("gross", "tncn", "thuế thu nhập cá nhân"), "cong-cu-tinh-luong-gross-net-tncn-2026"),
        (("phí sàn", "shopee", "tiktok"), "cong-cu-tinh-phi-san-tmdt"),
        (("đọc số thành chữ", "số thành chữ"), "cong-cu-doc-so-thanh-chu"),
        (("tách và chuẩn hóa địa chỉ", "chuẩn hóa địa chỉ"), "cong-cu-tach-va-chuan-hoa-dia-chi"),
        (("lãi kép", "lãi gộp", "dòng tiền"), "cong-cu-tinh-lai-gop"),
        (("mã số thuế", "vietregistry"), "tra-cuu-ma-so-thue-doanh-nghiep"),
        (("hợp đồng lao động", "thử việc"), "mau-hop-dong-lao-dong-2026"),
        (("bàn giao tài sản",), "bien-ban-ban-giao-tai-san"),
        (("xin việc", "ứng tuyển"), "mau-don-xin-viec"),
        (("nghỉ phép",), "mau-don-xin-nghi-phep-cong-ty"),
        (("tạm trú", "ct01"), "mau-don-xin-tam-tru"),
    ]
    for patterns, canonical in keyword_routes:
        if any(p in kw_lower for p in patterns):
            return canonical

    raise ValueError(
        f"Unsupported tool keyword/slug: '{niche_keyword}'. "
        "Placebo file-upload dropzones are disabled."
    )


def build_offline_tool_template(niche_keyword, slug, config=None):
    """Build deterministic standalone HTML for a curated flagship slug."""
    canonical_slug = resolve_canonical_slug(niche_keyword, slug=slug)
    builder = BUILDER_MAP[canonical_slug]
    cfg = config if config is not None else load_config()
    return builder(niche_keyword, canonical_slug, cfg)


def generate_tool(niche_keyword, slug=None):
    """Generate and write index.html for a supported flagship tool."""
    config = load_config()
    canonical_slug = resolve_canonical_slug(niche_keyword, slug=slug)
    tool_dir = os.path.join(WORKSPACE, canonical_slug)
    os.makedirs(tool_dir, exist_ok=True)

    print(f"Generating flagship tool for: '{niche_keyword}' (Slug: {canonical_slug})")
    html_content = build_offline_tool_template(niche_keyword, canonical_slug, config)

    index_path = os.path.join(tool_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Tool generation complete! Saved index.html in: {tool_dir}")
    return canonical_slug


if __name__ == "__main__":
    generate_tool("Công cụ tính thuế hộ kinh doanh 2026", "cong-cu-tinh-thue-ho-kinh-doanh")
