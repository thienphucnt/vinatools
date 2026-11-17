# -*- coding: utf-8 -*-
"""
Builders for the 5 Flagship LegalTech Document Wizards (Contracts & Petitions).
Strictly implements Decree 30/2020/ND-CP Appendix I A4 typography/margins,
Article 21 Labor Code 2019 & Circular 10/2020/TT-BLDTBXH (10 mandatory clauses),
Decree 293/2025/ND-CP regional minimum wage checks, Decree 161/2026/ND-CP SI cap,
dynamic ASCII-safe validateStep(step), and instant free Word (.doc) / Print PDF /
HTML / Markdown exports.
"""

from statutory_engines import render_tool_shell, REGION_MIN_WAGES_2026

DECREE30_CSS = """
  <style>
    .lg-grid { display: grid; grid-template-columns: 1fr; gap: 24px; max-width: 1320px; margin: 0 auto; padding: 0 16px; }
    @media (min-width: 1080px) { .lg-grid-2 { grid-template-columns: 470px 1fr; align-items: start; } }
    .lg-card { background: rgba(18, 22, 32, 0.82); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 22px; }
    .lg-label { display: block; font-size: 0.78rem; font-weight: 600; color: #cbd5e1; margin-bottom: 5px; }
    .lg-req { color: #f87171; margin-left: 2px; }
    .lg-input, .lg-select, .lg-textarea { width: 100%; background: rgba(10, 12, 16, 0.72); border: 1px solid rgba(255,255,255,0.14); border-radius: 9px; padding: 10px 12px; color: #fff; font-size: 0.9rem; font-family: inherit; box-sizing: border-box; transition: border-color 0.2s, box-shadow 0.2s; }
    .lg-input:focus, .lg-select:focus, .lg-textarea:focus { outline: none; border-color: #00a8ff; box-shadow: 0 0 0 3px rgba(0, 168, 255, 0.18); }
    .lg-input.invalid, .lg-select.invalid, .lg-textarea.invalid { border-color: #ef4444 !important; box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2); }
    .lg-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    @media (max-width: 560px) { .lg-row-2 { grid-template-columns: 1fr; } }
    .lg-stepper { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 20px; }
    .lg-step-btn { padding: 9px 10px; border-radius: 9px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.04); color: #9ca3af; font-size: 0.78rem; font-weight: 700; cursor: pointer; text-align: center; transition: all 0.2s; }
    .lg-step-btn.active { background: linear-gradient(135deg, #00a8ff 0%, #2563eb 100%); color: #fff; border-color: transparent; }
    .lg-step-btn.done { border-color: rgba(16,185,129,0.5); color: #34d399; background: rgba(16,185,129,0.1); }
    .form-step { display: none; }
    .form-step.active { display: block; }
    .lg-nav-actions { display: flex; justify-content: space-between; gap: 10px; margin-top: 20px; flex-wrap: wrap; }
    .lg-btn { display: inline-flex; align-items: center; justify-content: center; gap: 7px; padding: 10px 16px; border-radius: 10px; font-weight: 700; font-size: 0.86rem; cursor: pointer; border: none; transition: all 0.2s; }
    .lg-btn-primary { background: linear-gradient(135deg, #00a8ff 0%, #2563eb 100%); color: #fff; }
    .lg-btn-success { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #fff; }
    .lg-btn-secondary { background: rgba(255,255,255,0.07); color: #e2e8f0; border: 1px solid rgba(255,255,255,0.14); }
    .lg-btn:hover { transform: translateY(-1px); opacity: 0.95; }
    .lg-alert-err { display: none; margin-top: 12px; padding: 10px 12px; border-radius: 9px; background: rgba(239,68,68,0.14); border: 1px solid rgba(239,68,68,0.45); color: #fca5a5; font-size: 0.82rem; }
    .lg-alert-info { padding: 10px 12px; border-radius: 9px; font-size: 0.8rem; margin-top: 8px; }
    .lg-toolbar { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 14px; }

    /* Decree 30/2020/ND-CP Appendix I A4 Paper Sheet */
    .a4-viewport { overflow-x: auto; padding: 4px 0 16px 0; }
    .a4-document {
      width: 210mm;
      max-width: 100%;
      min-height: 297mm;
      margin: 0 auto;
      background: #ffffff;
      color: #000000;
      font-family: 'Times New Roman', Times, serif;
      font-size: 13pt;
      line-height: 1.5;
      padding: 20mm 15mm 20mm 30mm;
      box-sizing: border-box;
      box-shadow: 0 14px 44px rgba(0, 0, 0, 0.55);
      border-radius: 2px;
      text-align: justify;
    }
    @media (max-width: 820px) {
      .a4-document { padding: 18px 14px; font-size: 11.5pt; min-height: auto; }
    }
    .a4-document * { color: #000000; font-family: 'Times New Roman', Times, serif; }
    .a4-header-table { width: 100%; border-collapse: collapse; margin-bottom: 14pt; }
    .a4-header-table td { vertical-align: top; border: none; padding: 0; }
    .d30-org-block { width: 42%; text-align: center; font-size: 12pt; }
    .d30-motto-block { width: 58%; text-align: center; }
    .d30-quoc-hieu { font-size: 12pt; font-weight: bold; text-transform: uppercase; letter-spacing: 0.2px; margin: 0; text-align: center; }
    .d30-tieu-ngu-wrap { text-align: center; margin-top: 2pt; }
    .d30-tieu-ngu { display: inline-block; font-size: 13pt; font-weight: bold; padding-bottom: 3pt; border-bottom: 1.5px solid #000000; text-align: center; }
    .d30-date-line { font-size: 13pt; font-style: italic; text-align: center; margin-top: 6pt; }
    .d30-doc-title { font-size: 14pt; font-weight: bold; text-transform: uppercase; text-align: center; margin: 14pt 0 4pt 0; }
    .d30-doc-sub { font-size: 13pt; font-weight: bold; text-align: center; margin: 0 0 12pt 0; }
    .d30-section-h { font-size: 13pt; font-weight: bold; margin: 10pt 0 4pt 0; text-align: left; }
    .d30-p { margin: 4pt 0; text-indent: 0; }
    .d30-indent { text-indent: 10mm; }
    .d30-table { width: 100%; border-collapse: collapse; margin: 8pt 0; font-size: 12pt; }
    .d30-table th, .d30-table td { border: 1px solid #000000; padding: 5pt 6pt; text-align: left; vertical-align: top; }
    .d30-table th { font-weight: bold; text-align: center; background: #f8fafc; }
    .d30-sig-table { width: 100%; border-collapse: collapse; margin-top: 20pt; page-break-inside: avoid; }
    .d30-sig-table td { vertical-align: top; text-align: center; border: none; padding: 4pt; }
    .d30-sig-title { font-weight: bold; font-size: 13pt; text-transform: uppercase; }
    .d30-sig-note { font-style: italic; font-size: 11.5pt; }
    .d30-sig-space { height: 54pt; }
    .d30-asset-row { display: grid; grid-template-columns: 1.8fr 1fr 0.7fr 1.2fr 36px; gap: 6px; margin-bottom: 8px; align-items: center; }
    @media (max-width: 600px) { .d30-asset-row { grid-template-columns: 1fr 1fr; } }

    @media print {
      @page { size: A4 portrait; margin: 20mm 15mm 20mm 30mm; }
      body { background: #ffffff !important; color: #000000 !important; padding: 0 !important; margin: 0 !important; }
      .layout-container, .lg-grid, .lg-grid-2, .lg-card, .a4-viewport {
        display: block !important; max-width: 100% !important; width: 100% !important;
        padding: 0 !important; margin: 0 !important; background: transparent !important;
        border: none !important; box-shadow: none !important; overflow: visible !important;
      }
      .no-print { display: none !important; }
      .a4-document {
        width: 100% !important;
        max-width: 100% !important;
        min-height: auto !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        border: none !important;
        font-size: 13pt !important;
        line-height: 1.5 !important;
      }
    }
  </style>
"""

