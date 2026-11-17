# -*- coding: utf-8 -*-
import os
import re
import json
import sys
import random

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(WORKSPACE, "config.json")
DEPLOYED_LOG = os.path.join(WORKSPACE, "deployed_tools.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def classify_keyword(keyword):
    kw = keyword.lower()
    
    # 1. Employment / Job Application / Leave Forms (check BEFORE generic "đơn xin")
    if any(x in kw for x in ["xin việc", "ứng tuyển", "xin phép", "nghỉ phép", "nghỉ học", "nghỉ làm", "thôi việc", "nghỉ việc", "xin nghỉ", "vắng mặt"]):
        return "employment_leave_form"
    
    # 2. Civil/Administrative Forms
    if any(x in kw for x in ["tạm trú", "ct01", "sửa chữa nhà", "xây dựng", "thực tập", "hủy mã số", "tờ khai", "đơn xin", "mẫu đơn"]):
        return "civil_admin_form"
        
    # 3. Lease/Property Contracts
    if any(x in kw for x in ["thuê nhà", "thuê mặt bằng", "cho thuê", "đặt cọc", "mặt bằng", "cho ở nhờ"]):
        return "property_lease_contract"
        
    # 4. Employment/Labor Contracts & Handover Minutes
    if any(x in kw for x in ["lao động", "thử việc", "cộng tác viên", "hợp đồng", "bàn giao tài sản", "biên bản"]):
        return "labor_employment_contract"
        
    # 5. Financial/Tax Calculators
    if any(x in kw for x in ["tính", "lãi", "phí", "thuế", "doanh thu", "lương", "gross", "net", "tncn", "sàn"]):
        return "financial_calculator"
        
    # 6. Registry / Data Utilities
    if any(x in kw for x in ["đọc số", "địa chỉ", "tra cứu", "mã số thuế"]):
        return "document_utility"
        
    return "general_utility"

def get_specific_legal_basis(keyword):
    kw = keyword.lower()
    if "thuế hộ kinh doanh" in kw or "hộ kinh doanh" in kw:
        return "Nghị định 68/2026/NĐ-CP, Nghị định 141/2026/NĐ-CP, Thông tư 18/2026/TT-BTC và Nghị quyết 198/2025/QH15"
    if "thuế tncn" in kw or "gross" in kw or "lương" in kw:
        return "Luật Thuế thu nhập cá nhân số 109/2025/QH15, Nghị quyết 110/2025/UBTVQH15, Nghị định 293/2025/NĐ-CP và Nghị định 161/2026/NĐ-CP"
    if "phí sàn" in kw or "tmđt" in kw or "shopee" in kw or "tiktok" in kw:
        return "Nghị định 68/2026/NĐ-CP (Điều 11 về khấu trừ thuế TMĐT) và Biểu phí sàn Shopee, TikTok Shop cập nhật năm 2026"
    if "mã số thuế" in kw or "tra cứu" in kw or "vietregistry" in kw:
        return "Luật Quản lý thuế số 38/2019/QH14 và Nghị định 126/2020/NĐ-CP"
    if "xin việc" in kw or "ứng tuyển" in kw:
        return "Bộ luật Lao động 2019 và Nghị định 30/2020/NĐ-CP"
    if "tạm trú" in kw or "ct01" in kw:
        return "Điều 27 Luật Cư trú 2020, Thông tư 66/2023/TT-BCA (biểu mẫu CT01) và Nghị định 30/2020/NĐ-CP"
    if "thôi việc" in kw or "nghỉ việc" in kw:
        return "Điều 35 Bộ luật Lao động 2019 và Nghị định 30/2020/NĐ-CP"
    if "nghỉ phép" in kw or "nghỉ làm" in kw or "xin nghỉ" in kw:
        return "Điều 113 Bộ luật Lao động 2019 và Nghị định 30/2020/NĐ-CP"
    if "lao động" in kw or "thử việc" in kw:
        return "Điều 21 Bộ luật Lao động 2019, Thông tư 10/2020/TT-BLĐTBXH và Nghị định 30/2020/NĐ-CP"
    if "bàn giao" in kw:
        return "Bộ luật Dân sự 2015, Bộ luật Lao động 2019 và Nghị định 30/2020/NĐ-CP"
    return "quy định pháp luật hành chính, dân sự, thuế và lao động hiện hành tại Việt Nam năm 2026"

def get_specific_steps(keyword, category):
    kw = keyword.lower()
    if "đơn" in kw or "tờ khai" in kw or "xin" in kw or "phép" in kw:
        return [
            f"Bước 1: Điền thông tin cá nhân và đơn vị tiếp nhận trực tiếp vào trình hướng dẫn từng bước của biểu mẫu {keyword}.",
            f"Bước 2: Nhập chi tiết nội dung, thời gian áp dụng hoặc sử dụng trợ lý soạn thảo văn phong hành chính chuẩn mực.",
            f"Bước 3: Kiểm tra bản xem trước định dạng A4 chuẩn Nghị định 30/2020/NĐ-CP ngay ở khung bên phải.",
            f"Bước 4: Bấm nút 'Tải File Word (.doc)', 'Sao chép HTML/Markdown' hoặc 'In Trực Tiếp / Lưu PDF' hoàn toàn miễn phí ngay lập tức."
        ]
    elif "hợp đồng" in kw or "biên bản" in kw:
        return [
            f"Bước 1: Nhập thông tin pháp lý đầy đủ của Bên A và Bên B vào trình khởi tạo {keyword}.",
            f"Bước 2: Thiết lập điều khoản công việc, tiền lương/tài sản bàn giao và các cam kết bảo hiểm, an toàn lao động.",
            f"Bước 3: Đối chiếu bản xem trước A4 với đầy đủ Quốc hiệu, Tiêu ngữ và các điều khoản bắt buộc.",
            f"Bước 4: Xuất trực tiếp file Word (.doc), sao chép nội dung sạch hoặc in bản PDF A4 mà không cần đăng ký hay chờ đợi."
        ]
    elif "tra cứu" in kw or "mã số thuế" in kw:
        return [
            f"Bước 1: Chọn chế độ tra cứu theo Mã số thuế (MST 10 chữ số) hoặc tìm kiếm theo tên doanh nghiệp / tỉnh thành.",
            f"Bước 2: Nhấn 'Tra cứu ngay' để truy vấn trực tiếp qua API VietRegistry (/api/company hoặc /api/search).",
            f"Bước 3: Kiểm tra trạng thái hoạt động, người đại diện pháp luật và địa chỉ đăng ký từ Tổng cục Thuế.",
            f"Bước 4: Tải danh sách kết quả dưới dạng bảng tính CSV (UTF-8) hoặc sao chép thông tin để xuất hóa đơn."
        ]
    else:
        return [
            f"Bước 1: Nhập các thông số tài chính hoặc dữ liệu đầu vào cần xử lý vào công cụ {keyword}.",
            f"Bước 2: Lựa chọn phương pháp tính, nhóm ngành nghề, khu vực hoặc bộ quy tắc áp dụng cho năm 2026.",
            f"Bước 3: Xem ngay bảng phân tích chi tiết, số liệu so sánh và cảnh báo tuân thủ pháp lý được tính toán tự động client-side.",
            f"Bước 4: Xuất bảng tính CSV chuẩn UTF-8 BOM hoặc nhấn 'In / Xuất PDF' để lưu trữ báo cáo A4 ngay lập tức."
        ]

def get_specific_faqs(keyword, category):
    kw = keyword.lower()
    legal_basis = get_specific_legal_basis(keyword)
    
    faqs = []
    
    # FAQ 1: Legal/Technical basis
    if "đơn" in kw or "tờ khai" in kw or "xin" in kw or "phép" in kw or "hợp đồng" in kw or "biên bản" in kw:
        faqs.append({
            "q": f"Văn bản {keyword} tuân theo quy định pháp lý nào?",
            "a": f"Biểu mẫu {keyword} được xây dựng dựa trên {legal_basis}. Cấu trúc Quốc hiệu, Tiêu ngữ, phông chữ Times New Roman 13pt và căn lề A4 được chuẩn hóa theo Phụ lục I Nghị định 30/2020/NĐ-CP."
        })
    else:
        faqs.append({
            "q": f"Công cụ {keyword} sử dụng căn cứ pháp lý nào cho năm 2026?",
            "a": f"Công cụ áp dụng công thức và biểu suất theo {legal_basis}. Toàn bộ tính toán chạy trực tiếp bằng JavaScript trên trình duyệt của bạn, tuân thủ Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15."
        })
        
    # FAQ 2: Usage / Privacy
    if "đơn" in kw or "tờ khai" in kw or "xin" in kw or "phép" in kw:
        faqs.append({
            "q": f"Biểu mẫu {keyword} có thể in trực tiếp hoặc mở bằng Microsoft Word không?",
            "a": "Có. Bạn có thể bấm 'In Trực Tiếp / Lưu PDF' để xuất bản A4 chuẩn lề (trên/dưới 20mm, trái 30mm, phải 15mm) hoặc tải về file Word / sao chép mã HTML/Markdown ngay lập tức."
        })
    elif "hợp đồng" in kw or "biên bản" in kw:
        faqs.append({
            "q": f"{keyword} đã bao gồm đầy đủ điều khoản bắt buộc chưa?",
            "a": f"Có. Các biểu mẫu hợp đồng và biên bản trên VinaTools bám sát {legal_basis}, bảo đảm đầy đủ thông tin các bên và các điều khoản cốt lõi trước khi ký kết."
        })
    else:
        faqs.append({
            "q": f"Tôi có thể xuất bảng tính hoặc sử dụng {keyword} trên điện thoại không?",
            "a": f"Có. Giao diện VinaTools hỗ trợ đầy đủ trên điện thoại và máy tính bảng, đồng thời cho phép tải bảng tính CSV (mở trực tiếp trong Excel mà không lỗi font tiếng Việt) hoặc in báo cáo A4."
        })
        
    # FAQ 3: Instant Free Export
    faqs.append({
        "q": f"Sử dụng và tải kết quả từ {keyword} có mất phí hay phải chờ đếm ngược không?",
        "a": "Hoàn toàn miễn phí và tức thì. VinaTools không thu phí, không yêu cầu đăng nhập và không đặt đồng hồ đếm ngược khi tải xuống tệp kết quả CSV, Word hoặc in PDF."
    })
    
    # FAQ 4: Print/Edit options
    faqs.append({
        "q": "Dữ liệu nhập vào có được lưu lại trên máy chủ không?",
        "a": "Không. Mọi số liệu kinh doanh, thu nhập hay thông tin cá nhân đều được xử lý hoàn toàn tại trình duyệt người dùng (client-side), không lưu trữ trên máy chủ."
    })
    
    return faqs

def get_category_content(category, keyword):
    clean_kw = keyword.strip()
    cap_kw = clean_kw[:1].upper() + clean_kw[1:]
    
    content = {}
    legal_basis = get_specific_legal_basis(keyword)
    
    if category == "employment_leave_form":
        if "xin việc" in clean_kw.lower() or "ứng tuyển" in clean_kw.lower():
            content["intro"] = (
                f"Biểu mẫu <strong>{clean_kw}</strong> hỗ trợ ứng viên soạn thảo đơn ứng tuyển chuyên nghiệp, rõ ràng trình độ học vấn, kinh nghiệm làm việc và vị trí mong muốn theo đúng thể thức văn bản hành chính Việt Nam."
            )
            content["sec1_title"] = "Quy Chuẩn Thể Thức & Căn Cứ Pháp Lý Đơn Xin Việc"
            content["sec1_text"] = (
                f"Hồ sơ và đơn ứng tuyển lao động được xây dựng phù hợp với quy định tại {legal_basis}. Khi trình bày đơn xin việc gửi tới Ban Giám đốc và Bộ phận Tuyển dụng doanh nghiệp, văn bản cần nêu rõ thông tin liên hệ, vị trí ứng tuyển, quá trình đào tạo, kỹ năng chuyên môn nổi bật và cam kết trách nhiệm trong công việc."
            )
            content["sec3_pitfalls"] = (
                "Khuyến nghị dành cho ứng viên: Sử dụng phông chữ Times New Roman cỡ 13pt trên khổ giấy A4, kiểm tra kỹ chính tả tên doanh nghiệp/bộ phận tuyển dụng và thông tin liên lạc (email, số điện thoại) trước khi in PDF hoặc gửi trực tuyến."
            )
        else:
            content["intro"] = (
                f"Mẫu đơn <strong>{clean_kw}</strong> là văn bản hành chính nhân sự chính thức được sử dụng phổ biến trong các doanh nghiệp, tổ chức tại Việt Nam. Việc lập đơn xin nghỉ phép, bàn giao công việc hay thôi việc đúng quy chuẩn giúp doanh nghiệp chủ động điều phối nhân sự và bảo vệ quyền lợi hợp pháp của người lao động."
            )
            content["sec1_title"] = "Căn Cứ Pháp Lý Điều Chỉnh Quy Trình Nghỉ Phép & Bàn Giao"
            content["sec1_text"] = (
                f"Quy trình xin nghỉ phép năm, nghỉ việc hoặc đơn phương chấm dứt hợp đồng lao động được quy định chi tiết tại {legal_basis}. Người lao động có trách nhiệm thông báo trước theo thời hạn nội quy công ty hoặc luật định và ghi rõ người tiếp nhận bàn giao công việc tạm thời."
            )
            content["sec3_pitfalls"] = (
                "Khuyến nghị hành chính quan trọng: Ghi rõ khoảng thời gian nghỉ phép (từ ngày đến ngày), tổng số ngày nghỉ và họ tên/chức vụ của đồng nghiệp tiếp nhận bàn giao công việc để đơn sớm được Ban lãnh đạo phê duyệt."
            )
        
    elif category == "civil_admin_form":
        content["intro"] = (
            f"Biểu mẫu <strong>{clean_kw}</strong> là văn bản hành chính công dân dùng để thực hiện thủ tục khai báo cư trú trực tiếp hoặc nộp kèm hồ sơ hành chính công tại cơ quan Công an xã/phường theo chuẩn mới nhất."
        )
        content["sec1_title"] = "Quy Định Pháp Lý & Cơ Quan Tiếp Nhận Hồ Sơ"
        content["sec1_text"] = (
            f"Khi thực hiện thủ tục khai báo thông tin liên quan đến {keyword}, công dân cần đối chiếu chính xác dữ liệu dựa trên {legal_basis}. Họ tên khai sinh, số định danh cá nhân/CCCD, nơi thường trú và địa chỉ tạm trú mới phải thống nhất hoàn toàn với Cơ sở dữ liệu quốc gia về dân cư."
        )
        content["sec3_pitfalls"] = (
            "Lưu ý pháp lý đối với công dân: Chuẩn bị sẵn giấy tờ chứng minh chỗ ở hợp pháp (hợp đồng thuê nhà, văn bản đồng ý của chủ hộ) khi nộp tờ khai CT01 trực tiếp hoặc qua Cổng Dịch vụ công."
        )

    elif category == "property_lease_contract":
        content["intro"] = (
            f"Hợp đồng thỏa thuận <strong>{clean_kw}</strong> thiết lập các cam kết pháp lý ràng buộc giữa các bên trong việc khai thác và thuê tài sản."
        )
        content["sec1_title"] = "Nguyên Tắc Thiết Lập Hợp Đồng Thuê Tài Sản"
        content["sec1_text"] = (
            f"Hợp đồng thuê tài sản được xây dựng dựa trên các quy định tại {legal_basis}, bảo đảm minh bạch giá thuê, tiền cọc, thời hạn và trách nhiệm các bên."
        )
        content["sec3_pitfalls"] = (
            "Khuyến nghị phòng ngừa tranh chấp: Lập biên bản bàn giao hiện trạng tài sản đính kèm và ghi giá trị bằng Việt Nam Đồng (VND)."
        )

    elif category == "labor_employment_contract":
        content["intro"] = (
            f"Văn bản <strong>{clean_kw}</strong> ghi nhận đầy đủ các thỏa thuận pháp lý về quan hệ lao động, bàn giao tài sản, quyền lợi tiền lương và trách nhiệm bảo hộ, bảo hiểm giữa doanh nghiệp và người lao động."
        )
        content["sec1_title"] = "Quy Định Bộ Luật Lao Động & Điều Khoản Bắt Buộc"
        content["sec1_text"] = (
            f"Mọi nội dung trong {clean_kw} phải tuân thủ {legal_basis}. Đối với hợp đồng lao động, văn bản phải thể hiện đầy đủ 10 nội dung chủ yếu: thông tin hai bên, công việc và địa điểm làm việc, thời hạn hợp đồng, mức lương (không thấp hơn lương tối thiểu vùng NĐ 293/2025/NĐ-CP), hình thức trả lương, chế độ nâng lương, thời giờ làm việc - nghỉ ngơi, trang bị bảo hộ lao động, bảo hiểm bắt buộc (BHXH, BHYT, BHTN) và đào tạo bồi dưỡng nghề."
        )
        content["sec3_pitfalls"] = (
            "Khuyến nghị tuân thủ pháp luật lao động: Doanh nghiệp không được giữ bản chính giấy tờ tùy thân hoặc yêu cầu đặt cọc tiền mặt khi giao kết hợp đồng lao động; đồng thời lập biên bản bàn giao rõ ràng đối với thiết bị cấp phát."
        )

    elif category == "document_utility":
        content["intro"] = (
            f"Tiện ích <strong>{clean_kw}</strong> cung cấp giải pháp xử lý dữ liệu hành chính, kế toán và tra cứu doanh nghiệp chính xác theo thời gian thực ngay trên trình duyệt."
        )
        content["sec1_title"] = "Chuẩn Dữ Liệu Kế Toán, Địa Chính & Doanh Nghiệp Việt Nam"
        content["sec1_text"] = (
            f"Công cụ <strong>{clean_kw}</strong> được xây dựng bám sát {legal_basis}, hỗ trợ chuẩn hóa chuỗi dữ liệu tiếng Việt Unicode, xử lý hàng loạt không giới hạn dòng và xuất trực tiếp bảng tính CSV chuẩn UTF-8 BOM dùng ngay trong Excel."
        )
        content["sec3_pitfalls"] = (
            "Cam kết bảo mật dữ liệu: Các nghiệp vụ tách địa chỉ và đọc số tiền thành chữ chạy 100% cục bộ trên trình duyệt, tuân thủ Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15."
        )

    elif category == "financial_calculator":
        content["intro"] = (
            f"Công cụ tài chính <strong>{clean_kw}</strong> giúp cá nhân, hộ kinh doanh và nhà bán hàng thương mại điện tử mô phỏng chính xác nghĩa vụ thuế, bảo hiểm xã hội, biểu phí sàn và dòng tiền thực nhận theo quy định mới nhất năm 2026."
        )
        content["sec1_title"] = "Căn Cứ Pháp Lý & Biểu Suất Tính Toán Năm 2026"
        content["sec1_text"] = (
            f"Hệ thống công thức của <strong>{clean_kw}</strong> cập nhật trực tiếp theo {legal_basis}. Người dùng có thể so sánh song song các phương pháp kê khai, kiểm tra ngưỡng miễn thuế 1 tỷ đồng/năm, biểu thuế TNCN 5 bậc hoặc biên lợi nhuận ròng & Break-Even ROAS chỉ trong vài giây."
        )
        content["sec3_pitfalls"] = (
            "Lưu ý sử dụng: Số liệu mô phỏng bám sát văn bản quy phạm pháp luật năm 2026 và biểu phí sàn công bố chính thức; dữ liệu doanh thu/thu nhập được xử lý hoàn toàn cục bộ trên trình duyệt của bạn."
        )

    else:
        content["intro"] = (
            f"Công cụ trực tuyến <strong>{clean_kw}</strong> hỗ trợ tự động hóa tác vụ hành chính và tính toán tài chính nhanh chóng ngay trên trình duyệt."
        )
        content["sec1_title"] = "Xử Lý Client-Side An Toàn & Minh Bạch"
        content["sec1_text"] = (
            f"Tiện ích <strong>{clean_kw}</strong> hoạt động dựa trên {legal_basis} với mã nguồn xử lý hoàn toàn trên trình duyệt."
        )
        content["sec3_pitfalls"] = (
            "Cam kết bảo mật: Tuân thủ Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 và Nghị định 356/2025/NĐ-CP."
        )

    # Injected custom steps & FAQs based on exact keyword
    content["sec2_steps"] = get_specific_steps(keyword, category)
    content["faqs"] = get_specific_faqs(keyword, category)
    
    return content

def get_related_tools_html(current_keyword, category):
    """
    Selects up to 3 related tools deterministically from deployed_tools.json based on category.
    """
    tools = []
    
    if os.path.exists(DEPLOYED_LOG):
        try:
            with open(DEPLOYED_LOG, "r", encoding="utf-8") as f:
                tools = json.load(f)
        except Exception as e:
            print(f"Failed to read deployed_tools.json in related links generation: {e}")
            
    if not tools:
        return ""
        
    curr_kw = current_keyword.lower().strip()
    same_cat_tools = sorted(
        [
            t for t in tools
            if t.get("keyword", "").lower().strip() != curr_kw
            and classify_keyword(t.get("keyword", "")) == category
        ],
        key=lambda t: -t.get("estimated_volume", 0)
    )
    
    if len(same_cat_tools) < 3:
        other_tools = sorted(
            [
                t for t in tools
                if t.get("keyword", "").lower().strip() != curr_kw
                and t not in same_cat_tools
            ],
            key=lambda t: -t.get("estimated_volume", 0)
        )
        selected_tools = (same_cat_tools + other_tools)[:3]
    else:
        selected_tools = same_cat_tools[:3]
        
    cards_html = ""
    for t in selected_tools:
        kw = t["keyword"]
        slug = t["slug"]
        
        cards_html += f"""
        <a href="/{slug}" style="text-decoration: none; display: block;" class="related-tool-card">
          <div style="padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); background: rgba(255,255,255,0.015); transition: all 0.3s ease; height: 100%; box-sizing: border-box; display: flex; flex-direction: column;">
             <h4 style="margin: 0 0 10px 0; color: #fff; font-size: 0.98rem; font-weight: bold; line-height: 1.4;">{kw}</h4>
             <p style="margin: 0 0 15px 0; color: var(--text-secondary); font-size: 0.8rem; line-height: 1.45; flex-grow: 1;">
               Công cụ trực tuyến hỗ trợ {kw} chuẩn quy định 2026, bảo mật dữ liệu tuyệt đối.
             </p>
             <span style="font-size: 0.72rem; color: #10b981; display: flex; align-items: center; gap: 4px;">
               <i class="fa-solid fa-bolt"></i> Miễn phí • Client-Side
             </span>
          </div>
        </a>
        """
        
    related_html = f"""
      <!-- Related Tools Internal Linking Panel -->
      <section style="margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 30px; text-align: left;">
        <h3 style="color: #fff; font-size: 1.25rem; margin-bottom: 20px; display: flex; align-items: center; gap: 8px;">
          <i class="fa-solid fa-layer-group" style="color: var(--accent-secondary);"></i>
          Công Cụ Hữu Ích Liên Quan Gợi Ý
        </h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px;">
          {cards_html}
        </div>
      </section>
      
      <style>
        .related-tool-card:hover div {{
          border-color: var(--accent-secondary-glow) !important;
          background: rgba(255,255,255,0.035) !important;
          transform: translateY(-2px);
          box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }}
      </style>
    """
    
    return related_html

def generate_local_seo_article(keyword):
    category = classify_keyword(keyword)
    c = get_category_content(category, keyword)
    
    clean_kw = keyword.strip()
    cap_kw = clean_kw[:1].upper() + clean_kw[1:]
    
    # Generate related tools navigation links
    related_tools_section = get_related_tools_html(keyword, category)
    
    # 1. Build the HTML template for the article
    html_article = f"""
      <section class="glass-panel no-print" style="margin-top: 40px; border-color: rgba(255, 255, 255, 0.08); text-align: left; padding: 30px;">
        <h2 style="margin-bottom: 20px; font-size: 1.5rem; color: #fff; border-bottom: 2px solid rgba(255, 255, 255, 0.05); padding-bottom: 10px;">
          <i class="fa-solid fa-circle-info" style="color: var(--accent-secondary); margin-right: 8px;"></i>
          {cap_kw} là gì?
        </h2>
        
        <p style="margin-bottom: 25px; color: var(--text-secondary); line-height: 1.7; font-size: 0.95rem;">
          {c['intro']}
        </p>

        <h3 style="margin: 25px 0 15px 0; color: #fff; font-size: 1.2rem;">
          <i class="fa-solid fa-scale-balanced" style="color: var(--accent-primary); margin-right: 8px;"></i>
          {c['sec1_title']}
        </h3>
        <p style="margin-bottom: 25px; color: var(--text-secondary); line-height: 1.7; font-size: 0.95rem;">
          {c['sec1_text']}
        </p>

        <h2 style="margin: 35px 0 20px 0; font-size: 1.5rem; color: #fff; border-bottom: 2px solid rgba(255, 255, 255, 0.05); padding-bottom: 10px;">
          <i class="fa-solid fa-list-check" style="color: var(--accent-secondary); margin-right: 8px;"></i>
          Hướng dẫn sử dụng {clean_kw}
        </h2>
        <ol style="margin-left: 20px; margin-bottom: 25px; color: var(--text-secondary); display: grid; gap: 10px; line-height: 1.6; font-size: 0.95rem;">
    """
    
    for step in c['sec2_steps']:
        html_article += f"      <li style=\"padding-left: 5px;\">{step}</li>\n"
        
    html_article += f"""    </ol>

        <div style="background: rgba(245, 158, 11, 0.05); border-left: 4px solid #f59e0b; padding: 15px 20px; border-radius: 4px; margin-bottom: 30px;">
          <h4 style="margin: 0 0 8px 0; color: #f59e0b; font-weight: bold; font-size: 1rem;"><i class="fa-solid fa-triangle-exclamation"></i> Khuyến Nghị An Toàn & Bảo Mật</h4>
          <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem; line-height: 1.6;">
            {c['sec3_pitfalls']}
          </p>
        </div>

        <h2 style="margin: 40px 0 20px 0; font-size: 1.5rem; color: #fff; border-bottom: 2px solid rgba(255, 255, 255, 0.05); padding-bottom: 10px;">
          <i class="fa-solid fa-clipboard-question" style="color: var(--accent-primary); margin-right: 8px;"></i>
          Các câu hỏi thường gặp về {clean_kw} (FAQ)
        </h2>
        <div style="display: grid; gap: 20px;">
    """
    
    for faq in c['faqs']:
        html_article += f"""      <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); padding: 15px 20px; border-radius: 8px;">
            <h4 style="margin: 0 0 10px 0; color: #fff; font-size: 1.05rem; font-weight: bold;"><i class="fa-solid fa-circle-question" style="color: var(--accent-secondary); margin-right: 6px;"></i> {faq['q']}</h4>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.92rem; line-height: 1.6; text-align: justify;">{faq['a']}</p>
          </div>\n"""
          
    html_article += f"""    </div>
        
        {related_tools_section}
      </section>
    """
    
    # 2. Compile Schema.org FAQPage JSON-LD structured data
    schema_main = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }
    for faq in c['faqs']:
        schema_main["mainEntity"].append({
            "@type": "Question",
            "name": faq['q'],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq['a']
            }
        })
        
    schema_json = json.dumps(schema_main, ensure_ascii=False, indent=2)
    schema_tag = f"""\n  <script type="application/ld+json">\n  {schema_json}\n  </script>\n"""
    
    return html_article, schema_tag

