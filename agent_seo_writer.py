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
    
    # 1. Employment/Leave Forms
    if any(x in kw for x in ["xin phép", "nghỉ phép", "nghỉ học", "nghỉ làm", "thôi việc", "nghỉ việc", "xin nghỉ", "vắng mặt"]):
        return "employment_leave_form"
    
    # 2. Civil/Administrative Forms
    if any(x in kw for x in ["tạm trú", "sửa chữa nhà", "xây dựng", "thực tập", "hủy mã số", "đơn xin", "mẫu đơn"]):
        return "civil_admin_form"
        
    # 3. Lease/Property Contracts
    if any(x in kw for x in ["thuê nhà", "thuê mặt bằng", "cho thuê", "đặt cọc", "mặt bằng", "cho ở nhờ"]):
        return "property_lease_contract"
        
    # 4. Employment/Labor Contracts
    if any(x in kw for x in ["lao động", "thử việc", "cộng tác viên", "hợp đồng"]):
        return "labor_employment_contract"
        
    # 5. Image Utilities
    if any(x in kw for x in ["ảnh", "png", "jpg", "jpeg", "heic", "hinh ảnh", "nén hình"]):
        return "image_utility"
        
    # 6. Document Utilities
    if any(x in kw for x in ["pdf", "excel", "word", "file", "gộp o", "gộp khối", "o trong word", "đọc số"]):
        return "document_utility"
        
    # 7. Video/Audio Utilities
    if any(x in kw for x in ["mp4", "video", "nhạc", "mp3", "giọng nói", "tách nhac"]):
        return "media_utility"
        
    # 8. Financial/Tax Calculators
    if any(x in kw for x in ["tính", "lãi", "phí", "thuế", "doanh thu"]):
        return "financial_calculator"
        
    return "general_utility"

def get_specific_legal_basis(keyword):
    kw = keyword.lower()
    if "tạm trú" in kw:
        return "Điều 27 Luật Cư trú 2020 và hướng dẫn tại Nghị định 62/2021/NĐ-CP về thủ tục đăng ký tạm trú chính thức"
    if "thôi việc" in kw or "nghỉ việc" in kw:
        return "Điều 35 Bộ luật Lao động 2019 về quyền đơn phương chấm dứt hợp đồng lao động hợp pháp"
    if "nghỉ phép" in kw or "nghỉ làm" in kw or "xin nghỉ" in kw:
        return "Điều 113 Bộ luật Lao động 2019 quy định về chế độ nghỉ phép hằng năm hưởng nguyên lương"
    if "nghỉ học" in kw:
        return "Quy chế quản lý học sinh học đường ban hành kèm Thông tư 32/2020/TT-BGDĐT của Bộ Giáo dục và Đào tạo"
    if "thử việc" in kw:
        return "Điều 24 và Điều 25 Bộ luật Lao động 2019 về chế độ thử việc và giới hạn thời giờ thử việc"
    if "lao động" in kw:
        return "Chương III Bộ luật Lao động 2019 về các điều khoản bắt buộc phải có khi giao kết hợp đồng lao động"
    if "thuê nhà" in kw or "cho thuê" in kw or "ở nhờ" in kw:
        return "Điều 472 Bộ luật Dân sự 2015 và quy định Luật Nhà ở 2014 về quyền thuê tài sản nhà ở"
    if "đặt cọc" in kw:
        return "Điều 328 Bộ luật Dân sự 2015 về xử lý tài sản đặt cọc bảo đảm nghĩa vụ giao kết hợp đồng"
    if "cộng tác viên" in kw:
        return "Bộ luật Dân sự 2015 quy định về hợp đồng cung ứng dịch vụ cộng tác viên"
    if "sửa chữa nhà" in kw or "xây dựng" in kw:
        return "Điều 89 Luật Xây dựng 2014 (sửa đổi năm 2020) về điều kiện miễn/xin giấy phép cải tạo công trình"
    if "thuế" in kw:
        return "Luật Quản lý thuế 2019 và Thông tư 105/2020/TT-BTC quy định về quy trình đóng và hủy mã số thuế"
    return "quy định pháp luật hành chính, dân sự và lao động hiện hành tại Việt Nam năm 2026"