SHARED_EXPORT_AND_WIZARD_JS = """
    const REGION_WAGES_2026 = {
      "1": { label: "Vùng I (HN, HCM, Hải Phòng...)", minWage: 5310000 },
      "2": { label: "Vùng II (Đà Nẵng, Cần Thơ, Bắc Ninh...)", minWage: 4730000 },
      "3": { label: "Vùng III (Thành phố trực thuộc tỉnh)", minWage: 4140000 },
      "4": { label: "Vùng IV (Các địa bàn còn lại)", minWage: 3700000 }
    };

    function escHtml(v) {
      return String(v == null ? "" : v)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function fmtVnd(val) {
      const n = Number(val) || 0;
      return Math.round(n).toLocaleString("vi-VN");
    }

    function fmtDateVn(isoOrStr) {
      if (!isoOrStr) return "....../....../2026";
      const m = String(isoOrStr).match(/^(\\d{4})-(\\d{2})-(\\d{2})$/);
      if (m) return `${m[3]}/${m[2]}/${m[1]}`;
      return String(isoOrStr);
    }

    function getVal(id, fallback = "") {
      const el = document.getElementById(id);
      if (!el) return fallback;
      const v = (el.value || "").trim();
      return v || fallback;
    }

    function validateStep(step) {
      const activeStepEl = document.querySelector(`.form-step[data-step="${step}"]`);
      if (!activeStepEl) return true;
      const requiredInputs = activeStepEl.querySelectorAll('input[required], textarea[required], select[required]');
      for (const input of requiredInputs) {
        if (input.type === 'checkbox' && !input.checked) {
          input.classList.add('invalid');
          return false;
        }
        if (input.type !== 'checkbox' && !input.value.trim()) {
          input.classList.add('invalid');
          return false;
        }
        input.classList.remove('invalid');
      }
      return true;
    }

    let currentWizardStep = 1;

    function goToStep(targetStep) {
      const errBox = document.getElementById("wizard-error");
      if (targetStep > currentWizardStep) {
        for (let s = currentWizardStep; s < targetStep; s++) {
          if (!validateStep(s)) {
            if (errBox) {
              errBox.style.display = "block";
              errBox.textContent = `Vui lòng điền đầy đủ các trường bắt buộc (*) ở Bước ${s} trước khi tiếp tục.`;
            }
            return false;
          }
        }
      }
      if (errBox) errBox.style.display = "none";
      currentWizardStep = targetStep;
      document.querySelectorAll(".form-step").forEach(el => {
        el.classList.toggle("active", Number(el.dataset.step) === targetStep);
      });
      document.querySelectorAll(".lg-step-btn").forEach(btn => {
        const s = Number(btn.dataset.stepBtn);
        btn.classList.toggle("active", s === targetStep);
        btn.classList.toggle("done", s < targetStep);
      });
      if (typeof renderDocument === "function") renderDocument();
      return true;
    }

    function notifyAction(msg) {
      const toast = document.getElementById("export-toast");
      if (!toast) return;
      toast.textContent = msg;
      toast.style.display = "inline-flex";
      setTimeout(() => { toast.style.display = "none"; }, 2600);
    }

    function downloadWordDoc(filenameSlug) {
      if (!validateStep(1) || !validateStep(2) || !validateStep(3)) {
        const errBox = document.getElementById("wizard-error");
        if (errBox) {
          errBox.style.display = "block";
          errBox.textContent = "Vui lòng kiểm tra và điền đầy đủ các trường bắt buộc (*).";
        }
      }
      if (typeof renderDocument === "function") renderDocument();
      const docEl = document.getElementById("a4-preview-body");
      if (!docEl) return;
      const wordHtml = `<!DOCTYPE html>
<html xmlns:o="urn:schemas-microsoft-com:office:office"
      xmlns:w="urn:schemas-microsoft-com:office:word"
      xmlns="http://www.w3.org/TR/REC-html40">
<head>
  <meta charset="utf-8">
  <title>${escHtml(filenameSlug)}</title>
  <style>
    @page WordSection1 { size: 21cm 29.7cm; margin: 2cm 1.5cm 2cm 3cm; }
    div.WordSection1 { page: WordSection1; }
    body, p, td, th, li, div { font-family: "Times New Roman", Times, serif; font-size: 13pt; line-height: 1.5; color: #000000; }
    .a4-header-table, .d30-sig-table { width: 100%; border-collapse: collapse; }
    .a4-header-table td, .d30-sig-table td { border: none; vertical-align: top; }
    .d30-quoc-hieu { font-size: 12pt; font-weight: bold; text-transform: uppercase; text-align: center; margin: 0; }
    .d30-tieu-ngu { display: inline-block; font-size: 13pt; font-weight: bold; border-bottom: 1.5pt solid #000000; padding-bottom: 2pt; }
    .d30-doc-title { font-size: 14pt; font-weight: bold; text-transform: uppercase; text-align: center; margin: 12pt 0 4pt 0; }
    .d30-doc-sub { font-size: 13pt; font-weight: bold; text-align: center; margin: 0 0 10pt 0; }
    .d30-section-h { font-size: 13pt; font-weight: bold; margin: 10pt 0 4pt 0; }
    .d30-table { width: 100%; border-collapse: collapse; margin: 8pt 0; font-size: 12pt; }
    .d30-table th, .d30-table td { border: 1px solid #000000; padding: 5pt 6pt; }
  </style>
</head>
<body>
  <div class="WordSection1">${docEl.innerHTML}</div>
</body>
</html>`;
      const blob = new Blob(["\\ufeff" + wordHtml], { type: "application/msword;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${filenameSlug}.doc`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      notifyAction("Đã tải xuống file Word (.doc) chuẩn Nghị định 30/2020/NĐ-CP!");
    }

    function copyTextToClipboard(text, msg) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => notifyAction(msg)).catch(() => fallbackCopy(text, msg));
      } else {
        fallbackCopy(text, msg);
      }
    }

    function fallbackCopy(text, msg) {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); notifyAction(msg); } catch (e) {}
      ta.remove();
    }

    function copyDocHtml() {
      const el = document.getElementById("a4-preview-body");
      if (!el) return;
      copyTextToClipboard(el.innerHTML.trim(), "Đã sao chép mã HTML văn bản!");
    }

    function copyDocPlainText() {
      const el = document.getElementById("a4-preview-body");
      if (!el) return;
      const cleanText = (el.innerText || el.textContent || "").replace(/\\n{3,}/g, "\\n\\n").trim();
      copyTextToClipboard(cleanText, "Đã sao chép toàn bộ nội dung văn bản!");
    }

    function resetSampleFields() {
      document.querySelectorAll('#wizard-form-root input[type="text"], #wizard-form-root input[type="date"], #wizard-form-root textarea').forEach(el => {
        if (!el.dataset.keepDefault) el.value = "";
      });
      if (typeof renderDocument === "function") renderDocument();
      notifyAction("Đã xóa dữ liệu mẫu. Vui lòng nhập thông tin thực tế của bạn.");
    }
"""


def _wrap_wizard_layout(slug, form_steps_html, tool_js, extra_controls_html=""):
    tool_html = f"""
    <div class="lg-grid lg-grid-2">
      <!-- Left: Multi-step Wizard Form -->
      <div class="lg-card no-print" id="wizard-form-root">
        <div class="lg-stepper">
          <button type="button" class="lg-step-btn active" data-step-btn="1" onclick="goToStep(1)">Bước 1: Chủ thể</button>
          <button type="button" class="lg-step-btn" data-step-btn="2" onclick="goToStep(2)">Bước 2: Nội dung</button>
          <button type="button" class="lg-step-btn" data-step-btn="3" onclick="goToStep(3)">Bước 3: Xuất A4</button>
        </div>

        {form_steps_html}

        <div id="wizard-error" class="lg-alert-err"></div>
      </div>

      <!-- Right: Live Decree 30/2020/ND-CP A4 Document Preview -->
      <div>
        <div class="lg-card no-print" style="margin-bottom: 16px; padding: 14px 18px;">
          <div class="lg-toolbar" style="margin-bottom: 0;">
            <div style="font-size: 0.84rem; font-weight: 700; color: #38bdf8;">
              <i class="fa-solid fa-file-shield"></i> Bản xem trước A4 chuẩn Nghị định 30/2020/NĐ-CP
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
              <button type="button" class="lg-btn lg-btn-primary" onclick="window.print()">
                <i class="fa-solid fa-print"></i> In / Lưu PDF A4
              </button>
              <button type="button" class="lg-btn lg-btn-success" onclick="downloadWordDoc('{slug}')">
                <i class="fa-solid fa-file-word"></i> Tải Word (.doc)
              </button>
              <button type="button" class="lg-btn lg-btn-secondary" onclick="copyDocHtml()">
                <i class="fa-solid fa-code"></i> Copy HTML
              </button>
              <button type="button" class="lg-btn lg-btn-secondary" onclick="copyDocPlainText()">
                <i class="fa-solid fa-copy"></i> Copy Văn bản
              </button>
            </div>
          </div>
          {extra_controls_html}
          <div id="export-toast" style="display:none; margin-top: 10px; font-size: 0.8rem; color: #34d399; font-weight: 600;"></div>
        </div>

        <div class="a4-viewport">
          <article class="a4-document" id="a4-preview-body"></article>
        </div>
      </div>
    </div>
    """

    full_js = SHARED_EXPORT_AND_WIZARD_JS + "\n" + tool_js + """
    document.addEventListener("DOMContentLoaded", () => {
      document.querySelectorAll("#wizard-form-root input, #wizard-form-root textarea, #wizard-form-root select").forEach(el => {
        el.addEventListener("input", () => {
          el.classList.remove("invalid");
          if (typeof renderDocument === "function") renderDocument();
        });
        el.addEventListener("change", () => {
          el.classList.remove("invalid");
          if (typeof renderDocument === "function") renderDocument();
        });
      });
      if (typeof renderDocument === "function") renderDocument();
    });
    """
    return tool_html, full_js


