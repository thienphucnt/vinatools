"""
Vietnam Business Registry - Company Detail Lookup
Route: GET /api/company
Query Parameters:
  - tax_code  : Vietnamese MST (Mã số thuế) e.g. "0100109106"

Scrapes masothue.com and tracuunnt.gdt.gov.vn to return
full structured company data indexed from GDT public records.
"""

import json
import re
import urllib.request
import urllib.parse
import urllib.error
import hmac
import hashlib
import time
import os
from http.server import BaseHTTPRequestHandler

API_SECRET_KEY = os.environ.get("API_SECRET_KEY", "default_secret_key_change_me_in_production")

def verify_api_key(key: str) -> bool:
    """
    Verifies a cryptographically signed API key.
    Format: MSTAPI.<memo>.<expiry>.<signature>
    """
    if not key or not key.startswith("MSTAPI."):
        return False
    parts = key.split(".")
    if len(parts) != 4:
        return False
    _, memo, expiry_str, sig = parts
    try:
        expiry = int(expiry_str)
    except ValueError:
        return False
        
    # Verify expiration (0 is a lifetime key)
    if expiry != 0 and time.time() > expiry:
        return False
        
    # Verify HMAC signature
    msg = f"{memo}.{expiry_str}"
    expected_sig = hmac.new(API_SECRET_KEY.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).hexdigest()
    
    return hmac.compare_digest(sig, expected_sig)


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://masothue.com/",
}


def fetch_html(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                return raw.decode("utf-8")
            except UnicodeDecodeError:
                return raw.decode("latin-1")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}")
    except Exception as e:
        raise RuntimeError(f"Network error: {str(e)}")