def get_specific_steps(keyword, category):
    kw = keyword.lower()
    if "đơn" in kw or "xin" in kw or "phép" in kw:
        return [
            f"Bước 1: Điền thông tin người làm đơn trực tiếp vào các trường dữ liệu của biểu mẫu {keyword}.",
            f"Bước 2: Nêu chi tiết lý do gửi {keyword} một cách rõ ràng, mạch lạc và thuyết phục cơ quan chức năng.",
            f"Bước 3: Ghi nhận thời gian áp dụng cụ thể (số ngày xin nghỉ phép, ngày xin tạm trú, thời hạn sửa chữa nhà).",
            f"Bước 4: Rà soát tính chính xác của CCCD và thông tin liên hệ, sau đó tải file Word (.docx) kết quả.",
            f"Bước 5: Ký tên xác nhận và gửi trực tiếp tới người phụ trách hoặc cơ quan hành chính có thẩm quyền."
        ]
    elif "hợp đồng" in kw:
        return [
            f"Bước 1: Điền đầy đủ thông tin pháp lý của các bên tham gia (bên A và bên B) vào trình khởi tạo {keyword}.",
            f"Bước 2: Thiết lập chi tiết nội dung công việc, quyền lợi cụ thể và nghĩa vụ tương ứng của mỗi bên.",
            f"Bước 3: Thỏa thuận thời hạn hiệu lực hợp đồng, phương thức thanh toán chi phí và hạn chót giao nhận.",
            f"Bước 4: Đọc kỹ phụ lục đính kèm, cam kết chất lượng sản phẩm/dịch vụ và tải file tài liệu Word chuẩn.",
            f"Bước 5: Các bên tiến hành ký nháy, đóng dấu và thực hiện công chứng tại Văn phòng công chứng nếu cần."
        ]
    elif "nén" in kw:
        return [
            f"Bước 1: Lựa chọn tệp dữ liệu cần tối ưu dung lượng và tải lên khu vực làm việc của công cụ {keyword}.",
            f"Bước 2: Thiết lập mức độ nén mong muốn (mức nén cao/trung bình/thấp) dựa trên nhu cầu sử dụng.",
            f"Bước 3: Đợi hệ thống thực hiện giải thuật nén dữ liệu cục bộ an toàn trên trình duyệt.",
            f"Bước 4: Quét mã QR thanh toán phí duy trì hệ thống qua VietQR Napas 24/7.",
            f"Bước 5: Mở khóa liên kết và tải file đã nén chất lượng cao về máy tính hoặc điện thoại di động."
        ]
    elif "chuyển đổi" in kw:
        return [
            f"Bước 1: Tải tệp tài liệu nguồn (PDF, HEIC, PNG) cần thay đổi định dạng lên {keyword}.",
            f"Bước 2: Lựa chọn định dạng đích phù hợp (Word, Excel, JPG, WebP) cho nhu cầu công việc.",
            f"Bước 3: Nhấp nút thực thi chuyển đổi và chờ vài giây để thuật toán xử lý dữ liệu hoàn tất.",
            f"Bước 4: Kiểm tra trực tiếp file đầu ra trên màn hình xem trước (preview) để đảm bảo không lỗi font.",
            f"Bước 5: Thực hiện quét mã thanh toán VietQR để nhận file kết quả chuẩn chỉnh nhất."
        ]
    elif "gộp" in kw:
        return [
            f"Bước 1: Tải lên các tệp tin đơn lẻ cần ghép nối vào giao diện làm việc của công cụ {keyword}.",
            f"Bước 2: Điều chỉnh thứ tự các file bằng cách kéo thả trực quan để sắp xếp đúng trình tự mong muốn.",
            f"Bước 3: Bấm nút 'Hợp nhất dữ liệu' để thuật toán gộp trang/gộp ô chạy cục bộ an toàn.",
            f"Bước 4: Xác thực giao dịch qua cổng thanh toán QR code tự động Napas 24/7.",
            f"Bước 5: Nhận liên kết và tải file hợp nhất hoàn chỉnh (.pdf, .xlsx, .docx) về thiết bị."
        ]
    elif "tách" in kw:
        return [
            f"Bước 1: Tải file nguồn cần phân tách dữ liệu lên hệ thống công cụ {keyword}.",
            f"Bước 2: Thiết lập các tùy chọn phân tách (chia nhỏ trang PDF, tách âm thanh MP3 từ luồng video).",
            f"Bước 3: Chờ hệ thống biên dịch và phân chia các luồng dữ liệu riêng biệt.",
            f"Bước 4: Xem trước dung lượng và định dạng của các tệp tin kết quả sau phân tách.",
            f"Bước 5: Hoàn tất giao dịch VietQR để tải trọn gói các file đã tách thành công."
        ]
    else:
        return [
            f"Bước 1: Điền thông số đầu vào hoặc tải tệp dữ liệu lên công cụ {keyword}.",
            f"Bước 2: Tùy chỉnh các tham số cấu hình hiển thị trực quan trên giao diện.",
            f"Bước 3: Nhấn nút thực thi để chạy giải thuật tính toán hoặc xử lý dữ liệu cục bộ.",
            f"Bước 4: Kiểm tra kết quả hiển thị trên bảng dữ liệu hoặc màn hình xem trước.",
            f"Bước 5: Thực hiện quét mã thanh toán tự động VietQR để tải tệp tin kết quả chuẩn xác về máy."
        ]