def _build_labor_contract_wizard(keyword, slug):
    form_steps = """
        <div class="form-step active" data-step="1">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #38bdf8;">Điều 1: Thông tin hai bên giao kết</h2>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="contract-number">Số hợp đồng <span class="lg-req">*</span></label>
              <input type="text" id="contract-number" class="lg-input" value="01/2026/HĐLĐ-VT" required>
            </div>
            <div>
              <label class="lg-label" for="contract-place-date">Địa điểm &amp; Ngày ký <span class="lg-req">*</span></label>
              <input type="text" id="contract-place-date" class="lg-input" value="TP. Hồ Chí Minh, ngày 01 tháng 06 năm 2026" required>
            </div>
          </div>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="employer-name">Tên Người sử dụng lao động (Công ty/HKD) <span class="lg-req">*</span></label>
            <input type="text" id="employer-name" class="lg-input" value="CÔNG TY TNHH GIẢI PHÁP CÔNG NGHỆ MINH ANH" required>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="employer-tax-id">Mã số thuế (MST) <span class="lg-req">*</span></label>
              <input type="text" id="employer-tax-id" class="lg-input" value="0318245901" required>
            </div>
            <div>
              <label class="lg-label" for="employer-rep">Người đại diện pháp luật <span class="lg-req">*</span></label>
              <input type="text" id="employer-rep" class="lg-input" value="Ông Trần Quốc Bảo" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="employer-rep-title">Chức vụ đại diện <span class="lg-req">*</span></label>
              <input type="text" id="employer-rep-title" class="lg-input" value="Giám đốc điều hành" required>
            </div>
            <div>
              <label class="lg-label" for="employer-address">Địa chỉ trụ sở <span class="lg-req">*</span></label>
              <input type="text" id="employer-address" class="lg-input" value="Số 45 Nguyễn Thị Minh Khai, Quận 1, TP. Hồ Chí Minh" required>
            </div>
          </div>

          <hr style="border-color: rgba(255,255,255,0.08); margin: 14px 0;">

          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="employee-name">Họ và tên Người lao động <span class="lg-req">*</span></label>
              <input type="text" id="employee-name" class="lg-input" value="Nguyễn Hoàng Nam" required>
            </div>
            <div>
              <label class="lg-label" for="employee-dob">Ngày tháng năm sinh <span class="lg-req">*</span></label>
              <input type="text" id="employee-dob" class="lg-input" value="15/08/1996" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="employee-cccd">Số CCCD / Định danh cá nhân <span class="lg-req">*</span></label>
              <input type="text" id="employee-cccd" class="lg-input" value="079096001234" required>
            </div>
            <div>
              <label class="lg-label" for="employee-cccd-meta">Ngày cấp &amp; Nơi cấp CCCD <span class="lg-req">*</span></label>
              <input type="text" id="employee-cccd-meta" class="lg-input" value="12/05/2023 tại Cục CSQLHC về TTXH" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="employee-address">Địa chỉ cư trú NLĐ <span class="lg-req">*</span></label>
              <input type="text" id="employee-address" class="lg-input" value="128 Lê Văn Sỹ, Quận Phú Nhuận, TP. Hồ Chí Minh" required>
            </div>
            <div>
              <label class="lg-label" for="employee-phone">Số điện thoại NLĐ <span class="lg-req">*</span></label>
              <input type="text" id="employee-phone" class="lg-input" value="0908 123 456" required>
            </div>
          </div>

          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="resetSampleFields()"><i class="fa-solid fa-eraser"></i> Xóa mẫu</button>
            <button type="button" class="lg-btn lg-btn-primary" onclick="goToStep(2)">Tiếp tục Bước 2 <i class="fa-solid fa-arrow-right"></i></button>
          </div>
        </div>

        <div class="form-step" data-step="2">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #38bdf8;">Điều 2 – 9: Công việc, Lương, Thời giờ &amp; Bảo hiểm</h2>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="contract-type">Loại hợp đồng lao động <span class="lg-req">*</span></label>
              <select id="contract-type" class="lg-select" required>
                <option value="Hợp đồng lao động xác định thời hạn 12 tháng">Xác định thời hạn (12 tháng)</option>
                <option value="Hợp đồng lao động xác định thời hạn 24 tháng">Xác định thời hạn (24 tháng)</option>
                <option value="Hợp đồng lao động xác định thời hạn 36 tháng">Xác định thời hạn (36 tháng)</option>
                <option value="Hợp đồng lao động không xác định thời hạn">Không xác định thời hạn</option>
                <option value="Hợp đồng thử việc (60 ngày)">Hợp đồng thử việc</option>
              </select>
            </div>
            <div>
              <label class="lg-label" for="contract-term">Thời hạn hiệu lực (Từ - Đến) <span class="lg-req">*</span></label>
              <input type="text" id="contract-term" class="lg-input" value="Từ ngày 01/06/2026 đến ngày 31/05/2027" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="job-title">Chức danh chuyên môn <span class="lg-req">*</span></label>
              <input type="text" id="job-title" class="lg-input" value="Chuyên viên Kỹ thuật Phần mềm" required>
            </div>
            <div>
              <label class="lg-label" for="work-location">Địa điểm làm việc <span class="lg-req">*</span></label>
              <input type="text" id="work-location" class="lg-input" value="Trụ sở Công ty tại Số 45 Nguyễn Thị Minh Khai, Quận 1, TP.HCM" required>
            </div>
          </div>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="job-desc">Mô tả công việc phải làm (Điều 21 BLLĐ 2019) <span class="lg-req">*</span></label>
            <textarea id="job-desc" rows="2" class="lg-textarea" required>Thiết kế, phát triển, kiểm thử và bảo trì hệ thống phần mềm nghiệp vụ theo phân công của Trưởng bộ phận Kỹ thuật; báo cáo tiến độ định kỳ hàng tuần.</textarea>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="work-hours">Thời giờ làm việc &amp; Nghỉ ngơi <span class="lg-req">*</span></label>
              <input type="text" id="work-hours" class="lg-input" value="8 giờ/ngày (40 giờ/tuần, nghỉ Thứ 7 & Chủ nhật); 12 ngày phép năm nguyên lương" required>
            </div>
            <div>
              <label class="lg-label" for="wage-region">Vùng lương tối thiểu (NĐ 293/2025) <span class="lg-req">*</span></label>
              <select id="wage-region" class="lg-select" required>
                <option value="1">Vùng I (Tối thiểu 5.310.000đ/tháng)</option>
                <option value="2">Vùng II (Tối thiểu 4.730.000đ/tháng)</option>
                <option value="3">Vùng III (Tối thiểu 4.140.000đ/tháng)</option>
                <option value="4">Vùng IV (Tối thiểu 3.700.000đ/tháng)</option>
              </select>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="base-salary">Mức lương chính (VND/tháng) <span class="lg-req">*</span></label>
              <input type="number" id="base-salary" class="lg-input" value="18000000" min="0" step="500000" required>
            </div>
            <div>
              <label class="lg-label" for="allowance-info">Phụ cấp &amp; Khoản bổ sung</label>
              <input type="text" id="allowance-info" class="lg-input" value="Phụ cấp ăn trưa 730.000đ/tháng, phụ cấp xăng xe & điện thoại 1.270.000đ/tháng">
            </div>
          </div>
          <div id="wage-compliance-banner" class="lg-alert-info"></div>
          <div class="lg-row-2" style="margin-top: 10px; margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="pay-schedule">Hình thức &amp; Kỳ hạn trả lương <span class="lg-req">*</span></label>
              <input type="text" id="pay-schedule" class="lg-input" value="Chuyển khoản ngân hàng 01 lần/tháng vào ngày 05 tháng kế tiếp" required>
            </div>
            <div>
              <label class="lg-label" for="raise-policy">Chế độ nâng bậc, nâng lương <span class="lg-req">*</span></label>
              <input type="text" id="raise-policy" class="lg-input" value="Xét nâng lương định kỳ 01 lần/năm căn cứ KPI và kết quả kinh doanh" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="ppe-info">Bảo hộ lao động &amp; ATVSLĐ (Điều 5) <span class="lg-req">*</span></label>
              <input type="text" id="ppe-info" class="lg-input" value="Cấp phát máy tính làm việc, thẻ nhân viên và trang thiết bị văn phòng đạt chuẩn ATVSLĐ" required>
            </div>
            <div>
              <label class="lg-label" for="training-info">Đào tạo nâng cao tay nghề (Điều 7) <span class="lg-req">*</span></label>
              <input type="text" id="training-info" class="lg-input" value="Công ty tổ chức hoặc tài trợ khóa đào tạo chuyên môn theo kế hoạch nhân sự hàng năm" required>
            </div>
          </div>

          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="goToStep(1)"><i class="fa-solid fa-arrow-left"></i> Quay lại Bước 1</button>
            <button type="button" class="lg-btn lg-btn-primary" onclick="goToStep(3)">Tiếp tục Bước 3 <i class="fa-solid fa-arrow-right"></i></button>
          </div>
        </div>

        <div class="form-step" data-step="3">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #34d399;">Bước 3: Kiểm tra 10 nội dung bắt buộc &amp; Xuất bản</h2>
          <ul style="font-size: 0.84rem; color: #cbd5e1; padding-left: 18px; line-height: 1.65; margin-bottom: 16px;">
            <li>Đầy đủ <strong>Điều 1 đến Điều 9</strong> đáp ứng toàn bộ 10 khoản bắt buộc tại <strong>Điều 21 Bộ luật Lao động 2019</strong> và <strong>Điều 3 Thông tư 10/2020/TT-BLĐTBXH</strong>.</li>
            <li>Đối chiếu tự động mức lương tối thiểu vùng theo <strong>Nghị định 293/2025/NĐ-CP</strong> &amp; tỷ lệ đóng BHXH/BHYT/BHTN (32%) theo mức tham chiếu <strong>Nghị định 161/2026/NĐ-CP</strong>.</li>
            <li>Định dạng A4 chuẩn <strong>Nghị định 30/2020/NĐ-CP</strong> (Phông Times New Roman 13pt, lề trên/dưới 20mm, trái 30mm, phải 15mm).</li>
          </ul>
          <label style="display: flex; align-items: flex-start; gap: 10px; font-size: 0.82rem; color: #d1d5db; margin-bottom: 16px; cursor: pointer;">
            <input type="checkbox" id="tos-agree" checked required style="margin-top: 3px; width: 16px; height: 16px;">
            <span>Tôi xác nhận các thông tin hợp đồng tuân thủ quy định tự thỏa thuận của Bộ luật Lao động 2019.</span>
          </label>
          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="goToStep(2)"><i class="fa-solid fa-arrow-left"></i> Sửa Điều 2–7</button>
            <button type="button" class="lg-btn lg-btn-success" onclick="downloadWordDoc('""" + slug + """')"><i class="fa-solid fa-file-word"></i> Tải Word (.doc) ngay</button>
          </div>
        </div>
    """

    tool_js = """
    function renderDocument() {
      const regionKey = getVal("wage-region", "1");
      const regionInfo = REGION_WAGES_2026[regionKey] || REGION_WAGES_2026["1"];
      const baseSalary = Number(getVal("base-salary", "0")) || 0;
      const isWageCompliant = baseSalary >= regionInfo.minWage;

      const banner = document.getElementById("wage-compliance-banner");
      if (banner) {
        if (isWageCompliant) {
          banner.style.background = "rgba(16,185,129,0.12)";
          banner.style.border = "1px solid rgba(16,185,129,0.35)";
          banner.style.color = "#6ee7b7";
          banner.innerHTML = `<i class="fa-solid fa-circle-check"></i> Hợp lệ: Lương chính <strong>${fmtVnd(baseSalary)} đ</strong> đạt mức tối thiểu ${escHtml(regionInfo.label)} (${fmtVnd(regionInfo.minWage)} đ theo NĐ 293/2025/NĐ-CP).`;
        } else {
          banner.style.background = "rgba(239,68,68,0.14)";
          banner.style.border = "1px solid rgba(239,68,68,0.4)";
          banner.style.color = "#fca5a5";
          banner.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Cảnh báo pháp lý: Lương chính <strong>${fmtVnd(baseSalary)} đ</strong> đang THẤP HƠN mức tối thiểu ${escHtml(regionInfo.label)} (${fmtVnd(regionInfo.minWage)} đ theo NĐ 293/2025/NĐ-CP)!`;
        }
      }

      const preview = document.getElementById("a4-preview-body");
      if (!preview) return;
      preview.innerHTML = `
        <table class="a4-header-table">
          <tr>
            <td class="d30-org-block">
              <div style="font-weight:bold; text-transform:uppercase;">${escHtml(getVal("employer-name", "CÔNG TY ..."))}</div>
              <div style="margin-top:4pt;">Số: ${escHtml(getVal("contract-number", ".../HĐLĐ-2026"))}</div>
            </td>
            <td class="d30-motto-block">
              <div class="d30-quoc-hieu">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
              <div class="d30-tieu-ngu-wrap"><span class="d30-tieu-ngu">Độc lập - Tự do - Hạnh phúc</span></div>
              <div class="d30-date-line">${escHtml(getVal("contract-place-date", "......, ngày ... tháng ... năm 2026"))}</div>
            </td>
          </tr>
        </table>

        <div class="d30-doc-title">HỢP ĐỒNG LAO ĐỘNG</div>
        <div class="d30-doc-sub">(${escHtml(getVal("contract-type", "Hợp đồng lao động"))})</div>

        <p class="d30-p d30-indent"><em>Căn cứ Bộ luật Lao động số 45/2019/QH14 ngày 20/11/2019;</em></p>
        <p class="d30-p d30-indent"><em>Căn cứ Nghị định 145/2020/NĐ-CP và Thông tư 10/2020/TT-BLĐTBXH hướng dẫn về nội dung hợp đồng lao động;</em></p>
        <p class="d30-p d30-indent"><em>Căn cứ Nghị định 293/2025/NĐ-CP quy định mức lương tối thiểu vùng và Nghị định 161/2026/NĐ-CP về mức tham chiếu đóng bảo hiểm xã hội;</em></p>
        <p class="d30-p d30-indent">Hôm nay, tại ${escHtml(getVal("work-location", "trụ sở công ty"))}, chúng tôi gồm:</p>

        <div class="d30-section-h">Điều 1: Thông tin Người sử dụng lao động và Người lao động</div>
        <p class="d30-p"><strong>1. Bên A - Người sử dụng lao động: ${escHtml(getVal("employer-name"))}</strong></p>
        <p class="d30-p d30-indent">- Mã số thuế / ĐKKD: ${escHtml(getVal("employer-tax-id"))}</p>
        <p class="d30-p d30-indent">- Địa chỉ trụ sở chính: ${escHtml(getVal("employer-address"))}</p>
        <p class="d30-p d30-indent">- Người đại diện theo pháp luật: ${escHtml(getVal("employer-rep"))} — Chức vụ: ${escHtml(getVal("employer-rep-title"))}</p>
        <p class="d30-p" style="margin-top:6pt;"><strong>2. Bên B - Người lao động: ${escHtml(getVal("employee-name"))}</strong></p>
        <p class="d30-p d30-indent">- Ngày tháng năm sinh: ${escHtml(getVal("employee-dob"))} — Quốc tịch: Việt Nam</p>
        <p class="d30-p d30-indent">- Số CCCD / Định danh cá nhân: ${escHtml(getVal("employee-cccd"))} (Cấp ngày ${escHtml(getVal("employee-cccd-meta"))})</p>
        <p class="d30-p d30-indent">- Địa chỉ cư trú: ${escHtml(getVal("employee-address"))} — Điện thoại: ${escHtml(getVal("employee-phone"))}</p>
        <p class="d30-p d30-indent">Hai bên thỏa thuận ký kết Hợp đồng lao động và cam kết thực hiện đúng các điều khoản sau đây:</p>

        <div class="d30-section-h">Điều 2: Loại hợp đồng, Thời hạn, Địa điểm làm việc và Mô tả công việc</div>
        <p class="d30-p d30-indent">- Loại hợp đồng lao động: ${escHtml(getVal("contract-type"))}.</p>
        <p class="d30-p d30-indent">- Thời hạn hợp đồng: ${escHtml(getVal("contract-term"))}.</p>
        <p class="d30-p d30-indent">- Địa điểm làm việc: ${escHtml(getVal("work-location"))}.</p>
        <p class="d30-p d30-indent">- Chức danh chuyên môn: ${escHtml(getVal("job-title"))}.</p>
        <p class="d30-p d30-indent">- Công việc phải làm: ${escHtml(getVal("job-desc"))}</p>

        <div class="d30-section-h">Điều 3: Thời giờ làm việc và Thời giờ nghỉ ngơi</div>
        <p class="d30-p d30-indent">- Thời giờ làm việc &amp; nghỉ ngơi hàng tuần: ${escHtml(getVal("work-hours"))}.</p>
        <p class="d30-p d30-indent">- Nghỉ lễ, Tết và nghỉ hàng năm: Người lao động được nghỉ hưởng nguyên lương các ngày lễ, Tết theo Điều 112 và tối thiểu 12 ngày nghỉ hàng năm đối với người làm công việc bình thường theo Điều 113 Bộ luật Lao động 2019.</p>

        <div class="d30-section-h">Điều 4: Tiền lương, Phụ cấp, Hình thức trả lương và Chế độ nâng lương</div>
        <p class="d30-p d30-indent">- Mức lương chính theo công việc/chức danh: <strong>${fmtVnd(baseSalary)} VNĐ/tháng</strong> (đối chiếu ${escHtml(regionInfo.label)} theo Nghị định 293/2025/NĐ-CP).</p>
        <p class="d30-p d30-indent">- Phụ cấp lương và các khoản bổ sung khác: ${escHtml(getVal("allowance-info", "Theo quy chế lương thưởng của Công ty"))}.</p>
        <p class="d30-p d30-indent">- Hình thức và kỳ hạn trả lương: ${escHtml(getVal("pay-schedule"))}.</p>
        <p class="d30-p d30-indent">- Chế độ nâng bậc, nâng lương: ${escHtml(getVal("raise-policy"))}.</p>

        <div class="d30-section-h">Điều 5: Trang bị bảo hộ lao động và An toàn, vệ sinh lao động</div>
        <p class="d30-p d30-indent">Bên A trang bị cho Bên B phương tiện làm việc và bảo hộ lao động gồm: ${escHtml(getVal("ppe-info"))}. Hai bên có trách nhiệm tuân thủ nghiêm quy định pháp luật về An toàn, vệ sinh lao động tại nơi làm việc.</p>

        <div class="d30-section-h">Điều 6: Bảo hiểm xã hội, Bảo hiểm y tế và Bảo hiểm thất nghiệp</div>
        <p class="d30-p d30-indent">Hai bên thực hiện trích nộp đầy đủ Bảo hiểm xã hội (BHXH), Bảo hiểm y tế (BHYT) và Bảo hiểm thất nghiệp (BHTN) trên mức lương làm căn cứ đóng bảo hiểm và không vượt quá mức trần theo quy định hiện hành (áp dụng mức tham chiếu theo Nghị định 161/2026/NĐ-CP): Bên A đóng 21,5% (17,5% BHXH, 3% BHYT, 1% BHTN) và Bên B đóng 10,5% (8% BHXH, 1,5% BHYT, 1% BHTN).</p>

        <div class="d30-section-h">Điều 7: Đào tạo, bồi dưỡng nâng cao trình độ kỹ năng nghề</div>
        <p class="d30-p d30-indent">${escHtml(getVal("training-info"))}. Trường hợp Bên A tài trợ chi phí đào tạo nâng cao trình độ bằng ngân sách Công ty, hai bên sẽ ký Hợp đồng đào tạo nghề riêng theo Điều 62 Bộ luật Lao động 2019.</p>

        <div class="d30-section-h">Điều 8: Quyền, Nghĩa vụ hai bên; Bảo mật thông tin và Sở hữu trí tuệ</div>
        <p class="d30-p d30-indent">- Bên B được hưởng các quyền lợi theo Hợp đồng và nội quy lao động; có nghĩa vụ hoàn thành công việc được giao, bảo mật tuyệt đối bí mật kinh doanh, bí mật công nghệ và dữ liệu khách hàng trong suốt thời hạn hợp đồng và tối thiểu 24 tháng sau khi chấm dứt hợp đồng.</p>
        <p class="d30-p d30-indent">- Mọi sản phẩm trí tuệ, mã nguồn, tài liệu do Bên B sáng tạo trong quá trình thực hiện công việc theo Hợp đồng này thuộc quyền sở hữu của Bên A theo quy định Luật Sở hữu trí tuệ.</p>

        <div class="d30-section-h">Điều 9: Điều khoản thi hành</div>
        <p class="d30-p d30-indent">Mọi sửa đổi, bổ sung nội dung Hợp đồng phải được hai bên thỏa thuận bằng văn bản (Phụ lục hợp đồng lao động). Tranh chấp phát sinh được giải quyết ưu tiên qua thương lượng hoặc theo Bộ luật Lao động tại cơ quan có thẩm quyền. Hợp đồng được lập thành 02 bản có giá trị pháp lý như nhau, mỗi bên giữ 01 bản và có hiệu lực kể từ ngày ký.</p>

        <table class="d30-sig-table">
          <tr>
            <td style="width:50%;">
              <div class="d30-sig-title">NGƯỜI LAO ĐỘNG</div>
              <div class="d30-sig-note">(Ký và ghi rõ họ tên)</div>
              <div class="d30-sig-space"></div>
              <div style="font-weight:bold;">${escHtml(getVal("employee-name"))}</div>
            </td>
            <td style="width:50%;">
              <div class="d30-sig-title">NGƯỜI SỬ DỤNG LAO ĐỘNG</div>
              <div class="d30-sig-note">(Ký tên, ghi rõ họ tên và đóng dấu)</div>
              <div class="d30-sig-space"></div>
              <div style="font-weight:bold;">${escHtml(getVal("employer-rep"))}</div>
            </td>
          </tr>
        </table>
      `;
    }
    """

    tool_html, full_js = _wrap_wizard_layout(slug, form_steps, tool_js)
    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="Hợp đồng & Pháp lý",
        page_title=f"{keyword} - Chuẩn Điều 21 BLLĐ 2019 & Nghị Định 30/2020",
        meta_desc="Tạo mẫu hợp đồng lao động 2026 chuẩn 10 điều khoản bắt buộc (Điều 21 Bộ luật Lao động 2019, Thông tư 10/2020), kiểm tra lương tối thiểu vùng NĐ 293/2025, tải Word .doc và PDF A4 miễn phí.",
        meta_keywords="mẫu hợp đồng lao động 2026, điều 21 bộ luật lao động 2019, nghị định 293/2025/nđ-cp, nghị định 30/2020/nđ-cp",
        subtitle="Biểu mẫu Hợp đồng lao động 9 Điều (10 nội dung bắt buộc theo Điều 21 BLLĐ 2019 & TT 10/2020). Tự động kiểm tra Lương tối thiểu vùng NĐ 293/2025/NĐ-CP và xuất Word/PDF A4 miễn phí.",
        tool_html=tool_html,
        tool_js=full_js,
        extra_head=DECREE30_CSS,
        nav_badge="Nghị định 30/2020 A4",
    )


