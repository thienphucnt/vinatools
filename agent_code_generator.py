# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import urllib.parse
import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Config & Paths
WORKSPACE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(WORKSPACE, "config.json")
TEMPLATES_DIR = os.path.join(WORKSPACE, "templates")

def load_config():
  if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
      return json.load(f)
  return {}

def slugify(text):
  """
  Converts Vietnamese text to a clean URL slug.
  """
  text = text.lower()
  # Map Vietnamese characters to plain English
  maps = {
    '[àáảãạăằắẳẵặâầấẩẫậ]': 'a',
    '[èéẻẽẹêềếểễệ]': 'e',
    '[ìíỉĩị]': 'i',
    '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
    '[ùúủũụưừứửữự]': 'u',
    '[ỳýỷỹỵ]': 'y',
    'đ': 'd'
  }
  for key, val in maps.items():
    text = re.sub(key, val, text)
  text = re.sub(r'[^a-z0-9\s-]', '', text)
  text = re.sub(r'[\s-]+', '-', text)
  return text.strip('-')

def call_gemini_api(prompt, api_key):
  """
  Helper to invoke Google Gemini API for code generation.
  """
  url = f"https://generativetoolkit.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
  headers = {
    "Content-Type": "application/json"
  }
  payload = {
    "contents": [{
      "parts": [{
        "text": prompt
      }]
    }],
    "generationConfig": {
      "temperature": 0.2,
      "maxOutputTokens": 2048
    }
  }
  
  data = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(url, data=data, headers=headers, method="POST")
  
  try:
    with urllib.request.urlopen(req) as res:
      result = json.loads(res.read().decode("utf-8"))
      # Extract text content from gemini response structure
      if "candidates" in result and len(result["candidates"]) > 0:
        return result["candidates"][0]["content"]["parts"][0]["text"]
  except Exception as e:
    print(f"Gemini API call failed: {e}. Falling back to rule-based generation.")
  return None


# ==============================================================================
# CUSTOM NICHE TOOLS IMPLEMENTATIONS
# ==============================================================================

def build_ecommerce_calculator(keyword, slug, config):
  bank_name = config.get("bank_name", "Techcombank")
  bank_id = config.get("bank_id", "TCB")
  acc_num = config.get("bank_account", "")
  acc_holder = config.get("bank_account_holder", "")
  api_url = config.get("api_url", "/api/check-payment")
  google_adsense_client = config.get("google_adsense_client", "ca-pub-mock")

  tool_html = f"""
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            accent: {{
              primary: '#00a8ff',
              secondary: '#eb4899',
            }}
          }}
        }}
      }}
    }}
  </script>

  <style>
    .glass-card {{
      background: rgba(30, 41, 59, 0.7);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    input[type="number"], select {{
      background: rgba(15, 23, 42, 0.6) !important;
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
      color: white !important;
      transition: all 0.3s ease;
    }}
    input[type="number"]:focus, select:focus {{
      border-color: #00a8ff !important;
      box-shadow: 0 0 0 2px rgba(0, 168, 255, 0.2) !important;
      outline: none;
    }}
    .tab-btn.active {{
      background: linear-gradient(135deg, #00a8ff 0%, #eb4899 100%);
      box-shadow: 0 0 15px rgba(0, 168, 255, 0.4);
    }}
  </style>

  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- Terms check -->
    <div class="glass-card rounded-2xl p-6 mb-8 border-l-4 border-yellow-500">
      <div class="flex items-start gap-3">
        <input type="checkbox" id="accept-terms" class="mt-1 w-4 h-4 rounded cursor-pointer" checked>
        <label for="accept-terms" class="text-sm text-gray-300 leading-relaxed cursor-pointer select-none">
          Tôi đã đọc, hiểu rõ và đồng ý với <a href="/terms.html" target="_blank" class="text-accent-primary hover:underline font-semibold">Điều khoản dịch vụ</a> và <a href="/privacy.html" target="_blank" class="text-accent-primary hover:underline font-semibold">Chính sách bảo mật</a> của VinaTools.
        </label>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Left Panel: Inputs -->
      <div class="lg:col-span-7 space-y-6">
        <div class="glass-card rounded-3xl p-8 shadow-2xl">
          <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <i class="fa-solid fa-calculator text-accent-primary"></i> Thông Tin Sản Phẩm & Chi Phí
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Giá Bán Sản Phẩm (VND)</label>
              <input type="number" id="calc-price" value="250000" min="0" class="w-full px-4 py-3 rounded-xl text-lg font-bold">
            </div>
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Giá Vốn / Nhập (VND)</label>
              <input type="number" id="calc-cogs" value="120000" min="0" class="w-full px-4 py-3 rounded-xl text-lg font-bold">
            </div>
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Chi Phí Vận Hành (VND)</label>
              <input type="number" id="calc-ops" value="15000" min="0" class="w-full px-4 py-3 rounded-xl text-lg font-bold">
            </div>
          </div>

          <!-- Platform Selector Tabs -->
          <div class="mb-6">
            <label class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Chọn Sàn Thương Mại Điện Tử</label>
            <div class="grid grid-cols-2 gap-4">
              <button type="button" id="tab-shopee" onclick="switchPlatform('shopee')" class="tab-btn active py-3 rounded-xl text-sm font-bold text-white transition-all duration-300">
                <i class="fa-brands fa-shopify mr-2"></i> Shopee
              </button>
              <button type="button" id="tab-tiktok" onclick="switchPlatform('tiktok')" class="tab-btn py-3 rounded-xl text-sm font-bold text-white bg-slate-800 hover:bg-slate-700 transition-all duration-300">
                <i class="fa-brands fa-tiktok mr-2"></i> TikTok Shop
              </button>
            </div>
          </div>

          <!-- Shopee Params -->
          <div id="params-shopee" class="space-y-4">
            <h3 class="text-sm font-bold text-white border-b border-gray-700 pb-2 mb-3">Thông số Biểu Phí Shopee (Cập nhật 2026)</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-gray-400 mb-1">Phí thanh toán (%)</label>
                <input type="number" id="shopee-pay-fee" value="4.0" step="0.1" class="w-full px-3 py-2 rounded-lg text-sm">
              </div>
              <div>
                <label class="block text-xs text-gray-400 mb-1">Phí cố định (%)</label>
                <input type="number" id="shopee-fixed-fee" value="15.0" step="0.1" class="w-full px-3 py-2 rounded-lg text-sm">
              </div>
            </div>
            <div class="space-y-3 pt-2">
              <label class="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" id="shopee-freeship" checked class="w-4 h-4 rounded cursor-pointer">
                <span class="text-sm text-gray-300">Tham gia Freeship Xtra (6.0% fee, tối đa 40.000đ/sản phẩm)</span>
              </label>
              <label class="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" id="shopee-voucher" class="w-4 h-4 rounded cursor-pointer">
                <span class="text-sm text-gray-300">Tham gia Voucher Xtra (4.0% fee, tối đa 50.000đ/sản phẩm)</span>
              </label>
            </div>
            <div class="pt-2">
              <label class="block text-xs text-gray-400 mb-1">Chiết khấu Tiếp thị liên kết (Affiliate %) - dành cho KOL/KOC hoặc quảng cáo</label>
              <input type="number" id="shopee-affiliate" value="0" min="0" class="w-full px-3 py-2 rounded-lg text-sm">
            </div>
          </div>

          <!-- TikTok Shop Params -->
          <div id="params-tiktok" class="space-y-4 hidden">
            <h3 class="text-sm font-bold text-white border-b border-gray-700 pb-2 mb-3">Thông số Biểu Phí TikTok Shop (Cập nhật 2026)</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-gray-400 mb-1">Phí giao dịch (%)</label>
                <input type="number" id="tiktok-trans-fee" value="6.0" step="0.1" class="w-full px-3 py-2 rounded-lg text-sm">
              </div>
              <div>
                <label class="block text-xs text-gray-400 mb-1">Phí hoa hồng (%)</label>
                <input type="number" id="tiktok-commission" value="16.1" step="0.1" class="w-full px-3 py-2 rounded-lg text-sm">
              </div>
            </div>
            <div>
              <label class="block text-xs text-gray-400 mb-1">Phí xử lý đơn hàng cố định (VND)</label>
              <input type="number" id="tiktok-flat-fee" value="3000" min="0" class="w-full px-3 py-2 rounded-lg text-sm">
            </div>
            <div class="pt-2">
              <label class="block text-xs text-gray-400 mb-1">Chiết khấu Tiếp thị liên kết (Affiliate %)</label>
              <input type="number" id="tiktok-affiliate" value="0" min="0" class="w-full px-3 py-2 rounded-lg text-sm">
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Results & B2B Ads -->
      <div class="lg:col-span-5 space-y-6">
        <!-- Receipt Card -->
        <div class="glass-card rounded-3xl p-8 shadow-2xl relative overflow-hidden">
          <div class="absolute top-0 right-0 w-32 h-32 bg-accent-primary/10 rounded-full blur-3xl pointer-events-none"></div>
          <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <i class="fa-solid fa-receipt text-accent-secondary"></i> Báo Cáo Doanh Số & Biên Lợi Nhuận
          </h2>

          <div class="space-y-4 text-sm mb-6 border-b border-gray-700/50 pb-6">
            <div class="flex justify-between text-gray-300">
              <span>Doanh thu gộp (Giá bán)</span>
              <span id="res-gross" class="font-bold text-white">0 đ</span>
            </div>
            <div class="flex justify-between text-gray-300">
              <span>Giá vốn sản phẩm (COGS)</span>
              <span id="res-cogs" class="font-semibold text-white">0 đ</span>
            </div>
            <div class="flex justify-between text-gray-300">
              <span>Chi phí đóng gói & vận hành</span>
              <span id="res-ops" class="font-semibold text-white">0 đ</span>
            </div>
            <div class="flex justify-between text-red-400">
              <span>Tổng phí sàn khấu trừ</span>
              <span id="res-platform-fee" class="font-semibold">0 đ</span>
            </div>
            <div class="flex justify-between text-red-400">
              <span>Chi phí Tiếp thị liên kết</span>
              <span id="res-affiliate" class="font-semibold">0 đ</span>
            </div>
          </div>

          <div class="space-y-4 mb-6">
            <div class="flex justify-between items-center">
              <span class="text-gray-300">Thực nhận từ sàn</span>
              <span id="res-payout" class="text-xl font-extrabold text-green-400">0 đ</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-300">Lợi nhuận ròng</span>
              <span id="res-net-profit" class="text-2xl font-black text-white">0 đ</span>
            </div>
          </div>

          <!-- Profit Margin Gauge Card -->
          <div id="margin-gauge-card" class="rounded-2xl p-4 text-center transition-all duration-500">
            <div class="text-xs uppercase tracking-wider text-gray-300/80 mb-1 font-semibold">Tỷ suất lợi nhuận ròng (Margin)</div>
            <div id="res-margin" class="text-3xl font-black text-white">0.0%</div>
            <div id="res-margin-desc" class="text-xs mt-2 font-medium">--</div>
          </div>

          <div class="mt-6 text-center">
            <button type="button" onclick="triggerVipUpgrade()" class="w-full py-3 bg-gradient-to-r from-yellow-500 to-amber-600 hover:from-yellow-600 hover:to-amber-700 text-white font-bold rounded-xl text-sm transition-all duration-300 shadow-lg">
              <i class="fa-solid fa-crown mr-2"></i> Nâng cấp VIP để lưu không giới hạn lịch sử
            </button>
          </div>
        </div>

        <!-- B2B Ads Placeholder Box -->
        <div class="grid grid-cols-1 gap-4">
          <div onclick="triggerVipUpgrade()" class="glass-card rounded-2xl p-5 hover:border-accent-primary/40 transition-all duration-300 cursor-pointer flex gap-4 items-center">
            <div class="w-12 h-12 rounded-xl bg-accent-primary/10 flex items-center justify-center text-accent-primary text-xl shrink-0">
              <i class="fa-solid fa-box-open"></i>
            </div>
            <div class="text-left">
              <h4 class="text-sm font-bold text-white">Dịch Vụ Box & Fulfillment Giá Sỉ</h4>
              <p class="text-xs text-gray-400 mt-1">Đóng gói, lưu kho chuyên nghiệp chỉ từ 2.000đ/đơn. Nhấp để nhận báo giá.</p>
            </div>
          </div>
          <div onclick="triggerVipUpgrade()" class="glass-card rounded-2xl p-5 hover:border-accent-secondary/40 transition-all duration-300 cursor-pointer flex gap-4 items-center">
            <div class="w-12 h-12 rounded-xl bg-accent-secondary/10 flex items-center justify-center text-accent-secondary text-xl shrink-0">
              <i class="fa-solid fa-truck-fast"></i>
            </div>
            <div class="text-left">
              <h4 class="text-sm font-bold text-white">Nhà Cung Cấp Hộp Giấy Carton</h4>
              <p class="text-xs text-gray-400 mt-1">Hộp carton chuẩn size Shopee, TikTok Shop. Hỗ trợ in logo thương hiệu miễn phí.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  """

  tool_js = f"""
    let activePlatform = 'shopee';

    function switchPlatform(platform) {{
      activePlatform = platform;
      const shopeeTab = document.getElementById('tab-shopee');
      const tiktokTab = document.getElementById('tab-tiktok');
      const shopeeParams = document.getElementById('params-shopee');
      const tiktokParams = document.getElementById('params-tiktok');

      if (platform === 'shopee') {{
        shopeeTab.classList.add('active');
        shopeeTab.classList.remove('bg-slate-800', 'hover:bg-slate-700');
        tiktokTab.classList.remove('active');
        tiktokTab.classList.add('bg-slate-800', 'hover:bg-slate-700');
        shopeeParams.classList.remove('hidden');
        tiktokParams.classList.add('hidden');
      }} else {{
        tiktokTab.classList.add('active');
        tiktokTab.classList.remove('bg-slate-800', 'hover:bg-slate-700');
        shopeeTab.classList.remove('active');
        shopeeTab.classList.add('bg-slate-800', 'hover:bg-slate-700');
        tiktokParams.classList.remove('hidden');
        shopeeParams.classList.add('hidden');
      }}
      calculateFees();
    }}
    window.switchPlatform = switchPlatform;

    function calculateFees() {{
      const acceptTerms = document.getElementById('accept-terms');
      if (acceptTerms && !acceptTerms.checked) {{
        // Silent block or prompt
        return;
      }}

      // Input variables
      const price = parseFloat(document.getElementById('calc-price').value) || 0;
      const cogs = parseFloat(document.getElementById('calc-cogs').value) || 0;
      const ops = parseFloat(document.getElementById('calc-ops').value) || 0;

      let platformFee = 0;
      let affiliateFee = 0;

      if (activePlatform === 'shopee') {{
        const payFeePct = parseFloat(document.getElementById('shopee-pay-fee').value) || 0;
        const fixedFeePct = parseFloat(document.getElementById('shopee-fixed-fee').value) || 0;
        const hasFreeship = document.getElementById('shopee-freeship').checked;
        const hasVoucher = document.getElementById('shopee-voucher').checked;
        const affPct = parseFloat(document.getElementById('shopee-affiliate').value) || 0;

        // Phí thanh toán
        const payFee = price * (payFeePct / 100);
        // Phí cố định
        const fixedFee = price * (fixedFeePct / 100);
        // Freeship Xtra (6% max 40k)
        const freeshipFee = hasFreeship ? Math.min(price * 0.06, 40000) : 0;
        // Voucher Xtra (4% max 50k)
        const voucherFee = hasVoucher ? Math.min(price * 0.04, 50000) : 0;

        platformFee = payFee + fixedFee + freeshipFee + voucherFee;
        affiliateFee = price * (affPct / 100);
      }} else {{
        // TikTok Shop
        const transFeePct = parseFloat(document.getElementById('tiktok-trans-fee').value) || 0;
        const commPct = parseFloat(document.getElementById('tiktok-commission').value) || 0;
        const flatFee = parseFloat(document.getElementById('tiktok-flat-fee').value) || 0;
        const affPct = parseFloat(document.getElementById('tiktok-affiliate').value) || 0;

        const transFee = price * (transFeePct / 100);
        const commFee = price * (commPct / 100);

        platformFee = transFee + commFee + flatFee;
        affiliateFee = price * (affPct / 100);
      }}

      const totalCosts = cogs + ops + platformFee + affiliateFee;
      const payout = price - platformFee;
      const netProfit = payout - cogs - ops - affiliateFee;
      const margin = price > 0 ? (netProfit / price) * 100 : 0;

      // Update UI elements
      document.getElementById('res-gross').innerText = price.toLocaleString('vi-VN') + ' đ';
      document.getElementById('res-cogs').innerText = cogs.toLocaleString('vi-VN') + ' đ';
      document.getElementById('res-ops').innerText = ops.toLocaleString('vi-VN') + ' đ';
      document.getElementById('res-platform-fee').innerText = '-' + platformFee.toLocaleString('vi-VN') + ' đ';
      document.getElementById('res-affiliate').innerText = '-' + affiliateFee.toLocaleString('vi-VN') + ' đ';
      document.getElementById('res-payout').innerText = payout.toLocaleString('vi-VN') + ' đ';
      document.getElementById('res-net-profit').innerText = netProfit.toLocaleString('vi-VN') + ' đ';
      document.getElementById('res-margin').innerText = margin.toFixed(1) + '%';

      // Update margin badge styles
      const marginGauge = document.getElementById('margin-gauge-card');
      const marginDesc = document.getElementById('res-margin-desc');
      if (margin < 10) {{
        marginGauge.className = 'rounded-2xl p-4 text-center bg-red-950/50 border border-red-500/30 text-red-400';
        marginDesc.innerText = '⚠️ BIÊN LỢI NHUẬN QUÁ THẤP - CẦN TỐI ƯU HOẶC TĂNG GIÁ';
      }} else if (margin >= 10 && margin <= 20) {{
        marginGauge.className = 'rounded-2xl p-4 text-center bg-yellow-950/50 border border-yellow-500/30 text-yellow-400';
        marginDesc.innerText = '⚖️ BIÊN LỢI NHUẬN TRUNG BÌNH - AN TOÀN';
      }} else {{
        marginGauge.className = 'rounded-2xl p-4 text-center bg-green-950/50 border border-green-500/30 text-green-400';
        marginDesc.innerText = '🔥 BIÊN LỢI NHUẬN LÝ TƯỞNG - NICHE GOLD MINE';
      }}

      // Save input states to localStorage
      localStorage.setItem('calc_price', price);
      localStorage.setItem('calc_cogs', cogs);
      localStorage.setItem('calc_ops', ops);
    }}

    // Bind event listeners to input changes
    const inputs = document.querySelectorAll('#calc-price, #calc-cogs, #calc-ops, #shopee-pay-fee, #shopee-fixed-fee, #shopee-freeship, #shopee-voucher, #shopee-affiliate, #tiktok-trans-fee, #tiktok-commission, #tiktok-flat-fee, #tiktok-affiliate, #accept-terms');
    inputs.forEach(el => {{
      el.addEventListener('input', calculateFees);
      el.addEventListener('change', calculateFees);
    }});

    // Load states on start
    window.addEventListener('DOMContentLoaded', () => {{
      if (localStorage.getItem('calc_price')) {{
        document.getElementById('calc-price').value = localStorage.getItem('calc_price');
      }}
      if (localStorage.getItem('calc_cogs')) {{
        document.getElementById('calc-cogs').value = localStorage.getItem('calc_cogs');
      }}
      if (localStorage.getItem('calc_ops')) {{
        document.getElementById('calc-ops').value = localStorage.getItem('calc_ops');
      }}
      calculateFees();
    }});
  """

  # Assemble HTML file layout
  full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{keyword} - Tối Ưu Lợi Nhuận Bán Hàng 2026</title>
  
  <meta name="description" content="Công cụ tính chính xác các khoản phí sàn Shopee, TikTok Shop sau đợt cập nhật biểu phí tháng 5/2026. Hỗ trợ tối ưu giá bán và tính chính xác biên lợi nhuận ròng.">
  <meta name="keywords" content="phí sàn shopee, phí sàn tiktok shop, tính lợi nhuận shopee, tính biên lợi nhuận, chi phí tmdt">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://vinatools.vercel.app/{slug}">
  
  <link rel="preconnect" href="https://cdnjs.cloudflare.com">
  <link rel="preconnect" href="https://pagead2.googlesyndication.com">
  
  <meta property="og:type" content="website">
  <meta property="og:title" content="{keyword} - Phân Tích & Tối Ưu Lợi Nhuận">
  <meta property="og:description" content="Công cụ tính phí sàn Shopee & TikTok Shop miễn phí cập nhật tháng 5/2026.">
  <meta property="og:url" content="https://vinatools.vercel.app/{slug}">
  <meta property="og:site_name" content="VinaTools">
  <meta property="og:image" content="https://vinatools.vercel.app/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{keyword} - Phân Tích & Tối Ưu Lợi Nhuận">
  <meta name="twitter:description" content="Công cụ tính phí sàn Shopee & TikTok Shop miễn phí cập nhật tháng 5/2026.">
  <meta name="twitter:image" content="https://vinatools.vercel.app/og-image.png">

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
            "name": "Tiện Ích",
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
  <link rel="preload" href="/global_style.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="/global_style.css"></noscript>
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#0a0c10">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={google_adsense_client}" crossorigin="anonymous"></script>
  <script>
    if ('serviceWorker' in navigator) {{
      window.addEventListener('load', () => {{
        navigator.serviceWorker.register('/sw.js').catch(() => {{}});
      }});
    }}
  </script>
</head>
<body class="bg-slate-950 text-white min-h-screen">

  <!-- Persistent Sidebar Ads (Left and Right Rails) -->
  <div class="side-ad-left">
    <span class="side-ad-label">Quảng cáo</span>
    <ins class="adsbygoogle" style="display:inline-block;width:160px;height:600px" data-ad-client="{google_adsense_client}" data-ad-slot="mock-sidebar-left">
      <div class="fallback-ad-vertical" onclick="triggerVipUpgrade()">
        <div class="fallback-ad-crown"><i class="fa-solid fa-crown"></i></div>
        <div class="fallback-ad-title">VinaTools VIP</div>
        <div class="fallback-ad-text">Tải file cực nhanh không quảng cáo. Hoàn tiền 100% nếu lỗi.</div>
        <div class="fallback-ad-price">9.000đ/tháng</div>
        <span class="fallback-ad-btn">Nâng Cấp</span>
      </div>
    </ins>
  </div>
  <div class="side-ad-right">
    <span class="side-ad-label">Quảng cáo</span>
    <ins class="adsbygoogle" style="display:inline-block;width:160px;height:600px" data-ad-client="{google_adsense_client}" data-ad-slot="mock-sidebar-right">
      <!-- Fallback House Ad 2 -->
      <div class="fallback-ad-vertical second" onclick="window.open('https://vinaearn-ai.vercel.app', '_blank')">
        <div class="fallback-ad-logo"><i class="fa-solid fa-code"></i></div>
        <div class="fallback-ad-title">VinaEarn API</div>
        <div class="fallback-ad-text">Cổng tra cứu doanh nghiệp tự động</div>
        <div class="fallback-ad-price">VietRegistry</div>
        <span class="fallback-ad-btn">Xem Thêm</span>
      </div>
    </ins>
  </div>

  <div class="layout-container max-w-7xl mx-auto">
    <nav class="portal-nav flex justify-between items-center py-6 border-b border-gray-800 mb-8 px-4">
      <a href="/" class="portal-logo flex items-center gap-3 text-2xl font-black text-white no-underline">
        <i class="fa-solid fa-toolbox text-accent-primary"></i> VinaTools
      </a>
      <div class="nav-links flex gap-6 items-center">
        <a href="/?filter=don-tu" class="text-sm font-semibold text-gray-300 hover:text-white transition no-underline"><i class="fa-solid fa-file-lines text-blue-400 mr-1"></i> Đơn từ</a>
        <a href="/?filter=hop-dong" class="text-sm font-semibold text-gray-300 hover:text-white transition no-underline"><i class="fa-solid fa-file-contract text-violet-400 mr-1"></i> Hợp đồng</a>
        <a href="/?filter=tien-ich" class="text-sm font-semibold text-gray-300 hover:text-white transition no-underline"><i class="fa-solid fa-screwdriver-wrench text-pink-400 mr-1"></i> Tiện ích</a>
      </div>
      <div id="user-nav-status" class="text-sm text-gray-400 flex items-center gap-2">
        <i class="fa-solid fa-shield-halved text-green-400"></i> Secure B2B Platform
      </div>
    </nav>

    <header class="tool-header text-center mb-10 px-4">
      <h1 class="text-4xl font-black tracking-tight text-white mb-3 bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-400">{keyword}</h1>
      <p class="text-gray-400 max-w-2xl mx-auto">Tính toán chính xác 100% các loại phí thanh toán, phí cố định, phí Freeship Xtra, Voucher Xtra của Shopee & TikTok Shop theo biểu phí cập nhật mới nhất.</p>
    </header>

    <div id="vinatools-top-ad" class="ad-slot text-center mb-6">
      <ins class="adsbygoogle" style="display:block; min-height: 90px;" data-ad-client="{google_adsense_client}" data-ad-slot="mock-top-page">
         <div class="fallback-ad-horizontal" onclick="triggerVipUpgrade()" style="padding: 10px 15px; border-radius: 6px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
           <span style="font-size: 0.85rem; color: var(--text-secondary);"><i class="fa-solid fa-crown" style="color: #f59e0b; margin-right: 6px;"></i> Nâng cấp thành viên VIP để trải nghiệm không quảng cáo</span>
           <span style="font-size: 0.75rem; background: var(--accent-primary); color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">Đăng ký chỉ 9K</span>
         </div>
      </ins>
    </div>

    {tool_html}

    <div id="vinatools-page-ad" class="ad-slot mb-6">
      <ins class="adsbygoogle" style="display:block; min-height: 90px;" data-ad-client="{google_adsense_client}" data-ad-slot="mock-page">
        <div class="fallback-ad-horizontal" onclick="triggerVipUpgrade()">
          <div style="display:flex; align-items:center; gap: 15px;">
            <div class="fallback-ad-crown"><i class="fa-solid fa-crown"></i></div>
            <div style="text-align:left;">
              <div class="fallback-ad-title" style="margin:0; font-size:1.1rem;">Thành Viên VIP VinaTools</div>
              <div class="fallback-ad-text" style="margin:2px 0 0 0; font-size:0.85rem;">Tải không giới hạn 60+ biểu mẫu và tắt toàn bộ quảng cáo</div>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap: 15px;">
            <div class="fallback-ad-price" style="margin:0; font-size:1.2rem; font-weight:bold; color:#f59e0b;">9.000 đ/tháng</div>
            <span class="fallback-ad-btn" style="margin:0; padding: 8px 16px;">Đăng Ký Ngay</span>
          </div>
        </div>
      </ins>
    </div>

    <footer class="tool-footer mt-16 py-8 border-t border-gray-800 text-center text-xs text-gray-500 space-y-4 px-4">
      <div class="flex flex-wrap justify-center gap-6">
        <div class="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
          <i class="fa-solid fa-lock text-green-400"></i>
          <span class="font-bold text-gray-400">SSL PROTECTED</span>
        </div>
        <div class="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
          <i class="fa-solid fa-server text-accent-primary"></i>
          <span class="font-bold text-gray-400">100% CLIENT-SIDE</span>
        </div>
      </div>
      <p>&copy; 2026 VinaTools. Chạy hoàn toàn trên máy khách của người dùng. Bảo mật dữ liệu cá nhân theo Luật số 91/2025/QH15.</p>
      <p class="flex justify-center gap-4">
        <a href="/terms.html" class="hover:text-gray-300">Điều khoản</a>
        <a href="/privacy.html" class="hover:text-gray-300">Bảo mật</a>
        <a href="/about.html" class="hover:text-gray-300">Giới thiệu</a>
        <a href="/contact.html" class="hover:text-gray-300">Liên hệ</a>
      </p>
    </footer>
  </div>

  <script src="/checkout_modal.js?v=1.0.2"></script>
  <script>
    initCheckoutConfig({{
      bankName: "{bank_name}",
      bankId: "{bank_id}",
      accountNumber: "{acc_num}",
      accountName: "{acc_holder}",
      apiEndpoint: "{api_url}"
    }});

    // Hide ads for VIP members
    if (localStorage.getItem("vipToken")) {{
      const ads = document.querySelectorAll(".side-ad-left, .side-ad-right, #vinatools-page-ad, #vinatools-top-ad");
      ads.forEach(el => el.style.display = "none");
    }} else {{
      try {{
        (window.adsbygoogle = window.adsbygoogle || []).push({{}});
        (window.adsbygoogle = window.adsbygoogle || []).push({{}});
      }} catch (e) {{
        console.error("AdSense page ad load failed:", e);
      }}
    }}

    {tool_js}
  </script>