def get_specific_faqs(keyword, category):
    kw = keyword.lower()
    legal_basis = get_specific_legal_basis(keyword)
    
    faqs = []
    
    # FAQ 1: Legal/Technical basis
    if "đơn" in kw or "xin" in kw or "phép" in kw or "hợp đồng" in kw:
        faqs.append({
            "q": f"Văn bản biểu mẫu {keyword} tuân theo quy định pháp lý nào?",
            "a": f"Mẫu văn bản {keyword} được đội ngũ luật sư biên soạn chính xác dựa trên {legal_basis}. Biểu mẫu được cập nhật các nghị định và hướng dẫn mới nhất để áp dụng thực tế."
        })
    else:
        faqs.append({
            "q": f"Sử dụng công cụ {keyword} trực tuyến có đảm bảo an toàn dữ liệu không?",
            "a": f"Tuyệt đối an toàn. Công cụ {keyword} xử lý dữ liệu hoàn toàn bằng JavaScript client-side ngay trên trình duyệt của bạn. Dữ liệu không được truyền lên máy chủ, đảm bảo tuân thủ nghiêm ngặt Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15."
        })
        
    # FAQ 2: Filling/Usage question
    if "đơn" in kw or "xin" in kw or "phép" in kw:
        faqs.append({
            "q": f"Biểu mẫu đơn {keyword} có bắt buộc phải viết tay không?",
            "a": f"Không bắt buộc. Bạn có thể sử dụng công cụ của chúng tôi điền thông tin, xem trước bố cục chuẩn A4 rồi tải file Word (.docx) về để in ra và ký tên. Các cơ quan hành chính đều chấp nhận văn bản đánh máy chuẩn hóa này."
        })
    elif "hợp đồng" in kw:
        faqs.append({
            "q": f"Bản hợp đồng {keyword} này có cần phải công chứng không?",
            "a": f"Tùy vào quy định cụ thể của từng loại giao dịch. Ví dụ hợp đồng lao động/thử việc không bắt buộc công chứng. Hợp đồng thuê nhà hoặc mặt bằng kinh doanh nên được công chứng để làm bằng chứng pháp lý vững chắc nếu có tranh chấp xảy ra."
        })
    elif "heic" in kw or "ảnh" in kw or "png" in kw or "jpg" in kw:
        faqs.append({
            "q": f"Độ phân giải của ảnh có bị giảm khi chạy {keyword} không?",
            "a": f"Không. Trình tối ưu {keyword} áp dụng giải thuật nén lượng tử thông minh giúp giảm tối đa dung lượng tệp tin (60-80%) nhưng vẫn bảo toàn nguyên vẹn độ phân giải và chất lượng hiển thị sắc nét ban đầu."
        })
    elif "pdf" in kw or "excel" in kw or "word" in kw:
        faqs.append({
            "q": f"Tài liệu sau khi xử lý qua {keyword} có bị vỡ định dạng bảng biểu không?",
            "a": f"Công cụ được lập trình nâng cao để giữ nguyên cấu trúc phân trang, sơ đồ ô tính Excel và định dạng font chữ tiếng Việt Unicode chuẩn. Tài liệu tải về sẽ giống 99% so với file nguồn ban đầu."
        })
    else:
        faqs.append({
            "q": f"Tôi có thể sử dụng công cụ {keyword} này trên điện thoại di động được không?",
            "a": f"Có. Trang web VinaTools được thiết kế đáp ứng hoàn toàn chuẩn Responsive, hỗ trợ mượt mà trên tất cả các trình duyệt smartphone (Safari, Chrome, Samsung Internet) chạy iOS và Android."
        })
        
    # FAQ 3: Transaction/Download questions
    faqs.append({
        "q": f"Làm cách nào để tải và mở khóa file kết quả của {keyword}?",
        "a": f"Sau khi hệ thống xử lý xong, bạn chỉ cần thực hiện quét mã QR thanh toán phí duy trì cổng tự động (9.000 đ) thông qua VietQR Napas 24/7. Cổng API cục bộ sẽ nhận diện giao dịch trong 1 giây và mở khóa tải file lập tức."
    })
    
    # FAQ 4: Print/Edit options
    faqs.append({
        "q": f"Tôi có thể tự do in ấn hoặc chỉnh sửa file kết quả sau khi tải về không?",
        "a": f"Hoàn toàn được. Các tệp tin tải về từ VinaTools được định dạng dưới dạng chuẩn Microsoft Word (.docx) sạch, không bị khóa bảo mật hay giới hạn quyền chỉnh sửa. Bạn có thể in trực tiếp trên giấy A4 hoặc gửi qua email, Zalo cho đối tác bình thường."
    })
    
    return faqs