def _build_asset_handover_wizard(keyword, slug):
    form_steps = """
        <div class="form-step active" data-step="1">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #38bdf8;">Bước 1: Thông tin Bên giao &amp; Bên nhận tài sản</h2>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="doc-number">Số biên bản <span class="lg-req">*</span></label>
              <input type="text" id="doc-number" class="lg-input" value="12/BBBG-TS/2026" required>
            </div>
            <div>
              <label class="lg-label" for="doc-place-date">Địa điểm &amp; Ngày lập <span class="lg-req">*</span></label>
              <input type="text" id="doc-place-date" class="lg-input" value="Hà Nội, ngày 15 tháng 06 năm 2026" required>
            </div>
          </div>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="org-name">Tên Cơ quan / Doanh nghiệp <span class="lg-req">*</span></label>
            <input type="text" id="org-name" class="lg-input" value="CÔNG TY CỔ PHẦN THƯƠNG MẠI VÀ ĐẦU TƯ AN PHÁT" required>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="giver-name">Đại diện Bên giao <span class="lg-req">*</span></label>
              <input type="text" id="giver-name" class="lg-input" value="Lê Minh Tuấn" required>
            </div>
            <div>
              <label class="lg-label" for="giver-title">Chức vụ / Bộ phận Bên giao <span class="lg-req">*</span></label>
              <input type="text" id="giver-title" class="lg-input" value="Trưởng phòng Hành chính - IT" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="receiver-name">Đại diện Bên nhận <span class="lg-req">*</span></label>
              <input type="text" id="receiver-name" class="lg-input" value="Phạm Thu Hương" required>
            </div>
            <div>
              <label class="lg-label" for="receiver-title">Chức vụ / Bộ phận Bên nhận <span class="lg-req">*</span></label>
              <input type="text" id="receiver-title" class="lg-input" value="Chuyên viên Tài chính - Kế toán" required>
            </div>
          </div>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="handover-reason">Lý do &amp; Căn cứ bàn giao <span class="lg-req">*</span></label>
            <input type="text" id="handover-reason" class="lg-input" value="Bàn giao trang thiết bị làm việc phục vụ nhân sự nhận công tác theo Quyết định tiếp nhận số 28/QĐ-NS" required>
          </div>

          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="resetSampleFields()"><i class="fa-solid fa-eraser"></i> Xóa mẫu</button>
            <button type="button" class="lg-btn lg-btn-primary" onclick="goToStep(2)">Tiếp tục Bước 2 <i class="fa-solid fa-arrow-right"></i></button>
          </div>
        </div>

        <div class="form-step" data-step="2">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #38bdf8;">Bước 2: Danh mục tài sản, số lượng &amp; giá trị</h2>
          <div id="asset-rows-container"></div>
          <button type="button" class="lg-btn lg-btn-secondary" style="width:100%; margin: 8px 0 12px 0;" onclick="addAssetRow()">
            <i class="fa-solid fa-plus"></i> Thêm dòng tài sản / thiết bị
          </button>
          <div>
            <label class="lg-label" for="handover-note">Ghi chú &amp; Cam kết bảo quản <span class="lg-req">*</span></label>
            <textarea id="handover-note" rows="2" class="lg-textarea" required>Bên nhận đã kiểm tra đầy đủ số lượng, thông số kỹ thuật và tình trạng hoạt động thực tế của từng tài sản nêu trên; cam kết sử dụng đúng mục đích công việc và hoàn trả khi kết thúc công tác.</textarea>
          </div>

          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="goToStep(1)"><i class="fa-solid fa-arrow-left"></i> Quay lại Bước 1</button>
            <button type="button" class="lg-btn lg-btn-primary" onclick="goToStep(3)">Tiếp tục Bước 3 <i class="fa-solid fa-arrow-right"></i></button>
          </div>
        </div>

        <div class="form-step" data-step="3">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #34d399;">Bước 3: Xác nhận &amp; Tải Biên bản A4</h2>
          <p style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 14px;">Hệ thống đã tự động tổng hợp bảng danh mục tài sản, tổng số lượng và tổng giá trị bàn giao lên mẫu A4 chuẩn Nghị định 30/2020/NĐ-CP.</p>
          <label style="display: flex; align-items: flex-start; gap: 10px; font-size: 0.82rem; color: #d1d5db; margin-bottom: 16px; cursor: pointer;">
            <input type="checkbox" id="tos-agree" checked required style="margin-top: 3px; width: 16px; height: 16px;">
            <span>Xác nhận số liệu tài sản do hai bên tự đối chiếu trực tiếp trên trình duyệt.</span>
          </label>
          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="goToStep(2)"><i class="fa-solid fa-arrow-left"></i> Sửa danh mục</button>
            <button type="button" class="lg-btn lg-btn-success" onclick="downloadWordDoc('""" + slug + """')"><i class="fa-solid fa-file-word"></i> Tải Word (.doc) ngay</button>
          </div>
        </div>
    """

    tool_js = """
    let assetItems = [
      { name: "Laptop Dell Latitude 5440 (S/N: DL-88921)", qty: 1, unitPrice: 21500000, cond: "Mới 100%, đủ sạc" },
      { name: "Màn hình LG 27 inch FullHD", qty: 1, unitPrice: 4800000, cond: "Hoạt động bình thường" },
      { name: "Thẻ từ ra vào văn phòng + Dây đeo", qty: 1, unitPrice: 150000, cond: "Mới 100%" }
    ];

    function renderAssetInputs() {
      const container = document.getElementById("asset-rows-container");
      if (!container) return;
      container.innerHTML = assetItems.map((item, idx) => `
        <div class="d30-asset-row">
          <input type="text" class="lg-input" placeholder="Tên &amp; Serial tài sản" value="${escHtml(item.name)}" required oninput="updateAssetField(${idx}, 'name', this.value)">
          <input type="text" class="lg-input" placeholder="Tình trạng" value="${escHtml(item.cond)}" required oninput="updateAssetField(${idx}, 'cond', this.value)">
          <input type="number" class="lg-input" placeholder="SL" value="${item.qty}" min="1" required oninput="updateAssetField(${idx}, 'qty', Number(this.value)||0)">
          <input type="number" class="lg-input" placeholder="Đơn giá (đ)" value="${item.unitPrice}" min="0" step="50000" required oninput="updateAssetField(${idx}, 'unitPrice', Number(this.value)||0)">
          <button type="button" class="lg-btn lg-btn-secondary" style="padding: 8px; color: #f87171;" onclick="removeAssetRow(${idx})" title="Xóa dòng">&times;</button>
        </div>
      `).join("");
    }

    function updateAssetField(idx, field, val) {
      if (!assetItems[idx]) return;
      assetItems[idx][field] = val;
      renderDocument();
    }

    function addAssetRow() {
      assetItems.push({ name: "Thiết bị mới", qty: 1, unitPrice: 0, cond: "Hoạt động tốt" });
      renderAssetInputs();
      renderDocument();
    }

    function removeAssetRow(idx) {
      if (assetItems.length <= 1) return;
      assetItems.splice(idx, 1);
      renderAssetInputs();
      renderDocument();
    }

    function renderDocument() {
      const preview = document.getElementById("a4-preview-body");
      if (!preview) return;
      let totalQty = 0;
      let totalVal = 0;
      const rowsHtml = assetItems.map((it, i) => {
        const q = Number(it.qty) || 0;
        const p = Number(it.unitPrice) || 0;
        const sub = q * p;
        totalQty += q;
        totalVal += sub;
        return `
          <tr>
            <td style="text-align:center;">${i + 1}</td>
            <td>${escHtml(it.name)}</td>
            <td style="text-align:center;">${q}</td>
            <td>${escHtml(it.cond)}</td>
            <td style="text-align:right;">${fmtVnd(sub)} đ</td>
          </tr>
        `;
      }).join("");

      preview.innerHTML = `
        <table class="a4-header-table">
          <tr>
            <td class="d30-org-block">
              <div style="font-weight:bold; text-transform:uppercase;">${escHtml(getVal("org-name"))}</div>
              <div style="margin-top:4pt;">Số: ${escHtml(getVal("doc-number"))}</div>
            </td>
            <td class="d30-motto-block">
              <div class="d30-quoc-hieu">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
              <div class="d30-tieu-ngu-wrap"><span class="d30-tieu-ngu">Độc lập - Tự do - Hạnh phúc</span></div>
              <div class="d30-date-line">${escHtml(getVal("doc-place-date"))}</div>
            </td>
          </tr>
        </table>

        <div class="d30-doc-title">BIÊN BẢN BÀN GIAO TÀI SẢN &amp; THIẾT BỊ</div>
        <div class="d30-doc-sub">(V/v: Bàn giao trang thiết bị, công cụ dụng cụ phục vụ công tác)</div>

        <p class="d30-p d30-indent">Căn cứ: ${escHtml(getVal("handover-reason"))}.</p>
        <p class="d30-p d30-indent">Hôm nay, ${escHtml(getVal("doc-place-date"))}, tại trụ sở ${escHtml(getVal("org-name"))}, chúng tôi gồm các bên sau:</p>

        <p class="d30-p"><strong>1. BÊN GIAO TÀI SẢN (BÊN A):</strong> Ông/Bà <strong>${escHtml(getVal("giver-name"))}</strong> — Chức vụ/Bộ phận: ${escHtml(getVal("giver-title"))}.</p>
        <p class="d30-p"><strong>2. BÊN NHẬN TÀI SẢN (BÊN B):</strong> Ông/Bà <strong>${escHtml(getVal("receiver-name"))}</strong> — Chức vụ/Bộ phận: ${escHtml(getVal("receiver-title"))}.</p>
        <p class="d30-p d30-indent">Hai bên thống nhất tiến hành kiểm đếm, bàn giao các tài sản, thiết bị theo danh mục dưới đây:</p>

        <table class="d30-table">
          <thead>
            <tr>
              <th style="width:40pt;">STT</th>
              <th>Tên tài sản / Mã Serial</th>
              <th style="width:55pt;">Số lượng</th>
              <th style="width:120pt;">Tình trạng thực tế</th>
              <th style="width:105pt;">Giá trị (VNĐ)</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
            <tr>
              <td colspan="2" style="font-weight:bold; text-align:right;">TỔNG CỘNG BÀN GIAO:</td>
              <td style="font-weight:bold; text-align:center;">${totalQty}</td>
              <td></td>
              <td style="font-weight:bold; text-align:right;">${fmtVnd(totalVal)} đ</td>
            </tr>
          </tbody>
        </table>

        <p class="d30-p d30-indent"><strong>Cam kết và trách nhiệm:</strong> ${escHtml(getVal("handover-note"))}</p>
        <p class="d30-p d30-indent">Biên bản được lập thành 02 bản có giá trị pháp lý như nhau, Bên A giữ 01 bản, Bên B giữ 01 bản làm căn cứ quản lý và đối chiếu tài sản.</p>

        <table class="d30-sig-table">
          <tr>
            <td style="width:33.3%;">
              <div class="d30-sig-title">BÊN GIAO</div>
              <div class="d30-sig-note">(Ký, ghi rõ họ tên)</div>
              <div class="d30-sig-space"></div>
              <div style="font-weight:bold;">${escHtml(getVal("giver-name"))}</div>
            </td>
            <td style="width:33.3%;">
              <div class="d30-sig-title">XÁC NHẬN KẾ TOÁN / HCNS</div>
              <div class="d30-sig-note">(Ký, ghi rõ họ tên)</div>
              <div class="d30-sig-space"></div>
            </td>
            <td style="width:33.3%;">
              <div class="d30-sig-title">BÊN NHẬN</div>
              <div class="d30-sig-note">(Ký, ghi rõ họ tên)</div>
              <div class="d30-sig-space"></div>
              <div style="font-weight:bold;">${escHtml(getVal("receiver-name"))}</div>
            </td>
          </tr>
        </table>
      `;
    }

    document.addEventListener("DOMContentLoaded", renderAssetInputs);
    """

    tool_html, full_js = _wrap_wizard_layout(slug, form_steps, tool_js)
    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="Hợp đồng & Biên bản",
        page_title=f"{keyword} - Chuẩn Kiểm Toán & Nghị Định 30/2020",
        meta_desc="Tạo biên bản bàn giao tài sản, máy tính, thiết bị văn phòng tự động tính tổng số lượng & giá trị, xuất file Word .doc và PDF A4 miễn phí.",
        meta_keywords="biên bản bàn giao tài sản, bàn giao thiết bị công ty, nghị định 30/2020/nđ-cp",
        subtitle="Biểu mẫu Biên bản bàn giao tài sản & thiết bị hỗ trợ thêm/xóa nhiều dòng thiết bị, tự động tổng hợp số lượng, giá trị và xuất Word/PDF chuẩn A4.",
        tool_html=tool_html,
        tool_js=full_js,
        extra_head=DECREE30_CSS,
        nav_badge="Nghị định 30/2020 A4",
    )