def clean(text: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_field(html: str, label_pattern: str) -> str:
    """
    Extract a field value from masothue.com detail page.
    The page uses <th> label : <td> value structure.
    """
    pattern = re.compile(
        label_pattern + r'.*?<td[^>]*>(.*?)</td>',
        re.IGNORECASE | re.DOTALL
    )
    match = pattern.search(html)
    if match:
        return clean(match.group(1))
    return ""


def lookup_company_vietqr(tax_code: str) -> dict:
    url = f"https://api.vietqr.io/v2/business/{tax_code}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get("code") == "00" and "data" in data:
                b_data = data["data"]
                status_raw = b_data.get("status", "")
                status = "active" if "đang hoạt động" in status_raw.lower() or "active" in status_raw.lower() else "inactive"
                metadata = data.get("metadata", {})
                
                result = {
                    "tax_code": tax_code,
                    "name_vietnamese": b_data.get("name", "N/A"),
                    "name_english": b_data.get("internationalName"),
                    "short_name": b_data.get("shortName"),
                    "address": b_data.get("address"),
                    "status": status,
                    "data_source": "Vietnam General Department of Taxation (GDT) via VietQR.io",
                    "note": metadata.get("disclaimer", "Data sourced from GDT records via VietQR API.")
                }
                return {k: v for k, v in result.items() if v is not None}
            else:
                return {"error": f"VietQR API returned error: {data.get('desc')}"}
    except Exception as e:
        return {"error": f"Failed to fetch from VietQR API: {str(e)}"}


def lookup_company(tax_code: str) -> dict:
    """
    Fetch and parse full company detail from masothue.com with fallback to VietQR.io.
    Tax code format: 10-digit string, e.g. "0100109106"
    """
    # Sanitize tax code — digits and hyphens only
    tax_code_clean = re.sub(r'[^\d\-]', '', tax_code).strip()
    if not tax_code_clean or len(tax_code_clean) < 8:
        return {"error": "Invalid tax code format. Must be 10 digits (e.g. 0100109106)"}

    # Try masothue.com first
    url = f"https://masothue.com/{tax_code_clean}"
    try:
        html = fetch_html(url)
        # Check for "not found" page
        if "không tìm thấy" in html.lower() or "not found" in html.lower():
            # If not found on masothue, try VietQR fallback
            return lookup_company_vietqr(tax_code_clean)

        # Extract fields using label anchors
        name_vn = extract_field(html, r'Tên doanh nghiệp')
        name_en = extract_field(html, r'Tên tiếng anh|Tên nước ngoài')
        short_name = extract_field(html, r'Tên viết tắt')
        legal_rep = extract_field(html, r'Người đại diện|Đại diện pháp luật')
        address = extract_field(html, r'Địa chỉ')
        phone = extract_field(html, r'Điện thoại|Phone')
        reg_date = extract_field(html, r'Ngày cấp|Ngày đăng ký')
        status_raw = extract_field(html, r'Trạng thái')
        industry_code = extract_field(html, r'Ngành nghề chính|Mã ngành')
        province = extract_field(html, r'Tỉnh thành')
        district = extract_field(html, r'Quận huyện|Quận/Huyện')
        charter_capital = extract_field(html, r'Vốn điều lệ')
        owners = extract_field(html, r'Thành viên|Cổ đông')

        # Normalize status
        status_lower = status_raw.lower() if status_raw else ""
        if "đang hoạt động" in status_lower or "active" in status_lower:
            status = "active"
        elif "ngừng" in status_lower or "giải thể" in status_lower or "dissolved" in status_lower:
            status = "inactive"
        else:
            status = "unknown"

        # If name couldn't be found via pattern, try og:title as fallback
        if not name_vn:
            og_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
            if og_match:
                name_vn = og_match.group(1).split("–")[0].strip()

        result = {
            "tax_code": tax_code_clean,
            "name_vietnamese": name_vn or "N/A",
            "name_english": name_en or None,
            "short_name": short_name or None,
            "legal_representative": legal_rep or None,
            "address": address or None,
            "province": province or None,
            "district": district or None,
            "phone": phone or None,
            "registration_date": reg_date or None,
            "charter_capital_vnd": charter_capital or None,
            "industry_code": industry_code or None,
            "status": status,
            "owners": owners or None,
            "profile_url": url,
            "data_source": "Vietnam General Department of Taxation (GDT) via masothue.com",
            "note": "Data sourced from publicly available Vietnamese government records."
        }
        return {k: v for k, v in result.items() if v is not None}

    except Exception as e:
        # Fallback to VietQR API if masothue.com fails (e.g. Cloudflare 403 on Vercel)
        return lookup_company_vietqr(tax_code_clean)



class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        def get_param(key, default=""):
            vals = params.get(key, [default])
            return vals[0].strip() if vals else default

        # 1. Authorization Verification
        referer = self.headers.get("Referer", "")
        origin = self.headers.get("Origin", "")
        
        is_sandbox = False
        # Allow queries directly from the developer portal website
        if referer and ("vinaearn" in referer or "vercel.app" in referer or "localhost" in referer):
            is_sandbox = True
        elif origin and ("vinaearn" in origin or "vercel.app" in origin or "localhost" in origin):
            is_sandbox = True

        if not is_sandbox:
            # Check API Key in headers
            auth_header = self.headers.get("Authorization", "")
            api_key = ""
            if auth_header.startswith("Bearer "):
                api_key = auth_header.split(" ")[1].strip()
            else:
                api_key = self.headers.get("x-api-key", "")
                
            if not api_key:
                # Query param fallback
                api_key = get_param("api_key")
                
            if not api_key or not verify_api_key(api_key):
                self._send_json({
                    "error": "Unauthorized. A valid API Key is required.",
                    "reason": "Missing or invalid API Key in headers (Authorization: Bearer <key> or x-api-key: <key>).",
                    "purchase_url": "https://vinaearn-ai.vercel.app/#pricing"
                }, status=401)
                return

        # 2. Parameter Extraction
        tax_code = get_param("tax_code")

        if not tax_code:
            self._send_json({
                "error": "Missing required parameter: tax_code",
                "example": "/api/company?tax_code=0100109106",
                "note": "tax_code is the Vietnamese MST (Ma so thue) — a 10-digit national business identifier"
            }, status=400)
            return

        try:
            result = lookup_company(tax_code)
            status_code = 404 if "error" in result else 200
            self._send_json(result, status=status_code)
        except Exception as e:
            self._send_json({"error": str(e)}, status=500)

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