def generate_seo_article(slug, keyword):
    tool_dir = os.path.join(WORKSPACE, slug)
    index_path = os.path.join(tool_dir, "index.html")
    
    if not os.path.exists(index_path):
        print(f"Error: index.html for {slug} not found.")
        return False

    print(f"Generating SEO article & Schema for tool: '{keyword}'...")
    
    # Generate article content block & Schema
    article_html, schema_tag = generate_local_seo_article(keyword)
    article_html = f"\n    <!-- VINATOOLS_SEO_START -->\n{article_html}\n    <!-- VINATOOLS_SEO_END -->"
    
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Clean comment-wrapped SEO articles if already existing
    html_content = re.sub(
        r'<!--\s*VINATOOLS_SEO_START\s*-->[\s\S]*?<!--\s*VINATOOLS_SEO_END\s*-->',
        "",
        html_content
    )

    # Clean legacy SEO articles & related tools if already existing (safely using non-greedy regex, max 1 replacement)
    legacy_patterns = [
        r'<section class="glass-panel" style="margin-top: 40px;[\s\S]*?</section>',
        r'<section class="glass-panel" style="margin-top: 40px; border-color: rgba\(255, 255, 255, 0\.08\);[\s\S]*?</section>'
    ]
    for pattern in legacy_patterns:
        html_content = re.sub(pattern, '', html_content, count=1)

    # Remove any existing application/ld+json FAQPage schemas
    html_content = re.sub(
        r'\n\s*<script type="application/ld\+json">\s*{\s*"@context":\s*"https://schema\.org",\s*"@type":\s*"FAQPage"[\s\S]*?</script>',
        "",
        html_content
    )

    # Insert the article right before the footer block
    footer_match = re.search(r'<footer\s+[^>]*class=["\'][^"\']*tool-footer[^"\']*["\']', html_content)
    if footer_match:
        idx = footer_match.start()
        updated_html = html_content[:idx] + article_html + "\n\n    " + html_content[idx:]
    else:
        # Fallback to appending right before the last body close tag (to avoid matching strings inside JS scripts)
        idx = html_content.rfind("</body>")
        if idx != -1:
            updated_html = html_content[:idx] + article_html + "\n\n    " + html_content[idx:]
        else:
            updated_html = html_content + f"\n{article_html}"
        
    # Inject the Schema into the head section (limit to first occurrence to avoid matching inside JS scripts)
    if "</head>" in updated_html:
        updated_html = updated_html.replace("</head>", f"{schema_tag}</head>", 1)
    elif "<head>" in updated_html:
        updated_html = updated_html.replace("<head>", f"<head>{schema_tag}", 1)
    elif "<body>" in updated_html:
        updated_html = updated_html.replace("<body>", f"{schema_tag}<body>", 1)
    else:
        updated_html = schema_tag + updated_html

    # Ensure correct meta description
    meta_desc = f"Sử dụng công cụ {keyword} trực tuyến nhanh chóng, an toàn và chính xác nhất năm 2026. Tải file kết quả ngay tức thì."
    if '<meta name="description"' not in updated_html:
        meta_tag = f'\n  <meta name="description" content="{meta_desc}">'
        updated_html = updated_html.replace('</title>', f'</title>{meta_tag}')
        
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(updated_html)

    print(f"SEO Content & Schema successfully written to index.html for slug: {slug}")
    return True

if __name__ == "__main__":
    # Simple test run on slug
    generate_seo_article("mau-don-xin-tam-tru", "Mẫu đơn xin tạm trú")