def _build_job_application_wizard(keyword, slug):
    form_steps = """
        <div class="form-step active" data-step="1">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #38bdf8;">Bước 1: Kính gửi &amp; Thông tin ứng viên</h2>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="user-recipient">Kính gửi (Ban Giám đốc / Bộ phận Tuyển dụng) <span class="lg-req">*</span></label>
            <input type="text" id="user-recipient" class="lg-input" value="Ban Giám đốc và Phòng Nhân sự Công ty Cổ phần Công nghệ Số Việt Nam" required>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="applicant-name">Họ và tên ứng viên <span class="lg-req">*</span></label>
              <input type="text" id="applicant-name" class="lg-input" value="Nguyễn Thảo Vy" required>
            </div>
            <div>
              <label class="lg-label" for="applicant-dob">Ngày sinh <span class="lg-req">*</span></label>
              <input type="text" id="applicant-dob" class="lg-input" value="20/10/1998" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="applicant-phone">Số điện thoại <span class="lg-req">*</span></label>
              <input type="text" id="applicant-phone" class="lg-input" value="0912 345 678" required>
            </div>
            <div>
              <label class="lg-label" for="applicant-email">Email liên hệ <span class="lg-req">*</span></label>
              <input type="text" id="applicant-email" class="lg-input" value="thaovy.nguyen@example.com" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="applicant-cccd">Số CCCD (nếu cần bổ sung hồ sơ) <span class="lg-req">*</span></label>
              <input type="text" id="applicant-cccd" class="lg-input" value="001198004567" required>
            </div>
            <div>
              <label class="lg-label" for="applicant-address">Địa chỉ hiện tại <span class="lg-req">*</span></label>
              <input type="text" id="applicant-address" class="lg-input" value="Quận Cầu Giấy, TP. Hà Nội" required>
            </div>
          </div>
          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="resetSampleFields()"><i class="fa-solid fa-eraser"></i> Xóa mẫu</button>
            <button type="button" class="lg-btn lg-btn-primary" onclick="goToStep(2)">Tiếp tục Bước 2 <i class="fa-solid fa-arrow-right"></i></button>
          </div>
        </div>

        <div class="form-step" data-step="2">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #38bdf8;">Bước 2: Vị trí ứng tuyển &amp; Năng lực nổi bật</h2>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="applied-position">Vị trí ứng tuyển <span class="lg-req">*</span></label>
              <input type="text" id="applied-position" class="lg-input" value="Chuyên viên Phân tích Nghiệp vụ (Business Analyst)" required>
            </div>
            <div>
              <label class="lg-label" for="doc-place-date">Địa điểm &amp; Ngày viết đơn <span class="lg-req">*</span></label>
              <input type="text" id="doc-place-date" class="lg-input" value="Hà Nội, ngày 15 tháng 06 năm 2026" required>
            </div>
          </div>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="education-summary">Trình độ học vấn &amp; Bằng cấp <span class="lg-req">*</span></label>
            <input type="text" id="education-summary" class="lg-input" value="Cử nhân Hệ thống Thông tin Quản lý - Trường Đại học Kinh tế Quốc dân (Loại Giỏi)" required>
          </div>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="experience-summary">Tóm tắt kinh nghiệm &amp; Kỹ năng cốt lõi <span class="lg-req">*</span></label>
            <textarea id="experience-summary" rows="3" class="lg-textarea" required>Có hơn 03 năm kinh nghiệm phân tích nghiệp vụ FinTech/ERP, viết tài liệu SRS/BRD, thiết kế luồng quy trình BPMN và làm việc trực tiếp với đội ngũ kỹ sư phần mềm theo phương pháp Agile/Scrum.</textarea>
          </div>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="commitment-note">Nguyện vọng &amp; Cam kết thử việc <span class="lg-req">*</span></label>
            <textarea id="commitment-note" rows="2" class="lg-textarea" required>Tôi cam kết tuân thủ nội quy lao động, hoàn thành tốt nhiệm vụ được giao và sẵn sàng nhận việc ngay khi Quý Công ty sắp xếp lịch phỏng vấn.</textarea>
          </div>

          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="goToStep(1)"><i class="fa-solid fa-arrow-left"></i> Quay lại Bước 1</button>
            <button type="button" class="lg-btn lg-btn-primary" onclick="goToStep(3)">Tiếp tục Bước 3 <i class="fa-solid fa-arrow-right"></i></button>
          </div>
        </div>

        <div class="form-step" data-step="3">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #34d399;">Bước 3: Hoàn tất Đơn xin việc chuẩn hành chính</h2>
          <p style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 14px;">Đơn xin việc được trình bày chuẩn thể thức hành chính Nghị định 30/2020/NĐ-CP và quy chuẩn Bộ luật Lao động 2019, phù hợp gửi trực tiếp hoặc kèm hồ sơ ứng tuyển online.</p>
          <label style="display: flex; align-items: flex-start; gap: 10px; font-size: 0.82rem; color: #d1d5db; margin-bottom: 16px; cursor: pointer;">
            <input type="checkbox" id="tos-agree" checked required style="margin-top: 3px; width: 16px; height: 16px;">
            <span>Tôi cam đoan thông tin hồ sơ ứng tuyển là trung thực và chính xác.</span>
          </label>
          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="goToStep(2)"><i class="fa-solid fa-arrow-left"></i> Chỉnh sửa</button>
            <button type="button" class="lg-btn lg-btn-success" onclick="downloadWordDoc('""" + slug + """')"><i class="fa-solid fa-file-word"></i> Tải Word (.doc) ngay</button>
          </div>
        </div>
    """

    tool_js = """
    function renderDocument() {
      const preview = document.getElementById("a4-preview-body");
      if (!preview) return;
      preview.innerHTML = `
        <div class="d30-quoc-hieu">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="d30-tieu-ngu-wrap"><span class="d30-tieu-ngu">Độc lập - Tự do - Hạnh phúc</span></div>
        <div class="d30-date-line" style="text-align:right; margin-top:10pt;">${escHtml(getVal("doc-place-date"))}</div>

        <div class="d30-doc-title">ĐƠN XIN VIỆC</div>
        <div class="d30-doc-sub">(V/v: Ứng tuyển vị trí ${escHtml(getVal("applied-position"))})</div>

        <p class="d30-p" style="margin-top: 12pt;"><strong>Kính gửi: ${escHtml(getVal("user-recipient"))}</strong></p>
        <p class="d30-p d30-indent">Tôi tên là: <strong>${escHtml(getVal("applicant-name"))}</strong> — Ngày sinh: ${escHtml(getVal("applicant-dob"))}</p>
        <p class="d30-p d30-indent">Số CCCD: ${escHtml(getVal("applicant-cccd"))} — Địa chỉ hiện tại: ${escHtml(getVal("applicant-address"))}</p>
        <p class="d30-p d30-indent">Điện thoại: ${escHtml(getVal("applicant-phone"))} — Email: ${escHtml(getVal("applicant-email"))}</p>

        <p class="d30-p d30-indent" style="margin-top:8pt;">Qua tìm hiểu thông tin tuyển dụng của Quý Công ty, tôi được biết Quý Công ty đang có nhu cầu tuyển dụng nhân sự cho vị trí <strong>${escHtml(getVal("applied-position"))}</strong>. Bằng đơn này, tôi trân trọng bày tỏ nguyện vọng được tham gia ứng tuyển và đóng góp năng lực chuyên môn tại Quý Công ty.</p>

        <p class="d30-p d30-indent"><strong>1. Trình độ chuyên môn:</strong> ${escHtml(getVal("education-summary"))}.</p>
        <p class="d30-p d30-indent"><strong>2. Kinh nghiệm &amp; Kỹ năng:</strong> ${escHtml(getVal("experience-summary"))}</p>
        <p class="d30-p d30-indent"><strong>3. Cam kết cá nhân:</strong> ${escHtml(getVal("commitment-note"))}</p>

        <p class="d30-p d30-indent" style="margin-top:8pt;">Tôi xin gửi kèm theo đơn này Sơ yếu lý lịch và các văn bằng chứng chỉ liên quan để Quý Công ty xem xét. Kính mong Ban Giám đốc và Phòng Nhân sự tạo điều kiện sắp xếp cho tôi một buổi phỏng vấn trực tiếp để trình bày rõ hơn về kinh nghiệm làm việc.</p>
        <p class="d30-p d30-indent">Xin trân trọng cảm ơn!</p>

        <table class="d30-sig-table">
          <tr>
            <td style="width:50%;"></td>
            <td style="width:50%;">
              <div class="d30-sig-title">NGƯỜI LÀM ĐƠN</div>
              <div class="d30-sig-note">(Ký và ghi rõ họ tên)</div>
              <div class="d30-sig-space"></div>
              <div style="font-weight:bold;">${escHtml(getVal("applicant-name"))}</div>
            </td>
          </tr>
        </table>
      `;
    }
    """

    tool_html, full_js = _wrap_wizard_layout(slug, form_steps, tool_js)
    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="Đơn từ Hành chính",
        page_title=f"{keyword} - Chuẩn Hành Chính Nghị Định 30/2020",
        meta_desc="Tạo mẫu đơn xin việc và thư ứng tuyển chuẩn thể thức hành chính Nghị định 30/2020/NĐ-CP & Bộ luật Lao động 2019, tải file Word .doc và in PDF A4 miễn phí.",
        meta_keywords="mẫu đơn xin việc, thư ứng tuyển chuẩn hành chính, nghị định 30/2020/nđ-cp",
        subtitle="Biểu mẫu Đơn xin việc & Thư ứng tuyển chuẩn thể thức hành chính Nghị định 30/2020/NĐ-CP, chỉnh sửa trực tiếp và tải file Word/PDF miễn phí.",
        tool_html=tool_html,
        tool_js=full_js,
        extra_head=DECREE30_CSS,
        nav_badge="Nghị định 30/2020 A4",
    )


