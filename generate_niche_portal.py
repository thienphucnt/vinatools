import json
import os

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
DEPLOYED_LOG = os.path.join(WORKSPACE, "deployed_tools.json")

def generate_index():
    if not os.path.exists(DEPLOYED_LOG):
        print("No deployed tools found. Skipping niche portal generation.")
        return
        
    with open(DEPLOYED_LOG, "r", encoding="utf-8") as f:
        tools = json.load(f)
        
    # Load config to get Google AdSense Client
    config_path = os.path.join(WORKSPACE, "config.json")
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Failed to load config.json: {e}")
            
    google_adsense_client = config.get("google_adsense_client", "ca-pub-mock")
    bank_name = config.get("bank_name", "Techcombank")
    bank_id = config.get("bank_id", "TCB")
    acc_num = config.get("bank_account", "")
    acc_holder = config.get("bank_account_holder", "")
    api_url = config.get("api_url", "/api/check-payment")
        
    print(f"Generating niche portal directory for {len(tools)} tools...")
    
    # Categorize tools based on keyword name
    cards_html = ""
    for tool in tools:
        kw = tool["keyword"]
        slug = tool["slug"]
        
        # Determine category and icon
        if "hợp đồng" in kw.lower():
            category = "hop-dong"
            category_label = "Hợp đồng"
            icon = "fa-file-contract"
            color_class = "violet"
            desc = f"Khởi tạo {kw} trực tuyến. Cập nhật các điều khoản mới nhất, xuất file Word (.docx) chuẩn pháp lý nhanh chóng."
        elif "đơn" in kw.lower():
            category = "don-tu"
            category_label = "Đơn từ"
            icon = "fa-file-signature"
            color_class = "teal"
            desc = f"Mẫu {kw} chuẩn quy định hành chính. Điền thông tin trực quan, tải file xem trước và bản chuẩn tức thì."
        else:
            category = "tien-ich"
            category_label = "Tiện ích"
            icon = "fa-toolbox"
            color_class = "pink"
            desc = f"Công cụ hỗ trợ {kw} trực tuyến, xử lý dữ liệu tự động, bảo mật và an toàn tuyệt đối."
            
        cards_html += f"""
        <article class="glass-panel feature-card {color_class} tool-card" data-category="{category}" data-keyword="{kw.lower()}">
          <div class="feature-icon">
            <i class="fa-solid {icon}"></i>
          </div>
          <span class="tool-badge">{category_label}</span>
          <h4 class="feature-title" style="margin-top: 12px; font-size: 1.15rem; color: #fff;">{kw.capitalize()}</h4>
          <p class="feature-desc" style="margin-top: 8px; font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">{desc}</p>
          <div style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.75rem; color: var(--text-muted);"><i class="fa-solid fa-fire" style="color: #f59e0b; margin-right: 4px;"></i> {tool.get('estimated_volume', 1000)} lượt tìm kiếm</span>
            <a href="/{slug}" class="btn" style="padding: 8px 16px; font-size: 0.8rem; border-radius: 6px;">Sử dụng <i class="fa-solid fa-arrow-right" style="font-size: 0.75rem;"></i></a>
          </div>
        </article>
        """

    full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VinaTools - Thư Viện Mẫu Đơn Từ Hành Chính &amp; Hợp Đồng Pháp Lý Trực Tuyến 2026</title>
  
  <!-- SEO Meta Tags -->
  <meta name="description" content="VinaTools - Thư viện 35+ mẫu đơn từ hành chính, mẫu hợp đồng lao động, hợp đồng dịch vụ chuẩn quy định pháp luật 2026. Điền thông tin trực tuyến, xem trước A4, tải file Word miễn phí. Đơn xin việc, đơn xin phép, đơn xin nghỉ việc và nhiều biểu mẫu khác.">
  <meta name="keywords" content="mẫu đơn xin việc, mẫu hợp đồng lao động, đơn xin nghỉ phép, đơn xin tạm trú, mẫu đơn hành chính, biểu mẫu trực tuyến, mẫu hợp đồng dịch vụ, đơn xin thôi việc, vinatools">
  <meta name="author" content="VinaTools">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <meta name="google-site-verification" content="sFH2HKNSUZ5RjFpF5tNCnfjBTWMGRTajAHA4_by0mhE">
  
  <!-- Canonical URL -->
  <link rel="canonical" href="https://vinatools.vercel.app">
  
  <link rel="preconnect" href="https://cdnjs.cloudflare.com">
  <link rel="preconnect" href="https://pagead2.googlesyndication.com">
  
  <!-- Language / Locale -->
  <link rel="alternate" hreflang="vi" href="https://vinatools.vercel.app">
  <link rel="alternate" hreflang="x-default" href="https://vinatools.vercel.app">
  <meta property="og:locale" content="vi_VN">
  
  <!-- Open Graph Tags -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="VinaTools - Thư Viện Mẫu Đơn Từ &amp; Hợp Đồng Trực Tuyến 2026">
  <meta property="og:description" content="35+ mẫu đơn từ hành chính, hợp đồng pháp lý chuẩn quy định. Điền thông tin trực quan, xem trước A4, tải file Word nhanh chóng.">
  <meta property="og:url" content="https://vinatools.vercel.app">
  <meta property="og:site_name" content="VinaTools">
  <meta property="og:image" content="https://vinatools.vercel.app/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  
  <!-- Twitter Card Tags -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="VinaTools - Thư Viện Mẫu Đơn Từ &amp; Hợp Đồng Trực Tuyến 2026">
  <meta name="twitter:description" content="35+ mẫu đơn từ hành chính, hợp đồng pháp lý chuẩn quy định. Điền thông tin trực quan, xem trước A4, tải file Word nhanh chóng.">
  <meta name="twitter:image" content="https://vinatools.vercel.app/og-image.png">
  
  <!-- JSON-LD WebSite Schema -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "VinaTools",
    "url": "https://vinatools.vercel.app",
    "potentialAction": {{
      "@type": "SearchAction",
      "target": "https://vinatools.vercel.app/?q={{search_term_string}}",
      "query-input": "required name=search_term_string"
    }}
  }}
  </script>

  <!-- Google AdSense -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={google_adsense_client}" crossorigin="anonymous"></script>

  <!-- Font Awesome -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <!-- Stylesheets -->
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
  
  <style>
    body {{
      padding: 0 !important;
      margin: 0;
      background-color: #0a0c10;
    }}
    
    .portal-container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 20px;
    }}
    
    header.hero-section {{
      text-align: center;
      padding: 100px 0 60px 0;
      background: radial-gradient(circle, rgba(0, 168, 255, 0.1) 0%, transparent 60%);
    }}
    
    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(0, 168, 255, 0.1);
      color: #00a8ff;
      border: 1px solid rgba(0, 168, 255, 0.2);
      padding: 6px 16px;
      border-radius: 100px;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 24px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    
    .hero-title {{
      font-size: 3rem;
      margin-bottom: 20px;
      background: linear-gradient(135deg, #fff 40%, #00a8ff 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      font-family: var(--font-display);
      line-height: 1.2;
    }}
    
    .hero-subtitle {{
      font-size: 1.2rem;
      color: var(--text-secondary);
      max-width: 700px;
      margin: 0 auto 40px auto;
      line-height: 1.6;
    }}
    
    /* Navigation Bar */
    .portal-nav {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 24px 0;
      border-bottom: 1px solid var(--border-glass);
      position: sticky;
      top: 0;
      background: rgba(10, 12, 16, 0.8);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      z-index: 1000;
    }}
    
    .portal-logo {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 1.4rem;
      font-weight: 800;
      font-family: var(--font-display);
      color: white;
      text-decoration: none;
    }}
    
    .portal-logo i {{
      color: #00a8ff;
      filter: drop-shadow(0 0 8px #00a8ff);
    }}
    
    /* Search & Filter Panel */
    .filter-panel {{
      display: flex;
      flex-direction: column;
      gap: 20px;
      margin-bottom: 40px;
      padding: 24px;
    }}
    
    .search-row {{
      display: flex;
      position: relative;
    }}
    
    .search-icon {{
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-secondary);
    }}
    
    .search-input {{
      padding-left: 48px !important;
    }}
    
    .category-tabs {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    
    .category-btn {{
      background: rgba(255,255,255,0.02);
      border: 1px solid var(--border-glass);
      color: var(--text-secondary);
      padding: 8px 18px;
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      border-radius: var(--radius-sm);
      transition: var(--transition-smooth);
    }}
    
    .category-btn:hover, .category-btn.active {{
      background: rgba(0, 168, 255, 0.1);
      border-color: rgba(0, 168, 255, 0.3);
      color: white;
    }}
    
    /* Tools Grid */
    .tools-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 24px;
      margin-bottom: 80px;
    }}
    
    @media (max-width: 992px) {{
      .tools-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}
    
    @media (max-width: 600px) {{
      .tools-grid {{
        grid-template-columns: 1fr;
      }}
    }}
    
    .feature-card {{
      padding: 24px;
      display: flex;
      flex-direction: column;
      position: relative;
    }}
    
    .feature-icon {{
      width: 44px;
      height: 44px;
      border-radius: var(--radius-sm);
      background: rgba(0, 168, 255, 0.1);
      border: 1px solid rgba(0, 168, 255, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #00a8ff;
      font-size: 1.15rem;
    }}
    
    .feature-card.violet .feature-icon {{
      background: rgba(139, 92, 246, 0.1);
      border-color: rgba(139, 92, 246, 0.2);
      color: #8b5cf6;
    }}
    
    .feature-card.pink .feature-icon {{
      background: rgba(236, 72, 153, 0.1);
      border-color: rgba(236, 72, 153, 0.2);
      color: #ec4899;
    }}
    
    .tool-badge {{
      position: absolute;
      top: 24px;
      right: 24px;
      font-size: 0.75rem;
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border-glass);
      color: var(--text-secondary);
      padding: 4px 10px;
      border-radius: 4px;
      font-weight: 500;
    }}
    
    /* Footer */
    .portal-footer {{
      border-top: 1px solid var(--border-glass);
      padding: 40px 0;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
    }}
  </style>
<body class="portal-body">

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

  <div class="portal-container">
    
    <!-- Navigation -->
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
        <i class="fa-solid fa-server" style="color: #10b981;"></i> Hoạt động 24/7
      </div>
    </nav>
    
    <!-- Hero Banner -->
    <header class="hero-section">
      <div class="hero-badge">
        <i class="fa-solid fa-wand-magic-sparkles" style="color: #00a8ff;"></i> Đăng ký biểu mẫu tự động bằng AI
      </div>
      <h1 class="hero-title">VinaTools Directory</h1>
      <p class="hero-subtitle">
        Thư viện công cụ trực tuyến và các mẫu đơn từ hành chính, mẫu hợp đồng dân sự chuẩn quy định pháp luật. Điền thông tin trực quan, xem trước định dạng chuẩn A4 và tải xuống file Word nhanh chóng.
      </p>
    </header>
    
    <!-- Filters & Search -->
    <section class="glass-panel filter-panel">
      <div class="search-row">
        <i class="fa-solid fa-magnifying-glass search-icon"></i>
        <input type="text" id="search-bar" class="search-input" placeholder="Tìm kiếm mẫu đơn, hợp đồng hoặc công cụ tiện ích... (ví dụ: tạm trú, lao động)">
      </div>
      
      <div class="category-tabs">
        <button class="category-btn active" data-filter="all">Tất cả ({len(tools)} công cụ)</button>
        <button class="category-btn" data-filter="don-tu">Đơn từ hành chính</button>
        <button class="category-btn" data-filter="hop-dong">Hợp đồng pháp lý</button>
        <button class="category-btn" data-filter="tien-ich">Công cụ tiện ích</button>
      </div>
    </section>
    
    <!-- Grid List -->
    <section class="tools-grid" id="tools-list">
      {cards_html}
    </section>
    
    <!-- Ad Slot: Between tools and FAQ -->
    <div id="vinatools-portal-ad" class="ad-slot" style="grid-column: 1 / -1; margin-bottom: 40px;">
      <ins class="adsbygoogle" style="display:block" data-ad-client="{google_adsense_client}" data-ad-slot="mock-page" data-ad-format="auto" data-full-width-responsive="true">
        <!-- Fallback Horizontal Banner -->
        <div class="fallback-ad-horizontal" onclick="triggerVipUpgrade()">
          <div style="display:flex; align-items:center; gap: 15px;">
            <div class="fallback-ad-crown"><i class="fa-solid fa-crown"></i></div>
            <div style="text-align:left;">
              <div class="fallback-ad-title" style="margin:0; font-size:1.1rem;">Thành Viên VIP VinaTools</div>
              <div class="fallback-ad-text" style="margin:2px 0 0 0; font-size:0.85rem; color:#a3a3a3;">Tải trọn bộ VIP Bundle, in trực tiếp và tắt sạch quảng cáo. <strong>Cam kết hoàn tiền 100% trong vòng 7 ngày!</strong></div>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap: 15px;">
            <div class="fallback-ad-price" style="margin:0; font-size:1.2rem; font-weight:bold; color:#f59e0b;">9.000 đ/tháng</div>
            <span class="fallback-ad-btn" style="margin:0; padding: 8px 16px;">Đăng Ký Ngay</span>
          </div>
        </div>
      </ins>
    </div>

    <!-- FAQ Section for SEO -->
    <section class="glass-panel" style="margin-bottom: 40px; padding: 30px; grid-column: 1 / -1;" id="faq">
      <h2 style="color: #fff; margin-bottom: 24px; font-size: 1.5rem;">
        <i class="fa-solid fa-circle-question" style="color: #00a8ff; margin-right: 8px;"></i>
        Câu Hỏi Thường Gặp (FAQ)
      </h2>
      <div style="display: grid; gap: 16px;">
        <details style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 16px;">
          <summary style="cursor: pointer; font-weight: 600; color: #fff; font-size: 1rem;">VinaTools là gì?</summary>
          <p style="margin-top: 12px; color: var(--text-secondary); line-height: 1.7; font-size: 0.9rem;">VinaTools là thư viện trực tuyến cung cấp các mẫu đơn từ hành chính và hợp đồng pháp lý chuẩn quy định pháp luật Việt Nam. Người dùng có thể điền thông tin trực quan, xem trước định dạng A4 và tải xuống file Word (.docx) nhanh chóng.</p>
        </details>
        <details style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 16px;">
          <summary style="cursor: pointer; font-weight: 600; color: #fff; font-size: 1rem;">Làm sao để tải mẫu đơn xin việc trên VinaTools?</summary>
          <p style="margin-top: 12px; color: var(--text-secondary); line-height: 1.7; font-size: 0.9rem;">Bạn chỉ cần truy cập trang mẫu đơn xin việc mong muốn, nhập thông tin đầy đủ vào biểu mẫu trực tuyến, nhấn 'Xem trước' để kiểm tra bản nháp và chọn 'Mở khóa / Tải xuống' để xem quảng cáo tài trợ và tải file Word bản chuẩn sạch hoàn toàn miễn phí.</p>
        </details>
        <details style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 16px;">
          <summary style="cursor: pointer; font-weight: 600; color: #fff; font-size: 1rem;">VinaTools có an toàn không?</summary>
          <p style="margin-top: 12px; color: var(--text-secondary); line-height: 1.7; font-size: 0.9rem;">Toàn bộ quá trình điền thông tin của bạn được thực hiện cục bộ trên trình duyệt của bạn và không lưu giữ thông tin nhạy cảm của người dùng trên bất kỳ máy chủ nào. Thanh toán nâng cấp VIP được xử lý an toàn thông qua cổng chuyển khoản tự động Techcombank VietQR.</p>
        </details>
      </div>
    </section>

    <!-- Footer -->
    <footer class="portal-footer" style="grid-column: 1 / -1;">
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 30px; text-align: left; margin-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 40px;">
        <div>
          <h3 style="color: #fff; font-size: 0.95rem; margin-bottom: 12px;">Về VinaTools</h3>
          <p style="font-size: 0.8rem; line-height: 1.6;">VinaTools cung cấp các giải pháp tự động hóa biểu mẫu, giúp cá nhân và doanh nghiệp tiết kiệm hàng giờ soạn thảo văn bản hành chính.</p>
        </div>
        <div>
          <h3 style="color: #fff; font-size: 0.95rem; margin-bottom: 12px;">Mẫu Đơn Phổ Thông</h3>
          <nav>
            <a href="/mau-don-xin-viec-chuan" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;">Đơn xin việc chuẩn</a>
            <a href="/mau-don-xin-phep-nghi-hoc" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;">Đơn xin nghỉ học</a>
            <a href="/mau-don-xin-tam-tru" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;">Đơn xin tạm trú</a>
            <a href="/mau-don-xin-thuc-tap" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;">Đơn xin thực tập</a>
          </nav>
        </div>
        <div>
          <h3 style="color: #fff; font-size: 0.95rem; margin-bottom: 12px;">Mẫu Hợp Đồng</h3>
          <nav>
            <a href="/mau-hop-dong-lao-dong-2026" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;">Hợp đồng lao động 2026</a>
            <a href="/mau-hop-dong-dich-vu" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;">Hợp đồng dịch vụ</a>
            <a href="/mau-hop-dong-cho-thue-mat-bang" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;">Hợp đồng thuê mặt bằng</a>
            <a href="/mau-hop-dong-cho-thue-nha" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;">Hợp đồng thuê nhà</a>
          </nav>
        </div>
        <div>
          <h3 style="color: #fff; font-size: 0.95rem; margin-bottom: 12px;">Chính Sách & Hỗ Trợ</h3>
          <nav>
            <a href="/terms.html" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;"><i class="fa-solid fa-file-contract" style="width: 16px;"></i> Điều khoản dịch vụ</a>
            <a href="/privacy.html" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;"><i class="fa-solid fa-shield-halved" style="width: 16px;"></i> Chính sách bảo mật</a>
            <a href="/about.html" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;"><i class="fa-solid fa-circle-info" style="width: 16px;"></i> Giới thiệu</a>
            <a href="/contact.html" style="display: block; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 6px; text-decoration: none;"><i class="fa-solid fa-envelope" style="width: 16px;"></i> Liên hệ ban quản trị</a>
          </nav>
        </div>
      </div>
      <div style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 25px; font-size: 0.75rem; color: var(--text-muted); line-height: 1.6; display: flex; flex-direction: column; align-items: center; gap: 16px;">
        <div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 24px; margin-bottom: 10px;">
          <!-- SSL Protected Badge -->
          <div style="display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 8px 16px; border-radius: 8px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);">
            <i class="fa-solid fa-lock" style="color: #10b981; font-size: 1.2rem; filter: drop-shadow(0 0 5px rgba(16,185,129,0.4));"></i>
            <div style="text-align: left; line-height: 1.2;">
              <div style="color: #fff; font-weight: bold; font-size: 0.72rem; letter-spacing: 0.05em;">SSL SECURE</div>
              <div style="color: var(--text-muted); font-size: 0.62rem; letter-spacing: 0.02em;">256-BIT ENCRYPTION</div>
            </div>
          </div>
          <!-- Napas 24/7 Instant Transfer Badge -->
          <div style="display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 8px 16px; border-radius: 8px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);">
            <i class="fa-solid fa-shield-halved" style="color: var(--accent-secondary); font-size: 1.2rem; filter: drop-shadow(0 0 5px rgba(236,72,153,0.4));"></i>
            <div style="text-align: left; line-height: 1.2;">
              <div style="color: #fff; font-weight: bold; font-size: 0.72rem; letter-spacing: 0.05em;">NAPAS 24/7</div>
              <div style="color: var(--text-muted); font-size: 0.62rem; letter-spacing: 0.02em;">XÁC THỰC TỰ ĐỘNG</div>
            </div>
          </div>
        </div>
        <p>© 2026 VinaTools - Thư viện mẫu đơn từ hành chính và hợp đồng pháp lý trực tuyến.</p>
        <p style="margin-top: 4px;"><strong>Đại diện sở hữu:</strong> Ban quản trị VinaTools | <strong>Địa chỉ liên hệ:</strong> Quận 1, Thành phố Hồ Chí Minh, Việt Nam | <strong>Email:</strong> vinatools.support@gmail.com</p>
        <p style="margin-top: 4px; max-width: 800px; margin-left: auto; margin-right: auto; text-align: center;"><strong>Tuyên bố tuân thủ:</strong> Hệ thống hoạt động hoàn toàn tự động client-side trên trình duyệt người dùng. Mọi thông tin biểu mẫu được xử lý bảo mật cục bộ, tuân thủ Luật An ninh mạng 2018, Luật Bảo vệ dữ liệu cá nhân (Luật số 91/2025/QH15) và Nghị định số 356/2025/NĐ-CP.</p>
      </div>
    </footer>
  </div>

  <script src="/checkout_modal.js?v=1.0.2"></script>
  <script>
    // Search & Category Filtering Logic
    const searchBar = document.getElementById('search-bar');
    const filterBtns = document.querySelectorAll('.category-btn');
    const toolCards = document.querySelectorAll('.tool-card');
    
    let currentFilter = 'all';
    let searchQuery = '';
    
    function filterCards() {{
      toolCards.forEach(card => {{
        const cardCategory = card.getAttribute('data-category');
        const cardKeyword = card.getAttribute('data-keyword');
        
        const matchesCategory = currentFilter === 'all' || cardCategory === currentFilter;
        const matchesSearch = cardKeyword.includes(searchQuery);
        
        if (matchesCategory && matchesSearch) {{
          card.style.display = 'flex';
        }} else {{
          card.style.display = 'none';
        }}
      }});
    }}
    
    searchBar.addEventListener('input', function(e) {{
      searchQuery = e.target.value.toLowerCase().trim();
      filterCards();
    }});
    
    filterBtns.forEach(btn => {{
      btn.addEventListener('click', function() {{
        filterBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        currentFilter = this.getAttribute('data-filter');
        filterCards();
      }});
    }});

    // Parse URL parameter on load to set pre-filter
    const urlParams = new URLSearchParams(window.location.search);
    const filterParam = urlParams.get('filter');
    if (filterParam) {{
      currentFilter = filterParam;
      filterBtns.forEach(b => {{
        if (b.getAttribute('data-filter') === filterParam) {{
          b.classList.add('active');
        }} else {{
          b.classList.remove('active');
        }}
      }});
      filterCards();
    }}

    initCheckoutConfig({{
      bankName: "{bank_name}",
      bankId: "{bank_id}",
      accountNumber: "{acc_num}",
      accountName: "{acc_holder}",
      apiEndpoint: "{api_url}"
    }});

    function triggerVipUpgrade() {{
      const email = localStorage.getItem("userEmail");
      if (!email) {{
        showAuthModal(function(registeredEmail) {{
          proceedToVipUpgrade();
        }});
      }} else {{
        proceedToVipUpgrade();
      }}
    }}

    function proceedToVipUpgrade() {{
      const memo = "VE_VIP_" + Math.floor(Date.now() / 1000).toString().slice(-6);
      showCheckoutModal(9000, memo, function(token) {{
        localStorage.setItem("vipToken", token);
        alert('Chúc mừng! Bạn đã nâng cấp VIP thành viên thành công.');
        location.reload();
      }});
    }}
    window.triggerVipUpgrade = triggerVipUpgrade;

    // Initialize Google AdSense
    document.addEventListener("DOMContentLoaded", function() {{
      if (localStorage.getItem("vipToken")) {{
        const ads = document.querySelectorAll(".side-ad-left, .side-ad-right, #vinatools-portal-ad");
        ads.forEach(el => el.style.display = "none");
      }} else {{
        try {{
          (window.adsbygoogle = window.adsbygoogle || []).push({{}});
          (window.adsbygoogle = window.adsbygoogle || []).push({{}});
          (window.adsbygoogle = window.adsbygoogle || []).push({{}});
        }} catch (e) {{
          console.error("AdSense initialization failed:", e);
        }}
      }}
    }});
  </script>
</body>
</html>
"""
    
    index_path = os.path.join(WORKSPACE, "vinatools_index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print("vinatools_index.html generated successfully!")

if __name__ == "__main__":
    generate_index()