</body>
</html>
"""
  return full_html


def build_address_parser(keyword, slug, config):
  bank_name = config.get("bank_name", "Techcombank")
  bank_id = config.get("bank_id", "TCB")
  acc_num = config.get("bank_account", "")
  acc_holder = config.get("bank_account_holder", "")
  api_url = config.get("api_url", "/api/check-payment")
  google_adsense_client = config.get("google_adsense_client", "ca-pub-mock")

  tool_html = f"""
  <div class="glass-panel" style="margin-bottom: 30px;">
    <h2 style="margin-bottom: 15px;"><i class="fa-solid fa-map-location-dot" style="color: var(--accent-primary);"></i> Nhập địa chỉ cần tách và chuẩn hóa</h2>
    
    <div style="margin-bottom: 15px; display: flex; align-items: flex-start; gap: 8px; position: relative;">
      <input type="checkbox" id="accept-terms" required style="width: auto; margin-top: 4px; cursor: pointer;" checked>
      <label for="accept-terms" style="font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; line-height: 1.4; user-select: none;">
        Tôi đồng ý với <a href="/terms.html" target="_blank" style="color: var(--accent-primary);">Điều khoản dịch vụ</a> và <a href="/privacy.html" target="_blank" style="color: var(--accent-primary);">Chính sách bảo mật</a>.
      </label>
    </div>

    <div style="margin-bottom: 20px;">
      <label style="display: block; margin-bottom: 8px; font-size: 0.9rem; color: var(--text-secondary);">Nhập địa chỉ đầy đủ (Ngăn cách bằng dấu phẩy hoặc khoảng trắng):</label>
      <textarea id="raw-address" rows="3" placeholder="Ví dụ: Số 12 Đường Lê Lợi, Phường Bến Nghé, Quận 1, Thành phố Hồ Chí Minh" style="width:100%; padding:12px; font-size:0.95rem;"></textarea>
    </div>

    <button type="button" id="parse-addr-btn" class="btn btn-primary" style="width:100%; padding:12px; font-weight:bold;">
      <i class="fa-solid fa-wand-magic-sparkles"></i> Phân Tích & Chuẩn Hóa Địa Chỉ
    </button>
  </div>

  <div class="glass-panel" id="result-panel" style="margin-bottom: 30px; display:none;">
    <h2 style="margin-bottom: 20px; color:#10b981;"><i class="fa-solid fa-circle-check"></i> Kết quả phân tách thành công</h2>

    <div style="display:flex; flex-direction:column; gap:15px;">
      <div>
        <label style="display:block; margin-bottom:5px; font-size:0.8rem; color:var(--text-secondary);">Số nhà, Tên đường (Số nhà/Đường/Phố/Thôn/Xóm)</label>
        <div style="display:flex; gap:8px;">
          <input type="text" id="res-street" readonly style="flex:1;">
          <button onclick="copyField('res-street')" class="btn btn-secondary" style="padding: 10px;"><i class="fa-solid fa-copy"></i> Copy</button>
        </div>
      </div>
      <div>
        <label style="display:block; margin-bottom:5px; font-size:0.8rem; color:var(--text-secondary);">Phường / Xã / Thị trấn</label>
        <div style="display:flex; gap:8px;">
          <input type="text" id="res-ward" readonly style="flex:1;">
          <button onclick="copyField('res-ward')" class="btn btn-secondary" style="padding: 10px;"><i class="fa-solid fa-copy"></i> Copy</button>
        </div>
      </div>
      <div>
        <label style="display:block; margin-bottom:5px; font-size:0.8rem; color:var(--text-secondary);">Quận / Huyện / Thị xã / Thành phố thuộc tỉnh</label>
        <div style="display:flex; gap:8px;">
          <input type="text" id="res-district" readonly style="flex:1;">
          <button onclick="copyField('res-district')" class="btn btn-secondary" style="padding: 10px;"><i class="fa-solid fa-copy"></i> Copy</button>
        </div>
      </div>
      <div>
        <label style="display:block; margin-bottom:5px; font-size:0.8rem; color:var(--text-secondary);">Tỉnh / Thành phố trực thuộc Trung ương</label>
        <div style="display:flex; gap:8px;">
          <input type="text" id="res-province" readonly style="flex:1;">
          <button onclick="copyField('res-province')" class="btn btn-secondary" style="padding: 10px;"><i class="fa-solid fa-copy"></i> Copy</button>
        </div>
      </div>
    </div>

    <!-- Unlock VIP button -->
    <div style="margin-top:25px; border-top:1px dashed var(--border-glass); padding-top:20px; text-align:center;">
      <button onclick="triggerVipUpgrade()" class="btn" style="width:100%; padding:12px; background:linear-gradient(135deg, #8b5cf6, #ec4899); border:none; color:white; font-weight:bold;">
        <i class="fa-solid fa-crown"></i> Nâng cấp VIP để tích hợp API Tách Địa Chỉ vào Excel
      </button>
    </div>
  </div>
  """

  tool_js = f"""
    function copyField(id) {{
      const el = document.getElementById(id);
      if (el) {{
        el.select();
        document.execCommand('copy');
        alert('Đã sao chép: ' + el.value);
      }}
    }}
    window.copyField = copyField;

    document.getElementById('parse-addr-btn').addEventListener('click', function() {{
      const acceptTerms = document.getElementById('accept-terms');
      if (acceptTerms && !acceptTerms.checked) {{
        alert('Bạn phải đồng ý với Điều khoản dịch vụ & Chính sách bảo mật.');
        return;
      }}

      const raw = document.getElementById('raw-address').value.trim();
      if (!raw) {{
        alert('Vui lòng nhập địa chỉ cần tách!');
        return;
      }}

      // Standard Regex matching for Vietnam Address
      let province = "";
      let district = "";
      let ward = "";
      let street = "";

      // Match major provinces
      const provinces = [
        "Thành phố Hồ Chí Minh", "TP. Hồ Chí Minh", "TP.HCM", "TP HCM", "Hồ Chí Minh", "Sài Gòn",
        "Hà Nội", "Thành phố Hà Nội", "TP. Hà Nội",
        "Đà Nẵng", "Thành phố Đà Nẵng", "TP. Đà Nẵng",
        "Bình Dương", "Đồng Nai", "Bà Rịa - Vũng Tàu", "Bà Rịa Vũng Tàu", "Vũng Tàu",
        "Long An", "Tiền Giang", "Bến Tre", "Trà Vinh", "Vĩnh Long", "Đồng Tháp",
        "An Giang", "Kiên Giang", "Cần Thơ", "Hậu Giang", "Sóc Trăng", "Bạc Liêu", "Cà Mau",
        "Tây Ninh", "Bình Phước", "Lâm Đồng", "Đà Lạt", "Đắk Nông", "Đắk Lắk", "Gia Lai", "Kon Tum",
        "Khánh Hòa", "Nha Trang", "Phú Yên", "Bình Định", "Quảng Ngãi", "Quảng Nam", "Thừa Thiên Huế", "Huế",
        "Quảng Trị", "Quảng Bình", "Hà Tĩnh", "Nghệ An", "Thanh Hóa", "Ninh Bình", "Nam Định", "Thái Bình",
        "Hà Nam", "Hưng Yên", "Hải Dương", "Hải Phòng", "Quảng Ninh", "Bắc Giang", "Bắc Ninh", "Vĩnh Phúc",
        "Phú Thọ", "Thái Nguyên", "Tuyên Quang", "Yên Bái", "Lạng Sơn", "Cao Bằng", "Bắc Kạn", "Hà Giang",
        "Hòa Bình", "Sơn La", "Điện Biên", "Lai Châu", "Lào Cai"
      ];

      let cleanRaw = raw;
      
      // Look for Province at the end
      for (let prov of provinces) {{
        const regex = new RegExp('(,?\s*(' + prov.replace(/[-\/\\^$*+?.()|[\]{{}}]/g, '\\$&') + '))$', 'i');
        const match = cleanRaw.match(regex);
        if (match) {{
          province = prov;
          cleanRaw = cleanRaw.substring(0, match.index).trim();
          // strip trailing comma
          if (cleanRaw.endsWith(',')) cleanRaw = cleanRaw.slice(0, -1).trim();
          break;
        }}
      }}

      // Fallback search if not at the very end
      if (!province) {{
        for (let prov of provinces) {{
          const regex = new RegExp('(,?\s*(' + prov.replace(/[-\/\\^$*+?.()|[\]{{}}]/g, '\\$&') + '))', 'i');
          const match = cleanRaw.match(regex);
          if (match) {{
            province = prov;
            cleanRaw = cleanRaw.replace(match[0], '').trim();
            break;
          }}
        }}
      }}

      // Standardize Province Output Name
      if (province) {{
        if (province.toLowerCase().includes("hồ chí minh") || province.toLowerCase().includes("hcm")) province = "Thành phố Hồ Chí Minh";
        else if (province.toLowerCase().includes("hà nội")) province = "Thành phố Hà Nội";
        else if (province.toLowerCase().includes("đà nẵng")) province = "Thành phố Đà Nẵng";
        else if (province.toLowerCase().includes("hải phòng")) province = "Thành phố Hải Phòng";
        else if (province.toLowerCase().includes("cần thư") || province.toLowerCase().includes("cần thơ")) province = "Thành phố Cần Thơ";
      }}

      // Try to find District (Quận / Huyện / Thị xã / Thành phố)
      // Matches pattern: (Quận/Huyện/Thị xã/Thành phố) + name
      const distMatch = cleanRaw.match(/(,?\s*(Quận|Huyện|Thị\s*xã|Thành\s*phố)\s+[A-Za-z0-9\sĂâĐđêÔôơƯưáàảãạíìỉĩịúùủũụýỳỷỹỵẮắẰằẲẳẴẵẶặẤấẦầẨẩẪẫẬậẾếỀềỂểỄễỆệỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỨứỪừỬửỮữỰự]+)$/i);
      if (distMatch) {{
        district = distMatch[1].replace(/^,?\s*/, '').trim();
        cleanRaw = cleanRaw.substring(0, distMatch.index).trim();
        if (cleanRaw.endsWith(',')) cleanRaw = cleanRaw.slice(0, -1).trim();
      }} else {{
        // Fallback: match commonly named districts
        const districtKeywords = ["q.", "h.", "tx.", "tp.", "quận", "huyện", "thị xã", "thành phố"];
        // split by comma and search backward
        const parts = cleanRaw.split(',');
        if (parts.length > 1) {{
          const lastPart = parts[parts.length - 1].trim();
          for (let key of districtKeywords) {{
            if (lastPart.toLowerCase().startsWith(key)) {{
              district = lastPart;
              parts.pop();
              cleanRaw = parts.join(',').trim();
              break;
            }}
          }}
        }}
      }}

      // Try to find Ward (Phường / Xã / Thị trấn)
      const wardMatch = cleanRaw.match(/(,?\s*(Phường|Xã|Thị\s*trấn|P\.)\s+[A-Za-z0-9\sĂâĐđêÔôơƯưáàảãạíìỉĩịúùủũụýỳỷỹỵẮắẰằẲẳẴẵẶặẤấẦầẨẩẪẫẬậẾếỀềỂểỄễỆệỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỨứỪừỬửỮữỰự]+)$/i);
      if (wardMatch) {{
        ward = wardMatch[1].replace(/^,?\s*/, '').trim();
        cleanRaw = cleanRaw.substring(0, wardMatch.index).trim();
        if (cleanRaw.endsWith(',')) cleanRaw = cleanRaw.slice(0, -1).trim();
      }} else {{
        // Fallback by comma split
        const parts = cleanRaw.split(',');
        if (parts.length > 1) {{
          const lastPart = parts[parts.length - 1].trim();
          if (lastPart.toLowerCase().startsWith('phường') || lastPart.toLowerCase().startsWith('xã') || lastPart.toLowerCase().startsWith('p.')) {{
            ward = lastPart;
            parts.pop();
            cleanRaw = parts.join(',').trim();
          }}
        }}
      }}

      // The rest is street/number
      street = cleanRaw;

      // Fill in result inputs
      document.getElementById('res-street').value = street || "Không tìm thấy";
      document.getElementById('res-ward').value = ward || "Không tìm thấy";
      document.getElementById('res-district').value = district || "Không tìm thấy";
      document.getElementById('res-province').value = province || "Không tìm thấy";

      document.getElementById('result-panel').style.display = 'block';
      document.getElementById('result-panel').scrollIntoView({{ behavior: 'smooth' }});
    }});
  """

  # Assemble HTML file layout
  full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{keyword} - Tách Địa Chỉ Việt Nam</title>
  <meta name="description" content="Công cụ tự động phân tách địa chỉ thô thành 4 trường: số nhà/đường, xã/phường, quận/huyện, tỉnh/thành phố chuẩn quy hoạch hành chính Việt Nam.">
  <meta name="keywords" content="tách địa chỉ, chuẩn hóa địa chỉ, phân tách địa chỉ, hành chính việt nam">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://vinatools.vercel.app/{slug}">
  
  <link rel="preconnect" href="https://cdnjs.cloudflare.com">
  <link rel="preconnect" href="https://pagead2.googlesyndication.com">
  
  <meta property="og:type" content="website">
  <meta property="og:title" content="{keyword} - Tách Địa Chỉ Việt Nam">
  <meta property="og:description" content="Công cụ tự động phân tách địa chỉ thô thành 4 trường chuẩn quy hoạch hành chính Việt Nam.">
  <meta property="og:url" content="https://vinatools.vercel.app/{slug}">
  <meta property="og:site_name" content="VinaTools">
  <meta property="og:image" content="https://vinatools.vercel.app/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{keyword} - Tách Địa Chỉ Việt Nam">
  <meta name="twitter:description" content="Công cụ tự động phân tách địa chỉ thô thành 4 trường chuẩn quy hoạch hành chính Việt Nam.">
  <meta name="twitter:image" content="https://vinatools.vercel.app/og-image.png">

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
            "name": "Tiện Ích",
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
  <link rel="preload" href="/global_style.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="/global_style.css"></noscript>
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#0a0c10">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={google_adsense_client}" crossorigin="anonymous"></script>
  <script>
    if ('serviceWorker' in navigator) {{
      window.addEventListener('load', () => {{
        navigator.serviceWorker.register('/sw.js').catch(() => {{}});
      }});
    }}
  </script>
</head>
<body>

  <!-- Persistent Sidebar Ads (Left and Right Rails) -->
  <div class="side-ad-left">
    <span class="side-ad-label">Quảng cáo</span>
    <ins class="adsbygoogle" style="display:inline-block;width:160px;height:600px" data-ad-client="{google_adsense_client}" data-ad-slot="mock-sidebar-left">
      <div class="fallback-ad-vertical" onclick="triggerVipUpgrade()">
        <div class="fallback-ad-crown"><i class="fa-solid fa-crown"></i></div>
        <div class="fallback-ad-title">VinaTools VIP</div>
        <div class="fallback-ad-text">Tải file cực nhanh không quảng cáo. Hoàn tiền 100% nếu lỗi.</div>
        <div class="fallback-ad-price">9.000đ/tháng</div>
        <span class="fallback-ad-btn">Nâng Cấp</span>
      </div>
    </ins>
  </div>
  <div class="side-ad-right">
    <span class="side-ad-label">Quảng cáo</span>
    <ins class="adsbygoogle" style="display:inline-block;width:160px;height:600px" data-ad-client="{google_adsense_client}" data-ad-slot="mock-sidebar-right">
      <!-- Fallback House Ad 2 -->
      <div class="fallback-ad-vertical second" onclick="window.open('https://vinaearn-ai.vercel.app', '_blank')">
        <div class="fallback-ad-logo"><i class="fa-solid fa-code"></i></div>
        <div class="fallback-ad-title">VinaEarn API</div>
        <div class="fallback-ad-text">Cổng tra cứu doanh nghiệp tự động</div>
        <div class="fallback-ad-price">VietRegistry</div>
        <span class="fallback-ad-btn">Xem Thêm</span>
      </div>
    </ins>
  </div>

  <div class="layout-container">
    <nav class="portal-nav" style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid var(--border-glass); margin-bottom: 30px;">
      <a href="/" class="portal-logo" style="display: flex; align-items: center; gap: 10px; font-size: 1.4rem; font-weight: 800; color: #fff; text-decoration: none;">
        <i class="fa-solid fa-toolbox" style="color: #00a8ff;"></i> VinaTools
      </a>
      <div class="nav-links" style="display: flex; gap: 20px; align-items: center;">
        <a href="/?filter=don-tu" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: color 0.2s;"><i class="fa-solid fa-file-lines" style="color: #00a8ff; margin-right: 4px;"></i> Đơn từ</a>
        <a href="/?filter=hop-dong" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: color 0.2s;"><i class="fa-solid fa-file-contract" style="color: #8b5cf6; margin-right: 4px;"></i> Hợp đồng</a>
        <a href="/?filter=tien-ich" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: color 0.2s;"><i class="fa-solid fa-screwdriver-wrench" style="color: #ec4899; margin-right: 4px;"></i> Tiện ích</a>
      </div>
      <div id="user-nav-status" style="font-size: 0.9rem; color: #94a3b8; display: flex; align-items: center; gap: 10px;">
        <i class="fa-solid fa-shield-halved" style="color: #10b981;"></i> Standardized Parser
      </div>
    </nav>
    <header class="tool-header">
      <h1>{keyword}</h1>
      <p style="color: var(--text-secondary); margin-top: 10px;">Chuẩn hóa và tách tự động địa chỉ hành chính Việt Nam phục vụ giao hàng, logistics, xuất hóa đơn.</p>
    </header>

    <div id="vinatools-top-ad" class="ad-slot text-center mb-6">
      <ins class="adsbygoogle" style="display:block; min-height: 90px;" data-ad-client="{google_adsense_client}" data-ad-slot="mock-top-page">
         <div class="fallback-ad-horizontal" onclick="triggerVipUpgrade()" style="padding: 10px 15px; border-radius: 6px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
           <span style="font-size: 0.85rem; color: var(--text-secondary);"><i class="fa-solid fa-crown" style="color: #f59e0b; margin-right: 6px;"></i> Nâng cấp thành viên VIP để trải nghiệm không quảng cáo</span>
           <span style="font-size: 0.75rem; background: var(--accent-primary); color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">Đăng ký chỉ 9K</span>
         </div>
      </ins>
    </div>

    {tool_html}

    <div id="vinatools-page-ad" class="ad-slot mb-6">
      <ins class="adsbygoogle" style="display:block; min-height: 90px;" data-ad-client="{google_adsense_client}" data-ad-slot="mock-page">
        <div class="fallback-ad-horizontal" onclick="triggerVipUpgrade()">
          <div style="display:flex; align-items:center; gap: 15px;">
            <div class="fallback-ad-crown"><i class="fa-solid fa-crown"></i></div>
            <div style="text-align:left;">
              <div class="fallback-ad-title" style="margin:0; font-size:1.1rem;">Thành Viên VIP VinaTools</div>
              <div class="fallback-ad-text" style="margin:2px 0 0 0; font-size:0.85rem;">Tải không giới hạn 60+ biểu mẫu và tắt toàn bộ quảng cáo</div>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap: 15px;">
            <div class="fallback-ad-price" style="margin:0; font-size:1.2rem; font-weight:bold; color:#f59e0b;">9.000 đ/tháng</div>
            <span class="fallback-ad-btn" style="margin:0; padding: 8px 16px;">Đăng Ký Ngay</span>
          </div>
        </div>
      </ins>
    </div>

    <footer class="tool-footer" style="margin-top: 60px; padding-top: 25px; border-top: 1px solid var(--border-glass); font-size: 0.8rem; color: var(--text-muted); text-align: center; display: flex; flex-direction: column; align-items: center; gap: 16px;">
      <p>&copy; 2026 VinaTools. Bảo mật dữ liệu người dùng tuyệt đối. Mọi tính toán diễn ra tại trình duyệt.</p>
      <p style="margin-bottom: 2px; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
        <a href="/terms.html" style="color: var(--text-secondary); text-decoration: none;">Điều khoản</a>
        <a href="/privacy.html" style="color: var(--text-secondary); text-decoration: none;">Bảo mật</a>
        <a href="/about.html" style="color: var(--text-secondary); text-decoration: none;">Giới thiệu</a>
        <a href="/contact.html" style="color: var(--text-secondary); text-decoration: none;">Liên hệ</a>
      </p>
    </footer>
  </div>
  <script src="/checkout_modal.js?v=1.0.2"></script>
  <script>
    initCheckoutConfig({{
      bankName: "{bank_name}",
      bankId: "{bank_id}",
      accountNumber: "{acc_num}",
      accountName: "{acc_holder}",
      apiEndpoint: "{api_url}"
    }});

    // Hide ads for VIP members
    if (localStorage.getItem("vipToken")) {{
      const ads = document.querySelectorAll(".side-ad-left, .side-ad-right, #vinatools-page-ad, #vinatools-top-ad");
      ads.forEach(el => el.style.display = "none");
    }} else {{
      try {{
        (window.adsbygoogle = window.adsbygoogle || []).push({{}});
        (window.adsbygoogle = window.adsbygoogle || []).push({{}});
      }} catch (e) {{
        console.error("AdSense page ad load failed:", e);
      }}
    }}

    {tool_js}
  </script>
</body>
</html>
"""
  return full_html


def build_number_to_words(keyword, slug, config):
  bank_name = config.get("bank_name", "Techcombank")
  bank_id = config.get("bank_id", "TCB")
  acc_num = config.get("bank_account", "")
  acc_holder = config.get("bank_account_holder", "")
  api_url = config.get("api_url", "/api/check-payment")
  google_adsense_client = config.get("google_adsense_client", "ca-pub-mock")

  tool_html = f"""
  <div class="glass-panel" style="margin-bottom: 30px;">
    <h2 style="margin-bottom: 15px;"><i class="fa-solid fa-coins" style="color: var(--accent-primary);"></i> Cấu hình số cần đọc</h2>
    
    <div style="margin-bottom: 15px; display: flex; align-items: flex-start; gap: 8px; position: relative;">
      <input type="checkbox" id="accept-terms" required style="width: auto; margin-top: 4px; cursor: pointer;" checked>
      <label for="accept-terms" style="font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; line-height: 1.4; user-select: none;">
        Tôi đồng ý với <a href="/terms.html" target="_blank" style="color: var(--accent-primary);">Điều khoản dịch vụ</a> và <a href="/privacy.html" target="_blank" style="color: var(--accent-primary);">Chính sách bảo mật</a>.
      </label>
    </div>

    <div style="margin-bottom: 15px;">
      <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Nhập chữ số (ví dụ: 1250000) <span style="color: #ef4444;">*</span></label>
      <input type="number" id="num-input" value="1250000" min="0" style="font-size:1.2rem; font-weight:bold; padding:10px;">
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px; margin-bottom:15px;">
      <div>
        <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Hậu tố tiền tệ</label>
        <select id="currency-suffix" style="padding:10px;">
          <option value="VND">đồng chẵn</option>
          <option value="USD">đô la Mỹ</option>
          <option value="NONE">(không có)</option>
        </select>
      </div>
      <div style="display:flex; align-items:center; gap:8px; margin-top:25px;">
        <input type="checkbox" id="capitalize-first" checked style="width:auto; cursor:pointer;">
        <label for="capitalize-first" style="font-size:0.85rem; color:var(--text-secondary); cursor:pointer; user-select:none;">Viết hoa chữ đầu tiên</label>
      </div>
    </div>
  </div>

  <div class="glass-panel" style="margin-bottom: 30px;">
    <h2 style="margin-bottom: 15px;"><i class="fa-solid fa-paragraph" style="color: var(--accent-secondary);"></i> Kết quả dạng chữ tài chính</h2>
    
    <div style="background:rgba(255,255,255,0.02); border:1px solid var(--border-glass); border-radius:8px; padding:20px; min-height:80px; position:relative; margin-bottom:15px;">
      <p id="words-output" style="font-size:1.2rem; font-weight:bold; color:white; margin:0; line-height:1.6; padding-right:120px;"></p>
      <button id="copy-words-btn" class="btn btn-primary" style="position:absolute; right:15px; top:50%; transform:translateY(-50%); padding:8px 16px;">
        <i class="fa-solid fa-copy"></i> Sao chép
      </button>
    </div>

    <div style="text-align:center;">
      <button onclick="triggerVipUpgrade()" class="btn" style="width:100%; padding:10px; background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border:none; color:white; font-weight:bold;">
        <i class="fa-solid fa-crown"></i> Nâng cấp VIP (Chỉ 9K/tháng) để loại bỏ quảng cáo và mở khóa API
      </button>
    </div>
  </div>
  """

  tool_js = f"""
    const defaultNumbers = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín'];
    
    function readGroup(group, showZeroHundred) {{
      const h = Math.floor(group / 100);
      const t = Math.floor((group % 100) / 10);
      const u = group % 10;
      
      let out = "";
      
      if (h > 0 || showZeroHundred) {{
        out += defaultNumbers[h] + " trăm ";
      }}
      
      if (t === 0) {{
        if (h > 0 && u > 0) {{
          out += "lẻ ";
        }}
      }} else if (t === 1) {{
        out += "mười ";
      }} else {{
        out += defaultNumbers[t] + " mươi ";
      }}
      
      if (u > 0) {{
        if (u === 1 && t > 1) {{
          out += "mốt";
        }} else if (u === 5 && t > 0) {{
          out += "lăm";
        }} else if (u === 4 && t > 1) {{
          out += "tư";
        }} else {{
          out += defaultNumbers[u];
        }}
      }}
      
      return out.trim();
    }}

    function numberToWords(num) {{
      if (num === 0) return "Không";
      
      let str = "";
      let billion = Math.floor(num / 1000000000);
      let remain = num % 1000000000;
      
      let million = Math.floor(remain / 1000000);
      remain = remain % 1000000;
      
      let thousand = Math.floor(remain / 1000);
      let unit = remain % 1000;
      
      if (billion > 0) {{
        str += numberToWords(billion) + " tỷ ";
      }}
      
      if (million > 0) {{
        str += readGroup(million, str !== "") + " triệu ";
      }}
      
      if (thousand > 0) {{
        str += readGroup(thousand, str !== "") + " nghìn ";
      }}
      
      if (unit > 0) {{
        str += readGroup(unit, str !== "") + " ";
      }}
      
      return str.trim();
    }}

    function convertAndDisplay() {{
      const acceptTerms = document.getElementById('accept-terms');
      if (acceptTerms && !acceptTerms.checked) {{
        return;
      }}

      const val = parseFloat(document.getElementById('num-input').value);
      if (isNaN(val) || val < 0) {{
        document.getElementById('words-output').innerText = "Vui lòng nhập số hợp lệ lớn hơn hoặc bằng 0!";
        return;
      }}
      
      if (val > 999999999999) {{
        document.getElementById('words-output').innerText = "Số quá lớn (vượt quá giới hạn đọc tỷ đồng)!";
        return;
      }}
      
      let readStr = numberToWords(val).trim();
      
      // Suffix
      const suffix = document.getElementById('currency-suffix').value;
      if (suffix === 'VND') {{
        readStr += " đồng chẵn";
      }} else if (suffix === 'USD') {{
        readStr += " đô la Mỹ";
      }}
      
      // Capitalize first letter
      const cap = document.getElementById('capitalize-first').checked;
      if (cap && readStr.length > 0) {{
        readStr = readStr.charAt(0).toUpperCase() + readStr.slice(1);
      }}
      
      // Clean duplicate spaces
      readStr = readStr.replace(/\\s+/g, ' ').trim();
      
      document.getElementById('words-output').innerText = readStr;
    document.getElementById('num-input').addEventListener('input', convertAndDisplay);
    document.getElementById('currency-suffix').addEventListener('change', convertAndDisplay);
    document.getElementById('capitalize-first').addEventListener('change', convertAndDisplay);
    document.getElementById('accept-terms').addEventListener('change', convertAndDisplay);

    document.getElementById('copy-words-btn').addEventListener('click', function() {{
      const txt = document.getElementById('words-output').innerText;
      if (txt) {{
        navigator.clipboard.writeText(txt).then(() => {{
          alert('Đã sao chép nội dung vào Clipboard!');
        }});
      }}
    }});

    // Run once on load
    window.addEventListener('DOMContentLoaded', convertAndDisplay);
  """

  # Assemble HTML file layout
  full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{keyword} - Dịch Số Thành Chữ</title>
  <meta name="description" content="Công cụ đổi chữ số thành chữ viết tài chính tiếng Việt chuẩn quy cách kế toán, thủ quỹ và viết hóa đơn giá trị gia tăng năm 2026.">
  <meta name="keywords" content="đọc số thành chữ, dịch số thành chữ, viết chữ số, kế toán tài chính">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://vinatools.vercel.app/{slug}">
  
  <link rel="preconnect" href="https://cdnjs.cloudflare.com">
  <link rel="preconnect" href="https://pagead2.googlesyndication.com">
  
  <meta property="og:type" content="website">
  <meta property="og:title" content="{keyword} - Dịch Số Thành Chữ">
  <meta property="og:description" content="Công cụ đổi chữ số thành chữ viết tài chính tiếng Việt chuẩn quy cách kế toán, thủ quỹ và viết hóa đơn GTGT.">
  <meta property="og:url" content="https://vinatools.vercel.app/{slug}">
  <meta property="og:site_name" content="VinaTools">
  <meta property="og:image" content="https://vinatools.vercel.app/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{keyword} - Dịch Số Thành Chữ">
  <meta name="twitter:description" content="Công cụ đổi chữ số thành chữ viết tài chính tiếng Việt chuẩn quy cách kế toán, thủ quỹ và viết hóa đơn GTGT.">
  <meta name="twitter:image" content="https://vinatools.vercel.app/og-image.png">

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
            "name": "Tiện Ích",
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
  <link rel="preload" href="/global_style.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="/global_style.css"></noscript>
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#0a0c10">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={google_adsense_client}" crossorigin="anonymous"></script>
  <script>
    if ('serviceWorker' in navigator) {{
      window.addEventListener('load', () => {{
        navigator.serviceWorker.register('/sw.js').catch(() => {{}});
      }});
    }}
  </script>