def _build_leave_request_wizard(keyword, slug):
    form_steps = """
        <div class="form-step active" data-step="1">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #38bdf8;">Bước 1: Người duyệt đơn &amp; Thông tin nhân sự</h2>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="user-recipient">Kính gửi (Ban Giám đốc / Trưởng bộ phận) <span class="lg-req">*</span></label>
            <input type="text" id="user-recipient" class="lg-input" value="Ban Giám đốc Công ty và Trưởng phòng Kinh doanh" required>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="emp-name">Họ và tên nhân sự <span class="lg-req">*</span></label>
              <input type="text" id="emp-name" class="lg-input" value="Vũ Đức Huy" required>
            </div>
            <div>
              <label class="lg-label" for="emp-code">Mã nhân viên</label>
              <input type="text" id="emp-code" class="lg-input" value="NV-2026-042">
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="emp-title">Chức vụ <span class="lg-req">*</span></label>
              <input type="text" id="emp-title" class="lg-input" value="Chuyên viên Kinh doanh B2B" required>
            </div>
            <div>
              <label class="lg-label" for="emp-dept">Phòng ban / Bộ phận <span class="lg-req">*</span></label>
              <input type="text" id="emp-dept" class="lg-input" value="Phòng Kinh doanh" required>
            </div>
          </div>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="doc-place-date">Địa điểm &amp; Ngày làm đơn <span class="lg-req">*</span></label>
            <input type="text" id="doc-place-date" class="lg-input" value="TP. Hồ Chí Minh, ngày 18 tháng 06 năm 2026" required>
          </div>
          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="resetSampleFields()"><i class="fa-solid fa-eraser"></i> Xóa mẫu</button>
            <button type="button" class="lg-btn lg-btn-primary" onclick="goToStep(2)">Tiếp tục Bước 2 <i class="fa-solid fa-arrow-right"></i></button>
          </div>
        </div>

        <div class="form-step" data-step="2">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #38bdf8;">Bước 2: Thời gian nghỉ &amp; Bàn giao công việc</h2>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="leave-type">Loại hình nghỉ phép <span class="lg-req">*</span></label>
            <select id="leave-type" class="lg-select" required>
              <option value="Nghỉ phép năm hưởng nguyên lương (Điều 113 BLLĐ 2019)">Nghỉ phép năm hưởng nguyên lương (Điều 113 BLLĐ 2019)</option>
              <option value="Nghỉ việc riêng hưởng nguyên lương (Điều 115 BLLĐ 2019)">Nghỉ việc riêng hưởng nguyên lương (Điều 115 BLLĐ 2019)</option>
              <option value="Nghỉ việc riêng không hưởng lương">Nghỉ việc riêng không hưởng lương</option>
              <option value="Nghỉ ốm / hưởng chế độ BHXH">Nghỉ ốm / hưởng chế độ BHXH</option>
            </select>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="leave-from">Từ ngày <span class="lg-req">*</span></label>
              <input type="text" id="leave-from" class="lg-input" value="22/06/2026" required>
            </div>
            <div>
              <label class="lg-label" for="leave-to">Đến hết ngày <span class="lg-req">*</span></label>
              <input type="text" id="leave-to" class="lg-input" value="24/06/2026" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="leave-days">Tổng số ngày làm việc xin nghỉ <span class="lg-req">*</span></label>
              <input type="text" id="leave-days" class="lg-input" value="03 ngày làm việc" required>
            </div>
            <div>
              <label class="lg-label" for="emp-emergency-phone">SĐT liên hệ khi cần gấp <span class="lg-req">*</span></label>
              <input type="text" id="emp-emergency-phone" class="lg-input" value="0989 456 321" required>
            </div>
          </div>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="leave-reason">Lý do xin nghỉ phép <span class="lg-req">*</span></label>
            <input type="text" id="leave-reason" class="lg-input" value="Giải quyết công việc gia đình" required>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="handover-person">Người nhận bàn giao công việc <span class="lg-req">*</span></label>
              <input type="text" id="handover-person" class="lg-input" value="Nguyễn Thị Lan Anh (Chuyên viên Kinh doanh)" required>
            </div>
            <div>
              <label class="lg-label" for="handover-tasks">Nội dung bàn giao <span class="lg-req">*</span></label>
              <input type="text" id="handover-tasks" class="lg-input" value="Hỗ trợ khách hàng hợp đồng tháng 6 và báo cáo tuần" required>
            </div>
          </div>

          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="goToStep(1)"><i class="fa-solid fa-arrow-left"></i> Quay lại Bước 1</button>
            <button type="button" class="lg-btn lg-btn-primary" onclick="goToStep(3)">Tiếp tục Bước 3 <i class="fa-solid fa-arrow-right"></i></button>
          </div>
        </div>

        <div class="form-step" data-step="3">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #34d399;">Bước 3: Hoàn tất Đơn xin nghỉ phép</h2>
          <p style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 14px;">Đơn tích hợp sẵn chữ ký Người làm đơn, Người nhận bàn giao và ô phê duyệt của Trưởng bộ phận / Ban Giám đốc.</p>
          <label style="display: flex; align-items: flex-start; gap: 10px; font-size: 0.82rem; color: #d1d5db; margin-bottom: 16px; cursor: pointer;">
            <input type="checkbox" id="tos-agree" checked required style="margin-top: 3px; width: 16px; height: 16px;">
            <span>Tôi xác nhận đã thống nhất bàn giao công việc trước khi nghỉ phép.</span>
          </label>
          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="goToStep(2)"><i class="fa-solid fa-arrow-left"></i> Sửa thông tin</button>
            <button type="button" class="lg-btn lg-btn-success" onclick="downloadWordDoc('""" + slug + """')"><i class="fa-solid fa-file-word"></i> Tải Word (.doc) ngay</button>
          </div>
        </div>
    """

    tool_js = """
    function renderDocument() {
      const preview = document.getElementById("a4-preview-body");
      if (!preview) return;
      preview.innerHTML = `
        <div class="d30-quoc-hieu">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="d30-tieu-ngu-wrap"><span class="d30-tieu-ngu">Độc lập - Tự do - Hạnh phúc</span></div>
        <div class="d30-date-line" style="text-align:right; margin-top:10pt;">${escHtml(getVal("doc-place-date"))}</div>

        <div class="d30-doc-title">ĐƠN XIN NGHỈ PHÉP &amp; BÀN GIAO CÔNG VIỆC</div>

        <p class="d30-p" style="margin-top:10pt;"><strong>Kính gửi: ${escHtml(getVal("user-recipient"))}</strong></p>
        <p class="d30-p d30-indent">Tôi tên là: <strong>${escHtml(getVal("emp-name"))}</strong> — Mã nhân viên: ${escHtml(getVal("emp-code", "---"))}</p>
        <p class="d30-p d30-indent">Chức vụ: ${escHtml(getVal("emp-title"))} — Phòng ban: ${escHtml(getVal("emp-dept"))}</p>

        <p class="d30-p d30-indent" style="margin-top:8pt;">Nay tôi làm đơn này kính đề nghị Ban Giám đốc và Trưởng bộ phận xem xét cho phép tôi được nghỉ phép với thông tin cụ thể như sau:</p>
        <p class="d30-p d30-indent">- Hình thức nghỉ: ${escHtml(getVal("leave-type"))}.</p>
        <p class="d30-p d30-indent">- Thời gian xin nghỉ: Từ ngày <strong>${escHtml(getVal("leave-from"))}</strong> đến hết ngày <strong>${escHtml(getVal("leave-to"))}</strong> (Tổng cộng: <strong>${escHtml(getVal("leave-days"))}</strong>).</p>
        <p class="d30-p d30-indent">- Lý do xin nghỉ: ${escHtml(getVal("leave-reason"))}.</p>
        <p class="d30-p d30-indent">- Số điện thoại liên hệ khi phát sinh công việc khẩn cấp: ${escHtml(getVal("emp-emergency-phone"))}.</p>

        <div class="d30-section-h">Nội dung bàn giao công việc trong thời gian nghỉ phép:</div>
        <p class="d30-p d30-indent">- Nhân sự tiếp nhận bàn giao: <strong>${escHtml(getVal("handover-person"))}</strong>.</p>
        <p class="d30-p d30-indent">- Chi tiết công việc bàn giao: ${escHtml(getVal("handover-tasks"))}.</p>
        <p class="d30-p d30-indent" style="margin-top:8pt;">Tôi xin cam đoan các đầu việc đang xử lý đã được bàn giao đầy đủ, không làm gián đoạn hoạt động chung của Bộ phận. Kính mong Quý Lãnh đạo xem xét, phê duyệt.</p>
        <p class="d30-p d30-indent">Xin trân trọng cảm ơn!</p>

        <table class="d30-sig-table">
          <tr>
            <td style="width:33.3%;">
              <div class="d30-sig-title">NGƯỜI NHẬN BÀN GIAO</div>
              <div class="d30-sig-note">(Ký, ghi rõ họ tên)</div>
              <div class="d30-sig-space"></div>
            </td>
            <td style="width:33.3%;">
              <div class="d30-sig-title">TRƯỞNG BỘ PHẬN / BAN GIÁM ĐỐC</div>
              <div class="d30-sig-note">(Duyệt &amp; Ký tên)</div>
              <div class="d30-sig-space"></div>
            </td>
            <td style="width:33.3%;">
              <div class="d30-sig-title">NGƯỜI LÀM ĐƠN</div>
              <div class="d30-sig-note">(Ký, ghi rõ họ tên)</div>
              <div class="d30-sig-space"></div>
              <div style="font-weight:bold;">${escHtml(getVal("emp-name"))}</div>
            </td>
          </tr>
        </table>
      `;
    }
    """

    tool_html, full_js = _wrap_wizard_layout(slug, form_steps, tool_js)
    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="Đơn từ Công sở",
        page_title=f"{keyword} - Chuẩn Điều 113 BLLĐ 2019",
        meta_desc="Tạo mẫu đơn xin nghỉ phép năm & bàn giao công việc công ty chuẩn Bộ luật Lao động 2019 và Nghị định 30/2020/NĐ-CP, tải Word .doc và in PDF A4 miễn phí.",
        meta_keywords="mẫu đơn xin nghỉ phép công ty, bàn giao công việc, điều 113 bộ luật lao động",
        subtitle="Biểu mẫu Đơn xin nghỉ phép & Bàn giao công việc công ty chuẩn Điều 113/115 Bộ luật Lao động 2019 và Nghị định 30/2020/NĐ-CP.",
        tool_html=tool_html,
        tool_js=full_js,
        extra_head=DECREE30_CSS,
        nav_badge="Nghị định 30/2020 A4",
    )