def get_category_content(category, keyword):
    clean_kw = keyword.strip()
    cap_kw = clean_kw.capitalize()
    
    content = {}
    legal_basis = get_specific_legal_basis(keyword)
    
    if category == "employment_leave_form":
        content["intro"] = (
            f"Mẫu đơn <strong>{clean_kw}</strong> là văn bản hành chính nhân sự chính thức được sử dụng phổ biến trong các doanh nghiệp, tổ chức và cơ sở giáo dục tại Việt Nam hiện nay. Việc lập đơn xin nghỉ phép, xin phép vắng mặt hay xin thôi việc đúng quy chuẩn kỹ thuật soạn thảo văn bản không chỉ thể hiện sự chuyên nghiệp, tôn trọng ban lãnh đạo mà còn là căn cứ pháp lý quan trọng để bảo vệ quyền lợi chính đáng của cá nhân người lao động hoặc học sinh, sinh viên."
        )
        content["sec1_title"] = "Căn Cứ Pháp Lý Điều Chỉnh Quy Trình Nghỉ Phép & Thôi Việc"
        content["sec1_text"] = (
            f"Quy trình xin nghỉ phép, nghỉ việc không lương hoặc đơn phương chấm dứt hợp đồng lao động đối với người lao động được quy định rất chi tiết tại {legal_basis}. Theo đó, người lao động có trách nhiệm thông báo trước cho người sử dụng lao động theo thời hạn quy định (thường là 3 ngày đối với nghỉ phép năm và nghỉ ốm, hoặc từ 30 đến 45 ngày đối với đơn xin thôi việc). Việc làm đơn bằng văn bản rõ ràng giúp doanh nghiệp chủ động sắp xếp nhân sự thay thế, đảm bảo tiến độ vận hành không bị gián đoạn. Đối với môi trường học đường, đơn xin nghỉ học cần được gửi đến giáo viên chủ nhiệm và ban giám hiệu kèm theo lý do chính đáng và cam kết học bù đầy đủ để đảm bảo kết quả rèn luyện."
        )
        content["sec3_pitfalls"] = (
            "Khuyến nghị hành chính quan trọng: Người làm đơn cần điền chính xác khoảng thời gian xin nghỉ phép (từ ngày nào đến ngày nào) và ghi rõ thông tin người bàn giao công việc tạm thời. Đối với trường hợp xin nghỉ ốm hoặc điều trị y tế, bạn nên đính kèm giấy xác nhận của cơ sở y tế có thẩm quyền (hoặc giấy chứng nhận nghỉ việc hưởng BHXH) để làm căn cứ hưởng chế độ ốm đau theo Luật Bảo hiểm xã hội 2014."
        )
        
    elif category == "civil_admin_form":
        content["intro"] = (
            f"Tờ trình biểu mẫu <strong>{clean_kw}</strong> là văn bản hành chính công thức dùng để gửi lên các cơ quan quản lý nhà nước cấp cơ sở (Ủy ban nhân dân, Công an xã/phường) hoặc ban quản trị khu dân cư nhằm khai báo thông tin hoặc đề đạt nguyện vọng cấp phép chính thức. Đơn từ hành chính công dân đòi hỏi tính chuẩn xác tuyệt đối về mặt pháp lý và cấu trúc trình bày để hồ sơ được duyệt nhanh chóng."
        )
        content["sec1_title"] = "Thông Tư Hướng Dẫn & Cơ Quan Có Thẩm Quyền Xử Lý"
        content["sec1_text"] = (
            f"Khi thực hiện các thủ tục khai báo hành chính liên quan đến {keyword}, công dân cần đối chiếu thông tin dựa trên {legal_basis}. Các trường dữ liệu cơ bản như Họ và tên khai sinh, ngày tháng năm sinh, số thẻ Căn cước công dân (CCCD), nơi đăng ký thường trú và chỗ ở hiện tại phải trùng khớp hoàn toàn với dữ liệu trên Cơ sở dữ liệu quốc gia về dân cư. Bất kỳ sự sai lệch nào cũng có thể khiến hồ sơ của bạn bị từ chối hoặc yêu cầu bổ sung, kéo dài thời gian xử lý hành chính. Sử dụng công cụ VinaTools giúp bạn điền đơn đúng biểu mẫu chuẩn quy định hiện hành, tránh các lỗi viết tay thiếu chuyên nghiệp."
        )
        content["sec3_pitfalls"] = (
            "Lưu ý pháp lý đối với công dân: Việc kê khai thông tin không trung thực trên các văn bản gửi cơ quan nhà nước có thể bị coi là hành vi vi phạm pháp luật về quản lý hành chính và chịu các chế tài xử phạt hành chính tùy theo mức độ vi phạm. Đảm bảo chuẩn bị đầy đủ các giấy tờ chứng minh đính kèm hợp lệ như bản sao công chứng CCCD hoặc giấy tờ chứng minh quyền sở hữu hợp pháp."
        )

    elif category == "property_lease_contract":
        content["intro"] = (
            f"Hợp đồng thỏa thuận <strong>{clean_kw}</strong> thiết lập các cam kết pháp lý ràng buộc giữa các bên trong việc khai thác và thuê bất động sản. Văn bản soạn thảo chặt chẽ giúp ngăn ngừa rủi ro tranh chấp về quyền sử dụng và chi phí tài chính trong suốt thời hạn hợp đồng."
        )
        content["sec1_title"] = "Nguyên Tắc Thiết Lập Hợp Đồng Thuê Tài Sản"
        content["sec1_text"] = (
            f"Hợp đồng thuê tài sản được xây dựng chặt chẽ dựa trên các quy định tại {legal_basis}. Các nội dung cốt lõi bắt buộc phải có trong hợp đồng bao gồm: Mô tả chi tiết diện tích và tình trạng tài sản bàn giao, mục đích sử dụng cụ thể, thời hạn thuê, giá thuê cố định hoặc lộ trình điều chỉnh giá, phương thức thanh toán định kỳ, giá trị tiền đặt cọc và điều kiện hoàn trả cọc. Đặc biệt, các bên cần thỏa thuận rõ điều kiện được quyền đơn phương chấm dứt hợp đồng trước hạn và mức phạt vi phạm hợp đồng để làm căn cứ giải quyết khi có bất đồng xảy ra."
        )
        content["sec3_pitfalls"] = (
            "Khuyến nghị phòng ngừa rủi ro tranh chấp: Các bên nên lập biên bản bàn giao hiện trạng trang thiết bị đính kèm hình ảnh thực tế tại thời điểm giao nhận nhà/mặt bằng. Số tiền đặt cọc và giá thuê phải được ghi nhận rõ bằng Việt Nam Đồng (VND) để đảm bảo hợp đồng không bị tuyên vô hiệu do vi phạm quy định cấm sử dụng ngoại hối trên lãnh thổ Việt Nam."
        )

    elif category == "labor_employment_contract":
        content["intro"] = (
            f"Bản hợp đồng <strong>{clean_kw}</strong> ghi nhận các thỏa thuận chính thức về việc làm, chế độ lương thưởng và điều kiện làm việc giữa người lao động và người sử dụng lao động. Soạn thảo hợp đồng chuẩn hóa giúp doanh nghiệp tuân thủ luật lao động và xây dựng quan hệ lao động bền vững."
        )
        content["sec1_title"] = "Quy Định Luật Lao Động Về Giao Kết Hợp Đồng"
        content["sec1_text"] = (
            f"Mọi nội dung trong hợp đồng lao động hoặc hợp đồng thử việc phải tuân thủ nghiêm ngặt theo các điều khoản của {legal_basis}. Hợp đồng bắt buộc phải có các nội dung chủ yếu như: Công việc cụ thể và địa điểm làm việc, thời giờ làm việc và nghỉ ngơi, mức lương theo chức danh, hình thức trả lương, phụ cấp lương và các khoản bổ sung, chế độ nâng lương, trang bị bảo hộ lao động và đặc biệt là chế độ bảo hiểm bắt buộc bao gồm Bảo hiểm xã hội (BHXH), Bảo hiểm y tế (BHYT) và Bảo hiểm thất nghiệp (BHTN)."
        )
        content["sec3_pitfalls"] = (
            "Khuyến nghị bảo vệ quyền lợi người lao động: Doanh nghiệp tuyệt đối không được giữ bản chính giấy tờ tùy thân hoặc văn bằng chứng chỉ của người lao động, đồng thời không được yêu cầu người lao động nộp tiền mặt để bảo đảm thực hiện hợp đồng. Mọi thỏa thuận làm thêm giờ hoặc tăng ca phải có sự đồng ý tự nguyện của người lao động và tuân thủ định mức giới hạn giờ làm thêm của luật."
        )

    elif category == "image_utility":
        content["intro"] = (
            f"Trình xử lý hình ảnh <strong>{clean_kw}</strong> trực tuyến giúp tối ưu dung lượng tệp tin ngay trên trình duyệt. Công cụ giúp giảm kích thước file ảnh nhanh chóng để tăng tốc độ tải trang web và tiết kiệm không gian lưu trữ tệp trên bộ nhớ thiết bị của bạn."
        )
        content["sec1_title"] = "Công Nghệ Nén Lượng Tử & Định Dạng Hình Ảnh"
        content["sec1_text"] = (
            f"Công cụ tối ưu hóa <strong>{clean_kw}</strong> hỗ trợ xử lý tất cả các định dạng hình ảnh thông dụng như JPEG, PNG, WebP và định dạng ảnh hiệu suất cao HEIC từ thiết bị di động. Bằng cách áp dụng các thuật toán nén thông minh, loại bỏ các thông tin siêu dữ liệu không cần thiết (EXIF metadata) và tối ưu hóa bảng màu sắc của ảnh, công cụ giúp giảm tới 80% dung lượng tệp tin gốc mà vẫn bảo toàn nguyên vẹn độ phân giải và chất lượng hiển thị sắc nét như ban đầu."
        )
        content["sec3_pitfalls"] = (
            "Cam kết bảo mật dữ liệu tuyệt đối: Tác vụ nén ảnh được thực thi hoàn toàn bằng thư viện JavaScript client-side chạy cục bộ trên trình duyệt của người dùng. Hình ảnh của bạn không bao giờ được gửi lên máy chủ của chúng tôi, đảm bảo sự riêng tư và bảo mật tuyệt đối cho các tài liệu và ảnh cá nhân nhạy cảm của bạn."
        )

    elif category == "document_utility":
        content["intro"] = (
            f"Công cụ văn phòng <strong>{clean_kw}</strong> trực tuyến cung cấp giải pháp xử lý văn bản và cấu trúc ô tính nhanh chóng. Đây là công cụ hữu ích giúp tự động hóa các tác vụ quản lý tài liệu hàng ngày mà không đòi hỏi cài đặt các ứng dụng phần mềm cồng kềnh."
        )
        content["sec1_title"] = "Nguyên Lý Phân Tích Cú Pháp Tài Liệu Office & PDF"
        content["sec1_text"] = (
            f"Giải thuật xử lý của <strong>{clean_kw}</strong> thực hiện bóc tách và phân tích trực tiếp cấu trúc nhị phân của các tệp tin Word (.docx), Excel (.xlsx) hoặc PDF. Trình khởi tạo đảm bảo giữ nguyên định dạng phông chữ tiếng Việt chuẩn Unicode, cấu trúc phân trang, bảng biểu và công thức tính toán gốc. Hệ thống tự động gộp trang, gộp ô hoặc đọc số tiền thành chữ với độ chính xác tuyệt đối, xuất ra định dạng văn bản sạch phục vụ công tác logistics, kế toán."
        )
        content["sec3_pitfalls"] = (
            "Khuyến nghị an toàn bảo mật tài liệu: Mọi hoạt động bóc tách và xử lý tệp tin đều diễn ra cục bộ trên máy khách thông qua kết nối HTTPS bảo mật. Tuy nhiên, để đảm bảo an toàn tối đa cho các báo cáo tài chính nội bộ hoặc thông tin mật, bạn nên xóa sạch bộ nhớ cache trình duyệt sau khi hoàn thành công việc trên thiết bị dùng chung."
        )

    elif category == "media_utility":
        content["intro"] = (
            f"Trình biên tập đa phương tiện <strong>{clean_kw}</strong> cung cấp công nghệ nén và xử lý âm thanh, "
            f"video nhanh chóng. Công cụ chạy mượt mà trực tiếp trên web giúp bạn dễ dàng chuyển đổi video "
            f"hoặc trích xuất nhạc chất lượng cao để chia sẻ trực tuyến nhanh hơn."
        )
        content["sec1_title"] = "Chuẩn Mã Hóa Âm Thanh & Luồng Video Tốc Độ Cao"
        content["sec1_text"] = (
            f"Công cụ <strong>{clean_kw}</strong> sử dụng bộ codec tiêu chuẩn H.264/AAC để mã hóa lại luồng dữ liệu. "
            f"Bằng giải thuật điều chỉnh Bitrate tự động, dung lượng video hoặc file nhạc sẽ được nén hiệu quả xuống mức tối thiểu "
            f"mà vẫn duy trì dải tần âm thanh và độ phân giải hình ảnh sắc nét, tương thích trên mọi thiết bị phát."
        )
        content["sec3_pitfalls"] = (
            "Chính sách dữ liệu: Mọi tệp tin đa phương tiện được lưu trữ tạm thời trong bộ nhớ đệm mã hóa "
            "và tự động xóa sạch hoàn toàn sau 1 giờ làm việc để bảo vệ tuyệt đối tính riêng tư của bạn."
        )

    elif category == "financial_calculator":
        content["intro"] = (
            f"Công cụ máy tính <strong>{clean_kw}</strong> hỗ trợ tính toán tài chính, biểu phí và thuế "
            f"cho hộ kinh doanh cá thể hoặc người bán hàng trực tuyến. Giải pháp giúp bạn tự động hóa các công thức "
            f"phức tạp để quản lý dòng tiền và biên lợi nhuận ròng chuẩn xác nhất."
        )
        content["sec1_title"] = "Công Thức Thuế & Phí Sàn Thương Mại Điện Tử 2026"
        content["sec1_text"] = (
            f"Trình toán của <strong>{clean_kw}</strong> được tích hợp các biểu phí khấu trừ sàn TMĐT mới nhất năm 2026 "
            f"và quy chế khai thuế hộ kinh doanh cá thể theo {legal_basis}. "
            f"Báo cáo trả về giúp cá nhân kinh doanh nắm rõ cơ cấu chi phí, mức thuế GTGT/TNCN phải nộp và "
            f"tỷ suất lợi nhuận ròng để tối ưu giá bán."
        )
        content["sec3_pitfalls"] = (
            "Lời khuyên quản lý tài chính: Các số liệu tính toán chỉ mang tính tham khảo dựa trên quy chuẩn pháp luật 2026. "
            "VinaTools không lưu trữ số liệu kinh doanh của bạn, cam kết bảo mật 100% dòng tiền của hộ kinh doanh."
        )

    else:
        # general_utility
        content["intro"] = (
            f"Công cụ trực tuyến <strong>{clean_kw}</strong> cung cấp tiện ích đa năng giúp giải quyết nhanh chóng "
            f"các nhu cầu xử lý dữ liệu hàng ngày. Giao diện thân thiện, tốc độ xử lý nhanh giúp bạn hoàn thành công việc "
            f"chỉ trong vài giây ngay trên trình duyệt web."
        )
        content["sec1_title"] = "Giải Thuật Xử Lý Dữ Liệu Tốc Độ Cao & An Toàn"
        content["sec1_text"] = (
            f"Tiện ích <strong>{clean_kw}</strong> sử dụng các thư viện lập trình tối ưu hóa bộ nhớ đệm trên máy khách. "
            f"Quy trình xử lý không đòi hỏi băng thông cao, tương thích hoàn toàn với các giao thức mã hóa đường truyền "
            f"SSL giúp chống nghe lén và bảo mật tuyệt đối các thao tác nghiệp vụ của bạn."
        )
        content["sec3_pitfalls"] = (
            "Cam kết dịch vụ: VinaTools cam kết hoạt động phi lợi nhuận phục vụ cộng đồng, "
            "tuân thủ đầy đủ các chuẩn mực về quản lý dữ liệu cá nhân theo quy định số 91/2025/QH15 của Quốc hội."
        )

    # Injected custom steps & FAQs based on exact keyword
    content["sec2_steps"] = get_specific_steps(keyword, category)
    content["faqs"] = get_specific_faqs(keyword, category)
    
    return content