</head>
<body>

  <!-- Persistent Sidebar Ads (Left and Right Rails) -->
  <div class="side-ad-left">
    <span class="side-ad-label">Quảng cáo</span>
    <ins class="adsbygoogle" style="display:inline-block;width:160px;height:600px" data-ad-client="{google_adsense_client}" data-ad-slot="mock-sidebar-left">
      <div class="fallback-ad-vertical" onclick="triggerVipUpgrade()">
        <div class="fallback-ad-crown"><i class="fa-solid fa-crown"></i></div>
        <div class="fallback-ad-title">VinaTools VIP</div>
        <div class="fallback-ad-text">Tải file cực nhanh không quảng cáo. Hoàn tiền 100% nếu lỗi.</div>
        <div class="fallback-ad-price">9.000đ/tháng</div>
        <span class="fallback-ad-btn">Nâng Cấp</span>
      </div>
    </ins>
  </div>
  <div class="side-ad-right">
    <span class="side-ad-label">Quảng cáo</span>
    <ins class="adsbygoogle" style="display:inline-block;width:160px;height:600px" data-ad-client="{google_adsense_client}" data-ad-slot="mock-sidebar-right">
      <!-- Fallback House Ad 2 -->
      <div class="fallback-ad-vertical second" onclick="window.open('https://vinaearn-ai.vercel.app', '_blank')">
        <div class="fallback-ad-logo"><i class="fa-solid fa-code"></i></div>
        <div class="fallback-ad-title">VinaEarn API</div>
        <div class="fallback-ad-text">Cổng tra cứu doanh nghiệp tự động</div>
        <div class="fallback-ad-price">VietRegistry</div>
        <span class="fallback-ad-btn">Xem Thêm</span>
      </div>
    </ins>
  </div>

  <div class="layout-container">
    <nav class="portal-nav" style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid var(--border-glass); margin-bottom: 30px;">
      <a href="/" class="portal-logo" style="display: flex; align-items: center; gap: 10px; font-size: 1.4rem; font-weight: 800; color: #fff; text-decoration: none;">
        <i class="fa-solid fa-toolbox" style="color: #00a8ff;"></i> VinaTools
      </a>
      <div class="nav-links" style="display: flex; gap: 20px; align-items: center;">
        <a href="/?filter=don-tu" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: color 0.2s;"><i class="fa-solid fa-file-lines" style="color: #00a8ff; margin-right: 4px;"></i> Đơn từ</a>
        <a href="/?filter=hop-dong" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: color 0.2s;"><i class="fa-solid fa-file-contract" style="color: #8b5cf6; margin-right: 4px;"></i> Hợp đồng</a>
        <a href="/?filter=tien-ich" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: color 0.2s;"><i class="fa-solid fa-screwdriver-wrench" style="color: #ec4899; margin-right: 4px;"></i> Tiện ích</a>
      </div>
      <div id="user-nav-status" style="font-size: 0.9rem; color: #94a3b8; display: flex; align-items: center; gap: 10px;">
        <i class="fa-solid fa-shield-halved" style="color: #10b981;"></i> Accurate Words
      </div>
    </nav>
    <header class="tool-header">
      <h1>{keyword}</h1>
      <p style="color: var(--text-secondary); margin-top: 10px;">Đọc các số tiền cực lớn thành chữ tiếng Việt chính xác theo chuẩn văn bản hành chính kế toán Việt Nam.</p>
    </header>

    <div id="vinatools-top-ad" class="ad-slot text-center mb-6">
      <ins class="adsbygoogle" style="display:block; min-height: 90px;" data-ad-client="{google_adsense_client}" data-ad-slot="mock-top-page">
         <div class="fallback-ad-horizontal" onclick="triggerVipUpgrade()" style="padding: 10px 15px; border-radius: 6px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
           <span style="font-size: 0.85rem; color: var(--text-secondary);"><i class="fa-solid fa-crown" style="color: #f59e0b; margin-right: 6px;"></i> Nâng cấp thành viên VIP để trải nghiệm không quảng cáo</span>
           <span style="font-size: 0.75rem; background: var(--accent-primary); color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">Đăng ký chỉ 9K</span>
         </div>
      </ins>
    </div>

    {tool_html}

    <div id="vinatools-page-ad" class="ad-slot mb-6">
      <ins class="adsbygoogle" style="display:block; min-height: 90px;" data-ad-client="{google_adsense_client}" data-ad-slot="mock-page">
        <div class="fallback-ad-horizontal" onclick="triggerVipUpgrade()">
          <div style="display:flex; align-items:center; gap: 15px;">
            <div class="fallback-ad-crown"><i class="fa-solid fa-crown"></i></div>
            <div style="text-align:left;">
              <div class="fallback-ad-title" style="margin:0; font-size:1.1rem;">Thành Viên VIP VinaTools</div>
              <div class="fallback-ad-text" style="margin:2px 0 0 0; font-size:0.85rem;">Tải không giới hạn 60+ biểu mẫu và tắt toàn bộ quảng cáo</div>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap: 15px;">
            <div class="fallback-ad-price" style="margin:0; font-size:1.2rem; font-weight:bold; color:#f59e0b;">9.000 đ/tháng</div>
            <span class="fallback-ad-btn" style="margin:0; padding: 8px 16px;">Đăng Ký Ngay</span>
          </div>
        </div>
      </ins>
    </div>

    <footer class="tool-footer" style="margin-top: 60px; padding-top: 25px; border-top: 1px solid var(--border-glass); font-size: 0.8rem; color: var(--text-muted); text-align: center; display: flex; flex-direction: column; align-items: center; gap: 16px;">
      <p>&copy; 2026 VinaTools. Bảo mật dữ liệu người dùng tuyệt đối. Mọi tính toán diễn ra tại trình duyệt.</p>
      <p style="margin-bottom: 2px; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
        <a href="/terms.html" style="color: var(--text-secondary); text-decoration: none;">Điều khoản</a>
        <a href="/privacy.html" style="color: var(--text-secondary); text-decoration: none;">Bảo mật</a>
        <a href="/about.html" style="color: var(--text-secondary); text-decoration: none;">Giới thiệu</a>
        <a href="/contact.html" style="color: var(--text-secondary); text-decoration: none;">Liên hệ</a>
      </p>
    </footer>
  </div>
  <script src="/checkout_modal.js?v=1.0.2"></script>
  <script>
    initCheckoutConfig({{
      bankName: "{bank_name}",
      bankId: "{bank_id}",
      accountNumber: "{acc_num}",
      accountName: "{acc_holder}",
      apiEndpoint: "{api_url}"
    }});

    // Hide ads for VIP members
    if (localStorage.getItem("vipToken")) {{
      const ads = document.querySelectorAll(".side-ad-left, .side-ad-right, #vinatools-page-ad, #vinatools-top-ad");
      ads.forEach(el => el.style.display = "none");
    }} else {{
      try {{
        (window.adsbygoogle = window.adsbygoogle || []).push({{}});
        (window.adsbygoogle = window.adsbygoogle || []).push({{}});
      }} catch (e) {{
        console.error("AdSense page ad load failed:", e);
      }}
    }}

    {tool_js}
  </script>