def _build_ct01_residency_wizard(keyword, slug):
    form_steps = """
        <div class="form-step active" data-step="1">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #38bdf8;">Bước 1: Cơ quan Công an &amp; Thông tin người kê khai (CT01)</h2>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="user-recipient">Kính gửi (Cơ quan đăng ký cư trú) <span class="lg-req">*</span></label>
            <input type="text" id="user-recipient" class="lg-input" value="Công an Phường Dịch Vọng Hậu, Quận Cầu Giấy, Thành phố Hà Nội" required>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="citizen-name">Họ, chữ đệm và tên <span class="lg-req">*</span></label>
              <input type="text" id="citizen-name" class="lg-input" value="ĐẶNG QUỐC THÁI" required>
            </div>
            <div>
              <label class="lg-label" for="citizen-dob">Ngày, tháng, năm sinh <span class="lg-req">*</span></label>
              <input type="text" id="citizen-dob" class="lg-input" value="04/03/1995" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="citizen-gender">Giới tính <span class="lg-req">*</span></label>
              <select id="citizen-gender" class="lg-select" required>
                <option value="Nam">Nam</option>
                <option value="Nữ">Nữ</option>
              </select>
            </div>
            <div>
              <label class="lg-label" for="citizen-cccd">Số định danh cá nhân / CCCD <span class="lg-req">*</span></label>
              <input type="text" id="citizen-cccd" class="lg-input" value="036095007890" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="citizen-phone">Số điện thoại liên hệ <span class="lg-req">*</span></label>
              <input type="text" id="citizen-phone" class="lg-input" value="0977 888 999" required>
            </div>
            <div>
              <label class="lg-label" for="citizen-email">Email (nếu có)</label>
              <input type="text" id="citizen-email" class="lg-input" value="quocthai95@example.com">
            </div>
          </div>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="permanent-address">Nơi thường trú hiện nay <span class="lg-req">*</span></label>
            <input type="text" id="permanent-address" class="lg-input" value="Xã Hải Hưng, Huyện Hải Hậu, Tỉnh Nam Định" required>
          </div>
          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="resetSampleFields()"><i class="fa-solid fa-eraser"></i> Xóa mẫu</button>
            <button type="button" class="lg-btn lg-btn-primary" onclick="goToStep(2)">Tiếp tục Bước 2 <i class="fa-solid fa-arrow-right"></i></button>
          </div>
        </div>

        <div class="form-step" data-step="2">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #38bdf8;">Bước 2: Địa chỉ tạm trú &amp; Ý kiến Chủ hộ / Chủ nhà</h2>
          <div style="margin-bottom: 10px;">
            <label class="lg-label" for="temp-address">Nơi ở hiện tại / Địa chỉ đề nghị đăng ký tạm trú <span class="lg-req">*</span></label>
            <input type="text" id="temp-address" class="lg-input" value="Số 22, Ngõ 18 phố Duy Tân, Phường Dịch Vọng Hậu, Cầu Giấy, Hà Nội" required>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="residency-action">Nội dung đề nghị <span class="lg-req">*</span></label>
              <select id="residency-action" class="lg-select" required>
                <option value="Đăng ký tạm trú mới (thời hạn tối đa 24 tháng)">Đăng ký tạm trú mới</option>
                <option value="Gia hạn tạm trú">Gia hạn tạm trú</option>
              </select>
            </div>
            <div>
              <label class="lg-label" for="residency-duration">Thời hạn tạm trú đề nghị <span class="lg-req">*</span></label>
              <input type="text" id="residency-duration" class="lg-input" value="24 tháng (Từ 15/06/2026 đến 14/06/2028)" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="owner-name">Họ tên Chủ hộ / Chủ sở hữu chỗ ở <span class="lg-req">*</span></label>
              <input type="text" id="owner-name" class="lg-input" value="Bà Hoàng Thị Mai" required>
            </div>
            <div>
              <label class="lg-label" for="owner-cccd">Số CCCD của Chủ hộ / Chủ sở hữu <span class="lg-req">*</span></label>
              <input type="text" id="owner-cccd" class="lg-input" value="001172003344" required>
            </div>
          </div>
          <div class="lg-row-2" style="margin-bottom: 10px;">
            <div>
              <label class="lg-label" for="owner-relation">Quan hệ với chủ hộ / Loại chỗ ở <span class="lg-req">*</span></label>
              <input type="text" id="owner-relation" class="lg-input" value="Người thuê nhà ở hợp pháp (HĐ thuê số 05/2026)" required>
            </div>
            <div>
              <label class="lg-label" for="doc-place-date">Địa điểm &amp; Ngày kê khai <span class="lg-req">*</span></label>
              <input type="text" id="doc-place-date" class="lg-input" value="Hà Nội, ngày 15 tháng 06 năm 2026" required>
            </div>
          </div>

          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="goToStep(1)"><i class="fa-solid fa-arrow-left"></i> Quay lại Bước 1</button>
            <button type="button" class="lg-btn lg-btn-primary" onclick="goToStep(3)">Tiếp tục Bước 3 <i class="fa-solid fa-arrow-right"></i></button>
          </div>
        </div>

        <div class="form-step" data-step="3">
          <h2 style="font-size: 1.05rem; margin-bottom: 12px; color: #34d399;">Bước 3: Hoàn tất Tờ khai CT01 (Thông tư 66/2023/TT-BCA)</h2>
          <p style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 14px;">Mẫu CT01 đáp ứng Luật Cư trú 2020 và Thông tư 66/2023/TT-BCA, trình bày chuẩn Nghị định 30/2020/NĐ-CP với đầy đủ mục Ý kiến đồng ý của chủ hộ/chủ sở hữu chỗ ở hợp pháp.</p>
          <label style="display: flex; align-items: flex-start; gap: 10px; font-size: 0.82rem; color: #d1d5db; margin-bottom: 16px; cursor: pointer;">
            <input type="checkbox" id="tos-agree" checked required style="margin-top: 3px; width: 16px; height: 16px;">
            <span>Tôi chịu trách nhiệm trước pháp luật về lời khai cư trú trên Tờ khai CT01.</span>
          </label>
          <div class="lg-nav-actions">
            <button type="button" class="lg-btn lg-btn-secondary" onclick="goToStep(2)"><i class="fa-solid fa-arrow-left"></i> Sửa tờ khai</button>
            <button type="button" class="lg-btn lg-btn-success" onclick="downloadWordDoc('""" + slug + """')"><i class="fa-solid fa-file-word"></i> Tải Word (.doc) CT01</button>
          </div>
        </div>
    """

    tool_js = """
    function renderDocument() {
      const preview = document.getElementById("a4-preview-body");
      if (!preview) return;
      preview.innerHTML = `
        <table class="a4-header-table">
          <tr>
            <td style="width:32%; text-align:left; font-size:11pt;">
              <div><strong>Mẫu CT01</strong></div>
              <div><em>(Ban hành kèm theo Thông tư số 66/2023/TT-BCA)</em></div>
            </td>
            <td style="width:68%; text-align:center;">
              <div class="d30-quoc-hieu">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
              <div class="d30-tieu-ngu-wrap"><span class="d30-tieu-ngu">Độc lập - Tự do - Hạnh phúc</span></div>
            </td>
          </tr>
        </table>

        <div class="d30-doc-title">TỜ KHAI THAY ĐỔI THÔNG TIN CƯ TRÚ</div>
        <div class="d30-doc-sub">(Dùng cho công dân đăng ký / gia hạn tạm trú theo Luật Cư trú)</div>

        <p class="d30-p" style="margin-top:10pt;"><strong>Kính gửi: ${escHtml(getVal("user-recipient"))}</strong></p>

        <p class="d30-p">1. Họ, chữ đệm và tên: <strong>${escHtml(getVal("citizen-name"))}</strong></p>
        <p class="d30-p">2. Ngày, tháng, năm sinh: ${escHtml(getVal("citizen-dob"))} — 3. Giới tính: ${escHtml(getVal("citizen-gender"))}</p>
        <p class="d30-p">4. Số định danh cá nhân (CCCD): <strong>${escHtml(getVal("citizen-cccd"))}</strong></p>
        <p class="d30-p">5. Số điện thoại liên hệ: ${escHtml(getVal("citizen-phone"))} — 6. Email: ${escHtml(getVal("citizen-email", "---"))}</p>
        <p class="d30-p">7. Nơi thường trú: ${escHtml(getVal("permanent-address"))}</p>
        <p class="d30-p">8. Nơi tạm trú / Địa chỉ chỗ ở hợp pháp đề nghị đăng ký: <strong>${escHtml(getVal("temp-address"))}</strong></p>
        <p class="d30-p">9. Họ, chữ đệm và tên chủ hộ / chủ sở hữu chỗ ở hợp pháp: <strong>${escHtml(getVal("owner-name"))}</strong> — Số ĐDCN chủ hộ: ${escHtml(getVal("owner-cccd"))}</p>
        <p class="d30-p">10. Quan hệ với chủ hộ / Căn cứ chỗ ở hợp pháp: ${escHtml(getVal("owner-relation"))}</p>
        <p class="d30-p">11. Nội dung đề nghị: <strong>${escHtml(getVal("residency-action"))}</strong> — Thời hạn: <strong>${escHtml(getVal("residency-duration"))}</strong>.</p>

        <p class="d30-p d30-indent" style="margin-top:8pt;">Tôi xin cam đoan những thông tin kê khai trên đây là đúng sự thật và chịu hoàn toàn trách nhiệm trước pháp luật về lời khai của mình.</p>

        <table class="d30-sig-table">
          <tr>
            <td style="width:52%; border: 1px solid #000; padding: 8pt; text-align:left;">
              <div class="d30-sig-title" style="text-align:center; font-size:11.5pt;">Ý KIẾN CỦA CHỦ HỘ / CHỦ SỞ HỮU CHỖ Ở HỢP PHÁP</div>
              <p style="font-size:11.5pt; margin:6pt 0;">Tôi đồng ý cho công dân ${escHtml(getVal("citizen-name"))} (Số ĐDCN: ${escHtml(getVal("citizen-cccd"))}) đăng ký tạm trú tại địa chỉ nêu trên.</p>
              <div style="text-align:center; font-style:italic; font-size:11pt; margin-top:6pt;">(Ký, ghi rõ họ tên)</div>
              <div style="height:40pt;"></div>
              <div style="text-align:center; font-weight:bold;">${escHtml(getVal("owner-name"))}</div>
            </td>
            <td style="width:48%; padding: 8pt;">
              <div style="font-style:italic; font-size:12pt;">${escHtml(getVal("doc-place-date"))}</div>
              <div class="d30-sig-title" style="margin-top:4pt;">NGƯỜI KÊ KHAI</div>
              <div class="d30-sig-note">(Ký, ghi rõ họ tên)</div>
              <div class="d30-sig-space"></div>
              <div style="font-weight:bold;">${escHtml(getVal("citizen-name"))}</div>
            </td>
          </tr>
        </table>
      `;
    }
    """

    tool_html, full_js = _wrap_wizard_layout(slug, form_steps, tool_js)
    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="Hành chính & Cư trú",
        page_title=f"{keyword} - Chuẩn Thông Tư 66/2023/TT-BCA & NĐ 30/2020",
        meta_desc="Tạo mẫu tờ khai đăng ký tạm trú CT01 chuẩn Thông tư 66/2023/TT-BCA, đầy đủ ý kiến chủ hộ/chủ nhà, tải Word .doc và PDF A4 miễn phí.",
        meta_keywords="mẫu ct01, tờ khai đăng ký tạm trú, thông tư 66/2023/tt-bca, luật cư trú 2020",
        subtitle="Biểu mẫu Tờ khai thay đổi thông tin cư trú CT01 (Thông tư 66/2023/TT-BCA) định dạng chuẩn A4 Nghị định 30/2020/NĐ-CP, tải miễn phí.",
        tool_html=tool_html,
        tool_js=full_js,
        extra_head=DECREE30_CSS,
        nav_badge="Mẫu CT01 A4",
    )


def build_legal_document_wizard(keyword, slug, config=None):
    """
    Dispatches the 5 Flagship LegalTech Document Wizards with 100% deterministic,
    Decree 30/2020/ND-CP compliant A4 templates and unified validateStep().
    """
    s = slug.lower()
    if "lao-dong" in s or "thu-viec" in s:
        return _build_labor_contract_wizard(keyword, slug)
    if "ban-giao-tai-san" in s:
        return _build_asset_handover_wizard(keyword, slug)
    if "xin-viec" in s or "ung-tuyen" in s:
        return _build_job_application_wizard(keyword, slug)
    if "nghi-phep" in s:
        return _build_leave_request_wizard(keyword, slug)
    if "tam-tru" in s or "ct01" in s:
        return _build_ct01_residency_wizard(keyword, slug)
    raise ValueError(f"Unsupported legal wizard slug: {slug}")