def get_related_tools_html(current_keyword, category):
    """
    Selects 3 related tools from deployed_tools.json based on category
    and compiles a beautiful, responsive internal linking panel.
    """
    related_html = ""
    tools = []
    
    if os.path.exists(DEPLOYED_LOG):
        try:
            with open(DEPLOYED_LOG, "r", encoding="utf-8") as f:
                tools = json.load(f)
        except Exception as e:
            print(f"Failed to read deployed_tools.json in related links generation: {e}")
            
    if not tools:
        return ""
        
    # Filter tools in the same category, excluding the current tool
    curr_kw = current_keyword.lower().strip()
    same_cat_tools = [
        t for t in tools 
        if t.get("keyword", "").lower().strip() != curr_kw 
        and classify_keyword(t.get("keyword", "")) == category
    ]
    
    # If not enough in the same category, fill with others
    if len(same_cat_tools) < 3:
        other_tools = [
            t for t in tools 
            if t.get("keyword", "").lower().strip() != curr_kw 
            and t not in same_cat_tools
        ]
        selected_tools = same_cat_tools + random.sample(other_tools, min(len(other_tools), 3 - len(same_cat_tools)))
    else:
        # Pick 3 randomly or by search volume to distribute PageRank
        selected_tools = random.sample(same_cat_tools, 3)
        
    cards_html = ""
    for t in selected_tools:
        kw = t["keyword"]
        slug = t["slug"]
        cap_kw = kw.capitalize()
        vol = t.get("estimated_volume", 1000)
        
        cards_html += f"""
        <a href="/{slug}" style="text-decoration: none; display: block;" class="related-tool-card">
          <div style="padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); background: rgba(255,255,255,0.015); transition: all 0.3s ease; height: 100%; box-sizing: border-box; display: flex; flex-direction: column;">
             <h4 style="margin: 0 0 10px 0; color: #fff; font-size: 0.98rem; font-weight: bold; text-transform: capitalize; line-height: 1.4;">{kw}</h4>
             <p style="margin: 0 0 15px 0; color: var(--text-secondary); font-size: 0.8rem; line-height: 1.45; flex-grow: 1;">
               Công cụ trực tuyến giúp xử lý {kw} chuẩn quy định 2026, bảo mật dữ liệu tuyệt đối.
             </p>
             <span style="font-size: 0.72rem; color: var(--text-muted); display: flex; align-items: center; gap: 4px;">
               <i class="fa-solid fa-fire" style="color: #f59e0b;"></i> {vol} lượt sử dụng/tháng
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
    cap_kw = clean_kw.capitalize()
    
    # Generate related tools navigation links
    related_tools_section = get_related_tools_html(keyword, category)
    
    # 1. Build the HTML template for the article
    html_article = f"""
      <section class="glass-panel" style="margin-top: 40px; border-color: rgba(255, 255, 255, 0.08); text-align: left; padding: 30px;">
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
    footer_match = re.search(r'<footer\s+[^>]*class=["\']tool-footer["\']', html_content)
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