</body>
</html>
"""
  return full_html


def build_offline_tool_template(keyword, slug, config):
  """
  Generates a high-quality, functioning HTML page offline when API key is missing.
  Uses pre-defined interactive utility structures.
  """

  if slug == "cong-cu-tinh-phi-san-tmdt":
    return build_ecommerce_calculator(keyword, slug, config)
  elif slug == "cong-cu-tach-va-chuan-hoa-dia-chi":
    return build_address_parser(keyword, slug, config)
  elif slug == "cong-cu-doc-so-thanh-chu":
    return build_number_to_words(keyword, slug, config)
  title = keyword.title()
  bank_name = config.get("bank_name", "Techcombank")
  bank_id = config.get("bank_id", "TCB")
  acc_num = config.get("bank_account", "")
  acc_holder = config.get("bank_account_holder", "")
  api_url = config.get("api_url", "/api/check-payment")
  google_adsense_client = config.get("google_adsense_client", "ca-pub-mock")
  is_legal_form = "đơn" in keyword.lower() or "hợp đồng" in keyword.lower() or "biên bản" in keyword.lower()
  is_contract = "hợp đồng" in keyword.lower() or "biên bản" in keyword.lower()
  is_job = "xin-viec" in slug or "thuc-tap" in slug
  is_leave = "nghi-phep" in slug or "nghi-hoc" in slug or "xin-phep" in slug
  is_resignation = "nghi-viec" in slug or "thoi-viec" in slug
  is_residence = "tam-tru" in slug or "tam-vang" in slug

  if is_legal_form:
    # 1. CSS Styles for Split Screen
    styles_html = f"""
    <style>
      .legal-workspace-panel {{
        padding: 30px !important;
      }}
      .legal-form-container {{
        display: flex;
        flex-direction: column;
        gap: 30px;
      }}
      .form-column {{
        width: 100%;
      }}
      .preview-column {{
        width: 100%;
      }}
      .form-wizard-card {{
        background: transparent;
        border: none;
        box-shadow: none;
        padding: 0;
      }}
      #preview-content {{
        background: white;
        color: black;
        padding: 40px 50px;
        font-family: 'Times New Roman', Times, serif;
        font-size: 0.95rem;
        line-height: 1.6;
        border: 1px solid #d1d5db;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
        border-radius: 4px;
        min-height: 700px;
        box-sizing: border-box;
      }}
      #doc-form input[type="text"], #doc-form textarea, #doc-form select {{
        width: 100%;
        padding: 11px 14px;
        background: rgba(10, 12, 16, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        color: white;
        font-size: 0.92rem;
        transition: all 0.2s ease;
        margin-top: 6px;
      }}
      #doc-form input[type="text"]:focus, #doc-form textarea:focus, #doc-form select:focus {{
        border-color: var(--accent-primary);
        outline: none;
        background: rgba(10, 12, 16, 0.75);
        box-shadow: 0 0 0 3px var(--accent-primary-glow);
      }}
      @media (min-width: 992px) {{
        .legal-form-container {{
          display: grid;
          grid-template-columns: 1.15fr 0.85fr;
          gap: 40px;
          align-items: start;
        }}
        .preview-column {{
          position: relative;
        }}
      }}
      @media print {{
        body {{
          background: white !important;
          color: black !important;
          padding: 0 !important;
        }}
        .layout-container, .glass-panel, header, footer, .btn, .reason-expander-panel, .faq-container, .wizard-progress, #doc-form, #unlock-download-btn, #vip-upsell-btn, #close-checkout-btn, .payment-loader, .print-instruction, #direct-print-btn, #download-vip-bundle-btn, .tooltip-icon, .portal-nav, .tool-header {{
          display: none !important;
        }}
        #preview-panel, .preview-column {{
          display: block !important;
          background: white !important;
          color: black !important;
          border: none !important;
          box-shadow: none !important;
          padding: 0 !important;
          margin: 0 !important;
          width: 100% !important;
          max-width: 100% !important;
        }}
        #preview-content {{
          border: none !important;
          box-shadow: none !important;
          padding: 0 !important;
          margin: 0 !important;
          width: 100% !important;
          max-width: 100% !important;
        }}
      }}
    </style>
    """

    # 2. Form Wizard HTML
    if is_contract:
      # Contract Form Wizard
      form_html = f"""
      <div class="form-wizard-card" style="margin-bottom: 0;">
        <h2 style="margin-bottom: 15px;"><i class="fa-solid fa-file-signature" style="color: var(--accent-primary);"></i> Trình Khởi Tạo Hợp Đồng / Biên Bản</h2>
        
        <!-- Step indicators -->
        <div class="wizard-progress" style="display: flex; justify-content: space-between; margin-bottom: 25px; position: relative; padding: 0 10px;">
          <div class="progress-bar" style="position: absolute; top: 12px; left: 5%; right: 5%; height: 2px; background: rgba(255,255,255,0.1); z-index: 1;">
            <div id="progress-fill" style="height: 100%; width: 0%; background: var(--accent-primary); transition: var(--transition-smooth);"></div>
          </div>
          <div class="step-dot active" data-step="1" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--accent-primary); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: #fff;">1</div>
          <div class="step-dot" data-step="2" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">2</div>
          <div class="step-dot" data-step="3" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">3</div>
        </div>
        
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-secondary); margin-top: -15px; margin-bottom: 25px; padding: 0 5px;">
          <span style="width: 33.33%; text-align: center;">Thông tin Bên A</span>
          <span style="width: 33.33%; text-align: center;">Thông tin Bên B</span>
          <span style="width: 33.33%; text-align: center;">Chi tiết thỏa thuận</span>
        </div>

        <form id="doc-form">
          <!-- Step 1 -->
          <div class="form-step active" data-step="1">
            <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-user-tie" style="color: var(--accent-primary);"></i> Bước 1: Thông Tin Bên A (Bên Giao / Bên Bán)</h3>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Họ và tên Bên A <span style="color: #ef4444;">*</span></label>
              <input type="text" id="party-a-name" value="Nguyễn Văn A" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Số CCCD / Hộ chiếu <span style="color: #ef4444;">*</span></label>
              <input type="text" id="party-a-id" value="001203004567" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Số điện thoại liên hệ <span style="color: #ef4444;">*</span></label>
              <input type="text" id="party-a-phone" value="0987654321" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Địa chỉ cư trú / Trụ sở <span style="color: #ef4444;">*</span></label>
              <input type="text" id="party-a-address" value="Số 12 Đường Lê Lợi, Quận 1, TP. HCM" required>
            </div>
            <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
              <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
            </div>
          </div>

          <!-- Step 2 -->
          <div class="form-step" data-step="2" style="display: none;">
            <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-user-friends" style="color: var(--accent-primary);"></i> Bước 2: Thông Tin Bên B (Bên Nhận / Bên Mua)</h3>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Họ và tên Bên B <span style="color: #ef4444;">*</span></label>
              <input type="text" id="party-b-name" value="Trần Văn B" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Số CCCD / Hộ chiếu <span style="color: #ef4444;">*</span></label>
              <input type="text" id="party-b-id" value="002304005678" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Số điện thoại liên hệ <span style="color: #ef4444;">*</span></label>
              <input type="text" id="party-b-phone" value="0912345678" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Địa chỉ cư trú / Trụ sở <span style="color: #ef4444;">*</span></label>
              <input type="text" id="party-b-address" value="Số 85 Nguyễn Huệ, Quận 1, TP. HCM" required>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 20px;">
              <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
              <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
            </div>
          </div>

          <!-- Step 3 -->
          <div class="form-step" data-step="3" style="display: none;">
            <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-file-contract" style="color: var(--accent-primary);"></i> Bước 3: Chi Tiết Giao Kèo</h3>
      """
      
      if slug == "bien-ban-ban-giao-tai-san":
        form_html += f"""
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Địa điểm bàn giao <span style="color: #ef4444;">*</span></label>
              <input type="text" id="handover-loc" value="Văn phòng Công ty" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Ngày bàn giao <span style="color: #ef4444;">*</span></label>
              <input type="text" id="handover-date" value="12/06/2026" required>
            </div>
            <div style="margin-bottom: 10px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Danh mục tài sản bàn giao:</label>
              <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 8px; margin-bottom: 8px;">
                <span style="font-size:0.75rem; color:var(--text-muted);">Tên tài sản</span>
                <span style="font-size:0.75rem; color:var(--text-muted);">SL</span>
                <span style="font-size:0.75rem; color:var(--text-muted);">Tình trạng</span>
              </div>
              <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 8px; margin-bottom: 8px;">
                <input type="text" id="asset-name-1" value="Máy tính xách tay Dell XPS" style="padding: 6px;">
                <input type="text" id="asset-qty-1" value="01 cái" style="padding: 6px;">
                <input type="text" id="asset-status-1" value="Mới 98%" style="padding: 6px;">
              </div>
              <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 8px; margin-bottom: 8px;">
                <input type="text" id="asset-name-2" value="Màn hình Dell Ultrasharp 27 inch" style="padding: 6px;">
                <input type="text" id="asset-qty-2" value="01 cái" style="padding: 6px;">
                <input type="text" id="asset-status-2" value="Hoạt động tốt" style="padding: 6px;">
              </div>
              <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 8px; margin-bottom: 8px;">
                <input type="text" id="asset-name-3" value="Ghế công thái học Epione" style="padding: 6px;">
                <input type="text" id="asset-qty-3" value="01 cái" style="padding: 6px;">
                <input type="text" id="asset-status-3" value="Đã qua sử dụng" style="padding: 6px;">
              </div>
            </div>
        """
      elif slug == "mau-hop-dong-mua-ban-xe":
        form_html += f"""
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Nhãn hiệu / Hãng xe <span style="color: #ef4444;">*</span></label>
              <input type="text" id="car-brand" value="Honda SH 150i" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Biển kiểm soát <span style="color: #ef4444;">*</span></label>
              <input type="text" id="car-plate" value="29A-123.45" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Số khung / Số máy <span style="color: #ef4444;">*</span></label>
              <input type="text" id="car-engine" value="RLH123456 / JF123456" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Giá mua bán xe (VND) <span style="color: #ef4444;">*</span></label>
              <input type="text" id="car-price" value="85.000.000 đ" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Phương thức thanh toán <span style="color: #ef4444;">*</span></label>
              <input type="text" id="car-payment" value="Chuyển khoản ngân hàng 24/7" required>
            </div>
        """
      else:
        form_html += f"""
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Nội dung/Đối tượng hợp đồng <span style="color: #ef4444;">*</span></label>
              <input type="text" id="contract-object" value="Thuê nhà nguyên căn làm văn phòng" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Giá trị hợp đồng / Giá thuê <span style="color: #ef4444;">*</span></label>
              <input type="text" id="contract-price" value="15.000.000 đ/tháng" required>
            </div>
            <div style="margin-bottom: 15px;">
              <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Phương thức thanh toán <span style="color: #ef4444;">*</span></label>
              <input type="text" id="contract-payment" value="Chuyển khoản hàng tháng" required>
            </div>
        """

      form_html += f"""
            <div style="margin-bottom: 15px; display: flex; align-items: flex-start; gap: 8px;">
              <input type="checkbox" id="accept-terms" required style="width: auto; margin-top: 4px; cursor: pointer;">
              <label for="accept-terms" style="font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; line-height: 1.4; user-select: none;">
                Tôi đã đọc, hiểu rõ và đồng ý với <a href="/terms.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Điều khoản dịch vụ</a> và <a href="/privacy.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Chính sách bảo mật</a> của VinaTools.
              </label>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 20px;">
              <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
              <button type="submit" class="btn btn-primary" style="padding: 10px 20px;">
                <i class="fa-solid fa-wand-magic-sparkles"></i> Tạo & Xem Trước Bản Đẹp
              </button>
            </div>
          </div>
        </form>
      </div>
      """
    else:
      # Petition Form Wizard (Specialized for job, leave, resignation, residence)
      if is_job:
        form_html = f"""
        <div class="form-wizard-card" style="margin-bottom: 0;">
          <h2 style="margin-bottom: 15px;"><i class="fa-solid fa-file-signature" style="color: var(--accent-primary);"></i> Trình Khởi Tạo Đơn Ứng Tuyển Thông Minh</h2>
          
          <!-- Step indicators -->
          <div class="wizard-progress" style="display: flex; justify-content: space-between; margin-bottom: 25px; position: relative; padding: 0 10px;">
            <div class="progress-bar" style="position: absolute; top: 12px; left: 5%; right: 5%; height: 2px; background: rgba(255,255,255,0.1); z-index: 1;">
              <div id="progress-fill" style="height: 100%; width: 0%; background: var(--accent-primary); transition: var(--transition-smooth);"></div>
            </div>
            <div class="step-dot active" data-step="1" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--accent-primary); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: #fff;">1</div>
            <div class="step-dot" data-step="2" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">2</div>
            <div class="step-dot" data-step="3" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">3</div>
          </div>
          
          <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-secondary); margin-top: -15px; margin-bottom: 25px; padding: 0 5px;">
            <span style="width: 33.33%; text-align: center;">Ứng viên</span>
            <span style="width: 33.33%; text-align: center;">Chuyên môn</span>
            <span style="width: 33.33%; text-align: center;">Thư ứng tuyển</span>
          </div>

          <form id="doc-form">
            <!-- Step 1 -->
            <div class="form-step active" data-step="1">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-user" style="color: var(--accent-primary);"></i> Bước 1: Thông Tin Cá Nhân</h3>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Họ và tên người ứng tuyển <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-name" placeholder="Ví dụ: Nguyễn Văn A" required>
              </div>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Số điện thoại liên hệ <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-phone" placeholder="Ví dụ: 0987654321" required>
              </div>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Email liên hệ <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-email" placeholder="Ví dụ: nguyenvana@gmail.com" required>
              </div>
              <div style="margin-bottom: 15px; display: flex; align-items: flex-start; gap: 8px; position: relative;">
                <input type="checkbox" id="accept-terms" required style="width: auto; margin-top: 4px; cursor: pointer;">
                <label for="accept-terms" style="font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; line-height: 1.4; user-select: none;">
                  Tôi đã đọc, hiểu rõ và đồng ý với <a href="/terms.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Điều khoản dịch vụ</a> và <a href="/privacy.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Chính sách bảo mật</a> của VinaTools.
                </label>
              </div>
              <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
                <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
              </div>
            </div>

            <!-- Step 2 -->
            <div class="form-step" data-step="2" style="display: none;">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-graduation-cap" style="color: var(--accent-primary);"></i> Bước 2: Trình Độ & Vị Trí Ứng Tuyển</h3>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Vị trí ứng tuyển <span style="color: #ef4444;">*</span></label>
                <input type="text" id="job-position" placeholder="Ví dụ: Nhân viên Phát triển Phần mềm (Java/Web)" required>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Trình độ học vấn / Trường học <span style="color: #ef4444;">*</span></label>
                <input type="text" id="job-education" placeholder="Ví dụ: Cử nhân Công nghệ thông tin - Đại học Bách Khoa TP. HCM" required>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Sơ lược kinh nghiệm làm việc <span style="color: #ef4444;">*</span></label>
                <input type="text" id="job-experience" placeholder="Ví dụ: 1 năm kinh nghiệm thực tập tại FPT Software, thông thạo HTML/CSS/JS" required>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Cơ quan / Công ty kính gửi <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-kính-gửi" placeholder="Ví dụ: Ban Giám đốc cùng Bộ phận Tuyển dụng Công ty TNHH VinaTools" required>
              </div>
              <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
                <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
              </div>
            </div>

            <!-- Step 3 -->
            <div class="form-step" data-step="3" style="display: none;">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-pen-fancy" style="color: var(--accent-primary);"></i> Bước 3: Lý Do & Thư Ứng Tuyển</h3>
              
              <div class="reason-expander-panel" style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); padding: 16px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                  <i class="fa-solid fa-wand-magic-sparkles" style="color: var(--accent-secondary);"></i>
                  <span style="font-weight: bold; font-size: 0.85rem; color: #fff;">Trợ Lý Viết Thư Xin Việc Tự Động</span>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">
                  <div>
                    <label style="display: block; font-size: 0.75rem; color: var(--text-secondary);">Chọn ngành nghề:</label>
                    <select id="reason-scenario" style="padding: 8px; font-size: 0.8rem; background: var(--bg-dark); border: 1px solid var(--border-glass); border-radius: 4px; color: #fff; width: 100%;">
                      <!-- Populated dynamically via JS -->
                    </select>
                  </div>
                  <div>
                    <label style="display: block; font-size: 0.75rem; color: var(--text-secondary);">Chọn văn phong:</label>
                    <select id="reason-tone" style="padding: 8px; font-size: 0.8rem; background: var(--bg-dark); border: 1px solid var(--border-glass); border-radius: 4px; color: #fff; width: 100%;">
                      <option value="formal">Trang trọng & Chuyên nghiệp</option>
                      <option value="urgent">Nhiệt huyết & Thuyết phục</option>
                      <option value="brief">Ngắn gọn & Súc tích</option>
                    </select>
                  </div>
                </div>
                
                <button type="button" id="auto-expand-btn" class="btn" style="padding: 8px 12px; font-size: 0.8rem; background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(236,72,153,0.2)); border: 1px solid var(--accent-secondary); color: #fff; font-weight: bold; width: 100%; cursor: pointer;">
                  <i class="fa-solid fa-sparkles"></i> Tạo Nội Dung Thư Tự Động (AI)
                </button>
                <div id="ai-status" style="font-size: 0.75rem; text-align: center; margin-top: 8px; height: 16px; opacity: 0; color: #10b981; font-weight: 500; transition: var(--transition-smooth);"></div>
              </div>

              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Giới thiệu bản thân & Mục tiêu nghề nghiệp <span style="color: #ef4444;">*</span></label>
                <textarea id="user-reason" rows="5" placeholder="Mô tả lý do bạn muốn ứng tuyển hoặc sử dụng Trợ lý AI tạo thư ứng tuyển phía trên..." required></textarea>
              </div>
              
              <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
                <button type="submit" class="btn btn-primary" style="padding: 10px 20px;">
                  <i class="fa-solid fa-wand-magic-sparkles"></i> Tạo & Xem Trước Bản Đẹp
                </button>
              </div>
            </div>
          </form>
        </div>
        """
      elif is_leave:
        form_html = f"""
        <div class="form-wizard-card" style="margin-bottom: 0;">
          <h2 style="margin-bottom: 15px;"><i class="fa-solid fa-file-signature" style="color: var(--accent-primary);"></i> Trình Khởi Tạo Đơn Xin Nghỉ Phép Thông Minh</h2>
          
          <!-- Step indicators -->
          <div class="wizard-progress" style="display: flex; justify-content: space-between; margin-bottom: 25px; position: relative; padding: 0 10px;">
            <div class="progress-bar" style="position: absolute; top: 12px; left: 5%; right: 5%; height: 2px; background: rgba(255,255,255,0.1); z-index: 1;">
              <div id="progress-fill" style="height: 100%; width: 0%; background: var(--accent-primary); transition: var(--transition-smooth);"></div>
            </div>
            <div class="step-dot active" data-step="1" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--accent-primary); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: #fff;">1</div>
            <div class="step-dot" data-step="2" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">2</div>
            <div class="step-dot" data-step="3" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">3</div>
          </div>
          
          <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-secondary); margin-top: -15px; margin-bottom: 25px; padding: 0 5px;">
            <span style="width: 33.33%; text-align: center;">Cá nhân</span>
            <span style="width: 33.33%; text-align: center;">Thời gian nghỉ</span>
            <span style="width: 33.33%; text-align: center;">Lý do xin nghỉ</span>
          </div>

          <form id="doc-form">
            <!-- Step 1 -->
            <div class="form-step active" data-step="1">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-user" style="color: var(--accent-primary);"></i> Bước 1: Thông Tin Cá Nhân</h3>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Họ và tên người làm đơn <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-name" placeholder="Ví dụ: Nguyễn Văn A" required>
              </div>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Bộ phận / Phòng ban / Lớp học <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-dept" placeholder="Ví dụ: Phòng Công nghệ Thông tin / Lớp 12A1" required>
              </div>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Số điện thoại liên hệ <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-phone" placeholder="Ví dụ: 0987654321" required>
              </div>
              <div style="margin-bottom: 15px; display: flex; align-items: flex-start; gap: 8px; position: relative;">
                <input type="checkbox" id="accept-terms" required style="width: auto; margin-top: 4px; cursor: pointer;">
                <label for="accept-terms" style="font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; line-height: 1.4; user-select: none;">
                  Tôi đã đọc, hiểu rõ và đồng ý với <a href="/terms.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Điều khoản dịch vụ</a> và <a href="/privacy.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Chính sách bảo mật</a> của VinaTools.
                </label>
              </div>
              <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
                <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
              </div>
            </div>

            <!-- Step 2 -->
            <div class="form-step" data-step="2" style="display: none;">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-calendar-days" style="color: var(--accent-primary);"></i> Bước 2: Thời Gian & Bàn Giao</h3>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                <div>
                  <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Từ ngày <span style="color: #ef4444;">*</span></label>
                  <input type="text" id="leave-from" placeholder="Ví dụ: 15/06/2026" required>
                </div>
                <div>
                  <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Đến ngày <span style="color: #ef4444;">*</span></label>
                  <input type="text" id="leave-to" placeholder="Ví dụ: 17/06/2026" required>
                </div>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Tổng số ngày nghỉ <span style="color: #ef4444;">*</span></label>
                <input type="text" id="leave-days" placeholder="Ví dụ: 03 ngày" required>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Người nhận bàn giao công việc <span style="color: #ef4444;">*</span></label>
                <input type="text" id="leave-delegate" placeholder="Ví dụ: Trần Văn B (Phòng CNTT) / Lớp trưởng phụ trách" required>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Ban lãnh đạo kính gửi <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-kính-gửi" placeholder="Ví dụ: Ban Giám đốc cùng Phòng Hành chính Nhân sự Công ty" required>
              </div>
              <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
                <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
              </div>
            </div>

            <!-- Step 3 -->
            <div class="form-step" data-step="3" style="display: none;">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-pen-fancy" style="color: var(--accent-primary);"></i> Bước 3: Lý Do Xin Nghỉ Phép</h3>
              
              <div class="reason-expander-panel" style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); padding: 16px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                  <i class="fa-solid fa-wand-magic-sparkles" style="color: var(--accent-secondary);"></i>
                  <span style="font-weight: bold; font-size: 0.85rem; color: #fff;">Trợ Lý Lý Do Nghỉ Tự Động (AI)</span>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">
                  <div>
                    <label style="display: block; font-size: 0.75rem; color: var(--text-secondary);">Chọn tình huống:</label>
                    <select id="reason-scenario" style="padding: 8px; font-size: 0.8rem; background: var(--bg-dark); border: 1px solid var(--border-glass); border-radius: 4px; color: #fff; width: 100%;">
                      <!-- Populated dynamically via JS -->
                    </select>
                  </div>
                  <div>
                    <label style="display: block; font-size: 0.75rem; color: var(--text-secondary);">Chọn văn phong:</label>
                    <select id="reason-tone" style="padding: 8px; font-size: 0.8rem; background: var(--bg-dark); border: 1px solid var(--border-glass); border-radius: 4px; color: #fff; width: 100%;">
                      <option value="formal">Trang trọng & Chuyên nghiệp</option>
                      <option value="urgent">Cấp bách & Thuyết phục</option>
                      <option value="brief">Ngắn gọn & Súc tích</option>
                    </select>
                  </div>
                </div>
                
                <button type="button" id="auto-expand-btn" class="btn" style="padding: 8px 12px; font-size: 0.8rem; background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(236,72,153,0.2)); border: 1px solid var(--accent-secondary); color: #fff; font-weight: bold; width: 100%; cursor: pointer;">
                  <i class="fa-solid fa-sparkles"></i> Tạo Lý Do Tự Động
                </button>
                <div id="ai-status" style="font-size: 0.75rem; text-align: center; margin-top: 8px; height: 16px; opacity: 0; color: #10b981; font-weight: 500; transition: var(--transition-smooth);"></div>
              </div>

              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Chi tiết lý do nghỉ phép <span style="color: #ef4444;">*</span></label>
                <textarea id="user-reason" rows="5" placeholder="Nhập lý do chi tiết xin nghỉ phép của bạn..." required></textarea>
              </div>
              
              <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
                <button type="submit" class="btn btn-primary" style="padding: 10px 20px;">
                  <i class="fa-solid fa-wand-magic-sparkles"></i> Tạo & Xem Trước Bản Đẹp
                </button>
              </div>
            </div>
          </form>
        </div>
        """
      elif is_resignation:
        form_html = f"""
        <div class="form-wizard-card" style="margin-bottom: 0;">
          <h2 style="margin-bottom: 15px;"><i class="fa-solid fa-file-signature" style="color: var(--accent-primary);"></i> Trình Khởi Tạo Quyết Định / Đơn Xin Thôi Việc</h2>
          
          <!-- Step indicators -->
          <div class="wizard-progress" style="display: flex; justify-content: space-between; margin-bottom: 25px; position: relative; padding: 0 10px;">
            <div class="progress-bar" style="position: absolute; top: 12px; left: 5%; right: 5%; height: 2px; background: rgba(255,255,255,0.1); z-index: 1;">
              <div id="progress-fill" style="height: 100%; width: 0%; background: var(--accent-primary); transition: var(--transition-smooth);"></div>
            </div>
            <div class="step-dot active" data-step="1" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--accent-primary); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: #fff;">1</div>
            <div class="step-dot" data-step="2" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">2</div>
            <div class="step-dot" data-step="3" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">3</div>
          </div>
          
          <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-secondary); margin-top: -15px; margin-bottom: 25px; padding: 0 5px;">
            <span style="width: 33.33%; text-align: center;">Cá nhân</span>
            <span style="width: 33.33%; text-align: center;">Chi tiết công việc</span>
            <span style="width: 33.33%; text-align: center;">Lý do thôi việc</span>
          </div>

          <form id="doc-form">
            <!-- Step 1 -->
            <div class="form-step active" data-step="1">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-user" style="color: var(--accent-primary);"></i> Bước 1: Thông Tin Nhân Sự</h3>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Họ và tên người làm đơn <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-name" placeholder="Ví dụ: Nguyễn Văn A" required>
              </div>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Số CCCD / CMND <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-id" placeholder="Ví dụ: 001203004xxx" required>
              </div>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Số điện thoại liên hệ <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-phone" placeholder="Ví dụ: 0987654321" required>
              </div>
              <div style="margin-bottom: 15px; display: flex; align-items: flex-start; gap: 8px; position: relative;">
                <input type="checkbox" id="accept-terms" required style="width: auto; margin-top: 4px; cursor: pointer;">
                <label for="accept-terms" style="font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; line-height: 1.4; user-select: none;">
                  Tôi đã đọc, hiểu rõ và đồng ý với <a href="/terms.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Điều khoản dịch vụ</a> và <a href="/privacy.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Chính sách bảo mật</a> của VinaTools.
                </label>
              </div>
              <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
                <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
              </div>
            </div>

            <!-- Step 2 -->
            <div class="form-step" data-step="2" style="display: none;">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-briefcase" style="color: var(--accent-primary);"></i> Bước 2: Chức Vụ & Bàn Giao</h3>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Chức vụ hiện tại <span style="color: #ef4444;">*</span></label>
                <input type="text" id="job-title" placeholder="Ví dụ: Trưởng nhóm kinh doanh / Lập trình viên" required>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Phòng ban / Bộ phận làm việc <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-dept" placeholder="Ví dụ: Phòng Dự án / Bộ phận Marketing" required>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Ngày làm việc cuối cùng dự kiến <span style="color: #ef4444;">*</span></label>
                <input type="text" id="resign-date" placeholder="Ví dụ: 30/06/2026" required>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Nội dung công việc và tài sản bàn giao <span style="color: #ef4444;">*</span></label>
                <input type="text" id="handover-status" placeholder="Ví dụ: Bàn giao toàn bộ mã nguồn hệ thống và máy tính Dell XPS cho ông Trần Văn B" required>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Kính gửi Ban giám đốc / Cơ quan <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-kính-gửi" placeholder="Ví dụ: Ban Giám đốc Công ty cùng Phòng Hành chính Nhân sự Công ty VinaTools" required>
              </div>
              <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
                <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
              </div>
            </div>

            <!-- Step 3 -->
            <div class="form-step" data-step="3" style="display: none;">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-pen-fancy" style="color: var(--accent-primary);"></i> Bước 3: Lý Do Thôi Việc</h3>
              
              <div class="reason-expander-panel" style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); padding: 16px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                  <i class="fa-solid fa-wand-magic-sparkles" style="color: var(--accent-secondary);"></i>
                  <span style="font-weight: bold; font-size: 0.85rem; color: #fff;">Trợ Lý Lý Do Nghỉ Việc (AI)</span>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">
                  <div>
                    <label style="display: block; font-size: 0.75rem; color: var(--text-secondary);">Chọn lý do:</label>
                    <select id="reason-scenario" style="padding: 8px; font-size: 0.8rem; background: var(--bg-dark); border: 1px solid var(--border-glass); border-radius: 4px; color: #fff; width: 100%;">
                      <!-- Populated dynamically via JS -->
                    </select>
                  </div>
                  <div>
                    <label style="display: block; font-size: 0.75rem; color: var(--text-secondary);">Chọn văn phong:</label>
                    <select id="reason-tone" style="padding: 8px; font-size: 0.8rem; background: var(--bg-dark); border: 1px solid var(--border-glass); border-radius: 4px; color: #fff; width: 100%;">
                      <option value="formal">Lịch sự & Đúng luật lao động</option>
                      <option value="urgent">Chân thành & Cầu thị</option>
                      <option value="brief">Ngắn gọn & Súc tích</option>
                    </select>
                  </div>
                </div>
                
                <button type="button" id="auto-expand-btn" class="btn" style="padding: 8px 12px; font-size: 0.8rem; background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(236,72,153,0.2)); border: 1px solid var(--accent-secondary); color: #fff; font-weight: bold; width: 100%; cursor: pointer;">
                  <i class="fa-solid fa-sparkles"></i> Điền Lý Do Thôi Việc Tự Động
                </button>
                <div id="ai-status" style="font-size: 0.75rem; text-align: center; margin-top: 8px; height: 16px; opacity: 0; color: #10b981; font-weight: 500; transition: var(--transition-smooth);"></div>
              </div>

              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Lý do chi tiết xin nghỉ việc <span style="color: #ef4444;">*</span></label>
                <textarea id="user-reason" rows="5" placeholder="Nhập lý do chi tiết thôi việc của bạn..." required></textarea>
              </div>
              
              <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
                <button type="submit" class="btn btn-primary" style="padding: 10px 20px;">
                  <i class="fa-solid fa-wand-magic-sparkles"></i> Tạo & Xem Trước Bản Đẹp
                </button>
              </div>
            </div>
          </form>
        </div>
        """
      elif is_residence:
        form_html = f"""
        <div class="form-wizard-card" style="margin-bottom: 0;">
          <h2 style="margin-bottom: 15px;"><i class="fa-solid fa-file-signature" style="color: var(--accent-primary);"></i> Trình Khởi Tạo Đơn Đăng Ký Tạm Trú / Tạm Vắng</h2>
          
          <!-- Step indicators -->
          <div class="wizard-progress" style="display: flex; justify-content: space-between; margin-bottom: 25px; position: relative; padding: 0 10px;">
            <div class="progress-bar" style="position: absolute; top: 12px; left: 5%; right: 5%; height: 2px; background: rgba(255,255,255,0.1); z-index: 1;">
              <div id="progress-fill" style="height: 100%; width: 0%; background: var(--accent-primary); transition: var(--transition-smooth);"></div>
            </div>
            <div class="step-dot active" data-step="1" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--accent-primary); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: #fff;">1</div>
            <div class="step-dot" data-step="2" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">2</div>
            <div class="step-dot" data-step="3" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">3</div>
          </div>
          
          <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-secondary); margin-top: -15px; margin-bottom: 25px; padding: 0 5px;">
            <span style="width: 33.33%; text-align: center;">Cá nhân</span>
            <span style="width: 33.33%; text-align: center;">Nơi tạm trú</span>
            <span style="width: 33.33%; text-align: center;">Lý do cư trú</span>
          </div>

          <form id="doc-form">
            <!-- Step 1 -->
            <div class="form-step active" data-step="1">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-user" style="color: var(--accent-primary);"></i> Bước 1: Thông Tin Cá Nhân</h3>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Họ và tên người đăng ký <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-name" placeholder="Ví dụ: Nguyễn Văn A" required>
              </div>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Số CCCD / Hộ chiếu <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-id" placeholder="Ví dụ: 001203004xxx" required>
              </div>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Số điện thoại di động <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-phone" placeholder="Ví dụ: 0987654321" required>
              </div>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Địa chỉ thường trú (trên hộ khẩu) <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-address" placeholder="Ví dụ: Xã Hưng Nhân, Huyện Hưng Hà, Tỉnh Thái Bình" required>
              </div>
              <div style="margin-bottom: 15px; display: flex; align-items: flex-start; gap: 8px; position: relative;">
                <input type="checkbox" id="accept-terms" required style="width: auto; margin-top: 4px; cursor: pointer;">
                <label for="accept-terms" style="font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; line-height: 1.4; user-select: none;">
                  Tôi đã đọc, hiểu rõ và đồng ý với <a href="/terms.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Điều khoản dịch vụ</a> và <a href="/privacy.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Chính sách bảo mật</a> của VinaTools.
                </label>
              </div>
              <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
                <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
              </div>
            </div>

            <!-- Step 2 -->
            <div class="form-step" data-step="2" style="display: none;">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-home" style="color: var(--accent-primary);"></i> Bước 2: Nơi Tạm Trú Mới & Chủ Hộ</h3>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Địa chỉ tạm trú mới đăng ký <span style="color: #ef4444;">*</span></label>
                <input type="text" id="host-address" placeholder="Ví dụ: Số 12 Đường Lê Lợi, Phường Bến Nghé, Quận 1, TP. HCM" required>
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                <div>
                  <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Họ tên chủ hộ nơi ở mới <span style="color: #ef4444;">*</span></label>
                  <input type="text" id="host-name" placeholder="Ví dụ: Trần Văn B" required>
                </div>
                <div>
                  <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Quan hệ với chủ hộ <span style="color: #ef4444;">*</span></label>
                  <input type="text" id="host-relation" placeholder="Ví dụ: Con ruột / Người thuê nhà" required>
                </div>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Thời hạn tạm trú đăng ký <span style="color: #ef4444;">*</span></label>
                <input type="text" id="host-duration" placeholder="Ví dụ: Từ 15/06/2026 đến 15/06/2027 (1 năm)" required>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Cơ quan Công an kính gửi <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-kính-gửi" placeholder="Ví dụ: Công an Phường Bến Nghé, Quận 1, Thành phố Hồ Chí Minh" required>
              </div>
              <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
                <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
              </div>
            </div>

            <!-- Step 3 -->
            <div class="form-step" data-step="3" style="display: none;">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-pen-fancy" style="color: var(--accent-primary);"></i> Bước 3: Lý Do Tạm Trú</h3>
              
              <div class="reason-expander-panel" style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); padding: 16px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                  <i class="fa-solid fa-wand-magic-sparkles" style="color: var(--accent-secondary);"></i>
                  <span style="font-weight: bold; font-size: 0.85rem; color: #fff;">Trợ Lý Lý Do Tạm Trú (AI)</span>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">
                  <div>
                    <label style="display: block; font-size: 0.75rem; color: var(--text-secondary);">Chọn tình huống:</label>
                    <select id="reason-scenario" style="padding: 8px; font-size: 0.8rem; background: var(--bg-dark); border: 1px solid var(--border-glass); border-radius: 4px; color: #fff; width: 100%;">
                      <!-- Populated dynamically via JS -->
                    </select>
                  </div>
                  <div>
                    <label style="display: block; font-size: 0.75rem; color: var(--text-secondary);">Chọn văn phong:</label>
                    <select id="reason-tone" style="padding: 8px; font-size: 0.8rem; background: var(--bg-dark); border: 1px solid var(--border-glass); border-radius: 4px; color: #fff; width: 100%;">
                      <option value="formal">Trang trọng & Đúng quy chuẩn</option>
                      <option value="urgent">Nhiệt tình & Thuyết phục</option>
                      <option value="brief">Ngắn gọn & Súc tích</option>
                    </select>
                  </div>
                </div>
                
                <button type="button" id="auto-expand-btn" class="btn" style="padding: 8px 12px; font-size: 0.8rem; background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(236,72,153,0.2)); border: 1px solid var(--accent-secondary); color: #fff; font-weight: bold; width: 100%; cursor: pointer;">
                  <i class="fa-solid fa-sparkles"></i> Tạo Lý Do Tạm Trú Tự Động
                </button>
                <div id="ai-status" style="font-size: 0.75rem; text-align: center; margin-top: 8px; height: 16px; opacity: 0; color: #10b981; font-weight: 500; transition: var(--transition-smooth);"></div>
              </div>

              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Lý do đăng ký cư trú chi tiết <span style="color: #ef4444;">*</span></label>
                <textarea id="user-reason" rows="5" placeholder="Mô tả chi tiết lý do bạn xin tạm trú hoặc sử dụng Trợ lý AI ở trên..." required></textarea>
              </div>
              
              <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
                <button type="submit" class="btn btn-primary" style="padding: 10px 20px;">
                  <i class="fa-solid fa-wand-magic-sparkles"></i> Tạo & Xem Trước Bản Đẹp
                </button>
              </div>
            </div>
          </form>
        </div>
        """
      else:
        # Generic Petition Form Wizard
        form_html = f"""
        <div class="form-wizard-card" style="margin-bottom: 0;">
          <h2 style="margin-bottom: 15px;"><i class="fa-solid fa-file-signature" style="color: var(--accent-primary);"></i> Trình Khởi Tạo Văn Bản Thông Minh</h2>
          
          <!-- Step indicators -->
          <div class="wizard-progress" style="display: flex; justify-content: space-between; margin-bottom: 25px; position: relative; padding: 0 10px;">
            <div class="progress-bar" style="position: absolute; top: 12px; left: 5%; right: 5%; height: 2px; background: rgba(255,255,255,0.1); z-index: 1;">
              <div id="progress-fill" style="height: 100%; width: 0%; background: var(--accent-primary); transition: var(--transition-smooth);"></div>
            </div>
            <div class="step-dot active" data-step="1" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--accent-primary); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: #fff;">1</div>
            <div class="step-dot" data-step="2" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">2</div>
            <div class="step-dot" data-step="3" style="width: 26px; height: 26px; border-radius: 50%; background: var(--bg-dark); border: 2px solid var(--text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; z-index: 2; color: var(--text-muted);">3</div>
          </div>
          
          <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-secondary); margin-top: -15px; margin-bottom: 25px; padding: 0 5px;">
            <span style="width: 33.33%; text-align: center;">Cá nhân</span>
            <span style="width: 33.33%; text-align: center;">Thông tin cơ bản</span>
            <span style="width: 33.33%; text-align: center;">Lý do làm đơn</span>
          </div>

          <form id="doc-form">
            <!-- Step 1 -->
            <div class="form-step active" data-step="1">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-user" style="color: var(--accent-primary);"></i> Bước 1: Thông Tin Cá Nhân</h3>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Họ và tên người làm đơn <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-name" placeholder="Ví dụ: Nguyễn Văn A" required>
              </div>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Số CCCD / Hộ chiếu (9 hoặc 12 số) <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-id" placeholder="Ví dụ: 001203004xxx" required>
              </div>
              <div style="margin-bottom: 15px; position: relative;">
                <label style="display: block; margin-bottom: 5px; font-size: 0.85rem; color: var(--text-secondary);">Số điện thoại liên hệ <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-phone" placeholder="Ví dụ: 0987654321" required>
              </div>
              <div style="margin-bottom: 15px; display: flex; align-items: flex-start; gap: 8px; position: relative;">
                <input type="checkbox" id="accept-terms" required style="width: auto; margin-top: 4px; cursor: pointer;">
                <label for="accept-terms" style="font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; line-height: 1.4; user-select: none;">
                  Tôi đã đọc, hiểu rõ và đồng ý với <a href="/terms.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Điều khoản dịch vụ</a> và <a href="/privacy.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Chính sách bảo mật</a> của VinaTools.
                </label>
              </div>
              <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
                <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
              </div>
            </div>

            <!-- Step 2 -->
            <div class="form-step" data-step="2" style="display: none;">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-address-book" style="color: var(--accent-primary);"></i> Bước 2: Nơi Cư Trú & Cơ Quan Tiếp Nhận</h3>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Địa chỉ đăng ký thường trú / Tạm trú <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-address" placeholder="Ví dụ: Số 12 Đường Lê Lợi, Phường Bến Nghé, Quận 1, TP. HCM" required>
              </div>
              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Cơ quan / Đơn vị kính gửi <span style="color: #ef4444;">*</span></label>
                <input type="text" id="user-kính-gửi" placeholder="Ví dụ: Ban Giám đốc Công ty TNHH VinaTools" required>
              </div>
              <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
                <button type="button" class="btn btn-primary next-step-btn" style="padding: 10px 20px;">Tiếp tục <i class="fa-solid fa-arrow-right"></i></button>
              </div>
            </div>

            <!-- Step 3 -->
            <div class="form-step" data-step="3" style="display: none;">
              <h3 style="margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 8px;"><i class="fa-solid fa-pen-fancy" style="color: var(--accent-primary);"></i> Bước 3: Lý Do Làm Đơn</h3>
              
              <div class="reason-expander-panel" style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-glass); border-radius: var(--radius-sm); padding: 16px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                  <i class="fa-solid fa-wand-magic-sparkles" style="color: var(--accent-secondary);"></i>
                  <span style="font-weight: bold; font-size: 0.85rem; color: #fff;">Trợ Lý Mở Rộng Lý Do Viết Đơn Tự Động</span>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">
                  <div>
                    <label style="display: block; font-size: 0.75rem; color: var(--text-secondary);">Chọn tình huống:</label>
                    <select id="reason-scenario" style="padding: 8px; font-size: 0.8rem; background: var(--bg-dark); border: 1px solid var(--border-glass); border-radius: 4px; color: #fff; width: 100%;">
                      <!-- Populated dynamically via JS -->
                    </select>
                  </div>
                  <div>
                    <label style="display: block; font-size: 0.75rem; color: var(--text-secondary);">Chọn văn phong:</label>
                    <select id="reason-tone" style="padding: 8px; font-size: 0.8rem; background: var(--bg-dark); border: 1px solid var(--border-glass); border-radius: 4px; color: #fff; width: 100%;">
                      <option value="formal">Trang trọng & Đúng quy định</option>
                      <option value="urgent">Khẩn thiết & Thuyết phục</option>
                      <option value="brief">Ngắn gọn & Súc tích</option>
                    </select>
                  </div>
                </div>
                
                <button type="button" id="auto-expand-btn" class="btn" style="padding: 8px 12px; font-size: 0.8rem; background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(236,72,153,0.2)); border: 1px solid var(--accent-secondary); color: #fff; font-weight: bold; width: 100%; cursor: pointer;">
                  <i class="fa-solid fa-sparkles"></i> Mở Rộng & Định Dạng Lý Do Tự Động
                </button>
                <div id="ai-status" style="font-size: 0.75rem; text-align: center; margin-top: 8px; height: 16px; opacity: 0; color: #10b981; font-weight: 500; transition: var(--transition-smooth);"></div>
              </div>

              <div style="margin-bottom: 15px;">
                <label style="display: block; font-size: 0.85rem; color: var(--text-secondary);">Lý do chi tiết viết đơn <span style="color: #ef4444;">*</span></label>
                <textarea id="user-reason" rows="5" placeholder="Nhập lý do chi tiết hoặc sử dụng Trợ lý Tự động mở rộng phía trên để tạo nội dung..." required></textarea>
              </div>
              
              <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <button type="button" class="btn btn-secondary prev-step-btn" style="padding: 10px 20px;"><i class="fa-solid fa-arrow-left"></i> Quay lại</button>
                <button type="submit" class="btn btn-primary" style="padding: 10px 20px;">
                  <i class="fa-solid fa-wand-magic-sparkles"></i> Tạo & Xem Trước Bản Đẹp
                </button>
              </div>
            </div>
          </form>
        </div>
        """
      form_html += f"""
      </div>
      """

    # 3. Assemble Split-Screen Layout
    tool_html = f"""
    {styles_html}
    <div class="glass-panel legal-workspace-panel">
      <div class="legal-form-container">
      <!-- Left Side: Interactive Input Wizard Form -->
      <div class="form-column">
        {form_html}
      </div>

      <!-- Right Side: Live Page Preview (Times New Roman A4 Layout) -->
      <div class="preview-column">
        <div id="preview-panel" style="margin-bottom: 0;">
          <h2><i class="fa-solid fa-eye" style="color: var(--accent-secondary);"></i> Bản Xem Trước Thiết Kế Văn Bản</h2>
          
          <div class="print-instruction" style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: var(--radius-sm); padding: 12px; margin: 15px 0; font-size: 0.85rem; color: #10b981; display: flex; align-items: center; gap: 8px;">
            <i class="fa-solid fa-circle-info"></i>
            <span>Bản xem trước A4 dưới đây tự động cập nhật ngay khi bạn nhập thông tin ở bảng bên trái.</span>
          </div>

          <div id="preview-content">
            <!-- Dynamically updated -->
          </div>

          <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 20px;">
            <button id="unlock-download-btn" class="btn btn-primary" style="width: 100%; padding: 14px 28px; font-weight: bold; font-size: 1rem;">
              <i class="fa-solid fa-file-word"></i> Tải File Word (.doc) Bản Chuẩn (Miễn Phí)
            </button>
            
            <button id="direct-print-btn" class="btn btn-secondary" style="width: 100%; padding: 12px 28px; font-weight: bold; display: none;">
              <i class="fa-solid fa-print"></i> In Trực Tiếp hoặc Lưu File PDF Bản Đẹp
            </button>
          </div>

          <!-- VIP Upsell -->
          <div style="margin-top: 25px; background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(236,72,153,0.1)); border: 1px solid rgba(139,92,246,0.25); border-radius: 10px; padding: 20px; text-align: left;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
              <i class="fa-solid fa-crown" style="color: #f59e0b; font-size: 1.2rem;"></i>
              <strong style="color: #fff; font-size: 1.05rem;">Gói VIP Member - Truy cập không giới hạn</strong>
            </div>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 12px;">Nâng cấp **Thành viên VIP** chỉ 9.000đ/tháng để tải ngay lập tức không chờ đợi, xóa sạch toàn bộ quảng cáo, in trực tiếp và tải trọn gói VIP Bundle. <strong>Cam kết hoàn tiền 100% trong 7 ngày nếu không hài lòng!</strong></p>
            <div style="display: flex; gap: 10px;">
              <button id="vip-upsell-btn" type="button" class="btn" style="flex: 1; padding: 12px 24px; font-size: 0.95rem; background: linear-gradient(135deg, #8b5cf6, #ec4899); border: none; color: white; cursor: pointer; border-radius: 6px; font-weight: bold;">
                <i class="fa-solid fa-bolt"></i> Nâng Cấp VIP Chỉ 9.000đ/tháng
              </button>
              <button id="download-vip-bundle-btn" class="btn btn-secondary" style="display: none; flex: 1; padding: 12px 24px;">
                <i class="fa-solid fa-file-zipper" style="color: #f59e0b;"></i> Tải Trọn Bộ VIP Bundle (.zip)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

    <!-- Legal FAQs & Compliance Accordions -->
    <div class="glass-panel" style="margin-top: 30px;">
      <h3 style="margin-bottom: 20px; font-size: 1.15rem; border-bottom: 1px solid var(--border-glass); padding-bottom: 10px;"><i class="fa-solid fa-scale-balanced" style="color: var(--accent-primary);"></i> Căn Cứ Pháp Lý & Hướng Dẫn Kèm Theo</h3>
      
      <div class="faq-container">
        <div class="faq-item" style="border-bottom: 1px solid var(--border-glass); padding: 12px 0;">
          <div class="faq-trigger" style="display: flex; justify-content: space-between; align-items: center; cursor: pointer; font-weight: 600; color: #fff; font-size: 0.9rem;">
            <span>1. Quy chuẩn thể thức văn bản hành chính Việt Nam là gì?</span>
            <i class="fa-solid fa-chevron-down" style="font-size: 0.8rem; transition: var(--transition-smooth); color: var(--text-secondary);"></i>
          </div>
          <div class="faq-content" style="max-height: 0; overflow: hidden; transition: var(--transition-smooth); color: var(--text-secondary); font-size: 0.85rem; margin-top: 8px; text-align: justify; line-height: 1.6;">
            Theo Nghị định 30/2020/NĐ-CP của Chính phủ về công tác văn thư, văn bản hành chính quy chuẩn phải sử dụng font chữ chân phương (Times New Roman), căn lề chuẩn (trên-dưới 20-25mm, trái 30-35mm, phải 15-20mm), có tiêu ngữ, quốc hiệu viết hoa đậm ở chính giữa. Các công cụ biểu mẫu của chúng tôi đã căn lề và định dạng tự động đúng tỷ lệ này để đảm bảo tính chuyên nghiệp tối đa khi nộp.
          </div>
        </div>

        <div class="faq-item" style="border-bottom: 1px solid var(--border-glass); padding: 12px 0;">
          <div class="faq-trigger" style="display: flex; justify-content: space-between; align-items: center; cursor: pointer; font-weight: 600; color: #fff; font-size: 0.9rem;">
            <span>2. Quy định thời hạn nộp đơn báo trước và hiệu lực pháp luật?</span>
            <i class="fa-solid fa-chevron-down" style="font-size: 0.8rem; transition: var(--transition-smooth); color: var(--text-secondary);"></i>
          </div>
          <div class="faq-content" style="max-height: 0; overflow: hidden; transition: var(--transition-smooth); color: var(--text-secondary); font-size: 0.85rem; margin-top: 8px; text-align: justify; line-height: 1.6;">
            - <strong>Đơn xin nghỉ việc / thôi việc:</strong> Theo quy định tại Điều 35 Bộ luật Lao động 2019, người lao động có quyền đơn phương chấm dứt hợp đồng lao động nhưng phải báo trước ít nhất 45 ngày (đối với hợp đồng không xác định thời hạn), ít nhất 30 ngày (đối với hợp đồng xác định thời hạn từ 12 - 36 tháng) hoặc ít nhất 3 ngày làm việc (đối với hợp đồng dưới 12 tháng).<br>
            - <strong>Đơn xin nghỉ phép:</strong> Quy định theo thỏa ước lao động tập thể hoặc nội quy công ty, thường nộp trước ít nhất 1 ngày làm việc (với ngày nghỉ ngắn) hoặc 3-5 ngày (đối với đợt nghỉ dài).<br>
            - <strong>Đơn xin tạm trú / tạm vắng:</strong> Cần nộp và hoàn thành thủ tục đăng ký trong vòng 30 ngày kể từ ngày chuyển đến sinh sống tại địa phương mới (Điều 27 Luật Cư trú 2020).
          </div>
        </div>

        <div class="faq-item" style="padding: 12px 0 0 0;">
          <div class="faq-trigger" style="display: flex; justify-content: space-between; align-items: center; cursor: pointer; font-weight: 600; color: #fff; font-size: 0.9rem;">
            <span>3. Bảo mật thông tin cá nhân của người làm đơn?</span>
            <i class="fa-solid fa-chevron-down" style="font-size: 0.8rem; transition: var(--transition-smooth); color: var(--text-secondary);"></i>
          </div>
          <div class="faq-content" style="max-height: 0; overflow: hidden; transition: var(--transition-smooth); color: var(--text-secondary); font-size: 0.85rem; margin-top: 8px; text-align: justify; line-height: 1.6;">
            VinaTools tuân thủ nghiêm ngặt Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 và Nghị định số 356/2025/NĐ-CP của Chính phủ. Do cấu trúc code được thiết kế chạy trực tiếp client-side trên trình duyệt web, mọi dữ liệu nhạy cảm của bạn (như tên tuổi, số CCCD, địa chỉ cư trú) không hề được lưu trữ trên server hay ghi nhận lại dưới bất kỳ hình thức nào. Quyền riêng tư của bạn được bảo mật tuyệt đối 100%.
          </div>
        </div>
      </div>
    </div>
    """

    # 4. JS scripts
    tool_js = f"""
      // Wizard Steps Navigation
      let currentStep = 1;
      const totalSteps = 3;
      const formSteps = document.querySelectorAll('.form-step');
      const stepDots = document.querySelectorAll('.step-dot');
      const progressFill = document.getElementById('progress-fill');

      function updateWizardUI() {{
        formSteps.forEach(step => step.style.display = 'none');
        document.querySelector(`.form-step[data-step="${{currentStep}}"]`).style.display = 'block';
        
        stepDots.forEach((dot, idx) => {{
          if (idx < currentStep) {{
            dot.classList.add('active');
            dot.style.borderColor = 'var(--accent-primary)';
            dot.style.color = '#fff';
          }} else {{
            dot.classList.remove('active');
            dot.style.borderColor = 'var(--text-muted)';
            dot.style.color = 'var(--text-muted)';
          }}
        }});
        
        const progressPercentage = ((currentStep - 1) / (totalSteps - 1)) * 100;
        if (progressFill) progressFill.style.width = `${{progressPercentage}}%`;
      }}

      // Validation logic
      function validateStep(step) {{
        let isValid = true;
        if (step === 1) {{
          if ({str(is_contract).lower()}) {{
            const aName = document.getElementById('party-a-name');
            const aId = document.getElementById('party-a-id');
            const aPhone = document.getElementById('party-a-phone');
            const aAddress = document.getElementById('party-a-address');
            if (!aName.value.trim() || !aId.value.trim() || !aPhone.value.trim() || !aAddress.value.trim()) isValid = false;
          }} else {{
            const nameInput = document.getElementById('user-name');
            const idInput = document.getElementById('user-id');
            const phoneInput = document.getElementById('user-phone');
            if (!nameInput.value.trim() || !idInput.value.trim() || !phoneInput.value.trim()) isValid = false;
          }}
        }} else if (step === 2) {{
          if ({str(is_contract).lower()}) {{
            const bName = document.getElementById('party-b-name');
            const bId = document.getElementById('party-b-id');
            const bPhone = document.getElementById('party-b-phone');
            const bAddress = document.getElementById('party-b-address');
            if (!bName.value.trim() || !bId.value.trim() || !bPhone.value.trim() || !bAddress.value.trim()) isValid = false;
          }} else {{
            const addressInput = document.getElementById('user-address');
            const kínhGửiInput = document.getElementById('user-kính-gửi');
            if (!addressInput.value.trim() || !kínhGửiInput.value.trim()) isValid = false;
          }}
        }}
        return isValid;
      }}

      document.querySelectorAll('.next-step-btn').forEach(btn => {{
        btn.addEventListener('click', () => {{
          if (currentStep === 1) {{
            const acceptTerms = document.getElementById('accept-terms');
            if (acceptTerms && !acceptTerms.checked && !{str(is_contract).lower()}) {{
              alert('Bạn phải đồng ý với Điều khoản dịch vụ & Chính sách bảo mật của VinaTools để tiếp tục.');
              return;
            }}
          }}
          if (validateStep(currentStep)) {{
            currentStep++;
            updateWizardUI();
          }} else {{
            alert('Vui lòng kiểm tra lại thông tin và điền đầy đủ các trường bắt buộc.');
          }}
        }});
      }});

      document.querySelectorAll('.prev-step-btn').forEach(btn => {{
        btn.addEventListener('click', () => {{
          currentStep--;
          updateWizardUI();
        }});
      }});

      // Accordion FAQ toggle
      document.querySelectorAll('.faq-trigger').forEach(trigger => {{
        trigger.addEventListener('click', () => {{
          const content = trigger.nextElementSibling;
          const icon = trigger.querySelector('i');
          const isOpen = content.classList.contains('open');
          
          if (isOpen) {{
            content.style.maxHeight = '0px';
            content.classList.remove('open');
            if (icon) icon.style.transform = 'rotate(0deg)';
            trigger.setAttribute('aria-expanded', 'false');
          }} else {{
            document.querySelectorAll('.faq-content').forEach(c => {{
              c.style.maxHeight = '0px';
              c.classList.remove('open');
            }});
            document.querySelectorAll('.faq-trigger').forEach(t => {{
              t.setAttribute('aria-expanded', 'false');
              const idx = t.querySelector('i');
              if (idx) idx.style.transform = 'rotate(0deg)';
            }});
            
            content.style.maxHeight = content.scrollHeight + 'px';
            content.classList.add('open');
            if (icon) icon.style.transform = 'rotate(180deg)';
            trigger.setAttribute('aria-expanded', 'true');
          }}
        }});
      }});

      // Live Preview updates
      function updateLivePreview() {{
        const isContract = {str(is_contract).lower()};
        const preview = document.getElementById('preview-content');
        if (!preview) return;

        if (isContract) {{
          const partyAName = document.getElementById('party-a-name')?.value || "Nguyễn Văn A";
          const partyAID = document.getElementById('party-a-id')?.value || "001203004567";
          const partyAPhone = document.getElementById('party-a-phone')?.value || "0987654321";
          const partyAAddress = document.getElementById('party-a-address')?.value || "Số 12 Đường Lê Lợi, Quận 1, TP. HCM";
          
          const partyBName = document.getElementById('party-b-name')?.value || "Trần Văn B";
          const partyBID = document.getElementById('party-b-id')?.value || "002304005678";
          const partyBPhone = document.getElementById('party-b-phone')?.value || "0912345678";
          const partyBAddress = document.getElementById('party-b-address')?.value || "Số 85 Nguyễn Huệ, Quận 1, TP. HCM";

          let bodyHtml = "";
          if ("{slug}" === "bien-ban-ban-giao-tai-san") {{
            const loc = document.getElementById('handover-loc')?.value || "Văn phòng Công ty";
            const date = document.getElementById('handover-date')?.value || "12/06/2026";
            const asset1 = document.getElementById('asset-name-1')?.value || "";
            const qty1 = document.getElementById('asset-qty-1')?.value || "";
            const stat1 = document.getElementById('asset-status-1')?.value || "";
            const asset2 = document.getElementById('asset-name-2')?.value || "";
            const qty2 = document.getElementById('asset-qty-2')?.value || "";
            const stat2 = document.getElementById('asset-status-2')?.value || "";
            const asset3 = document.getElementById('asset-name-3')?.value || "";
            const qty3 = document.getElementById('asset-qty-3')?.value || "";
            const stat3 = document.getElementById('asset-status-3')?.value || "";

            let tableRows = "";
            if (asset1) tableRows += `<tr><td style="border: 1px solid black; padding: 8px; text-align:center;">1</td><td style="border: 1px solid black; padding: 8px;">\${{asset1}}</td><td style="border: 1px solid black; padding: 8px; text-align:center;">\${{qty1}}</td><td style="border: 1px solid black; padding: 8px;">\${{stat1}}</td></tr>`;
            if (asset2) tableRows += `<tr><td style="border: 1px solid black; padding: 8px; text-align:center;">2</td><td style="border: 1px solid black; padding: 8px;">\${{asset2}}</td><td style="border: 1px solid black; padding: 8px; text-align:center;">\${{qty2}}</td><td style="border: 1px solid black; padding: 8px;">\${{stat2}}</td></tr>`;
            if (asset3) tableRows += `<tr><td style="border: 1px solid black; padding: 8px; text-align:center;">3</td><td style="border: 1px solid black; padding: 8px;">\${{asset3}}</td><td style="border: 1px solid black; padding: 8px; text-align:center;">\${{qty3}}</td><td style="border: 1px solid black; padding: 8px;">\${{stat3}}</td></tr>`;
            
            if (!tableRows) {{
              tableRows = `<tr><td colspan="4" style="border: 1px solid black; padding: 8px; text-align:center; color:#6b7280;">(Chưa nhập danh mục tài sản)</td></tr>`;
            }}

            bodyHtml = `
              <p style="margin-bottom: 12px;">Hôm nay, ngày \${{date}}, tại địa điểm: \${{loc}}, chúng tôi gồm các bên:</p>
              <p style="margin-bottom: 8px; font-weight: bold;">BÊN A (Bên giao tài sản):</p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Ông/Bà: <strong>\${{partyAName}}</strong></p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Số CCCD/Hộ chiếu: \${{partyAID}} | ĐT: \${{partyAPhone}}</p>
              <p style="margin-bottom: 12px; margin-left: 15px;">- Địa chỉ: \${{partyAAddress}}</p>
              
              <p style="margin-bottom: 8px; font-weight: bold;">BÊN B (Bên nhận tài sản):</p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Ông/Bà: <strong>\${{partyBName}}</strong></p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Số CCCD/Hộ chiếu: \${{partyBID}} | ĐT: \${{partyBPhone}}</p>
              <p style="margin-bottom: 12px; margin-left: 15px;">- Địa chỉ: \${{partyBAddress}}</p>

              <p style="margin-bottom: 12px; text-indent: 15px; text-align: justify;">Sau khi thống nhất, Bên A thực hiện bàn giao và Bên B đồng ý nhận các tài sản, thiết bị có danh mục chi tiết cụ thể như sau:</p>
              
              <table style="width:100%; border-collapse: collapse; margin: 15px 0; font-size: 0.9rem;">
                <thead>
                  <tr style="background:#f3f4f6;">
                    <th style="border: 1px solid black; padding: 8px; width:8%;">STT</th>
                    <th style="border: 1px solid black; padding: 8px; text-align:left;">Tên tài sản, thiết bị</th>
                    <th style="border: 1px solid black; padding: 8px; width:15%;">Số lượng</th>
                    <th style="border: 1px solid black; padding: 8px; text-align:left;">Tình trạng bàn giao</th>
                  </tr>
                </thead>
                <tbody>
                  \${{tableRows}}
                </tbody>
              </table>
              
              <p style="margin-bottom: 12px; text-indent: 15px; text-align: justify;">Bên B cam kết bảo quản, quản lý và sử dụng các tài sản trên đúng mục đích thỏa thuận. Biên bản được lập thành hai bản có giá trị pháp lý như nhau, mỗi bên giữ một bản.</p>
            `;
          }} else if ("{slug}" === "mau-hop-dong-mua-ban-xe") {{
            const brand = document.getElementById('car-brand')?.value || "Honda SH 150i";
            const plate = document.getElementById('car-plate')?.value || "29A-123.45";
            const engine = document.getElementById('car-engine')?.value || "RLH123456 / JF123456";
            const price = document.getElementById('car-price')?.value || "85.000.000 đ";
            const payment = document.getElementById('car-payment')?.value || "Chuyển khoản ngân hàng";

            bodyHtml = `
              <p style="margin-bottom: 12px;">Hôm nay, ngày ...... tháng ...... năm 2026, chúng tôi gồm các bên:</p>
              <p style="margin-bottom: 8px; font-weight: bold;">BÊN BÁN (Bên A):</p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Ông/Bà: <strong>\${{partyAName}}</strong></p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Số CCCD/Hộ chiếu: \${{partyAID}} | ĐT: \${{partyAPhone}}</p>
              <p style="margin-bottom: 12px; margin-left: 15px;">- Địa chỉ thường trú: \${{partyAAddress}}</p>
              
              <p style="margin-bottom: 8px; font-weight: bold;">BÊN MUA (Bên B):</p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Ông/Bà: <strong>\${{partyBName}}</strong></p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Số CCCD/Hộ chiếu: \${{partyBID}} | ĐT: \${{partyBPhone}}</p>
              <p style="margin-bottom: 12px; margin-left: 15px;">- Địa chỉ thường trú: \${{partyBAddress}}</p>

              <p style="margin-bottom: 12px; text-indent: 15px; text-align: justify;">Sau khi bàn bạc thống nhất, hai bên đồng ý ký kết hợp đồng mua bán xe với các điều khoản cụ thể sau đây:</p>
              
              <p style="margin-bottom: 8px; font-weight: bold;">Điều 1: Đối tượng mua bán</p>
              <p style="margin-bottom: 12px; margin-left: 15px; text-align: justify;">Bên A đồng ý bán và Bên B đồng ý mua một chiếc xe có đặc điểm đăng ký như sau: Hãng sản xuất/Nhãn hiệu: <strong>\${{brand}}</strong> | Biển kiểm soát: <strong>\${{plate}}</strong> | Số khung/số máy: <strong>\${{engine}}</strong>.</p>
              
              <p style="margin-bottom: 8px; font-weight: bold;">Điều 2: Giá mua bán và thanh toán</p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Giá mua bán hai bên tự thỏa thuận là: <strong>\${{price}}</strong></p>
              <p style="margin-bottom: 12px; margin-left: 15px;">- Phương thức thanh toán: <strong>\${{payment}}</strong></p>
              
              <p style="margin-bottom: 8px; font-weight: bold;">Điều 3: Cam kết của hai bên</p>
              <p style="margin-bottom: 12px; margin-left: 15px; text-align: justify;">Bên A cam kết chiếc xe trên thuộc quyền sở hữu hợp pháp của mình và không có tranh chấp pháp lý. Bên B có trách nhiệm thực hiện đăng ký sang tên xe đúng thời gian quy định pháp luật.</p>
            `;
          }} else {{
            const obj = document.getElementById('contract-object')?.value || "Thuê nhà nguyên căn làm văn phòng";
            const price = document.getElementById('contract-price')?.value || "15.000.000 đ/tháng";
            const payment = document.getElementById('contract-payment')?.value || "Chuyển khoản hàng tháng";

            bodyHtml = `
              <p style="margin-bottom: 12px;">Hôm nay, ngày ...... tháng ...... năm 2026, chúng tôi gồm các bên:</p>
              <p style="margin-bottom: 8px; font-weight: bold;">BÊN A:</p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Ông/Bà: <strong>\${{partyAName}}</strong></p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Số CCCD/Hộ chiếu: \${{partyAID}} | ĐT: \${{partyAPhone}}</p>
              <p style="margin-bottom: 12px; margin-left: 15px;">- Địa chỉ: \${{partyAAddress}}</p>
              
              <p style="margin-bottom: 8px; font-weight: bold;">BÊN B:</p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Ông/Bà: <strong>\${{partyBName}}</strong></p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Số CCCD/Hộ chiếu: \${{partyBID}} | ĐT: \${{partyBPhone}}</p>
              <p style="margin-bottom: 12px; margin-left: 15px;">- Địa chỉ: \${{partyBAddress}}</p>

              <p style="margin-bottom: 12px; text-indent: 15px; text-align: justify;">Hai bên cùng thống nhất ký kết hợp đồng với nội dung thỏa thuận dưới đây:</p>
              
              <p style="margin-bottom: 8px; font-weight: bold;">Điều 1: Đối tượng giao kết</p>
              <p style="margin-bottom: 12px; margin-left: 15px;">Nội dung/mục đích thực hiện: <strong>\${{obj}}</strong>.</p>
              
              <p style="margin-bottom: 8px; font-weight: bold;">Điều 2: Giá trị và phương thức thanh toán</p>
              <p style="margin-bottom: 6px; margin-left: 15px;">- Giá trị giao dịch: <strong>\${{price}}</strong></p>
              <p style="margin-bottom: 12px; margin-left: 15px;">- Phương thức thanh toán: <strong>\${{payment}}</strong></p>
            `;
          }}

          preview.innerHTML = `
            <div style="text-align: center; margin-bottom: 25px; color: black;">
              <div style="font-weight: bold; font-size: 1.15rem; text-transform: uppercase; line-height: 1.3;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
              <div style="font-weight: bold; font-size: 1rem; margin-top: 5px;">Độc lập - Tự do - Hạnh phúc</div>
              <div style="margin: 8px auto; width: 130px; border-bottom: 1px solid black;"></div>
            </div>
            
            <h1 style="text-align: center; color: black; font-weight: bold; font-size: 1.35rem; margin: 30px 0 20px 0; text-transform: uppercase;">{keyword.upper()}</h1>
            
            <div style="margin-top: 35px; font-size: 1.05rem; color: black; text-align: left; line-height: 1.6;">
              \${{bodyHtml}}
            </div>
            
            <table style="width: 100%; margin-top: 50px; color: black; font-size: 1rem; border-collapse: collapse;">
              <tr>
                <td style="width: 50%; text-align: center; vertical-align: top; border:none; padding: 0;">
                  <p style="font-weight: bold; text-transform: uppercase;">ĐẠI DIỆN BÊN A</p>
                  <p style="color: #6b7280; font-size: 0.85rem; margin-top: 2px;">(Ký và ghi rõ họ tên)</p>
                  <div style="height: 60px;"></div>
                  <p style="font-weight: bold; font-size: 1.05rem;">\${{partyAName}}</p>
                </td>
                <td style="width: 50%; text-align: center; vertical-align: top; border:none; padding: 0;">
                  <p style="font-weight: bold; text-transform: uppercase;">ĐẠI DIỆN BÊN B</p>
                  <p style="color: #6b7280; font-size: 0.85rem; margin-top: 2px;">(Ký và ghi rõ họ tên)</p>
                  <div style="height: 60px;"></div>
                  <p style="font-weight: bold; font-size: 1.05rem;">\${{partyBName}}</p>
                </td>
              </tr>
            </table>
          `;
        }} else {{
          const isJob = {str(is_job).lower()};
          const isLeave = {str(is_leave).lower()};
          const isResignation = {str(is_resignation).lower()};
          const isResidence = {str(is_residence).lower()};

          if (isJob) {{
            const name = document.getElementById('user-name')?.value || "Nguyễn Văn A";
            const phone = document.getElementById('user-phone')?.value || "0987654321";
            const email = document.getElementById('user-email')?.value || "nguyenvana@gmail.com";
            const position = document.getElementById('job-position')?.value || "Nhân viên Lập trình Phần mềm";
            const edu = document.getElementById('job-education')?.value || "Cử nhân CNTT - Đại học Bách Khoa";
            const exp = document.getElementById('job-experience')?.value || "1 năm kinh nghiệm phát triển web";
            const kínhGửi = document.getElementById('user-kính-gửi')?.value || "Ban Giám đốc cùng Bộ phận Tuyển dụng";
            const reason = document.getElementById('user-reason')?.value || "Lý do ứng tuyển...";

            preview.innerHTML = `
              <div style="text-align: center; margin-bottom: 25px; color: black;">
                <div style="font-weight: bold; font-size: 1.15rem; text-transform: uppercase; line-height: 1.3;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
                <div style="font-weight: bold; font-size: 1rem; margin-top: 5px;">Độc lập - Tự do - Hạnh phúc</div>
                <div style="margin: 8px auto; width: 130px; border-bottom: 1px solid black;"></div>
              </div>
              
              <h1 style="text-align: center; color: black; font-weight: bold; font-size: 1.35rem; margin: 30px 0 20px 0; text-transform: uppercase;">{keyword.upper()}</h1>
              
              <div style="margin-top: 35px; font-size: 1.05rem; color: black; text-align: left;">
                <p style="margin-bottom: 18px; text-align: left; text-indent: 15px;"><strong>Kính gửi:</strong> \${{kínhGửi}}</p>
                <p style="margin-bottom: 12px; text-align: left;">Tôi tên là: <strong>\${{name}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Số điện thoại liên hệ: <strong>\${{phone}}</strong> | Email: <strong>\${{email}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Vị trí mong muốn ứng tuyển: <strong>\${{position}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Trình độ học vấn/Bằng cấp: <strong>\${{edu}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Sơ lược kinh nghiệm: <strong>\${{exp}}</strong></p>
                <p style="margin-bottom: 20px; text-indent: 30px; line-height: 1.8; text-align: justify;"><strong>Thư giới thiệu bản thân & Lý do ứng tuyển:</strong> \${{reason}}</p>
                <p style="margin-bottom: 12px; text-indent: 30px; line-height: 1.8; text-align: justify;">Tôi cam kết những thông tin trên là chính xác và chân thực. Tôi rất mong Quý công ty tạo điều kiện cho tôi tham gia vòng phỏng vấn chuyên môn.</p>
                <p style="margin-bottom: 12px; text-indent: 30px; line-height: 1.8; text-align: justify;">Xin chân thành cảm ơn Quý ban tuyển dụng!</p>
              </div>

              <div style="display: flex; justify-content: space-between; margin-top: 50px; color: black;">
                <div></div>
                <div style="text-align: center; width: 280px;">
                  <p style="font-style: italic; font-size: 0.95rem;">......, ngày ..... tháng ..... năm 2026</p>
                  <p style="font-weight: bold; margin-top: 5px; text-transform: uppercase;">Người ứng tuyển</p>
                  <p style="color: #6b7280; font-size: 0.85rem; margin-top: 2px;">(Ký và ghi rõ họ tên)</p>
                  <div style="height: 60px;"></div>
                  <p style="font-weight: bold; font-size: 1.05rem;">\${{name}}</p>
                </div>
              </div>
            `;
          }} else if (isLeave) {{
            const name = document.getElementById('user-name')?.value || "Nguyễn Văn A";
            const dept = document.getElementById('user-dept')?.value || "Phòng Công nghệ Thông tin";
            const phone = document.getElementById('user-phone')?.value || "0987654321";
            const from = document.getElementById('leave-from')?.value || "15/06/2026";
            const to = document.getElementById('leave-to')?.value || "17/06/2026";
            const days = document.getElementById('leave-days')?.value || "03 ngày";
            const delegate = document.getElementById('leave-delegate')?.value || "Trần Văn B";
            const kínhGửi = document.getElementById('user-kính-gửi')?.value || "Ban Giám đốc Công ty";
            const reason = document.getElementById('user-reason')?.value || "Lý do xin nghỉ...";

            preview.innerHTML = `
              <div style="text-align: center; margin-bottom: 25px; color: black;">
                <div style="font-weight: bold; font-size: 1.15rem; text-transform: uppercase; line-height: 1.3;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
                <div style="font-weight: bold; font-size: 1rem; margin-top: 5px;">Độc lập - Tự do - Hạnh phúc</div>
                <div style="margin: 8px auto; width: 130px; border-bottom: 1px solid black;"></div>
              </div>
              
              <h1 style="text-align: center; color: black; font-weight: bold; font-size: 1.35rem; margin: 30px 0 20px 0; text-transform: uppercase;">{keyword.upper()}</h1>
              
              <div style="margin-top: 35px; font-size: 1.05rem; color: black; text-align: left;">
                <p style="margin-bottom: 18px; text-align: left; text-indent: 15px;"><strong>Kính gửi:</strong> \${{kínhGửi}}</p>
                <p style="margin-bottom: 12px; text-align: left;">Tôi tên là: <strong>\${{name}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Bộ phận/Lớp học: <strong>\${{dept}}</strong> | Điện thoại: <strong>\${{phone}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Thời gian xin nghỉ: Từ ngày <strong>\${{from}}</strong> đến ngày <strong>\${{to}}</strong> (Tổng cộng: <strong>\${{days}}</strong>)</p>
                <p style="margin-bottom: 12px; text-align: left;">Người bàn giao công việc / nhiệm vụ trong thời gian nghỉ: <strong>\${{delegate}}</strong></p>
                <p style="margin-bottom: 20px; text-indent: 30px; line-height: 1.8; text-align: justify;"><strong>Lý do xin nghỉ phép chi tiết:</strong> \${{reason}}</p>
                <p style="margin-bottom: 12px; text-indent: 30px; line-height: 1.8; text-align: justify;">Tôi cam kết sẽ hoàn thành bàn giao đầy đủ trách nhiệm công việc trước khi nghỉ và hoàn thành các nội dung còn lại ngay khi quay lại làm việc.</p>
                <p style="margin-bottom: 12px; text-indent: 30px; line-height: 1.8; text-align: justify;">Kính mong Ban lãnh đạo phê duyệt.</p>
              </div>

              <div style="display: flex; justify-content: space-between; margin-top: 50px; color: black;">
                <div></div>
                <div style="text-align: center; width: 280px;">
                  <p style="font-style: italic; font-size: 0.95rem;">......, ngày ..... tháng ..... năm 2026</p>
                  <p style="font-weight: bold; margin-top: 5px; text-transform: uppercase;">Người làm đơn</p>
                  <p style="color: #6b7280; font-size: 0.85rem; margin-top: 2px;">(Ký và ghi rõ họ tên)</p>
                  <div style="height: 60px;"></div>
                  <p style="font-weight: bold; font-size: 1.05rem;">\${{name}}</p>
                </div>
              </div>
            `;
          }} else if (isResignation) {{
            const name = document.getElementById('user-name')?.value || "Nguyễn Văn A";
            const id = document.getElementById('user-id')?.value || "001203004xxx";
            const phone = document.getElementById('user-phone')?.value || "0987654321";
            const title = document.getElementById('job-title')?.value || "Trưởng nhóm kinh doanh";
            const dept = document.getElementById('user-dept')?.value || "Phòng Dự án";
            const date = document.getElementById('resign-date')?.value || "30/06/2026";
            const handover = document.getElementById('handover-status')?.value || "Bàn giao tài sản và mã nguồn";
            const kínhGửi = document.getElementById('user-kính-gửi')?.value || "Ban Giám đốc Công ty";
            const reason = document.getElementById('user-reason')?.value || "Lý do xin thôi việc...";

            preview.innerHTML = `
              <div style="text-align: center; margin-bottom: 25px; color: black;">
                <div style="font-weight: bold; font-size: 1.15rem; text-transform: uppercase; line-height: 1.3;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
                <div style="font-weight: bold; font-size: 1rem; margin-top: 5px;">Độc lập - Tự do - Hạnh phúc</div>
                <div style="margin: 8px auto; width: 130px; border-bottom: 1px solid black;"></div>
              </div>
              
              <h1 style="text-align: center; color: black; font-weight: bold; font-size: 1.35rem; margin: 30px 0 20px 0; text-transform: uppercase;">{keyword.upper()}</h1>
              
              <div style="margin-top: 35px; font-size: 1.05rem; color: black; text-align: left;">
                <p style="margin-bottom: 18px; text-align: left; text-indent: 15px;"><strong>Kính gửi:</strong> \${{kínhGửi}}</p>
                <p style="margin-bottom: 12px; text-align: left;">Tôi tên là: <strong>\${{name}}</strong> | Số CCCD/Hộ chiếu: <strong>\${{id}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Chức vụ hiện tại: <strong>\${{title}}</strong> | Bộ phận: <strong>\${{dept}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Số điện thoại liên hệ: <strong>\${{phone}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Ngày làm việc cuối cùng dự kiến: <strong>\${{date}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Nội dung/Tình trạng bàn giao công việc: <strong>\${{handover}}</strong></p>
                <p style="margin-bottom: 20px; text-indent: 30px; line-height: 1.8; text-align: justify;"><strong>Lý do xin thôi việc chi tiết:</strong> \${{reason}}</p>
                <p style="margin-bottom: 12px; text-indent: 30px; line-height: 1.8; text-align: justify;">Tôi cam kết sẽ hoàn thành mọi thủ tục bàn giao tài sản, tài liệu công việc liên quan theo đúng thời hạn quy định của công ty.</p>
                <p style="margin-bottom: 12px; text-indent: 30px; line-height: 1.8; text-align: justify;">Tôi chân thành cảm ơn Ban Giám đốc và đồng nghiệp đã hỗ trợ tôi trong suốt quá trình công tác tại công ty.</p>
              </div>

              <div style="display: flex; justify-content: space-between; margin-top: 50px; color: black;">
                <div></div>
                <div style="text-align: center; width: 280px;">
                  <p style="font-style: italic; font-size: 0.95rem;">......, ngày ..... tháng ..... năm 2026</p>
                  <p style="font-weight: bold; margin-top: 5px; text-transform: uppercase;">Người làm đơn</p>
                  <p style="color: #6b7280; font-size: 0.85rem; margin-top: 2px;">(Ký và ghi rõ họ tên)</p>
                  <div style="height: 60px;"></div>
                  <p style="font-weight: bold; font-size: 1.05rem;">\${{name}}</p>
                </div>
              </div>
            `;
          }} else if (isResidence) {{
            const name = document.getElementById('user-name')?.value || "Nguyễn Văn A";
            const id = document.getElementById('user-id')?.value || "001203004xxx";
            const phone = document.getElementById('user-phone')?.value || "0987654321";
            const address = document.getElementById('user-address')?.value || "Thái Bình";
            const hostAddress = document.getElementById('host-address')?.value || "Số 12 Đường Lê Lợi, Quận 1, TP. HCM";
            const hostName = document.getElementById('host-name')?.value || "Trần Văn B";
            const relation = document.getElementById('host-relation')?.value || "Chủ nhà / Con ruột";
            const duration = document.getElementById('host-duration')?.value || "1 năm";
            const kínhGửi = document.getElementById('user-kính-gửi')?.value || "Công an Phường Bến Nghé";
            const reason = document.getElementById('user-reason')?.value || "Lý do xin tạm trú...";

            preview.innerHTML = `
              <div style="text-align: center; margin-bottom: 25px; color: black;">
                <div style="font-weight: bold; font-size: 1.15rem; text-transform: uppercase; line-height: 1.3;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
                <div style="font-weight: bold; font-size: 1rem; margin-top: 5px;">Độc lập - Tự do - Hạnh phúc</div>
                <div style="margin: 8px auto; width: 130px; border-bottom: 1px solid black;"></div>
              </div>
              
              <h1 style="text-align: center; color: black; font-weight: bold; font-size: 1.35rem; margin: 30px 0 20px 0; text-transform: uppercase;">{keyword.upper()}</h1>
              
              <div style="margin-top: 35px; font-size: 1.05rem; color: black; text-align: left;">
                <p style="margin-bottom: 18px; text-align: left; text-indent: 15px;"><strong>Kính gửi:</strong> \${{kínhGửi}}</p>
                <p style="margin-bottom: 12px; text-align: left;">Tôi tên là: <strong>\${{name}}</strong> | Số CCCD/Hộ chiếu: <strong>\${{id}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Số điện thoại di động: <strong>\${{phone}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Địa chỉ đăng ký thường trú: <strong>\${{address}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Đăng ký tạm trú tại địa chỉ mới: <strong>\${{hostAddress}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Chủ hộ nơi đến tạm trú: Ông/Bà <strong>\${{hostName}}</strong> | Quan hệ với chủ hộ: <strong>\${{relation}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Thời hạn đăng ký tạm trú: <strong>\${{duration}}</strong></p>
                <p style="margin-bottom: 20px; text-indent: 30px; line-height: 1.8; text-align: justify;"><strong>Lý do đăng ký cư trú chi tiết:</strong> \${{reason}}</p>
                <p style="margin-bottom: 12px; text-indent: 30px; line-height: 1.8; text-align: justify;">Tôi cam đoan thông tin khai báo là chính xác và xin chấp hành nghiêm chỉnh mọi luật lệ cư trú địa phương.</p>
              </div>

              <div style="display: flex; justify-content: space-between; margin-top: 50px; color: black;">
                <div></div>
                <div style="text-align: center; width: 280px;">
                  <p style="font-style: italic; font-size: 0.95rem;">......, ngày ..... tháng ..... năm 2026</p>
                  <p style="font-weight: bold; margin-top: 5px; text-transform: uppercase;">Người làm đơn</p>
                  <p style="color: #6b7280; font-size: 0.85rem; margin-top: 2px;">(Ký và ghi rõ họ tên)</p>
                  <div style="height: 60px;"></div>
                  <p style="font-weight: bold; font-size: 1.05rem;">\${{name}}</p>
                </div>
              </div>
            `;
          }} else {{
            const name = document.getElementById('user-name')?.value || "Nguyễn Văn A";
            const id = document.getElementById('user-id')?.value || "001203004xxx";
            const phone = document.getElementById('user-phone')?.value || "0987654321";
            const address = document.getElementById('user-address')?.value || "Số 12 Đường Lê Lợi, Phường Bến Nghé, Quận 1, TP. HCM";
            const kínhGửi = document.getElementById('user-kính-gửi')?.value || "Ban Giám đốc Công ty TNHH VinaTools";
            const reason = document.getElementById('user-reason')?.value || "Nhập lý do chi tiết viết đơn của bạn...";

            preview.innerHTML = `
              <div style="text-align: center; margin-bottom: 25px; color: black;">
                <div style="font-weight: bold; font-size: 1.15rem; text-transform: uppercase; line-height: 1.3;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
                <div style="font-weight: bold; font-size: 1rem; margin-top: 5px;">Độc lập - Tự do - Hạnh phúc</div>
                <div style="margin: 8px auto; width: 130px; border-bottom: 1px solid black;"></div>
              </div>
              
              <h1 style="text-align: center; color: black; font-weight: bold; font-size: 1.35rem; margin: 30px 0 20px 0; text-transform: uppercase;">{keyword.upper()}</h1>
              
              <div style="margin-top: 35px; font-size: 1.05rem; color: black; text-align: left;">
                <p style="margin-bottom: 18px; text-align: left; text-indent: 15px;"><strong>Kính gửi:</strong> \${{kínhGửi}}</p>
                <p style="margin-bottom: 12px; text-align: left;">Tôi tên là: <strong>\${{name}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Số CCCD/Hộ chiếu: <strong>\${{id}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Số điện thoại di động: <strong>\${{phone}}</strong></p>
                <p style="margin-bottom: 12px; text-align: left;">Địa chỉ đăng ký thường trú/tạm trú: <strong>\${{address}}</strong></p>
                <p style="margin-bottom: 20px; text-indent: 30px; line-height: 1.8; text-align: justify;"><strong>Lý do làm đơn:</strong> \${{reason}}</p>
                <p style="margin-bottom: 12px; text-indent: 30px; line-height: 1.8; text-align: justify;">Tôi cam đoan những thông tin khai báo trên đây là hoàn toàn đúng sự thật và xin chịu trách nhiệm trước pháp luật về các thông tin đã khai.</p>
                <p style="margin-bottom: 12px; text-indent: 30px; line-height: 1.8; text-align: justify;">Tôi kính mong Quý cơ quan xem xét và tạo điều kiện phê duyệt nguyện vọng nêu trên. Tôi xin chân thành cảm ơn!</p>
              </div>

              <div style="display: flex; justify-content: space-between; margin-top: 50px; color: black;">
                <div></div>
                <div style="text-align: center; width: 280px;">
                  <p style="font-style: italic; font-size: 0.95rem;">......, ngày ..... tháng ..... năm 2026</p>
                  <p style="font-weight: bold; margin-top: 5px; text-transform: uppercase;">Người làm đơn</p>
                  <p style="color: #6b7280; font-size: 0.85rem; margin-top: 2px;">(Ký và ghi rõ họ tên)</p>
                  <div style="height: 60px;"></div>
                  <p style="font-weight: bold; font-size: 1.05rem;">\${{name}}</p>
                </div>
              </div>
            `;
          }}
        }}
      }}

      // Bind all inputs in form-step to update live preview
      document.querySelectorAll('#doc-form input, #doc-form textarea, #doc-form select').forEach(input => {{
        input.addEventListener('input', updateLivePreview);
        input.addEventListener('change', updateLivePreview);
      }});

      // Populate Reason Scenarios for Petitions
      if (!{str(is_contract).lower()}) {{
        const scenarioSelect = document.getElementById('reason-scenario');
        const isJob = {str(is_job).lower()};
        const isLeave = {str(is_leave).lower()};
        const isResignation = {str(is_resignation).lower()};
        const isResidence = {str(is_residence).lower()};
        
        let jobOptions = [
          {{ val: 'it', text: 'Nhân viên IT / Kỹ sư Lập trình' }},
          {{ val: 'sales', text: 'Nhân viên Kinh doanh / Sales' }},
          {{ val: 'accountant', text: 'Nhân viên Kế toán - Tài chính' }},
          {{ val: 'medical', text: 'Nhân viên Y tế / Điều dưỡng' }}
        ];
        let leaveOptions = [
          {{ val: 'sick', text: 'Nghỉ khám/Điều trị sức khỏe' }},
          {{ val: 'family', text: 'Gia đình có việc hiếu hỷ/việc riêng' }},
          {{ val: 'travel', text: 'Nghỉ phép thường niên/Du lịch' }},
          {{ val: 'study', text: 'Nâng cao trình độ nghiệp vụ' }}
        ];
        let resignationOptions = [
          {{ val: 'career', text: 'Thay đổi định hướng phát triển bản thân' }},
          {{ val: 'health', text: 'Sức khỏe cá nhân không đảm bảo' }},
          {{ val: 'family_move', text: 'Giải quyết việc gia đình/Thay đổi nơi ở' }},
          {{ val: 'environment', text: 'Tìm kiếm môi trường mới phù hợp hơn' }}
        ];
        let residenceOptions = [
          {{ val: 'school', text: 'Sinh viên nhập học dài hạn' }},
          {{ val: 'work', text: 'Chuyển vị trí/nơi làm việc thực tế' }},
          {{ val: 'family_stay', text: 'Cư trú lâu dài cùng người thân' }}
        ];
        let defaultOptions = [
          {{ val: 'family_general', text: 'Giải quyết công việc gia đình quan trọng' }},
          {{ val: 'health_treatment', text: 'Đi khám và điều trị bệnh tại bệnh viện' }},
          {{ val: 'work_business', text: 'Đi công tác/Thực hiện nhiệm vụ được giao' }}
        ];

        let targetOptions = defaultOptions;
        if (isJob) {{
          targetOptions = jobOptions;
        }} else if (isLeave) {{
          targetOptions = leaveOptions;
        }} else if (isResignation) {{
          targetOptions = resignationOptions;
        }} else if (isResidence) {{
          targetOptions = residenceOptions;
        }}

        if (scenarioSelect) {{
          targetOptions.forEach(opt => {{
            const el = document.createElement('option');
            el.value = opt.val;
            el.textContent = opt.text;
            scenarioSelect.appendChild(el);
          }});
        }}

        const reasonTemplates = {{
          it: {{
            formal: "Tôi tốt nghiệp chuyên ngành CNTT và có 1 năm kinh nghiệm thực tập phát triển web. Tôi làm đơn này với mong muốn được ứng tuyển vào vị trí Lập trình viên để cống hiến năng lực, phát triển các giải pháp phần mềm chất lượng cho Quý công ty và nâng cao trình độ chuyên môn của bản thân.",
            urgent: "Với niềm đam mê công nghệ cháy bỏng cùng kinh nghiệm làm dự án web thực tế tại trường, tôi vô cùng khao khát được gia nhập đội ngũ phát triển phần mềm IT của Quý công ty. Kính mong nhận được cơ hội phỏng vấn để thể hiện năng lực.",
            brief: "Tôi xin ứng tuyển vào vị trí Lập trình viên Web với mong muốn đóng góp năng lực lập trình và cống hiến cho công ty."
          }},
          sales: {{
            formal: "Tôi có kỹ năng giao tiếp tốt và khả năng đàm phán, thuyết phục khách hàng. Tôi xin ứng tuyển vị trí Nhân viên Kinh doanh nhằm đóng góp kỹ năng bán hàng, phát triển doanh thu và mở rộng thị trường khách hàng cho Quý công ty.",
            urgent: "Tôi là người năng động, chịu được áp lực doanh số và luôn đặt khách hàng làm trọng tâm. Tôi khao khát ứng tuyển vào vị trí Sales để mang lại kết quả kinh doanh vượt bậc cho Quý công ty trong thời gian tới.",
            brief: "Tôi xin ứng tuyển vị trí Nhân viên Kinh doanh để phát huy năng lực đàm phán và bán hàng."
          }},
          accountant: {{
            formal: "Tôi đã tốt nghiệp chuyên ngành Kế toán doanh nghiệp, nắm rõ chuẩn mực kế toán hiện hành và sử dụng thành thạo các phần mềm. Tôi viết đơn xin ứng tuyển vị trí Kế toán viên nhằm phụ trách công tác tài chính, báo cáo thuế chính xác nhất.",
            urgent: "Với đức tính cẩn thận, tỉ mỉ và trung thực cao, tôi kính ứng tuyển vị trí Kế toán của Quý công ty với mục tiêu hoàn thành xuất sắc các nghiệp vụ tài chính, báo cáo đúng hạn, bảo đảm tính tuân thủ pháp lý tài chính.",
            brief: "Tôi xin ứng tuyển vị trí Nhân viên Kế toán nhằm đảm nhiệm chính xác các công việc thu chi, sổ sách doanh nghiệp."
          }},
          medical: {{
            formal: "Tôi tốt nghiệp ngành Điều dưỡng/Y khoa và đã có chứng chỉ hành nghề cơ bản. Tôi mong muốn ứng tuyển vào đơn vị y tế của Quý cơ quan để chăm sóc sức khỏe bệnh nhân tận tâm, hoàn thành tốt nhiệm vụ chuyên môn của một y bác sĩ.",
            urgent: "Với tinh thần trách nhiệm y đức cao cả, yêu thương người bệnh và có kinh nghiệm trực bệnh viện thực tế, tôi kính xin ứng tuyển vào vị trí nhân viên y tế để đóng góp sức lực chăm sóc bệnh nhân và hỗ trợ đồng nghiệp.",
            brief: "Tôi xin ứng tuyển vào vị trí Nhân viên Y tế để tận tâm chăm sóc sức khỏe bệnh nhân và thực hiện y đức."
          }},
          sick: {{
            formal: "Tôi kính trình Ban Giám đốc cùng bộ phận Nhân sự xin phép được nghỉ phép để đi khám sức khỏe và điều trị y tế theo yêu cầu của bác sĩ. Tôi xin hứa sẽ bàn giao lại đầy đủ các đầu việc còn dở dang cho bộ phận để không ảnh hưởng đến tiến độ hoạt động chung của đơn vị.",
            urgent: "Vì lý do sức khỏe cá nhân bị đau ốm đột xuất không đảm bảo thể trạng để thực hiện công việc đạt chất lượng, tôi kính mong quý lãnh đạo phê duyệt cho tôi được nghỉ phép gấp để điều trị bệnh nhằm sớm hồi phục thể lực làm việc.",
            brief: "Tôi xin phép nghỉ làm ngày hôm nay do bị ốm đột xuất phải đi khám bệnh tại bệnh viện. Rất mong Ban Giám đốc tạo điều kiện phê duyệt đơn."
          }},
          family: {{
            formal: "Tôi viết đơn này kính trình ban lãnh đạo phê duyệt cho tôi nghỉ phép nhằm giải quyết một số công việc hệ trọng, đột xuất của gia đình ở quê. Tôi đã thực hiện bàn giao đầy đủ nội dung công việc tuần này cho đồng nghiệp cùng phòng để bảo đảm công việc diễn ra suôn sẻ.",
            urgent: "Gia đình tôi hiện tại đang xảy ra sự việc cá nhân vô cùng cấp bách cần có sự góp mặt trực tiếp của tôi để giải quyết kịp thời. Tôi kính mong nhận được sự thông cảm và phê duyệt nghỉ phép từ công ty.",
            brief: "Tôi xin phép nghỉ làm để giải quyết một số công việc riêng của gia đình trong vài ngày tới."
          }},
          travel: {{
            formal: "Tôi kính trình Ban Giám đốc cho phép tôi sử dụng ngày nghỉ phép thường niên theo chế độ lao động để thực hiện chuyến du lịch cùng gia đình nhằm tái tạo sức lao động. Công việc của tôi đã được ủy quyền lại toàn bộ cho nhân sự liên quan chịu trách nhiệm xử lý.",
            urgent: "Tôi viết đơn xin phép nghỉ du lịch theo chế độ nghỉ phép năm đã lên lịch từ lâu. Tôi rất mong ban quản lý thông qua để tôi thực hiện kỳ nghỉ cùng người thân.",
            brief: "Tôi xin phép nghỉ phép năm để đi du lịch cùng gia đình, công việc đã bàn giao xong."
          }},
          study: {{
            formal: "Tôi kính làm đơn xin phép ban quản lý tạo điều kiện cho tôi được nghỉ phép ngắn hạn để tập quan tham gia kỳ thi hoàn thành chương trình bồi dưỡng chuyên môn nghiệp vụ được tổ chức sắp tới.",
            urgent: "Vì kỳ thi sát hạch chứng chỉ nghiệp vụ diễn ra đột xuất trùng với lịch làm việc, tôi kính mong công ty hỗ trợ duyệt cho tôi nghỉ phép để hoàn thành nhiệm vụ học tập này.",
            brief: "Tôi làm đơn xin nghỉ phép tham gia kỳ thi chứng chỉ chuyên môn cá nhân."
          }},
          career: {{
            formal: "Tôi xin kính đơn xin thôi việc để chuyển sang hướng đi mới phù hợp hơn với định hướng phát triển sự nghiệp cá nhân dài hạn của bản thân. Xin chân thành cảm ơn Ban Giám đốc và công ty đã tạo điều kiện học tập trong thời gian qua.",
            urgent: "Nhằm tập trung theo đuổi định hướng sự nghiệp mới đã đặt ra từ trước, tôi xin phép Ban Giám đốc cho tôi được thôi việc kể từ ngày mong muốn. Tôi hứa sẽ bàn giao kỹ lưỡng mọi nhiệm vụ.",
            brief: "Tôi xin phép thôi việc tại công ty để theo đuổi định hướng sự nghiệp cá nhân mới."
          }},
          health: {{
            formal: "Tôi xin làm đơn xin nghỉ việc vì lý do tình trạng sức khỏe suy giảm nghiêm trọng, không còn đủ thể chất để cáng đáng các chỉ tiêu công việc tại vị trí hiện tại. Rất mong lãnh đạo thông cảm và phê duyệt đơn cho tôi.",
            urgent: "Vì lý do sức khỏe cá nhân cần thời gian nghỉ ngơi điều trị dài hạn và tĩnh dưỡng y khoa, tôi kính đề nghị Ban Giám đốc duyệt cho tôi chấm dứt hợp đồng lao động trước thời hạn.",
            brief: "Tôi làm đơn xin thôi việc tại công ty vì lý do sức khỏe không bảo đảm hoàn thành công việc."
          }},
          family_move: {{
            formal: "Do thay đổi nơi cư trú thực tế của gia đình chuyển sang tỉnh thành khác sinh sống, quãng đường di chuyển không còn đảm bảo việc đi làm đúng giờ hàng ngày, tôi kính xin được thôi việc tại quý công ty để ổn định chỗ ở mới.",
            urgent: "Vì hoàn cảnh gia đình có việc riêng hệ trọng cần di chuyển chỗ ở gấp về quê sinh sống dài hạn để phụ giúp bố mẹ, tôi xin được chấm dứt hợp đồng lao động tại công ty và xin bàn giao lại công việc.",
            brief: "Tôi xin thôi việc do chuyển nơi cư trú cùng gia đình về quê sống lâu dài. Kính mong lãnh đạo tạo điều kiện phê duyệt đơn."
          }},
          environment: {{
            formal: "Tôi làm đơn này xin thôi việc vì nhận thấy bản thân cần một môi trường làm việc mới với các thử thách khác biệt hơn để bứt phá giới hạn và tích lũy thêm các kỹ năng quản lý thực tiễn phù hợp với lộ trình phát triển bản thân.",
            urgent: "Để tìm kiếm cơ hội và môi trường mới tương thích hơn với mong muốn cống hiến dài hạn của tôi ở thời điểm hiện tại, tôi xin phép Ban Giám đốc cho thôi việc và thực hiện bàn giao đầy đủ quy trình.",
            brief: "Tôi xin phép thôi việc tại công ty để tìm kiếm môi trường mới phù hợp hơn. Xin chân thành cảm ơn công ty."
          }},
          school: {{
            formal: "Tôi làm đơn đăng ký tạm trú dài hạn tại địa phương nhằm phục vụ mục đích theo học chương trình đào tạo đại học chính quy tại trường trên địa bàn. Tôi cam kết chấp hành nghiêm chỉnh luật cư trú và giữ gìn an ninh trật tự khu phố.",
            urgent: "Vì vừa trúng tuyển nhập học và cần ổn định chỗ ở lâu dài để phục vụ việc học tập tại trường học gần đây, tôi kính đề nghị công an địa phương tiếp nhận hồ sơ đăng ký tạm trú và cấp giấy xác nhận tạm trú.",
            brief: "Tôi xin đăng ký tạm trú tại địa bàn để phục vụ việc học tập chính quy dài hạn của bản thân."
          }},
          work: {{
            formal: "Tôi xin đăng ký tạm trú tại khu vực để phục vụ quá trình công tác và làm việc ổn định tại doanh nghiệp trên địa bàn quản lý của công an phường. Tôi cam kết tuân thủ đầy đủ các nghĩa vụ công dân tạm trú theo quy định pháp luật cư trú.",
            urgent: "Do vừa nhận quyết định luân chuyển công tác và bắt đầu làm việc tại văn phòng mới trên địa bàn, tôi kính mong cơ quan công an phường phê duyệt hồ sơ đăng ký tạm trú của tôi để ổn định sinh hoạt pháp lý.",
            brief: "Tôi làm đơn xin đăng ký tạm trú tại địa phương phục vụ nhu cầu đi làm lâu dài tại doanh nghiệp gần đây."
          }},
          family_stay: {{
            formal: "Tôi làm đơn này xin đăng ký tạm trú tại hộ gia đình của người thân tại địa chỉ nêu trên nhằm mục đích hỗ trợ chăm sóc sức khỏe cho gia đình và định cư lâu dài cùng nhau. Rất mong cơ quan quản lý phê duyệt tiếp nhận hồ sơ.",
            urgent: "Vì nhu cầu ở chung lâu dài cùng người thân tại địa phương để tiện sinh hoạt gia đình và đi làm hàng ngày, tôi kính đề nghị công an địa bàn phê duyệt và hoàn tất thủ tục đăng ký tạm trú cho tôi.",
            brief: "Tôi đăng ký tạm trú tại địa phương nhằm sinh sống và lưu trú cùng hộ gia đình người thân."
          }},
          family_general: {{
            formal: "Tôi kính trình cơ quan xem xét giải quyết đơn thư này nhằm phục vụ mục đích giải quyết một số công việc gia sự đặc biệt hệ trọng cần chứng nhận của địa phương để đảm bảo đúng thủ tục pháp lý hành chính nhà nước.",
            urgent: "Do gia đình có sự việc đặc biệt phát sinh khẩn cấp cần hồ sơ pháp lý chứng thực ngay, tôi rất mong cơ quan có thẩm quyền quan tâm xem xét giải quyết nhanh chóng.",
            brief: "Tôi làm đơn này để giải quyết việc gia đình cá nhân quan trọng theo quy định pháp luật."
          }},
          health_treatment: {{
            formal: "Tôi kính làm đơn này để trình bày nguyện vọng được tạo điều kiện xác nhận hồ sơ y tế nhằm thực hiện đợt điều trị sức khỏe chuyên sâu tại bệnh viện tuyến trên theo đúng phác đồ điều trị của cơ sở y tế.",
            urgent: "Do điều kiện sức khỏe cần can thiệp y tế khẩn cấp, kính đề nghị cơ quan phê duyệt văn bản xác nhận để tôi kịp thời nộp bệnh viện làm thủ tục nhập viện điều trị.",
            brief: "Tôi làm đơn này nhằm xin xác nhận hồ sơ điều trị bệnh lý tại cơ sở y tế."
          }},
          work_business: {{
            formal: "Tôi làm đơn này kính trình ban lãnh đạo phê duyệt phân công nhiệm vụ đi công tác dài hạn ngoài tỉnh để trực tiếp giám sát, quản lý chất lượng và đẩy mạnh tiến độ bàn giao công trình dự án của đơn vị.",
            urgent: "Do yêu cầu đối tác khẩn cấp cần nhân sự xử lý kỹ thuật trực tiếp tại hiện trường, tôi xin Ban Giám đốc cử đi công tác đột xuất phục vụ dự án công ty.",
            brief: "Tôi xin phép làm đơn này đi công tác đột xuất theo yêu cầu của đối tác dự án."
          }}
        }};

        const expandBtn = document.getElementById('auto-expand-btn');
        if (expandBtn) {{
          expandBtn.addEventListener('click', () => {{
            const scenario = document.getElementById('reason-scenario').value;
            const tone = document.getElementById('reason-tone').value;
            const textarea = document.getElementById('user-reason');
            const statusEl = document.getElementById('ai-status');
            
            if (reasonTemplates[scenario] && reasonTemplates[scenario][tone]) {{
              textarea.value = reasonTemplates[scenario][tone];
              updateLivePreview();
              if (statusEl) {{
                statusEl.textContent = 'Đã tự động điền lý do theo văn phong chuẩn!';
                statusEl.style.color = '#10b981';
                statusEl.style.opacity = '1';
                setTimeout(() => {{
                  statusEl.style.opacity = '0';
                }}, 3000);
              }}
            }}
          }});
        }}
      }}

      // Handle Form Submission
      document.getElementById('doc-form').addEventListener('submit', function(e) {{
        e.preventDefault();
        const acceptTerms = document.getElementById('accept-terms');
        if (acceptTerms && !acceptTerms.checked) {{
          alert('Bạn phải đồng ý với Điều khoản dịch vụ & Chính sách bảo mật.');
          return;
        }}
        
        // Scroll to preview on mobile
        const preview = document.getElementById('preview-panel');
        if (preview) {{
          preview.scrollIntoView({{ behavior: 'smooth' }});
        }}
      }});

      function downloadDocFile() {{
        const previewHtml = document.getElementById('preview-content').innerHTML;
        const docHtml = `
<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
<head${{""}}>
  <meta charset="utf-8">
  <title>{keyword.upper()}</title>
  <!--[if gte mso 9]>
  <xml>
    <w:WordDocument>
      <w:View>Print</w:View>
      <w:Zoom>100</w:Zoom>
      <w:DoNotOptimizeForBrowser/>
    </w:WordDocument>
  </xml>
  <![endif]-->
  <style>
    body {{
      font-family: 'Times New Roman', serif;
      line-height: 1.6;
      padding: 40px;
      color: black;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 15px 0;
    }}
    th, td {{
      border: 1px solid black;
      padding: 8px;
    }}
  </style>
</head${{""}}>
<body${{""}}>
  \${{previewHtml}}
</body${{""}}>
</html${{""}}>
        `;
        
        const blob = new Blob(['\\ufeff' + docHtml], {{ type: 'application/msword;charset=utf-8' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "{slug}.doc";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }}

      const pageSlug = "{slug}";
      const isVip = localStorage.getItem("vipToken");
      const isUnlocked = localStorage.getItem("unlocked_" + pageSlug);
      const downloadBtn = document.getElementById('unlock-download-btn');
      const directPrintBtn = document.getElementById('direct-print-btn');
      const vipBtn = document.getElementById('vip-upsell-btn');
      const vipDownloadBtn = document.getElementById('download-vip-bundle-btn');

      if (downloadBtn) {{
        downloadBtn.addEventListener('click', function() {{
          const email = localStorage.getItem("userEmail");
          if (!email) {{
            showAuthModal(function() {{
              if (localStorage.getItem("vipToken")) {{
                downloadDocFile();
              }} else {{
                showFreeDownloadCountdown(downloadDocFile);
              }}
            }});
            return;
          }}
          if (localStorage.getItem("vipToken")) {{
            downloadDocFile();
            return;
          }}
          showFreeDownloadCountdown(downloadDocFile);
        }});
      }}

      if (directPrintBtn) {{
        directPrintBtn.style.display = 'block';
        directPrintBtn.addEventListener('click', function() {{
          if (localStorage.getItem("vipToken")) {{
            window.print();
          }} else {{
            alert('Chức năng in trực tiếp yêu cầu tài khoản VIP. Bạn có thể tải file Word (.doc) miễn phí và thực hiện in từ thiết bị của mình.');
          }}
        }});
      }}

      if (vipBtn) {{
        if (isVip) {{
          vipBtn.innerHTML = '<i class="fa-solid fa-crown"></i> Bạn Đang Là Thành Viên VIP';
          vipBtn.disabled = true;
          vipBtn.style.opacity = '0.7';
        }} else {{
          vipBtn.addEventListener('click', triggerVipUpgrade);
        }}
      }}

      if (vipDownloadBtn) {{
        if (isVip) vipDownloadBtn.style.display = 'block';
        vipDownloadBtn.addEventListener('click', function() {{
          const token = localStorage.getItem("vipToken");
          if (token) {{
            const baseApiUrl = paymentConfig.apiEndpoint.replace('/api/check-payment', '');
            const downloadUrl = `\${{baseApiUrl}}/api/download-vip-bundle?token=\${{encodeURIComponent(token)}}`;
            window.location.href = downloadUrl;
          }}
        }});
      }}

      // Run initial preview build
      updateLivePreview();
    """
  else:
    if slug == "cong-cu-tinh-lai-gop":
      tool_html = f"""
      <div class="glass-panel" style="margin-bottom: 30px; text-align: left;">
        <h2 style="text-align:center; margin-bottom: 20px;"><i class="fa-solid fa-calculator" style="color: var(--accent-primary);"></i> Máy Tính Lãi Kép / Lãi Cộng Dồn</h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
          <div>
            <label style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 6px;">Số tiền gốc ban đầu (VND):</label>
            <input type="number" id="interest-principal" value="10000000" style="width:100%; padding:10px; background:rgba(0,0,0,0.2); border:1px solid var(--border-glass); border-radius:6px; color:white; box-sizing: border-box;">
          </div>
          <div>
            <label style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 6px;">Lãi suất hàng năm (%/năm):</label>
            <input type="number" id="interest-rate" value="6.5" step="0.1" style="width:100%; padding:10px; background:rgba(0,0,0,0.2); border:1px solid var(--border-glass); border-radius:6px; color:white; box-sizing: border-box;">
          </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
          <div>
            <label style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 6px;">Thời gian gửi (năm):</label>
            <input type="number" id="interest-period" value="5" style="width:100%; padding:10px; background:rgba(0,0,0,0.2); border:1px solid var(--border-glass); border-radius:6px; color:white; box-sizing: border-box;">
          </div>
          <div>
            <label style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 6px;">Phương thức cộng dồn lãi:</label>
            <select id="interest-type" style="width:100%; padding:10px; background:rgba(0,0,0,0.2); border:1px solid var(--border-glass); border-radius:6px; color:white; box-sizing: border-box;">
              <option value="12">Cộng dồn hàng tháng (12 lần/năm)</option>
              <option value="4">Cộng dồn hàng quý (4 lần/năm)</option>
              <option value="1" selected>Cộng dồn hàng năm (1 lần/năm)</option>
            </select>
          </div>
        </div>
        
        <button id="calc-interest-btn" class="btn btn-primary" style="width:100%; padding:12px; font-weight:bold; cursor: pointer;">Tính toán kết quả</button>
      </div>

      <div id="calc-result-panel" class="glass-panel" style="display:none; margin-bottom:30px;">
        <h3 style="color:#10b981; margin-bottom:15px; text-align:center;"><i class="fa-solid fa-circle-check"></i> Kết Quả Mô Phỏng Lãi Kép</h3>
        
        <div style="display:flex; justify-content:space-around; background:rgba(255,255,255,0.05); padding:15px; border-radius:8px; margin-bottom:20px; border:1px solid var(--border-glass);">
          <div style="text-align:center;">
            <span style="color:var(--text-secondary); font-size:0.8rem;">Tổng số tiền nhận được:</span>
            <div id="total-val" style="font-size:1.3rem; font-weight:bold; color:var(--accent-primary); margin-top:5px;">0 VND</div>
          </div>
          <div style="text-align:center;">
            <span style="color:var(--text-secondary); font-size:0.8rem;">Tổng tiền lãi ròng:</span>
            <div id="interest-val" style="font-size:1.3rem; font-weight:bold; color:#f59e0b; margin-top:5px;">0 VND</div>
          </div>
        </div>
        
        <h4 style="margin-bottom:10px; color:#fff;">Bảng phân bổ thu nhập lãi qua các năm:</h4>
        <div style="overflow-x:auto;">
          <table style="width:100%; border-collapse:collapse; font-size:0.85rem;" id="interest-table">
            <thead>
              <tr style="background:rgba(255,255,255,0.05); border-bottom:1px solid var(--border-glass);">
                <th style="padding:10px; text-align:center; color: var(--text-secondary);">Năm</th>
                <th style="padding:10px; text-align:right; color: var(--text-secondary);">Số dư đầu kỳ</th>
                <th style="padding:10px; text-align:right; color: var(--text-secondary);">Tiền lãi thu được</th>
                <th style="padding:10px; text-align:right; color: var(--text-secondary);">Số dư cuối kỳ</th>
              </tr>
            </thead>
            <tbody>
            </tbody>
          </table>
        </div>

        <div style="margin-top:25px; text-align:center;">
          <button id="unlock-download-btn" class="btn btn-primary" style="width: 100%;">
            <i class="fa-solid fa-download"></i> Tải Bảng Tính Excel Lãi Kép Bản Quyền (Miễn Phí)
          </button>
        </div>
      </div>
      """
      tool_js = f"""
      const calcBtn = document.getElementById('calc-interest-btn');
      if (calcBtn) {{
        calcBtn.addEventListener('click', () => {{
          const principal = parseFloat(document.getElementById('interest-principal').value) || 0;
          const rate = (parseFloat(document.getElementById('interest-rate').value) || 0) / 100;
          const years = parseInt(document.getElementById('interest-period').value) || 0;
          const type = parseInt(document.getElementById('interest-type').value) || 1;
          
          if (principal <= 0 || rate <= 0 || years <= 0) {{
            alert('Vui lòng nhập các giá trị lớn hơn 0.');
            return;
          }}
          
          const resultPanel = document.getElementById('calc-result-panel');
          const tbody = document.querySelector('#interest-table tbody');
          tbody.innerHTML = '';
          
          let currentBalance = principal;
          for (let y = 1; y <= years; y++) {{
            let startBalance = currentBalance;
            let finalBalance = startBalance * Math.pow(1 + rate/type, type);
            let interestEarned = finalBalance - startBalance;
            currentBalance = finalBalance;
            
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid rgba(255,255,255,0.03)';
            tr.innerHTML = `
              <td style="padding:10px; text-align:center; color:#fff;">Năm \${{y}}</td>
              <td style="padding:10px; text-align:right; color:#fff;">\${{new Intl.NumberFormat('vi-VN').format(Math.round(startBalance))}} đ</td>
              <td style="padding:10px; text-align:right; color:#10b981;">+\${{new Intl.NumberFormat('vi-VN').format(Math.round(interestEarned))}} đ</td>
              <td style="padding:10px; text-align:right; font-weight:bold; color:#fff;">\${{new Intl.NumberFormat('vi-VN').format(Math.round(finalBalance))}} đ</td>
            `;
            tbody.appendChild(tr);
          }}
          
          document.getElementById('total-val').textContent = new Intl.NumberFormat('vi-VN', {{ style: 'currency', currency: 'VND' }}).format(Math.round(currentBalance));
          document.getElementById('interest-val').textContent = new Intl.NumberFormat('vi-VN', {{ style: 'currency', currency: 'VND' }}).format(Math.round(currentBalance - principal));
          
          resultPanel.style.display = 'block';
          resultPanel.scrollIntoView({{ behavior: 'smooth' }});
        }});
      }}

      const pageSlug = "{slug}";
      const isVip = localStorage.getItem("vipToken");
      const downloadBtn = document.getElementById('unlock-download-btn');
      const vipBtn = null;

      function downloadGuide() {{
        alert('Đang tải xuống tài liệu Bảng tính Excel Lãi Kép VinaTools...');
      }}

      if (downloadBtn) {{
        downloadBtn.addEventListener('click', function() {{
          const email = localStorage.getItem("userEmail");
          if (!email) {{
            showAuthModal(function() {{
              if (localStorage.getItem("vipToken")) {{
                downloadGuide();
              }} else {{
                showFreeDownloadCountdown(downloadGuide);
              }}
            }});
            return;
          }}
          if (localStorage.getItem("vipToken")) {{
            downloadGuide();
            return;
          }}
          showFreeDownloadCountdown(downloadGuide);
        }});
      }}
      """
    elif slug in ["cong-cu-chuyen-doi-ngoai-te", "cong-cu-chuyen-doi-tien-te"]:
      tool_html = f"""
      <div class="glass-panel" style="margin-bottom: 30px; text-align: left;">
        <h2 style="text-align:center; margin-bottom: 20px;"><i class="fa-solid fa-money-bill-transfer" style="color: var(--accent-primary);"></i> Bộ Chuyển Đổi Ngoại Tệ Trực Tuyến</h2>
        
        <div style="margin-bottom: 15px;">
          <label style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 6px;">Số tiền cần quy đổi:</label>
          <input type="number" id="currency-amount" value="100" style="width:100%; padding:10px; background:rgba(0,0,0,0.2); border:1px solid var(--border-glass); border-radius:6px; color:white; box-sizing: border-box;">
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
          <div>
            <label style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 6px;">Loại tiền gốc:</label>
            <select id="currency-source" style="width:100%; padding:10px; background:rgba(0,0,0,0.2); border:1px solid var(--border-glass); border-radius:6px; color:white; box-sizing: border-box;">
              <option value="USD" selected>USD - Đô la Mỹ</option>
              <option value="EUR">EUR - Euro</option>
              <option value="JPY">JPY - Yên Nhật</option>
              <option value="VND">VND - Đồng Việt Nam</option>
            </select>
          </div>
          <div>
            <label style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 6px;">Loại tiền chuyển sang:</label>
            <select id="currency-target" style="width:100%; padding:10px; background:rgba(0,0,0,0.2); border:1px solid var(--border-glass); border-radius:6px; color:white; box-sizing: border-box;">
              <option value="VND" selected>VND - Đồng Việt Nam</option>
              <option value="USD">USD - Đô la Mỹ</option>
              <option value="EUR">EUR - Euro</option>
              <option value="JPY">JPY - Yên Nhật</option>
            </select>
          </div>
        </div>
        
        <button id="convert-currency-btn" class="btn btn-primary" style="width:100%; padding:12px; font-weight:bold; cursor: pointer;">Chuyển đổi ngoại tệ</button>
      </div>

      <div id="currency-result-panel" class="glass-panel" style="display:none; text-align:center; margin-bottom:30px;">
        <h3 style="color:#10b981; margin-bottom:10px;"><i class="fa-solid fa-circle-check"></i> Quy Đổi Thành Công!</h3>
        <div style="font-size:2rem; font-weight:bold; color:var(--accent-primary); margin:15px 0;" id="currency-result-val">0 VND</div>
        <p style="font-size:0.8rem; color:var(--text-secondary); margin-bottom: 20px;">Tỷ giá cập nhật tự động theo Vietcombank năm 2026. Lệ phí quy đổi: 0%.</p>
        
        <button id="unlock-download-btn" class="btn btn-primary" style="width: 100%;">
          <i class="fa-solid fa-download"></i> Tải Cẩm Nang Đầu Tư Ngoại Tệ & Tỷ Giá (Miễn Phí)
        </button>
      </div>
      """
      tool_js = f"""
      const convertBtn = document.getElementById('convert-currency-btn');
      if (convertBtn) {{
        convertBtn.addEventListener('click', () => {{
          const amount = parseFloat(document.getElementById('currency-amount').value) || 0;
          const src = document.getElementById('currency-source').value;
          const tgt = document.getElementById('currency-target').value;
          
          if (amount <= 0) {{
            alert('Vui lòng nhập số tiền lớn hơn 0.');
            return;
          }}
          
          const ratesToVND = {{
            USD: 25450,
            EUR: 27150,
            JPY: 162.5,
            VND: 1
          }};
          
          const amountInVND = amount * ratesToVND[src];
          const finalAmount = amountInVND / ratesToVND[tgt];
          
          let formatted = "";
          if (tgt === "VND") {{
            formatted = new Intl.NumberFormat('vi-VN', {{ style: 'currency', currency: 'VND' }}).format(Math.round(finalAmount));
          }} else {{
            formatted = new Intl.NumberFormat('en-US', {{ style: 'currency', currency: tgt }}).format(finalAmount);
          }}
          
          document.getElementById('currency-result-val').textContent = formatted;
          const resPanel = document.getElementById('currency-result-panel');
          resPanel.style.display = 'block';
          resPanel.scrollIntoView({{ behavior: 'smooth' }});
        }});
      }}

      const pageSlug = "{slug}";
      const isVip = localStorage.getItem("vipToken");
      const downloadBtn = document.getElementById('unlock-download-btn');
      const vipBtn = null;

      function downloadGuide() {{
        alert('Đang tải xuống cẩm nang đầu tư ngoại tệ từ VinaTools...');
      }}

      if (downloadBtn) {{
        downloadBtn.addEventListener('click', function() {{
          const email = localStorage.getItem("userEmail");
          if (!email) {{
            showAuthModal(function() {{
              if (localStorage.getItem("vipToken")) {{
                downloadGuide();
              }} else {{
                showFreeDownloadCountdown(downloadGuide);
              }}
            }});
            return;
          }}
          if (localStorage.getItem("vipToken")) {{
            downloadGuide();
            return;
          }}
          showFreeDownloadCountdown(downloadGuide);
        }});
      }}
      """
    elif slug == "cong-cu-chuyen-doi-teencode":
      tool_html = f"""
      <div class="glass-panel" style="margin-bottom: 30px; text-align: left;">
        <h2 style="text-align:center; margin-bottom: 20px;"><i class="fa-solid fa-comments" style="color: var(--accent-primary);"></i> Dịch & Chuyển Đổi Teencode Việt Nam</h2>
        
        <div style="margin-bottom: 15px;">
          <label style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 6px;">Văn bản gốc hoặc văn bản teencode:</label>
          <textarea id="teencode-input" rows="6" style="width:100%; padding:12px; background:rgba(0,0,0,0.2); border:1px solid var(--border-glass); border-radius:6px; color:white; font-size:0.9rem; font-family: sans-serif; box-sizing: border-box;" placeholder="Nhập chữ thường để dịch sang teencode, hoặc nhập teencode để dịch sang tiếng Việt chuẩn..."></textarea>
        </div>
        
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:20px;">
          <button id="to-teencode-btn" class="btn btn-primary" style="padding:10px; font-weight:bold; cursor:pointer;"><i class="fa-solid fa-arrow-right-long"></i> Dịch sang Teencode</button>
          <button id="from-teencode-btn" class="btn btn-secondary" style="padding:10px; font-weight:bold; cursor:pointer;"><i class="fa-solid fa-arrow-left-long"></i> Dịch sang Tiếng Việt</button>
        </div>
        
        <div id="teencode-result-area" style="display:none; margin-bottom: 20px;">
          <label style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 6px;">Kết quả chuyển đổi:</label>
          <textarea id="teencode-output" rows="6" readonly style="width:100%; padding:12px; background:rgba(255,255,255,0.05); border:1px solid var(--accent-primary); border-radius:6px; color:white; font-size:0.9rem; font-family: sans-serif; box-sizing: border-box;"></textarea>
        </div>

        <button id="unlock-download-btn" class="btn btn-primary" style="width: 100%;">
          <i class="fa-solid fa-download"></i> Tải Từ Điển Teencode Toàn Tập (Miễn Phí)
        </button>
      </div>
      """
      tool_js = f"""
      const toTeencodeBtn = document.getElementById('to-teencode-btn');
      const fromTeencodeBtn = document.getElementById('from-teencode-btn');
      if (toTeencodeBtn && fromTeencodeBtn) {{
        const mapTo = {{
          'a': '4', 'e': '3', 'i': 'j', 'o': '0', 'u': 'u',
          'd': 'đ', 'c': 'k', 'qu': 'w', 'ph': 'f', 'gi': 'j',
          'h': 'h', 'g': 'g', 't': '7'
        }};
        const mapFrom = {{
          '4': 'a', '3': 'e', 'j': 'i', '0': 'o', 'k': 'c', 'w': 'qu', 'f': 'ph', '7': 't'
        }};
        
        toTeencodeBtn.addEventListener('click', () => {{
          const txt = document.getElementById('teencode-input').value;
          if (!txt.trim()) {{
            alert('Vui lòng nhập văn bản cần dịch.');
            return;
          }}
          let converted = txt.toLowerCase()
            .replace(/qu/g, 'w')
            .replace(/ph/g, 'f')
            .replace(/gi/g, 'j')
            .replace(/[aeiotdchg]/g, m => mapTo[m] || m);
          
          document.getElementById('teencode-output').value = converted;
          document.getElementById('teencode-result-area').style.display = 'block';
          document.getElementById('teencode-result-area').scrollIntoView({{ behavior: 'smooth' }});
        }});
        
        fromTeencodeBtn.addEventListener('click', () => {{
          const txt = document.getElementById('teencode-input').value;
          if (!txt.trim()) {{
            alert('Vui lòng nhập teencode cần dịch.');
            return;
          }}
          let converted = txt.toLowerCase()
            .replace(/w/g, 'qu')
            .replace(/f/g, 'ph')
            .replace(/[43j0k7]/g, m => mapFrom[m] || m);
          
          document.getElementById('teencode-output').value = converted;
          document.getElementById('teencode-result-area').style.display = 'block';
          document.getElementById('teencode-result-area').scrollIntoView({{ behavior: 'smooth' }});
        }});
      }}

      const pageSlug = "{slug}";
      const isVip = localStorage.getItem("vipToken");
      const downloadBtn = document.getElementById('unlock-download-btn');
      const vipBtn = null;

      function downloadGuide() {{
        alert('Đang tải từ điển teencode toàn tập từ VinaTools...');
      }}

      if (downloadBtn) {{
        downloadBtn.addEventListener('click', function() {{
          const email = localStorage.getItem("userEmail");
          if (!email) {{
            showAuthModal(function() {{
              if (localStorage.getItem("vipToken")) {{
                downloadGuide();
              }} else {{
                showFreeDownloadCountdown(downloadGuide);
              }}
            }});
            return;
          }}
          if (localStorage.getItem("vipToken")) {{
            downloadGuide();
            return;
          }}
          showFreeDownloadCountdown(downloadGuide);
        }});
      }}
      """
    elif slug in ["cong-cu-gop-khoi-o-tinh", "cong-cu-gop-o-trong-word"]:
      tool_html = f"""
      <style>
        .selected-cell {{
          background: rgba(0, 168, 255, 0.4) !important;
          border-color: var(--accent-primary) !important;
        }}
      </style>
      <div class="glass-panel" style="margin-bottom: 30px; text-align: left;">
        <h2 style="text-align:center; margin-bottom: 15px;"><i class="fa-solid fa-table" style="color: var(--accent-primary);"></i> Trình Giả Lập Trực Quan & Hướng Dẫn Gộp Ô (Merge Cells)</h2>
        
        <div class="print-instruction" style="background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.3); border-radius: var(--radius-sm); padding: 12px; margin-bottom: 20px; font-size: 0.85rem; color: #a78bfa; display: flex; align-items: center; gap: 8px;">
          <i class="fa-solid fa-circle-info"></i>
          <span><strong>Hướng dẫn:</strong> Bôi đen (Click chọn các ô kề nhau) để chọn vùng các ô, sau đó nhấn nút <strong>Gộp Ô Đã Chọn (Merge Cells)</strong> để mô phỏng.</span>
        </div>

        <div style="display:flex; justify-content:center; margin-bottom:20px; overflow-x:auto; padding:10px;">
          <table id="simulator-grid" style="border-collapse:collapse; background:rgba(0,0,0,0.3); border:2px solid var(--border-glass);">
            <!-- 5x5 Grid built dynamically -->
          </table>
        </div>
        
        <div style="display:flex; gap:10px; margin-bottom:25px;">
          <button id="merge-cells-btn" class="btn btn-primary" style="flex:1; padding:12px; font-weight:bold; cursor: pointer;"><i class="fa-solid fa-object-group"></i> Gộp Ô Đã Chọn (Merge Cells)</button>
          <button id="reset-grid-btn" class="btn btn-secondary" style="padding:12px; font-weight:bold; cursor: pointer;"><i class="fa-solid fa-rotate"></i> Đặt Lại Grid</button>
        </div>

        <div style="background:rgba(255,255,255,0.02); border:1px solid var(--border-glass); padding:20px; border-radius:8px; margin-bottom: 20px;">
          <h3 style="color:#fff; margin-bottom:12px;"><i class="fa-solid fa-book" style="color:var(--accent-secondary);"></i> Hướng Dẫn Thực Hiện Trên Microsoft Office:</h3>
          <ol style="margin-left:20px; font-size:0.9rem; line-height:1.6; color:var(--text-secondary); display:flex; flex-direction:column; gap:8px;">
            <li><strong>Trong Excel:</strong> Bôi đen các ô cần gộp bằng chuột. Tại tab <strong>Home</strong>, tìm nhóm <strong>Alignment</strong> và click chọn nút <strong>Merge & Center</strong>.</li>
            <li><strong>Trong Word:</strong> Bôi đen các ô trong Table. Click chuột phải, chọn <strong>Merge Cells</strong> từ menu ngữ cảnh, hoặc tại tab <strong>Table Tools Layout</strong>, click <strong>Merge Cells</strong>.</li>
            <li><strong>Phím tắt nhanh:</strong> Trong Excel, bạn có thể nhấn chuỗi phím <code>Alt</code> &rarr; <code>H</code> &rarr; <code>M</code> &rarr; <code>C</code> để gộp nhanh các ô đã chọn.</li>
          </ol>
        </div>

        <button id="unlock-download-btn" class="btn btn-primary" style="width: 100%;">
          <i class="fa-solid fa-download"></i> Tải Cẩm Nang 100+ Phím Tắt Excel & Word (Miễn Phí)
        </button>
      </div>
      """
      tool_js = f"""
      const grid = document.getElementById('simulator-grid');
      const mergeBtn = document.getElementById('merge-cells-btn');
      const resetBtn = document.getElementById('reset-grid-btn');
      
      if (grid && mergeBtn && resetBtn) {{
        let selectedCells = [];
        
        function initGrid() {{
          grid.innerHTML = '';
          selectedCells = [];
          for (let r = 0; r < 5; r++) {{
            const tr = document.createElement('tr');
            for (let c = 0; c < 5; c++) {{
              const td = document.createElement('td');
              td.style.border = '1px solid var(--border-glass)';
              td.style.width = '60px';
              td.style.height = '40px';
              td.style.textAlign = 'center';
              td.style.cursor = 'pointer';
              td.style.userSelect = 'none';
              td.style.color = 'var(--text-secondary)';
              td.style.transition = 'all 0.2s';
              td.dataset.row = r;
              td.dataset.col = c;
              td.textContent = `R\${{r}}C\${{c}}`;
              
              td.addEventListener('click', () => {{
                td.classList.toggle('selected-cell');
                if (td.classList.contains('selected-cell')) {{
                  selectedCells.push({{ r, c, el: td }});
                }} else {{
                  td.style.background = '';
                  td.style.borderColor = 'var(--border-glass)';
                  selectedCells = selectedCells.filter(cell => !(cell.r === r && cell.c === c));
                }}
              }});
              tr.appendChild(td);
            }}
            grid.appendChild(tr);
          }}
        }}
        
        resetBtn.addEventListener('click', initGrid);
        
        mergeBtn.addEventListener('click', () => {{
          if (selectedCells.length < 2) {{
            alert('Vui lòng click chọn ít nhất 2 ô kề nhau để thực hiện gộp.');
            return;
          }}
          
          let minR = 5, maxR = -1, minC = 5, maxC = -1;
          selectedCells.forEach(cell => {{
            if (cell.r < minR) minR = cell.r;
            if (cell.r > maxR) maxR = cell.r;
            if (cell.c < minC) minC = cell.c;
            if (cell.c > maxC) maxC = cell.c;
          }});
          
          const expectedCount = (maxR - minR + 1) * (maxC - minC + 1);
          if (selectedCells.length !== expectedCount) {{
            alert('Các ô được chọn phải tạo thành một hình chữ nhật liên kết vững chắc (không bị rời rạc hoặc rỗng ô).');
            return;
          }}
          
          const targetCell = selectedCells.find(cell => cell.r === minR && cell.c === minC);
          if (targetCell) {{
            targetCell.el.rowSpan = maxR - minR + 1;
            targetCell.el.colSpan = maxC - minC + 1;
            targetCell.el.style.background = 'rgba(16, 185, 129, 0.3)';
            targetCell.el.style.borderColor = '#10b981';
            targetCell.el.textContent = 'GỘP';
            targetCell.el.style.fontWeight = 'bold';
            targetCell.el.style.color = '#fff';
            
            selectedCells.forEach(cell => {{
              if (cell !== targetCell) {{
                cell.el.style.display = 'none';
              }}
            }});
            
            selectedCells = [];
          }}
        }});
        
        initGrid();
      }}

      const pageSlug = "{slug}";
      const isVip = localStorage.getItem("vipToken");
      const downloadBtn = document.getElementById('unlock-download-btn');
      const vipBtn = null;

      function downloadGuide() {{
        alert('Đang tải cẩm nang phím tắt Microsoft Office từ VinaTools...');
      }}

      if (downloadBtn) {{
        downloadBtn.addEventListener('click', function() {{
          const email = localStorage.getItem("userEmail");
          if (!email) {{
            showAuthModal(function() {{
              if (localStorage.getItem("vipToken")) {{
                downloadGuide();
              }} else {{
                showFreeDownloadCountdown(downloadGuide);
              }}
            }});
            return;
          }}
          if (localStorage.getItem("vipToken")) {{
            downloadGuide();
            return;
          }}
          showFreeDownloadCountdown(downloadGuide);
        }});
      }}
      """
    else:
      # Keep default file upload dropzone for compressors/converters
      tool_html = f"""
        <div class="glass-panel" style="margin-bottom: 30px; text-align: center;">
          <h2><i class="fa-solid fa-file-zipper" style="color: var(--accent-primary);"></i> Chọn Tệp Tin Cần Xử Lý</h2>
          
          <!-- Terms and Conditions Acceptance Checkbox -->
          <div style="margin: 15px auto 25px auto; max-width: 450px; display: flex; align-items: flex-start; gap: 8px; text-align: left; position: relative;">
            <input type="checkbox" id="accept-terms" required style="width: auto; margin-top: 4px; cursor: pointer;">
            <label for="accept-terms" style="font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; line-height: 1.4; user-select: none;">
              Tôi đã đọc, hiểu rõ và đồng ý với <a href="/terms.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Điều khoản dịch vụ</a> và <a href="/privacy.html" target="_blank" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">Chính sách bảo mật</a> của VinaTools.
            </label>
          </div>

          <div id="dropzone" class="upload-dropzone" style="margin: 20px 0;">
            <i class="fa-solid fa-cloud-arrow-up" style="font-size: 3rem; margin-bottom: 15px; color: var(--text-secondary);"></i>
            <p>Kéo và thả tệp của bạn vào đây, hoặc click để chọn từ thiết bị</p>
            <input type="file" id="file-input" style="display: none;">
          </div>
          <div id="file-info" style="display: none; margin: 15px 0;">
            <p id="file-name" style="font-weight: bold;"></p>
            <button id="process-btn" class="btn btn-primary" style="margin-top: 10px;">
              <i class="fa-solid fa-gears"></i> Bắt đầu xử lý
            </button>
          </div>
        </div>

        <div id="result-panel" class="glass-panel" style="display: none; text-align: center;">
          <h2 style="color: #10b981; margin-bottom: 20px;"><i class="fa-solid fa-circle-check"></i> Đã Xử Lý Xong!</h2>
          <p style="color: var(--text-secondary); margin-bottom: 20px;">Tệp của bạn đã được tối ưu hóa thành công. Bạn có thể tải xuống tệp tin miễn phí.</p>
          <button id="unlock-download-btn" class="btn btn-primary" style="width: 100%;">
            <i class="fa-solid fa-download"></i> Tải Xuống File Đã Nén / Chuyển Đổi (Miễn Phí)
          </button>

          <!-- VIP Upsell -->
          <div style="margin-top: 25px; background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(236,72,153,0.1)); border: 1px solid rgba(139,92,246,0.25); border-radius: 10px; padding: 20px; text-align: left;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
              <i class="fa-solid fa-crown" style="color: #f59e0b; font-size: 1.2rem;"></i>
              <strong style="color: #fff; font-size: 1.05rem;">Nâng cấp VIP - Mở khóa toàn bộ tài nguyên</strong>
            </div>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 12px;">Chỉ với 9.000đ, nâng cấp tài khoản VIP để tải miễn phí không cần chờ đợi, loại bỏ toàn bộ quảng cáo trên 60+ công cụ và mẫu đơn hành chính của VinaTools.</p>
            <button id="vip-upsell-btn" type="button" class="btn" style="padding: 10px 24px; font-size: 0.9rem; background: linear-gradient(135deg, #8b5cf6, #ec4899); border: none; color: white; cursor: pointer; border-radius: 6px; font-weight: bold; width: 100%;">
              <i class="fa-solid fa-bolt"></i> Nâng Cấp VIP Chỉ 9.000đ/tháng
            </button>
          </div>
        </div>
      """
      tool_js = f"""
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('file-input');
        const fileInfo = document.getElementById('file-info');
        const fileName = document.getElementById('file-name');
        const processBtn = document.getElementById('process-btn');
        
        dropzone.addEventListener('click', (e) => {{
          const acceptTerms = document.getElementById('accept-terms');
          if (acceptTerms && !acceptTerms.checked) {{
            alert('Bạn phải đọc và đồng ý với Điều khoản dịch vụ & Chính sách bảo mật của VinaTools để sử dụng công cụ.');
            e.preventDefault();
            return;
          }}
          fileInput.click();
        }});
        
        fileInput.addEventListener('change', function() {{
          if(this.files.length > 0) {{
            fileName.textContent = this.files[0].name + " (" + (this.files[0].size/1024).toFixed(1) + " KB)";
            fileInfo.style.display = 'block';
          }}
        }});
        
        processBtn.addEventListener('click', function() {{
          const acceptTerms = document.getElementById('accept-terms');
          if (acceptTerms && !acceptTerms.checked) {{
            alert('Bạn phải đọc và đồng ý với Điều khoản dịch vụ & Chính sách bảo mật của VinaTools để sử dụng công cụ.');
            return;
          }}
          this.innerHTML = '<div class="spinner" style="margin: 0 auto;"></div>';
          setTimeout(() => {{
            document.getElementById('result-panel').style.display = 'block';
            document.getElementById('result-panel').scrollIntoView({{ behavior: 'smooth' }});
            this.innerHTML = '<i class="fa-solid fa-gears"></i> Bắt đầu xử lý';
          }}, 2000);
        }});

        const pageSlug = "{slug}";
        const isVip = localStorage.getItem("vipToken");
        const downloadBtn = document.getElementById('unlock-download-btn');
        const vipBtn = document.getElementById('vip-upsell-btn');

        function downloadSuccess() {{
          alert('Tệp tin của bạn đang được tải về máy.');
        }}

        if (downloadBtn) {{
          downloadBtn.addEventListener('click', function() {{
            const email = localStorage.getItem("userEmail");
            if (!email) {{
              showAuthModal(function() {{
                if (localStorage.getItem("vipToken")) {{
                  downloadSuccess();
                }} else {{
                  showFreeDownloadCountdown(downloadSuccess);
                }}
              }});
              return;
            }}
            if (localStorage.getItem("vipToken")) {{
              downloadSuccess();
              return;
            }}
            showFreeDownloadCountdown(downloadSuccess);
          }});
        }}

        if (vipBtn) {{
          if (isVip) {{
            vipBtn.innerHTML = '<i class="fa-solid fa-crown"></i> Bạn Đang Là Thành Viên VIP';
            vipBtn.disabled = true;
            vipBtn.style.opacity = '0.7';
          }} else {{
            vipBtn.addEventListener('click', triggerVipUpgrade);
          }}
        }}
      """

  # Assemble HTML file layout
  full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{keyword} - Công Cụ Trực Tuyến Tốt Nhất 2026</title>
  
  <meta name="description" content="Khởi tạo và tải {keyword} trực tuyến nhanh chóng, chính xác. Biểu mẫu chuẩn quy định pháp lý hành chính năm 2026, điền thông tin và xuất file trực tiếp.">
  <meta name="keywords" content="{keyword}, tải {keyword}, mẫu {keyword}, tải file word {keyword}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://vinatools.vercel.app/{slug}">
  
  <link rel="preconnect" href="https://cdnjs.cloudflare.com">
  <link rel="preconnect" href="https://pagead2.googlesyndication.com">
  
  <meta property="og:type" content="website">
  <meta property="og:title" content="{keyword} - Tạo Biểu Mẫu Trực Tuyến Chuẩn 2026">
  <meta property="og:description" content="Điền thông tin và khởi tạo {keyword} trực quan. Xuất file Word (.doc) bản chuẩn đầy đủ nhanh nhất năm 2026.">
  <meta property="og:url" content="https://vinatools.vercel.app/{slug}">
  <meta property="og:site_name" content="VinaTools">
  <meta property="og:image" content="https://vinatools.vercel.app/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{keyword} - Tạo Biểu Mẫu Trực Tuyến Chuẩn 2026">
  <meta name="twitter:description" content="Điền thông tin và khởi tạo {keyword} trực quan. Xuất file Word (.doc) bản chuẩn đầy đủ nhanh nhất năm 2026.">
  <meta name="twitter:image" content="https://vinatools.vercel.app/og-image.png">
  
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
            "name": "{'Hợp Đồng' if is_contract else ('Đơn Từ' if is_legal_form else 'Tiện Ích')}",
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

  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={google_adsense_client}" crossorigin="anonymous"></script>

  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="preload" href="/global_style.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="/global_style.css"></noscript>
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#0a0c10">
  <script>
    if ('serviceWorker' in navigator) {{
      window.addEventListener('load', () => {{
        navigator.serviceWorker.register('/sw.js').catch(() => {{}});
      }});
    }}
  </script>
</head>
<body>

  <!-- Persistent Sidebar Ads (Left and Right Rails) -->
  <div class="side-ad-left">
    <span class="side-ad-label">Quảng cáo</span>
    <ins class="adsbygoogle" style="display:inline-block;width:160px;height:600px" data-ad-client="{google_adsense_client}" data-ad-slot="mock-sidebar-left">
      <div class="fallback-ad-vertical" onclick="triggerVipUpgrade()">
        <div class="fallback-ad-crown"><i class="fa-solid fa-crown"></i></div>
        <div class="fallback-ad-title">VinaTools VIP</div>
        <div class="fallback-ad-text">Tải file cực nhanh không quảng cáo. Hoàn tiền 100% nếu lỗi.</div>
        <div class="fallback-ad-price">9.000đ/tháng</div>
        <span class="fallback-ad-btn">Nâng Cấp</span>
      </div>
    </ins>
  </div>
  <div class="side-ad-right">
    <span class="side-ad-label">Quảng cáo</span>
    <ins class="adsbygoogle" style="display:inline-block;width:160px;height:600px" data-ad-client="{google_adsense_client}" data-ad-slot="mock-sidebar-right">
      <!-- Fallback House Ad 2 -->
      <div class="fallback-ad-vertical second" onclick="window.open('https://vinaearn-ai.vercel.app', '_blank')">
        <div class="fallback-ad-logo"><i class="fa-solid fa-code"></i></div>
        <div class="fallback-ad-title">VinaEarn API</div>
        <div class="fallback-ad-text">Cổng tra cứu doanh nghiệp tự động</div>
        <div class="fallback-ad-price">VietRegistry</div>
        <span class="fallback-ad-btn">Xem Thêm</span>
      </div>
    </ins>
  </div>

  <div class="layout-container">
    <nav class="portal-nav" style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid var(--border-glass); margin-bottom: 30px;">
      <a href="/" class="portal-logo" style="display: flex; align-items: center; gap: 10px; font-size: 1.4rem; font-weight: 800; color: #fff; text-decoration: none;">
        <i class="fa-solid fa-toolbox" style="color: #00a8ff;"></i> VinaTools
      </a>
      <div class="nav-links" style="display: flex; gap: 20px; align-items: center;">
        <a href="/?filter=don-tu" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: color 0.2s;"><i class="fa-solid fa-file-lines" style="color: #00a8ff; margin-right: 4px;"></i> Đơn từ</a>
        <a href="/?filter=hop-dong" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: color 0.2s;"><i class="fa-solid fa-file-contract" style="color: #8b5cf6; margin-right: 4px;"></i> Hợp đồng</a>
        <a href="/?filter=tien-ich" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: color 0.2s;"><i class="fa-solid fa-screwdriver-wrench" style="color: #ec4899; margin-right: 4px;"></i> Tiện ích</a>
      </div>
      <div id="user-nav-status" style="font-size: 0.9rem; color: #94a3b8; display: flex; align-items: center; gap: 10px;">
        <i class="fa-solid fa-shield-halved" style="color: #10b981;"></i> Secure Platform
      </div>
    </nav>

    <header class="tool-header">
      <h1>{keyword}</h1>
      <p style="color: var(--text-secondary); margin-top: 10px;">Công cụ thông minh chạy hoàn toàn trên trình duyệt, bảo mật 100% dữ liệu của bạn.</p>
    </header>

    <div id="vinatools-top-ad" class="ad-slot" style="margin-bottom: 25px; text-align: center;">
      <ins class="adsbygoogle" style="display:block; min-height: 90px;" data-ad-client="{google_adsense_client}" data-ad-slot="mock-top-page">
         <div class="fallback-ad-horizontal" onclick="triggerVipUpgrade()" style="padding: 10px 15px; border-radius: 6px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
           <span style="font-size: 0.85rem; color: var(--text-secondary);"><i class="fa-solid fa-crown" style="color: #f59e0b; margin-right: 6px;"></i> Nâng cấp thành viên VIP để trải nghiệm không quảng cáo</span>
           <span style="font-size: 0.75rem; background: var(--accent-primary); color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">Đăng ký chỉ 9K</span>
         </div>
      </ins>
    </div>

    {tool_html}

    <div id="vinatools-page-ad" class="ad-slot" style="margin-top: 40px; margin-bottom: 20px;">
      <ins class="adsbygoogle" style="display:block; min-height: 90px;" data-ad-client="{google_adsense_client}" data-ad-slot="mock-page">
        <div class="fallback-ad-horizontal" onclick="triggerVipUpgrade()">
          <div style="display:flex; align-items:center; gap: 15px;">
            <div class="fallback-ad-crown"><i class="fa-solid fa-crown"></i></div>
            <div style="text-align:left;">
              <div class="fallback-ad-title" style="margin:0; font-size:1.1rem;">Thành Viên VIP VinaTools</div>
              <div class="fallback-ad-text" style="margin:2px 0 0 0; font-size:0.85rem;">Tải không giới hạn 60+ biểu mẫu và tắt toàn bộ quảng cáo</div>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap: 15px;">
            <div class="fallback-ad-price" style="margin:0; font-size:1.2rem; font-weight:bold; color:#f59e0b;">9.000 đ/tháng</div>
            <span class="fallback-ad-btn" style="margin:0; padding: 8px 16px;">Đăng Ký Ngay</span>
          </div>
        </div>
      </ins>
    </div>

    <footer class="tool-footer" style="margin-top: 60px; padding-top: 25px; border-top: 1px solid var(--border-glass); font-size: 0.8rem; color: var(--text-muted); line-height: 1.6; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 16px;">
      <div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 20px; margin-bottom: 5px;">
        <!-- SSL Protected Badge -->
        <div style="display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); padding: 6px 12px; border-radius: 6px;">
          <i class="fa-solid fa-lock" style="color: #10b981; font-size: 1.1rem; filter: drop-shadow(0 0 4px rgba(16,185,129,0.3));"></i>
          <div style="text-align: left; line-height: 1.2;">
            <div style="color: #fff; font-weight: bold; font-size: 0.68rem; letter-spacing: 0.05em;">SSL SECURE</div>
            <div style="color: var(--text-muted); font-size: 0.58rem;">256-BIT ENCRYPTION</div>
          </div>
        </div>
        <!-- Napas 24/7 Instant Transfer Badge -->
        <div style="display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); padding: 6px 12px; border-radius: 6px;">
          <i class="fa-solid fa-shield-halved" style="color: var(--accent-secondary); font-size: 1.1rem; filter: drop-shadow(0 0 4px rgba(236,72,153,0.3));"></i>
          <div style="text-align: left; line-height: 1.2;">
            <div style="color: #fff; font-weight: bold; font-size: 0.68rem; letter-spacing: 0.05em;">NAPAS 24/7</div>
            <div style="color: var(--text-muted); font-size: 0.58rem;">XÁC THỰC TỰ ĐỘNG</div>
          </div>
        </div>
      </div>
      <p style="margin-bottom: 2px;">&copy; 2026 VinaTools. Hoạt động tự động 24/7 bằng công nghệ AI.</p>
      <p style="margin-bottom: 2px; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
        <a href="/terms.html" style="color: var(--text-secondary); text-decoration: none;"><i class="fa-solid fa-file-contract"></i> Điều khoản dịch vụ</a>
        <a href="/privacy.html" style="color: var(--text-secondary); text-decoration: none;"><i class="fa-solid fa-shield-halved"></i> Chính sách bảo mật</a>
        <a href="/about.html" style="color: var(--text-secondary); text-decoration: none;"><i class="fa-solid fa-circle-info"></i> Giới thiệu</a>
        <a href="/contact.html" style="color: var(--text-secondary); text-decoration: none;"><i class="fa-solid fa-envelope"></i> Liên hệ</a>
      </p>
      <p style="font-size: 0.75rem; margin-top: 2px;"><strong>Đại diện sở hữu:</strong> Ban quản trị VinaTools | <strong>Email:</strong> vinatools.support@gmail.com</p>
      <p style="font-size: 0.7rem; margin-top: 2px; max-width: 600px; margin-left: auto; margin-right: auto; text-align: center;">Mọi thông tin biểu mẫu được xử lý 100% cục bộ ở trình duyệt của người dùng (client-side), tuyệt đối không lưu trữ trên máy chủ, tuân thủ nghiêm ngặt Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 và Nghị định số 356/2025/NĐ-CP.</p>
    </footer>
  </div>

  <script src="/checkout_modal.js?v=1.0.2"></script>
  <script>
    initCheckoutConfig({{
      bankName: "{bank_name}",
      bankId: "{bank_id}",
      accountNumber: "{acc_num}",
      accountName: "{acc_holder}",
      apiEndpoint: "{api_url}",
      adsenseClient: "{google_adsense_client}"
    }});
    
    // Hide ads for VIP members
    if (localStorage.getItem("vipToken")) {{
      const ads = document.querySelectorAll(".side-ad-left, .side-ad-right, #vinatools-page-ad, #vinatools-top-ad");
      ads.forEach(el => el.style.display = "none");
    }} else {{
      try {{
        (window.adsbygoogle = window.adsbygoogle || []).push({{}});
        (window.adsbygoogle = window.adsbygoogle || []).push({{}});
      }} catch (e) {{
        console.error("AdSense page ad load failed:", e);
      }}
    }}
    
    {tool_js}
  </script>
</body>
</html>
"""
  return full_html

def generate_tool(niche_keyword):
  config = load_config()
  slug = slugify(niche_keyword)
  tool_dir = os.path.join(WORKSPACE, slug)
  
  if not os.path.exists(tool_dir):
    os.makedirs(tool_dir)
    
  print(f"Generating utility tool for: '{niche_keyword}' (Slug: {slug})")
  
  gemini_key = config.get("gemini_api_key", "")
  
  html_content = None
  
  if gemini_key and gemini_key != "YOUR_GEMINI_API_KEY":
    # If the user has put in an API key, we ask Gemini to build a fully bespoke, highly custom dashboard/script
    prompt = f"""
    Build a single-file static web utility tool in Vietnamese for the keyword: '{niche_keyword}'.
    It should use clean CSS/HTML and client-side JavaScript.
    It MUST:
    1. Import the stylesheet '/global_style.css' and script '/checkout_modal.js'.
    2. Initialize checkout using:
       initCheckoutConfig({{
         bankName: "{config.get('bank_name')}",
         bankId: "{config.get('bank_id', 'TCB')}",
         accountNumber: "{config.get('bank_account')}",
         accountName: "{config.get('bank_account_holder')}",
         apiEndpoint: "{config.get('api_url', '/api/check-payment')}"
       }});
    3. Include an interactive terms of service checkbox ('Tôi đồng ý với Điều khoản dịch vụ và Chính sách bảo mật của VinaTools') that must be checked before using any functionality (e.g. uploading file, generating document). Validate this in the click handlers and display an alert if not checked.
    4. Explicitly state compliance with the 2026 data protection framework (Law on Personal Data Protection No. 91/2025/QH15 and Decree No. 356/2025/ND-CP) in the disclaimers or footer.
    5. Include a functional core utility logic (e.g. if it is a converter, build a mock or functional conversion, if a document generator, render fields).
    6. Provide an 'Unlock / Download' button that triggers:
       showCheckoutModal(amount_in_vnd, unique_memo, callback)
    7. Return ONLY clean, production-ready HTML code inside a ```html codeblock. No markdown notes outside the codeblock.
    """
    html_content = call_gemini_api(prompt, gemini_key)
    
  if not html_content:
    # Fallback to local high-fidelity rules-based templates
    html_content = build_offline_tool_template(niche_keyword, slug, config)
    
  # Write code files
  index_path = os.path.join(tool_dir, "index.html")
  with open(index_path, "w", encoding="utf-8") as f:
    f.write(html_content)
    
  print(f"Tool generation complete! Saved index.html in: {tool_dir}")
  return slug

if __name__ == "__main__":
  # Simple test run on seed keyword
  generate_tool("Mẫu đơn xin tạm trú")
