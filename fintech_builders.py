# -*- coding: utf-8 -*-
"""
Builders for the 7 Flagship FinTech, Tax, Data & Registry Tools.
Every calculator uses pure client-side ES6 JavaScript synchronized with statutory_engines.py,
with zero external JS framework dependencies, zero fake countdowns, and real UTF-8 BOM CSV / A4 Print exports.
"""

from statutory_engines import render_tool_shell

SHARED_FINTECH_CSS = """
  <style>
    .ft-grid { display: grid; grid-template-columns: 1fr; gap: 24px; max-width: 1180px; margin: 0 auto; padding: 0 16px; }
    @media (min-width: 992px) { .ft-grid-2 { grid-template-columns: 1.05fr 0.95fr; align-items: start; } }
    .ft-card { background: rgba(18, 22, 32, 0.78); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px; }
    .ft-label { display: block; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: #9ca3af; margin-bottom: 6px; }
    .ft-input, .ft-select, .ft-textarea { width: 100%; background: rgba(10, 12, 16, 0.65); border: 1px solid rgba(255,255,255,0.12); border-radius: 10px; padding: 11px 14px; color: #fff; font-size: 0.95rem; font-family: inherit; box-sizing: border-box; }
    .ft-input:focus, .ft-select:focus, .ft-textarea:focus { outline: none; border-color: #00a8ff; box-shadow: 0 0 0 3px rgba(0, 168, 255, 0.18); }
    .ft-presets { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
    .ft-preset-btn { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12); color: #e5e7eb; padding: 6px 12px; border-radius: 8px; font-size: 0.78rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
    .ft-preset-btn:hover { background: rgba(0,168,255,0.18); border-color: #00a8ff; color: #fff; }
    .ft-tabs { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 18px; }
    .ft-tab { padding: 11px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.04); color: #d1d5db; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: all 0.2s; }
    .ft-tab.active { background: linear-gradient(135deg, #00a8ff 0%, #2563eb 100%); color: #fff; border-color: transparent; box-shadow: 0 4px 16px rgba(0, 168, 255, 0.3); }
    .ft-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 0.9rem; }
    .ft-row:last-child { border-bottom: none; }
    .ft-badge { display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 700; }
    .ft-badge-green { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.35); }
    .ft-badge-amber { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.35); }
    .ft-badge-red { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.35); }
    .ft-badge-blue { background: rgba(0,168,255,0.15); color: #38bdf8; border: 1px solid rgba(0,168,255,0.35); }
    .ft-table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
    .ft-table th, .ft-table td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.08); text-align: left; }
    .ft-table th { color: #9ca3af; font-weight: 600; font-size: 0.78rem; text-transform: uppercase; }
    .ft-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }
    .ft-grid-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    @media (max-width: 640px) { .ft-grid-2col { grid-template-columns: 1fr; } }
    .print-only { display: none; }
    @media print {
      body { background: #fff !important; color: #000 !important; padding: 0 !important; }
      .no-print { display: none !important; }
      .print-only { display: block !important; }
      .ft-grid, .ft-grid-2 { display: block !important; max-width: 100% !important; padding: 0 !important; }
      .ft-card, .print-report { background: #fff !important; color: #000 !important; border: 1px solid #cbd5e1 !important; box-shadow: none !important; backdrop-filter: none !important; page-break-inside: avoid; margin-bottom: 16px !important; }
      .ft-card *, .print-report * { color: #111827 !important; border-color: #cbd5e1 !important; }
      .ft-badge { border: 1px solid #334155 !important; background: #f8fafc !important; }
      @page { size: A4 portrait; margin: 18mm 15mm; }
    }
  </style>
"""


def build_hkd_tax_simulator(keyword, slug, config):
    tool_html = """
    <div class="ft-grid ft-grid-2">
      <!-- Inputs -->
      <div class="ft-card no-print">
        <h2 style="font-size: 1.25rem; margin-bottom: 18px; display: flex; align-items: center; gap: 8px;">
          <i class="fa-solid fa-sliders" style="color: #00a8ff;"></i> Thông Số Kinh Doanh Năm 2026
        </h2>

        <div style="margin-bottom: 18px;">
          <label class="ft-label" for="hkd-revenue">Tổng Doanh Thu Năm Dự Kiến (VND)</label>
          <input type="number" id="hkd-revenue" class="ft-input" value="1500000000" min="0" step="10000000">
          <div class="ft-presets">
            <button type="button" class="ft-preset-btn" data-rev="800000000">800 Triệu</button>
            <button type="button" class="ft-preset-btn" data-rev="1500000000">1,5 Tỷ</button>
            <button type="button" class="ft-preset-btn" data-rev="2500000000">2,5 Tỷ</button>
            <button type="button" class="ft-preset-btn" data-rev="5000000000">5 Tỷ</button>
            <button type="button" class="ft-preset-btn" data-rev="60000000000">60 Tỷ</button>
          </div>
        </div>

        <div style="margin-bottom: 18px;">
          <label class="ft-label" for="hkd-expenses">Chi Phí Hợp Lý Có Hóa Đơn Chứng Từ / Năm (VND)</label>
          <input type="number" id="hkd-expenses" class="ft-input" value="1200000000" min="0" step="10000000">
          <p style="font-size: 0.76rem; color: #9ca3af; margin-top: 6px;">Dùng để so sánh Phương pháp tính thuế TNCN trên lợi nhuận (15% với bậc 1–3 tỷ; bắt buộc 17% ở bậc 3–50 tỷ; 20% trên 50 tỷ).</p>
        </div>

        <div style="margin-bottom: 18px;">
          <label class="ft-label" for="hkd-industry">Nhóm Ngành Nghề (Phụ lục I - NĐ 68/2026 &amp; TT 18/2026)</label>
          <select id="hkd-industry" class="ft-select">
            <option value="group1">Nhóm 1: Phân phối, cung cấp hàng hóa (VAT 1.0% | TNCN 0.5%)</option>
            <option value="group2">Nhóm 2: Dịch vụ, xây dựng không bao thầu NVL (VAT 5.0% | TNCN 2.0%)</option>
            <option value="group3">Nhóm 3: Sản xuất, vận tải, dịch vụ gắn hàng hóa, ăn uống (VAT 3.0% | TNCN 1.5%)</option>
            <option value="group4">Nhóm 4: Hoạt động kinh doanh khác (VAT 2.0% | TNCN 1.0%)</option>
            <option value="group5">Nhóm 5: Cho thuê tài sản (VAT 5.0% | TNCN 5.0%)</option>
          </select>
        </div>

        <div style="margin-bottom: 10px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <label class="ft-label" for="hkd-ecom-pct" style="margin-bottom: 0;">Tỷ trọng Doanh Thu qua Sàn TMĐT có thanh toán (%)</label>
            <strong id="hkd-ecom-pct-label" style="color: #00a8ff; font-size: 0.9rem;">0%</strong>
          </div>
          <input type="range" id="hkd-ecom-pct" min="0" max="100" value="0" style="width: 100%; margin-top: 10px; accent-color: #00a8ff;">
          <p style="font-size: 0.76rem; color: #9ca3af; margin-top: 4px;">Shopee, TikTok Shop, Lazada khấu trừ thuế tại nguồn theo Điều 11 Nghị định 68/2026/NĐ-CP; phần còn lại tự kê khai trên Mẫu 01/CNKD.</p>
        </div>
      </div>

      <!-- Results -->
      <div class="print-report" style="display: flex; flex-direction: column; gap: 18px;">
        <div class="ft-card">
          <div class="print-only" style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 16px;">
            <h2 style="margin: 0; font-size: 16pt; text-transform: uppercase;">BÁO CÁO DỰ TOÁN THUẾ &amp; TUÂN THỦ HỘ KINH DOANH 2026</h2>
            <p style="margin: 4px 0 0 0; font-size: 10pt;">Căn cứ: Nghị định 68/2026/NĐ-CP, Thông tư 18/2026/TT-BTC, Nghị định 141/2026/NĐ-CP &amp; Nghị quyết 198/2025/QH15</p>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 16px;">
            <h2 style="font-size: 1.2rem; margin: 0;">Kết Quả Phân Tích Nghĩa Vụ Thuế</h2>
            <span id="hkd-tier-badge" class="ft-badge ft-badge-amber">Bậc 2: 1 - 3 Tỷ/năm</span>
          </div>

          <div id="hkd-status-box" style="padding: 14px; border-radius: 10px; background: rgba(0, 168, 255, 0.08); border: 1px solid rgba(0, 168, 255, 0.25); margin-bottom: 18px;">
            <div id="hkd-status-title" style="font-weight: 800; font-size: 1rem; margin-bottom: 4px;">--</div>
            <div id="hkd-compliance-msg" style="font-size: 0.85rem; color: #d1d5db; line-height: 1.55;">--</div>
          </div>

          <div class="ft-row">
            <span>Lệ phí môn bài (Bãi bỏ từ 01/01/2026 - NQ 198/2025/QH15)</span>
            <strong id="hkd-license-fee" style="color: #34d399;">0 đ</strong>
          </div>
          <div class="ft-row">
            <span>Thuế GTGT (VAT <span id="hkd-vat-rate-lbl">1.0%</span> trên tổng doanh thu)</span>
            <strong id="hkd-vat-val">0 đ</strong>
          </div>
          <div class="ft-row">
            <span>Thuế TNCN tối ưu phải nộp</span>
            <strong id="hkd-pit-val">0 đ</strong>
          </div>
          <div class="ft-row" style="background: rgba(0,168,255,0.08); padding: 12px; border-radius: 8px; margin-top: 8px;">
            <span style="font-weight: 700; color: #fff;">Tổng Thuế Phải Nộp Năm 2026</span>
            <strong id="hkd-total-tax" style="font-size: 1.3rem; color: #38bdf8;">0 đ</strong>
          </div>

          <!-- Tier 2 Method Comparison Panel -->
          <div id="hkd-tier2-panel" style="margin-top: 18px; padding: 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.02);">
            <div style="font-size: 0.82rem; font-weight: 700; text-transform: uppercase; color: #fbbf24; margin-bottom: 10px;">
              So Sánh 2 Phương Pháp Tính Thuế TNCN (Ngưỡng &gt; 1 Tỷ đến 3 Tỷ - Ổn định 2 năm theo Điều 5 NĐ 68/2026)
            </div>
            <div class="ft-grid-2col">
              <div id="hkd-m1-card" style="padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 0.78rem; color: #9ca3af;">Cách 1: Trên doanh thu vượt 1 tỷ</div>
                <div style="font-size: 0.74rem; color: #6b7280; margin-top: 2px;">(Doanh thu - 1 tỷ) &times; Thuế suất TNCN</div>
                <div id="hkd-m1-val" style="font-size: 1.1rem; font-weight: 800; margin-top: 6px; color: #fff;">0 đ</div>
              </div>
              <div id="hkd-m2-card" style="padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 0.78rem; color: #9ca3af;">Cách 2: Trên thu nhập tính thuế (15%)</div>
                <div style="font-size: 0.74rem; color: #6b7280; margin-top: 2px;">max(0, Doanh thu - Chi phí) &times; 15%</div>
                <div id="hkd-m2-val" style="font-size: 1.1rem; font-weight: 800; margin-top: 6px; color: #fff;">0 đ</div>
              </div>
            </div>
            <div id="hkd-method-recommend" style="margin-top: 10px; font-size: 0.82rem; font-weight: 600; color: #34d399;">--</div>
          </div>

          <!-- Sales Channel Mix Breakdown -->
          <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.08);">
            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #9ca3af; margin-bottom: 8px;">Phân Bổ Kê Khai Theo Kênh Bán Hàng (Điều 11 NĐ 68/2026)</div>
            <div class="ft-row">
              <span>Thuế sàn TMĐT khấu trừ tại nguồn (<span id="hkd-ecom-rev-lbl">0 đ</span>)</span>
              <strong id="hkd-withheld-val">0 đ</strong>
            </div>
            <div class="ft-row">
              <span>Thuế ước tính tự kê khai qua Mẫu 01/CNKD (<span id="hkd-direct-rev-lbl">0 đ</span>)</span>
              <strong id="hkd-self-declared-val">0 đ</strong>
            </div>
          </div>

          <div class="ft-actions no-print">
            <button type="button" id="hkd-print-btn" class="btn btn-primary" style="flex: 1;"><i class="fa-solid fa-print"></i> In Báo Cáo Thuế A4 / Xuất PDF</button>
            <button type="button" id="hkd-csv-btn" class="btn btn-secondary" style="flex: 1;"><i class="fa-solid fa-file-csv"></i> Tải Bảng Tính CSV</button>
          </div>
        </div>
      </div>
    </div>
    """

    tool_js = """
    const HKD_RATES = {
      group1: { name: 'Nhóm 1: Phân phối, cung cấp hàng hóa', vat: 0.01, pit: 0.005 },
      group2: { name: 'Nhóm 2: Dịch vụ, xây dựng không bao thầu NVL', vat: 0.05, pit: 0.02 },
      group3: { name: 'Nhóm 3: Sản xuất, vận tải, dịch vụ gắn hàng hóa, ăn uống', vat: 0.03, pit: 0.015 },
      group4: { name: 'Nhóm 4: Hoạt động kinh doanh khác', vat: 0.02, pit: 0.01 },
      group5: { name: 'Nhóm 5: Cho thuê tài sản', vat: 0.05, pit: 0.05 }
    };
    let lastHkdState = {};
    function fmtVnd(n) { return Math.round(n).toLocaleString('vi-VN') + ' đ'; }

    function calculateHkd() {
      const rev = Math.max(0, parseFloat(document.getElementById('hkd-revenue').value) || 0);
      const exp = Math.max(0, parseFloat(document.getElementById('hkd-expenses').value) || 0);
      const indKey = document.getElementById('hkd-industry').value;
      const ecomPct = Math.min(100, Math.max(0, parseFloat(document.getElementById('hkd-ecom-pct').value) || 0));
      document.getElementById('hkd-ecom-pct-label').innerText = ecomPct + '%';

      const ind = HKD_RATES[indKey] || HKD_RATES.group1;
      const platformRev = rev * (ecomPct / 100);
      const directRev = rev - platformRev;

      let tierLabel = '', badgeClass = 'ft-badge-green', statusTitle = '', complianceMsg = '';
      let vat = 0, pit1 = null, pit2 = null, pitOptimal = 0, recText = '';
      const tier2Panel = document.getElementById('hkd-tier2-panel');

      if (rev <= 1000000000) {
        tierLabel = 'Bậc 1: ≤ 1 Tỷ/năm (Miễn thuế)';
        badgeClass = 'ft-badge-green';
        statusTitle = 'MIỄN THUẾ GTGT & TNCN NĂM 2026 (NĐ 141/2026/NĐ-CP)';
        complianceMsg = 'Doanh thu năm ≤ 1 tỷ đồng: Nộp thông báo doanh thu năm theo Mẫu 01/TKN-CNKD trước ngày 31/01 năm sau. Không bắt buộc sử dụng hóa đơn điện tử khởi tạo từ máy tính tiền.';
        tier2Panel.style.display = 'none';
      } else if (rev <= 3000000000) {
        tierLabel = 'Bậc 2: > 1 Tỷ - 3 Tỷ/năm';
        badgeClass = 'ft-badge-amber';
        vat = Math.round(rev * ind.vat);
        pit1 = Math.round((rev - 1000000000) * ind.pit);
        pit2 = Math.round(Math.max(0, rev - exp) * 0.15);
        pitOptimal = Math.min(pit1, pit2);
        tier2Panel.style.display = 'block';
        statusTitle = 'PHẢI NỘP THUẾ & KÊ KHAI THEO QUÝ (MẪU 01/CNKD)';
        complianceMsg = 'Bắt buộc đăng ký hóa đơn điện tử khởi tạo từ máy tính tiền, kê khai theo quý trên Mẫu 01/CNKD và thông báo tài khoản ngân hàng/ví điện tử phục vụ kinh doanh với cơ quan thuế.';
        document.getElementById('hkd-m1-val').innerText = fmtVnd(pit1);
        document.getElementById('hkd-m2-val').innerText = fmtVnd(pit2);
        const m1Card = document.getElementById('hkd-m1-card');
        const m2Card = document.getElementById('hkd-m2-card');
        if (pit1 <= pit2) {
          m1Card.style.borderColor = '#10b981'; m1Card.style.background = 'rgba(16,185,129,0.1)';
          m2Card.style.borderColor = 'rgba(255,255,255,0.1)'; m2Card.style.background = 'transparent';
          recText = 'Tối ưu: Chọn Cách 1 (trên doanh thu vượt 1 tỷ) tiết kiệm ' + fmtVnd(pit2 - pit1) + '/năm (ổn định 2 năm theo Điều 5 NĐ 68/2026).';
        } else {
          m2Card.style.borderColor = '#10b981'; m2Card.style.background = 'rgba(16,185,129,0.1)';
          m1Card.style.borderColor = 'rgba(255,255,255,0.1)'; m1Card.style.background = 'transparent';
          recText = 'Tối ưu: Chọn Cách 2 (15% trên lợi nhuận) tiết kiệm ' + fmtVnd(pit1 - pit2) + '/năm (yêu cầu đầy đủ hóa đơn chi phí & ổn định 2 năm).';
        }
        document.getElementById('hkd-method-recommend').innerText = recText;
      } else if (rev <= 50000000000) {
        tierLabel = 'Bậc 3: > 3 Tỷ - 50 Tỷ/năm';
        badgeClass = 'ft-badge-red';
        vat = Math.round(rev * ind.vat);
        pitOptimal = Math.round(Math.max(0, rev - exp) * 0.17);
        tier2Panel.style.display = 'none';
        statusTitle = 'BẮT BUỘC NỘP THUẾ TNCN 17% TRÊN LỢI NHUẬN & SỔ KẾ TOÁN ĐẦY ĐỦ';
        complianceMsg = 'Kê khai theo quý, bắt buộc sử dụng hóa đơn điện tử và ghi chép đầy đủ sổ sách kế toán hộ kinh doanh (S2b-HKD đến S2e-HKD theo Thông tư 18/2026/TT-BTC).';
      } else {
        tierLabel = 'Bậc 4: > 50 Tỷ/năm';
        badgeClass = 'ft-badge-red';
        vat = Math.round(rev * ind.vat);
        pitOptimal = Math.round(Math.max(0, rev - exp) * 0.20);
        tier2Panel.style.display = 'none';
        statusTitle = 'BẮT BUỘC NỘP THUẾ TNCN 20% TRÊN LỢI NHUẬN & KÊ KHAI THÁNG';
        complianceMsg = 'Kê khai thuế hàng tháng trước ngày 20 của tháng tiếp theo, bắt buộc hóa đơn điện tử và sổ kế toán đầy đủ (S2b-HKD đến S2e-HKD).';
      }

      const totalTax = vat + pitOptimal;
      const withheld = platformRev > 0 ? Math.round(platformRev * (ind.vat + ind.pit)) : 0;
      const selfDeclared = rev <= 1000000000 ? 0 : Math.max(0, totalTax - withheld);

      const badge = document.getElementById('hkd-tier-badge');
      badge.className = 'ft-badge ' + badgeClass;
      badge.innerText = tierLabel;
      document.getElementById('hkd-status-title').innerText = statusTitle;
      document.getElementById('hkd-compliance-msg').innerText = complianceMsg;
      document.getElementById('hkd-vat-rate-lbl').innerText = (ind.vat * 100).toFixed(1) + '%';
      document.getElementById('hkd-vat-val').innerText = fmtVnd(vat);
      document.getElementById('hkd-pit-val').innerText = fmtVnd(pitOptimal);
      document.getElementById('hkd-total-tax').innerText = fmtVnd(totalTax);
      document.getElementById('hkd-ecom-rev-lbl').innerText = fmtVnd(platformRev);
      document.getElementById('hkd-direct-rev-lbl').innerText = fmtVnd(directRev);
      document.getElementById('hkd-withheld-val').innerText = fmtVnd(withheld) + (rev <= 1000000000 && withheld > 0 ? ' (được hoàn/bù trừ do ≤ 1 tỷ)' : '');
      document.getElementById('hkd-self-declared-val').innerText = fmtVnd(selfDeclared);

      lastHkdState = { rev, exp, indName: ind.name, tierLabel, vat, pit1, pit2, pitOptimal, totalTax, withheld, selfDeclared };
    }

    document.querySelectorAll('.ft-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.getElementById('hkd-revenue').value = btn.getAttribute('data-rev');
        calculateHkd();
      });
    });
    ['hkd-revenue', 'hkd-expenses', 'hkd-industry', 'hkd-ecom-pct'].forEach(id => {
      const el = document.getElementById(id);
      el.addEventListener('input', calculateHkd);
      el.addEventListener('change', calculateHkd);
    });
    document.getElementById('hkd-print-btn').addEventListener('click', () => window.print());
    document.getElementById('hkd-csv-btn').addEventListener('click', () => {
      const s = lastHkdState;
      const rows = [
        ['Chi tieu', 'Gia tri (VND)'],
        ['Nhom nganh nghe', `"${s.indName}"`],
        ['Phan bac doanh thu', `"${s.tierLabel}"`],
        ['Doanh thu nam', s.rev],
        ['Chi phi hop ly', s.exp],
        ['Le phi mon bai (NQ 198/2025/QH15)', 0],
        ['Thue GTGT (VAT)', s.vat],
        ['Thue TNCN Cach 1 (Tren DT vuot 1 ty)', s.pit1 === null ? 'N/A' : s.pit1],
        ['Thue TNCN Cach 2 (Tren loi nhuan 15%)', s.pit2 === null ? 'N/A' : s.pit2],
        ['Thue TNCN toi uu phai nop', s.pitOptimal],
        ['Tong thue phai nop 2026', s.totalTax],
        ['Thue san TMDT khau tru tai nguon', s.withheld],
        ['Thue tu ke khai Mau 01/CNKD', s.selfDeclared]
      ];
      const csv = rows.map(r => r.join(',')).join('\\n');
      const blob = new Blob(['\\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'bao-cao-thue-ho-kinh-doanh-2026.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
    calculateHkd();
    """

    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="FinTech & Thuế 2026",
        page_title=f"{keyword} - Mô Phỏng Nghị Định 68 & 141/2026/NĐ-CP | VinaTools",
        meta_desc="Mô phỏng chính xác thuế GTGT, TNCN Hộ Kinh Doanh 2026 theo Nghị định 68/2026/NĐ-CP, Thông tư 18/2026/TT-BTC, Nghị định 141/2026/NĐ-CP (ngưỡng 1 tỷ) và Nghị quyết 198/2025/QH15.",
        meta_keywords="thuế hộ kinh doanh 2026, nghị định 68/2026, nghị định 141/2026, thông tư 18/2026, bãi bỏ thuế khoán, lệ phí môn bài 2026",
        subtitle="Tính thuế GTGT &amp; TNCN theo 4 bậc doanh thu, so sánh Cách 1 (doanh thu vượt 1 tỷ) vs. Cách 2 (lợi nhuận 15%/17%/20%), phân bổ khấu trừ sàn TMĐT và xuất báo cáo A4/CSV.",
        tool_html=tool_html,
        tool_js=tool_js,
        extra_head=SHARED_FINTECH_CSS,
        nav_badge="Chuẩn NĐ 68 & 141/2026",
    )


def build_pit_gross_net_simulator(keyword, slug, config):
    tool_html = """
    <div class="ft-grid ft-grid-2">
      <!-- Inputs -->
      <div class="ft-card no-print">
        <h2 style="font-size: 1.25rem; margin-bottom: 18px; display: flex; align-items: center; gap: 8px;">
          <i class="fa-solid fa-money-check-dollar" style="color: #00a8ff;"></i> Thông Số Lương &amp; Giảm Trừ 2026
        </h2>

        <div class="ft-tabs">
          <button type="button" id="mode-gross-net" class="ft-tab active">GROSS &rarr; NET</button>
          <button type="button" id="mode-net-gross" class="ft-tab">NET &rarr; GROSS</button>
        </div>

        <div style="margin-bottom: 16px;">
          <label class="ft-label" id="income-label" for="salary-income">Thu Nhập Gross Hàng Tháng (VND)</label>
          <input type="number" id="salary-income" class="ft-input" value="25000000" min="0" step="500000">
          <div class="ft-presets">
            <button type="button" class="ft-preset-btn" data-sal="15000000">15 Triệu</button>
            <button type="button" class="ft-preset-btn" data-sal="25000000">25 Triệu</button>
            <button type="button" class="ft-preset-btn" data-sal="40000000">40 Triệu</button>
            <button type="button" class="ft-preset-btn" data-sal="60000000">60 Triệu</button>
            <button type="button" class="ft-preset-btn" data-sal="100000000">100 Triệu</button>
          </div>
        </div>

        <div class="ft-grid-2col" style="margin-bottom: 16px;">
          <div>
            <label class="ft-label" for="salary-dependents">Số Người Phụ Thuộc</label>
            <input type="number" id="salary-dependents" class="ft-input" value="1" min="0" max="20">
          </div>
          <div>
            <label class="ft-label" for="salary-med-edu">Giảm Trừ Y Tế / Giáo Dục (VND/tháng)</label>
            <input type="number" id="salary-med-edu" class="ft-input" value="0" min="0" max="3916667" step="100000">
          </div>
        </div>

        <div class="ft-grid-2col" style="margin-bottom: 16px;">
          <div>
            <label class="ft-label" for="salary-region">Vùng Lương Tối Thiểu (NĐ 293/2025)</label>
            <select id="salary-region" class="ft-select">
              <option value="1">Vùng I: 5.310.000 đ (Trần BHTN: 106,2tr)</option>
              <option value="2">Vùng II: 4.730.000 đ (Trần BHTN: 94,6tr)</option>
              <option value="3">Vùng III: 4.140.000 đ (Trần BHTN: 82,8tr)</option>
              <option value="4">Vùng IV: 3.700.000 đ (Trần BHTN: 74,0tr)</option>
            </select>
          </div>
          <div>
            <label class="ft-label" for="salary-period">Giai Đoạn Lương Cơ Sở (NĐ 161/2026)</label>
            <select id="salary-period" class="ft-select">
              <option value="h2_2026">Từ 01/07/2026 (2.530.000 đ - Trần 50,6tr)</option>
              <option value="h1_2026">Nửa đầu 2026 (2.340.000 đ - Trần 46,8tr)</option>
            </select>
          </div>
        </div>

        <div class="ft-grid-2col" style="margin-bottom: 8px;">
          <div>
            <label class="ft-label" for="salary-ins-mode">Mức Đóng Bảo Hiểm</label>
            <select id="salary-ins-mode" class="ft-select">
              <option value="official">Trên lương chính thức</option>
              <option value="custom">Mức đóng tùy chỉnh (VND)</option>
            </select>
          </div>
          <div id="ins-custom-wrap" style="display: none;">
            <label class="ft-label" for="salary-ins-custom">Lương Đóng Bảo Hiểm (VND)</label>
            <input type="number" id="salary-ins-custom" class="ft-input" value="10000000" min="0" step="500000">
          </div>
        </div>
        <p style="font-size: 0.75rem; color: #9ca3af; margin-top: 8px;">NĐ 253/2026/NĐ-CP cho phép giảm trừ chi phí y tế tối đa 23 triệu/năm và giáo dục tối đa 24 triệu/năm (~3.916.667 đ/tháng).</p>
      </div>

      <!-- Outputs -->
      <div class="print-report" style="display: flex; flex-direction: column; gap: 18px;">
        <div class="ft-card">
          <div class="print-only" style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 16px;">
            <h2 style="margin: 0; font-size: 16pt; text-transform: uppercase;">BẢNG TÍNH LƯƠNG GROSS / NET &amp; THUẾ TNCN 5 BẬC 2026</h2>
            <p style="margin: 4px 0 0 0; font-size: 10pt;">Luật Thuế TNCN số 109/2025/QH15, Nghị quyết 110/2025/UBTVQH15, NĐ 293/2025 &amp; NĐ 161/2026</p>
          </div>

          <!-- Green Savings Card -->
          <div style="padding: 16px; border-radius: 12px; background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.35); margin-bottom: 18px;">
            <div style="font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: #34d399;">Tiết Kiệm Nhờ Cải Cách Thuế TNCN 2026 (Biểu 5 Bậc &amp; Giảm Trừ 15,5tr / 6,2tr)</div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 10px; margin-top: 8px;">
              <div>
                <span style="font-size: 0.82rem; color: #d1d5db;">Tiết kiệm/tháng: </span>
                <strong id="pit-saved-month" style="font-size: 1.2rem; color: #34d399;">0 đ</strong>
              </div>
              <div>
                <span style="font-size: 0.82rem; color: #d1d5db;">Tiết kiệm/năm: </span>
                <strong id="pit-saved-year" style="font-size: 1.35rem; color: #34d399;">0 đ</strong>
              </div>
            </div>
          </div>

          <div class="ft-row">
            <span>Lương Gross</span>
            <strong id="pit-res-gross" style="font-size: 1.1rem; color: #fff;">0 đ</strong>
          </div>
          <div class="ft-row">
            <span>BHXH (8%) + BHYT (1.5%) + BHTN (1%) = 10.5%</span>
            <strong id="pit-res-ins" style="color: #f87171;">-0 đ</strong>
          </div>
          <div class="ft-row" style="font-size: 0.82rem; color: #9ca3af;">
            <span>Chi tiết BH: BHXH (<span id="pit-bhxh">0</span>) • BHYT (<span id="pit-bhyt">0</span>) • BHTN (<span id="pit-bhtn">0</span>)</span>
          </div>
          <div class="ft-row">
            <span>Giảm trừ gia cảnh (15,5tr + <span id="pit-dep-count">1</span> &times; 6,2tr + Y tế/GD)</span>
            <strong id="pit-res-deductions">0 đ</strong>
          </div>
          <div class="ft-row">
            <span>Thu nhập tính thuế 2026 (TNTT)</span>
            <strong id="pit-res-tntt">0 đ</strong>
          </div>
          <div class="ft-row">
            <span>Thuế TNCN 2026 (Biểu 5 bậc - Luật 109/2025/QH15)</span>
            <strong id="pit-res-tax-2026" style="color: #f87171;">-0 đ</strong>
          </div>
          <div class="ft-row" style="background: rgba(0,168,255,0.08); padding: 12px; border-radius: 8px; margin-top: 8px;">
            <span style="font-weight: 700; color: #fff;">Lương Thực Nhận (NET 2026)</span>
            <strong id="pit-res-net" style="font-size: 1.35rem; color: #38bdf8;">0 đ</strong>
          </div>

          <div style="margin-top: 16px;">
            <h3 style="font-size: 0.9rem; color: #d1d5db; margin-bottom: 8px;">So Sánh Luật Cũ 2025 vs. Luật Mới 2026</h3>
            <table class="ft-table">
              <thead>
                <tr>
                  <th>Chỉ tiêu</th>
                  <th>Quy định cũ 2025 (7 bậc)</th>
                  <th>Quy định mới 2026 (5 bậc)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Giảm trừ bản thân / NPT</td>
                  <td>11,0tr / 4,4tr</td>
                  <td>15,5tr / 6,2tr</td>
                </tr>
                <tr>
                  <td>Thuế TNCN / tháng</td>
                  <td id="pit-cmp-2025-mo">0 đ</td>
                  <td id="pit-cmp-2026-mo" style="color: #34d399; font-weight: 700;">0 đ</td>
                </tr>
                <tr>
                  <td>Thuế TNCN / năm</td>
                  <td id="pit-cmp-2025-yr">0 đ</td>
                  <td id="pit-cmp-2026-yr" style="color: #34d399; font-weight: 700;">0 đ</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="ft-actions no-print">
            <button type="button" id="pit-print-btn" class="btn btn-primary" style="flex: 1;"><i class="fa-solid fa-print"></i> In Báo Cáo A4 / PDF</button>
            <button type="button" id="pit-csv-btn" class="btn btn-secondary" style="flex: 1;"><i class="fa-solid fa-file-csv"></i> Tải Bảng Lương CSV</button>
          </div>
        </div>
      </div>
    </div>
    """

    tool_js = """
    const REGION_WAGES = { '1': 5310000, '2': 4730000, '3': 4140000, '4': 3700000 };
    const BASE_SALARIES = { h2_2026: 2530000, h1_2026: 2340000 };
    let pitMode = 'gross-to-net';
    let lastPitState = {};
    function fmt(n) { return Math.round(n).toLocaleString('vi-VN') + ' đ'; }

    function pit2026(tntt) {
      if (tntt <= 0) return 0;
      if (tntt <= 10000000) return Math.round(tntt * 0.05);
      if (tntt <= 30000000) return Math.round(tntt * 0.10 - 500000);
      if (tntt <= 60000000) return Math.round(tntt * 0.20 - 3500000);
      if (tntt <= 100000000) return Math.round(tntt * 0.30 - 9500000);
      return Math.round(tntt * 0.35 - 14500000);
    }

    function pit2025(tntt) {
      if (tntt <= 0) return 0;
      if (tntt <= 5000000) return Math.round(tntt * 0.05);
      if (tntt <= 10000000) return Math.round(tntt * 0.10 - 250000);
      if (tntt <= 18000000) return Math.round(tntt * 0.15 - 750000);
      if (tntt <= 32000000) return Math.round(tntt * 0.20 - 1650000);
      if (tntt <= 52000000) return Math.round(tntt * 0.25 - 3250000);
      if (tntt <= 80000000) return Math.round(tntt * 0.30 - 5850000);
      return Math.round(tntt * 0.35 - 9850000);
    }

    function evalGross(gross, deps, region, period, insMode, insCustom, medEdu) {
      const insBase = insMode === 'custom' ? Math.max(0, insCustom) : gross;
      const capBhxh = 20 * (BASE_SALARIES[period] || 2530000);
      const capBhtn = 20 * (REGION_WAGES[region] || 5310000);
      const bhxh = Math.round(Math.min(insBase, capBhxh) * 0.08);
      const bhyt = Math.round(Math.min(insBase, capBhxh) * 0.015);
      const bhtn = Math.round(Math.min(insBase, capBhtn) * 0.01);
      const totalIns = bhxh + bhyt + bhtn;

      const ded2026 = 15500000 + deps * 6200000 + medEdu;
      const tntt2026 = Math.max(0, gross - totalIns - ded2026);
      const tax2026 = pit2026(tntt2026);
      const net2026 = Math.round(gross - totalIns - tax2026);

      const ded2025 = 11000000 + deps * 4400000;
      const tntt2025 = Math.max(0, gross - totalIns - ded2025);
      const tax2025 = pit2025(tntt2025);
      return { gross: Math.round(gross), net: net2026, bhxh, bhyt, bhtn, totalIns, ded2026, tntt2026, tax2026, tax2025 };
    }

    function computeSalary() {
      const income = Math.max(0, parseFloat(document.getElementById('salary-income').value) || 0);
      const deps = Math.max(0, parseInt(document.getElementById('salary-dependents').value, 10) || 0);
      const medEdu = Math.min(3916667, Math.max(0, parseFloat(document.getElementById('salary-med-edu').value) || 0));
      const region = document.getElementById('salary-region').value;
      const period = document.getElementById('salary-period').value;
      const insMode = document.getElementById('salary-ins-mode').value;
      const insCustom = parseFloat(document.getElementById('salary-ins-custom').value) || 0;

      document.getElementById('ins-custom-wrap').style.display = insMode === 'custom' ? 'block' : 'none';

      let res;
      if (pitMode === 'net-to-gross') {
        let low = income, high = Math.max(income * 2.2 + 50000000, 100000000);
        for (let i = 0; i < 80; i++) {
          const mid = (low + high) / 2;
          const cand = evalGross(mid, deps, region, period, insMode, insCustom, medEdu);
          if (cand.net < income) low = mid; else high = mid;
        }
        const gEst = Math.round((low + high) / 2);
        res = evalGross(gEst, deps, region, period, insMode, insCustom, medEdu);
        for (let d = -2; d <= 2; d++) {
          const cand = evalGross(Math.max(0, gEst + d), deps, region, period, insMode, insCustom, medEdu);
          if (Math.abs(cand.net - income) < Math.abs(res.net - income)) res = cand;
        }
      } else {
        res = evalGross(income, deps, region, period, insMode, insCustom, medEdu);
      }

      const savedMonth = res.tax2025 - res.tax2026;
      const savedYear = savedMonth * 12;

      document.getElementById('pit-saved-month').innerText = fmt(savedMonth);
      document.getElementById('pit-saved-year').innerText = fmt(savedYear);
      document.getElementById('pit-res-gross').innerText = fmt(res.gross);
      document.getElementById('pit-res-ins').innerText = '-' + fmt(res.totalIns);
      document.getElementById('pit-bhxh').innerText = fmt(res.bhxh);
      document.getElementById('pit-bhyt').innerText = fmt(res.bhyt);
      document.getElementById('pit-bhtn').innerText = fmt(res.bhtn);
      document.getElementById('pit-dep-count').innerText = deps;
      document.getElementById('pit-res-deductions').innerText = fmt(res.ded2026);
      document.getElementById('pit-res-tntt').innerText = fmt(res.tntt2026);
      document.getElementById('pit-res-tax-2026').innerText = '-' + fmt(res.tax2026);
      document.getElementById('pit-res-net').innerText = fmt(res.net);
      document.getElementById('pit-cmp-2025-mo').innerText = fmt(res.tax2025);
      document.getElementById('pit-cmp-2026-mo').innerText = fmt(res.tax2026);
      document.getElementById('pit-cmp-2025-yr').innerText = fmt(res.tax2025 * 12);
      document.getElementById('pit-cmp-2026-yr').innerText = fmt(res.tax2026 * 12);

      lastPitState = { ...res, deps, savedMonth, savedYear };
    }

    document.getElementById('mode-gross-net').addEventListener('click', () => {
      pitMode = 'gross-to-net';
      document.getElementById('mode-gross-net').classList.add('active');
      document.getElementById('mode-net-gross').classList.remove('active');
      document.getElementById('income-label').innerText = 'Thu Nhập Gross Hàng Tháng (VND)';
      computeSalary();
    });
    document.getElementById('mode-net-gross').addEventListener('click', () => {
      pitMode = 'net-to-gross';
      document.getElementById('mode-net-gross').classList.add('active');
      document.getElementById('mode-gross-net').classList.remove('active');
      document.getElementById('income-label').innerText = 'Thu Nhập Net Mong Muốn Hàng Tháng (VND)';
      computeSalary();
    });
    document.querySelectorAll('.ft-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.getElementById('salary-income').value = btn.getAttribute('data-sal');
        computeSalary();
      });
    });
    ['salary-income', 'salary-dependents', 'salary-med-edu', 'salary-region', 'salary-period', 'salary-ins-mode', 'salary-ins-custom'].forEach(id => {
      const el = document.getElementById(id);
      el.addEventListener('input', computeSalary);
      el.addEventListener('change', computeSalary);
    });
    document.getElementById('pit-print-btn').addEventListener('click', () => window.print());
    document.getElementById('pit-csv-btn').addEventListener('click', () => {
      const s = lastPitState;
      const rows = [
        ['Chi tieu', 'Thang (VND)', 'Nam (VND)'],
        ['Luong Gross', s.gross, s.gross * 12],
        ['BHXH (8%)', s.bhxh, s.bhxh * 12],
        ['BHYT (1.5%)', s.bhyt, s.bhyt * 12],
        ['BHTN (1%)', s.bhtn, s.bhtn * 12],
        ['Tong bao hiem (10.5%)', s.totalIns, s.totalIns * 12],
        ['Giam tru gia canh + Y te/GD', s.ded2026, s.ded2026 * 12],
        ['Thu nhap tinh thue 2026', s.tntt2026, s.tntt2026 * 12],
        ['Thue TNCN 2026 (5 bac)', s.tax2026, s.tax2026 * 12],
        ['Thue TNCN 2025 (7 bac cu)', s.tax2025, s.tax2025 * 12],
        ['Thue tiet kiem duoc nho cai cach 2026', s.savedMonth, s.savedYear],
        ['Luong thuc nhan (NET 2026)', s.net, s.net * 12]
      ];
      const csv = rows.map(r => r.join(',')).join('\\n');
      const blob = new Blob(['\\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'bang-tinh-luong-tncn-2026.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
    computeSalary();
    """

    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="FinTech & Thuế 2026",
        page_title=f"{keyword} - Biểu Thuế 5 Bậc Luật 109/2025/QH15 | VinaTools",
        meta_desc="Tính lương Gross sang Net và Net sang Gross năm 2026 theo Luật Thuế TNCN 109/2025/QH15 (5 bậc, giảm trừ 15,5 triệu/6,2 triệu), NĐ 253/2026, NĐ 293/2025 và NĐ 161/2026.",
        meta_keywords="tính lương gross sang net 2026, thuế tncn 2026 5 bậc, giảm trừ gia cảnh 15.5 triệu, lương tối thiểu vùng 2026, luật 109/2025/qh15",
        subtitle="Quy đổi hai chiều Gross &harr; Net, tự động áp trần BHXH/BHYT (NĐ 161/2026) &amp; BHTN (NĐ 293/2025), giảm trừ 15,5tr / 6,2tr và so sánh tiền thuế tiết kiệm so với 2025.",
        tool_html=tool_html,
        tool_js=tool_js,
        extra_head=SHARED_FINTECH_CSS,
        nav_badge="Luật TNCN 109/2025",
    )


def build_ecommerce_calculator(keyword, slug, config):
    tool_html = """
    <div class="ft-grid ft-grid-2">
      <!-- Left Inputs -->
      <div class="ft-card no-print">
        <h2 style="font-size: 1.25rem; margin-bottom: 18px; display: flex; align-items: center; gap: 8px;">
          <i class="fa-solid fa-store" style="color: #00a8ff;"></i> Thông Số Đơn Hàng &amp; Biểu Phí Sàn 2026
        </h2>

        <div class="ft-grid-2col" style="margin-bottom: 14px;">
          <div>
            <label class="ft-label" for="calc-price">Giá Bán Niêm Yết (VND)</label>
            <input type="number" id="calc-price" class="ft-input" value="1000000" min="0" step="10000">
          </div>
          <div>
            <label class="ft-label" for="calc-shop-voucher">Mã Giảm Giá Của Shop (VND)</label>
            <input type="number" id="calc-shop-voucher" class="ft-input" value="0" min="0" step="5000">
          </div>
        </div>

        <div class="ft-grid-2col" style="margin-bottom: 14px;">
          <div>
            <label class="ft-label" for="calc-cogs">Giá Vốn / Nhập Hàng (VND)</label>
            <input type="number" id="calc-cogs" class="ft-input" value="450000" min="0" step="10000">
          </div>
          <div>
            <label class="ft-label" for="calc-ops">Chi Phí Đóng Gói &amp; Vận Hành (VND)</label>
            <input type="number" id="calc-ops" class="ft-input" value="20000" min="0" step="5000">
          </div>
        </div>

        <div class="ft-grid-2col" style="margin-bottom: 18px;">
          <div>
            <label class="ft-label" for="calc-buyer-ship">Phí Ship Khách Trả (Tính phí giao dịch)</label>
            <input type="number" id="calc-buyer-ship" class="ft-input" value="0" min="0" step="5000">
          </div>
          <div>
            <label class="ft-label" for="calc-affiliate">Chiết Khấu Affiliate / KOL (%)</label>
            <input type="number" id="calc-affiliate" class="ft-input" value="0" min="0" step="0.5">
          </div>
        </div>

        <div class="ft-tabs">
          <button type="button" id="tab-shopee" class="ft-tab active"><i class="fa-solid fa-bag-shopping"></i> Shopee (T5/2026)</button>
          <button type="button" id="tab-tiktok" class="ft-tab"><i class="fa-brands fa-tiktok"></i> TikTok Shop (T5-8/2026)</button>
        </div>

        <!-- Shopee 2026 -->
        <div id="params-shopee" style="display: flex; flex-direction: column; gap: 12px;">
          <div style="padding: 10px 12px; border-radius: 8px; background: rgba(0,168,255,0.08); border: 1px solid rgba(0,168,255,0.25); font-size: 0.78rem; color: #7dd3fc;">
            <i class="fa-solid fa-circle-info"></i> <strong>Cập nhật 2026:</strong> Gói Freeship Xtra đã ngừng áp dụng từ 01/04/2025. Phí thanh toán đổi tên thành <strong>Phí xử lý giao dịch (6,0%)</strong> kèm <strong>Phí hạ tầng 3.000đ/đơn</strong>.
          </div>

          <div class="ft-grid-2col">
            <div>
              <label class="ft-label" for="shopee-shop-type">Loại Gian Hàng</label>
              <select id="shopee-shop-type" class="ft-select">
                <option value="regular">Shop Thường</option>
                <option value="mall">Shopee Mall</option>
              </select>
            </div>
            <div>
              <label class="ft-label" for="shopee-category">Nhóm Ngành Hàng (Phí Cố Định)</label>
              <select id="shopee-category" class="ft-select">
                <option value="3.5">Thời trang / Điện tử / Tiêu dùng (3,5%)</option>
                <option value="1.5">FMCG / Mẹ &amp; Bé - Shop Thường (1,5%)</option>
                <option value="5.4">FMCG / Mẹ &amp; Bé - Mall (5,4%)</option>
                <option value="6.5">Điện tử - Mall (6,5%)</option>
                <option value="12.0">Thời trang - Mall (12,0%)</option>
                <option value="custom">Tùy chỉnh % phí cố định</option>
              </select>
            </div>
          </div>

          <div class="ft-grid-2col">
            <div>
              <label class="ft-label" for="shopee-pay-fee">Phí xử lý giao dịch (%)</label>
              <input type="number" id="shopee-pay-fee" class="ft-input" value="6.0" step="0.1" min="0">
            </div>
            <div>
              <label class="ft-label" for="shopee-fixed-fee">Phí cố định (%)</label>
              <input type="number" id="shopee-fixed-fee" class="ft-input" value="3.5" step="0.1" min="0">
            </div>
          </div>

          <div>
            <label class="ft-label" for="shopee-infra-fee">Phí hạ tầng bắt buộc (VND/đơn)</label>
            <input type="number" id="shopee-infra-fee" class="ft-input" value="3000" min="0" step="500">
          </div>

          <label style="display: flex; align-items: center; gap: 10px; font-size: 0.86rem; color: #e5e7eb; cursor: pointer;">
            <input type="checkbox" id="shopee-voucher" checked style="width: auto;">
            <span>Tham gia Voucher Xtra (5,5% - tối đa 50.000đ/sp)</span>
          </label>
          <label style="display: flex; align-items: center; gap: 10px; font-size: 0.86rem; color: #e5e7eb; cursor: pointer;">
            <input type="checkbox" id="shopee-content-xtra" style="width: auto;">
            <span>Tham gia Content Xtra (2,95% - tối đa 50.000đ/sp cho Mall)</span>
          </label>
          <label style="display: flex; align-items: center; gap: 10px; font-size: 0.86rem; color: #e5e7eb; cursor: pointer;">
            <input type="checkbox" id="shopee-piship" style="width: auto;">
            <span>Tham gia Gói PiShip (2.700đ/đơn)</span>
          </label>
          <label style="display: flex; align-items: center; gap: 10px; font-size: 0.86rem; color: #fbbf24; cursor: pointer; font-weight: 600;">
            <input type="checkbox" id="shopee-tax-withholding" style="width: auto;">
            <span>Khấu trừ thuế hộ/cá nhân KD tại nguồn (1,5%: 1% GTGT + 0,5% TNCN - Điều 11 NĐ 68/2026)</span>
          </label>
        </div>

        <!-- TikTok Shop 2026 -->
        <div id="params-tiktok" style="display: none; flex-direction: column; gap: 12px;">
          <div>
            <label class="ft-label" for="tiktok-shop-type">Loại Gian Hàng TikTok Shop</label>
            <select id="tiktok-shop-type" class="ft-select">
              <option value="regular">Nhà bán thường (~14,0% hoa hồng)</option>
              <option value="mall_16">TikTok Shop Mall - Mức chuẩn (16,0% cập nhật 03/08/2026)</option>
              <option value="mall_198">TikTok Shop Mall - Ngành cao nhất (19,8% cập nhật 03/08/2026)</option>
            </select>
          </div>
          <div class="ft-grid-2col">
            <div>
              <label class="ft-label" for="tiktok-trans-fee">Phí giao dịch (% - từ 09/05/2026)</label>
              <input type="number" id="tiktok-trans-fee" class="ft-input" value="6.0" step="0.1" min="0">
            </div>
            <div>
              <label class="ft-label" for="tiktok-commission">Phí hoa hồng nền tảng (%)</label>
              <input type="number" id="tiktok-commission" class="ft-input" value="14.0" step="0.1" min="0">
            </div>
          </div>
          <div>
            <label class="ft-label" for="tiktok-flat-fee">Phí xử lý đơn hàng cố định (VND/đơn)</label>
            <input type="number" id="tiktok-flat-fee" class="ft-input" value="3000" min="0" step="500">
          </div>
          <label style="display: flex; align-items: center; gap: 10px; font-size: 0.86rem; color: #fbbf24; cursor: pointer; font-weight: 600;">
            <input type="checkbox" id="tiktok-tax-withholding" style="width: auto;">
            <span>Khấu trừ thuế TMĐT 1,5% tại nguồn (Điều 11 NĐ 68/2026)</span>
          </label>
        </div>
      </div>

      <!-- Right Results -->
      <div class="print-report">
        <div class="ft-card">
          <h2 style="font-size: 1.25rem; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
            <i class="fa-solid fa-receipt" style="color: #eb4899;"></i> Phân Tích Chi Phí &amp; Break-Even ROAS
          </h2>

          <div class="ft-row"><span>Doanh thu thuần sau Voucher Shop</span><strong id="res-gross">0 đ</strong></div>
          <div class="ft-row"><span>Phí xử lý giao dịch</span><strong id="res-trans-fee" style="color: #f87171;">0 đ</strong></div>
          <div class="ft-row"><span>Phí cố định / Hoa hồng nền tảng</span><strong id="res-fixed-fee" style="color: #f87171;">0 đ</strong></div>
          <div class="ft-row"><span>Phí hạ tầng / xử lý đơn &amp; Dịch vụ (VX/CX/PiShip)</span><strong id="res-addon-fee" style="color: #f87171;">0 đ</strong></div>
          <div class="ft-row"><span>Tổng phí sàn khấu trừ</span><strong id="res-platform-fee" style="color: #f87171;">0 đ</strong></div>
          <div class="ft-row"><span>Thuế TMĐT khấu trừ tại nguồn (1,5%)</span><strong id="res-tax-withheld" style="color: #fbbf24;">0 đ</strong></div>
          <div class="ft-row"><span>Chi phí Tiếp thị liên kết (Affiliate)</span><strong id="res-affiliate" style="color: #f87171;">0 đ</strong></div>
          <div class="ft-row"><span>Giá vốn (COGS) + Đóng gói vận hành</span><strong id="res-cogs-ops">0 đ</strong></div>

          <div class="ft-row" style="margin-top: 8px; padding: 12px; border-radius: 8px; background: rgba(16,185,129,0.08);">
            <span style="font-weight: 700;">Thực nhận từ sàn (Net Payout)</span>
            <strong id="res-payout" style="font-size: 1.15rem; color: #34d399;">0 đ</strong>
          </div>
          <div class="ft-row" style="margin-top: 8px; padding: 12px; border-radius: 8px; background: rgba(0,168,255,0.1);">
            <span style="font-weight: 700; color: #fff;">Lợi nhuận ròng (Net Profit)</span>
            <strong id="res-net-profit" style="font-size: 1.3rem; color: #38bdf8;">0 đ</strong>
          </div>

          <div class="ft-grid-2col" style="margin-top: 16px;">
            <div style="padding: 14px; border-radius: 10px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); text-align: center;">
              <div style="font-size: 0.74rem; text-transform: uppercase; color: #9ca3af;">Biên Lợi Nhuận (Margin)</div>
              <div id="res-margin" style="font-size: 1.6rem; font-weight: 900; margin-top: 4px;">0.0%</div>
            </div>
            <div style="padding: 14px; border-radius: 10px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); text-align: center;">
              <div style="font-size: 0.74rem; text-transform: uppercase; color: #9ca3af;">Break-Even ROAS Hòa Vốn</div>
              <div id="res-roas" style="font-size: 1.6rem; font-weight: 900; color: #fbbf24; margin-top: 4px;">--</div>
            </div>
          </div>

          <div class="ft-actions no-print">
            <button type="button" id="export-ecom-csv-btn" class="btn btn-primary" style="flex: 1;"><i class="fa-solid fa-file-csv"></i> Tải Báo Cáo Phí Sàn CSV</button>
            <button type="button" onclick="window.print()" class="btn btn-secondary" style="flex: 1;"><i class="fa-solid fa-print"></i> In / Lưu PDF</button>
          </div>
        </div>
      </div>
    </div>
    """

    tool_js = """
    let activePlatform = 'shopee';
    let lastEcomState = {};
    function fmt(n) { return Math.round(n).toLocaleString('vi-VN') + ' đ'; }

    document.getElementById('tab-shopee').addEventListener('click', () => {
      activePlatform = 'shopee';
      document.getElementById('tab-shopee').classList.add('active');
      document.getElementById('tab-tiktok').classList.remove('active');
      document.getElementById('params-shopee').style.display = 'flex';
      document.getElementById('params-tiktok').style.display = 'none';
      calculateFees();
    });
    document.getElementById('tab-tiktok').addEventListener('click', () => {
      activePlatform = 'tiktok';
      document.getElementById('tab-tiktok').classList.add('active');
      document.getElementById('tab-shopee').classList.remove('active');
      document.getElementById('params-tiktok').style.display = 'flex';
      document.getElementById('params-shopee').style.display = 'none';
      calculateFees();
    });

    document.getElementById('shopee-shop-type').addEventListener('change', (e) => {
      const cat = document.getElementById('shopee-category');
      if (e.target.value === 'mall' && cat.value === '3.5') {
        cat.value = '12.0';
        document.getElementById('shopee-fixed-fee').value = '12.0';
      } else if (e.target.value === 'regular' && (cat.value === '12.0' || cat.value === '5.4' || cat.value === '6.5')) {
        cat.value = '3.5';
        document.getElementById('shopee-fixed-fee').value = '3.5';
      }
      calculateFees();
    });
    document.getElementById('shopee-category').addEventListener('change', (e) => {
      if (e.target.value !== 'custom') {
        document.getElementById('shopee-fixed-fee').value = e.target.value;
      }
      calculateFees();
    });
    document.getElementById('tiktok-shop-type').addEventListener('change', (e) => {
      const map = { regular: '14.0', mall_16: '16.0', mall_198: '19.8' };
      document.getElementById('tiktok-commission').value = map[e.target.value] || '14.0';
      calculateFees();
    });

    function calculateFees() {
      const price = Math.max(0, parseFloat(document.getElementById('calc-price').value) || 0);
      const voucher = Math.max(0, parseFloat(document.getElementById('calc-shop-voucher').value) || 0);
      const cogs = Math.max(0, parseFloat(document.getElementById('calc-cogs').value) || 0);
      const ops = Math.max(0, parseFloat(document.getElementById('calc-ops').value) || 0);
      const buyerShip = Math.max(0, parseFloat(document.getElementById('calc-buyer-ship').value) || 0);
      const affPct = Math.max(0, parseFloat(document.getElementById('calc-affiliate').value) || 0);

      const itemNet = Math.max(0, price - voucher);
      const transBase = Math.max(0, price + buyerShip - voucher);

      let transFee = 0, fixedFee = 0, addonFee = 0, taxWithheld = 0;
      if (activePlatform === 'shopee') {
        const payPct = parseFloat(document.getElementById('shopee-pay-fee').value) || 0;
        const fixPct = parseFloat(document.getElementById('shopee-fixed-fee').value) || 0;
        const infraFee = Math.max(0, parseFloat(document.getElementById('shopee-infra-fee').value) || 0);
        const hasVx = document.getElementById('shopee-voucher').checked;
        const hasCx = document.getElementById('shopee-content-xtra').checked;
        const hasPi = document.getElementById('shopee-piship').checked;
        const hasTax = document.getElementById('shopee-tax-withholding').checked;

        transFee = Math.round(transBase * (payPct / 100));
        fixedFee = Math.round(itemNet * (fixPct / 100));
        const vxFee = hasVx ? Math.round(Math.min(itemNet * 0.055, 50000)) : 0;
        const cxFee = hasCx ? Math.round(Math.min(itemNet * 0.0295, 50000)) : 0;
        const piFee = hasPi ? 2700 : 0;
        addonFee = Math.round(infraFee + vxFee + cxFee + piFee);
        taxWithheld = hasTax ? Math.round(itemNet * 0.015) : 0;
      } else {
        const tTransPct = parseFloat(document.getElementById('tiktok-trans-fee').value) || 0;
        const tCommPct = parseFloat(document.getElementById('tiktok-commission').value) || 0;
        const tFlat = Math.max(0, parseFloat(document.getElementById('tiktok-flat-fee').value) || 0);
        const hasTax = document.getElementById('tiktok-tax-withholding').checked;

        transFee = Math.round(transBase * (tTransPct / 100));
        fixedFee = Math.round(itemNet * (tCommPct / 100));
        addonFee = Math.round(tFlat);
        taxWithheld = hasTax ? Math.round(itemNet * 0.015) : 0;
      }

      const platformFee = transFee + fixedFee + addonFee;
      const affiliateFee = Math.round(itemNet * (affPct / 100));
      const netPayout = itemNet - platformFee - taxWithheld;
      const profitBeforeAds = netPayout - cogs - ops;
      const netProfit = profitBeforeAds - affiliateFee;
      const margin = itemNet > 0 ? (netProfit / itemNet) * 100 : 0;
      const roasText = profitBeforeAds > 0 ? (itemNet / profitBeforeAds).toFixed(2) + 'x' : 'Không khả thi (Lỗ)';

      document.getElementById('res-gross').innerText = fmt(itemNet);
      document.getElementById('res-trans-fee').innerText = '-' + fmt(transFee);
      document.getElementById('res-fixed-fee').innerText = '-' + fmt(fixedFee);
      document.getElementById('res-addon-fee').innerText = '-' + fmt(addonFee);
      document.getElementById('res-platform-fee').innerText = '-' + fmt(platformFee);
      document.getElementById('res-tax-withheld').innerText = '-' + fmt(taxWithheld);
      document.getElementById('res-affiliate').innerText = '-' + fmt(affiliateFee);
      document.getElementById('res-cogs-ops').innerText = '-' + fmt(cogs + ops);
      document.getElementById('res-payout').innerText = fmt(netPayout);
      document.getElementById('res-net-profit').innerText = fmt(netProfit);
      document.getElementById('res-margin').innerText = margin.toFixed(1) + '%';
      document.getElementById('res-margin').style.color = margin >= 20 ? '#34d399' : (margin >= 10 ? '#fbbf24' : '#f87171');
      document.getElementById('res-roas').innerText = roasText;

      lastEcomState = { activePlatform, itemNet, transFee, fixedFee, addonFee, platformFee, taxWithheld, affiliateFee, cogs, ops, netPayout, netProfit, margin: margin.toFixed(2), roasText };
    }

    document.querySelectorAll('input, select').forEach(el => {
      el.addEventListener('input', calculateFees);
      el.addEventListener('change', calculateFees);
    });
    document.getElementById('export-ecom-csv-btn').addEventListener('click', () => {
      const s = lastEcomState;
      const rows = [
        ['Hang muc', 'Gia tri'],
        ['San TMDT', s.activePlatform],
        ['Doanh thu thuan (sau Voucher Shop)', s.itemNet],
        ['Phi xu ly giao dich', s.transFee],
        ['Phi co dinh / Hoa hong', s.fixedFee],
        ['Phi ha tang & dich vu', s.addonFee],
        ['Tong phi san', s.platformFee],
        ['Thue TMDT khau tru 1.5%', s.taxWithheld],
        ['Phi Affiliate', s.affiliateFee],
        ['Gia von + Van hanh', s.cogs + s.ops],
        ['Thuc nhan tu san (Net Payout)', s.netPayout],
        ['Loi nhuan rong', s.netProfit],
        ['Bien loi nhuan (%)', s.margin + '%'],
        ['Break-Even ROAS', s.roasText]
      ];
      const csv = rows.map(r => r.join(',')).join('\\n');
      const blob = new Blob(['\\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'bao-cao-phi-san-tmdt-2026.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
    calculateFees();
    """

    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="FinTech & Thuế 2026",
        page_title=f"{keyword} - Biểu Phí Tháng 5–8/2026 & ROAS | VinaTools",
        meta_desc="Tính phí sàn Shopee & TikTok Shop cập nhật tháng 5-8/2026: Phí xử lý giao dịch 6%, phí hạ tầng 3.000đ, Voucher Xtra 5,5%, Content Xtra 2,95%, PiShip 2.700đ, khấu trừ thuế 1,5% & Break-Even ROAS.",
        meta_keywords="tính phí sàn shopee 2026, phí sàn tiktok shop 2026, phí hạ tầng shopee, break even roas, khấu trừ thuế tmdt 1.5%",
        subtitle="Cập nhật biểu phí tháng 5–8/2026 của Shopee &amp; TikTok Shop, khấu trừ thuế TMĐT 1,5% (Điều 11 NĐ 68/2026), tính Break-Even ROAS và xuất bảng tính CSV.",
        tool_html=tool_html,
        tool_js=tool_js,
        extra_head=SHARED_FINTECH_CSS,
        nav_badge="Biểu phí T5-8/2026",
    )


def build_number_to_words(keyword, slug, config):
    tool_html = """
    <div class="ft-grid" style="max-width: 820px;">
      <div class="ft-card">
        <h2 style="font-size: 1.25rem; margin-bottom: 18px;"><i class="fa-solid fa-coins" style="color: #00a8ff;"></i> Nhập Số Tiền Cần Đọc Thành Chữ</h2>
        <div style="margin-bottom: 16px;">
          <label class="ft-label" for="num-input">Chữ số (Tối đa 999.999.999.999.999)</label>
          <input type="text" id="num-input" class="ft-input" value="1250000000" inputmode="numeric" style="font-size: 1.25rem; font-weight: 800;">
          <div class="ft-presets">
            <button type="button" class="ft-preset-btn" data-num="1005000">1.005.000</button>
            <button type="button" class="ft-preset-btn" data-num="25415000">25.415.000</button>
            <button type="button" class="ft-preset-btn" data-num="1000000000">1 Tỷ</button>
            <button type="button" class="ft-preset-btn" data-num="1500000000000">1.500 Tỷ</button>
            <button type="button" class="ft-preset-btn" data-num="999999999999999">999 Nghìn Tỷ</button>
          </div>
        </div>

        <div class="ft-grid-2col" style="margin-bottom: 18px;">
          <div>
            <label class="ft-label" for="currency-suffix">Đơn vị tiền tệ</label>
            <select id="currency-suffix" class="ft-select">
              <option value="VND">đồng</option>
              <option value="VND_CHAN">đồng chẵn</option>
              <option value="USD">đô la Mỹ</option>
              <option value="NONE">(không có đơn vị)</option>
            </select>
          </div>
          <div>
            <label class="ft-label" for="zero-ten-word">Quy tắc hàng chục bằng 0</label>
            <select id="zero-ten-word" class="ft-select">
              <option value="lẻ">Dùng chữ "lẻ" (Phổ thông / Kế toán)</option>
              <option value="linh">Dùng chữ "linh" (Văn bản miền Bắc)</option>
            </select>
          </div>
        </div>

        <label style="display: flex; align-items: center; gap: 10px; font-size: 0.88rem; color: #e5e7eb; margin-bottom: 20px; cursor: pointer;">
          <input type="checkbox" id="capitalize-first" checked style="width: auto;">
          <span>Viết hoa chữ cái đầu tiên</span>
        </label>

        <div style="padding: 18px; border-radius: 12px; background: rgba(0,168,255,0.08); border: 1px solid rgba(0,168,255,0.28);">
          <div style="font-size: 0.78rem; color: #9ca3af; text-transform: uppercase; margin-bottom: 8px;">Kết quả chuẩn kế toán</div>
          <p id="words-output" style="font-size: 1.15rem; font-weight: 700; color: #fff; line-height: 1.6; margin: 0 0 14px 0;"></p>
          <button type="button" id="copy-words-btn" class="btn btn-primary"><i class="fa-solid fa-copy"></i> Sao Chép Kết Quả</button>
        </div>
      </div>
    </div>
    """

    tool_js = """
    const DIGITS = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín'];

    function readGroup(group, showZeroHundred, zeroTenWord) {
      const h = Math.floor(group / 100);
      const t = Math.floor((group % 100) / 10);
      const u = group % 10;
      let out = '';

      if (h > 0 || showZeroHundred) {
        out += DIGITS[h] + ' trăm ';
      }
      if (t === 0) {
        if ((h > 0 || showZeroHundred) && u > 0) {
          out += zeroTenWord + ' ';
        }
      } else if (t === 1) {
        out += 'mười ';
      } else {
        out += DIGITS[t] + ' mươi ';
      }

      if (u > 0) {
        if (u === 1 && t > 1) out += 'mốt';
        else if (u === 4 && t > 1) out += 'tư';
        else if (u === 5 && t > 0) out += 'lăm';
        else out += DIGITS[u];
      }
      return out.trim();
    }

    function numberToWords(num, zeroTenWord) {
      if (num === 0) return 'không';
      const units = ['', ' nghìn', ' triệu', ' tỷ', ' nghìn tỷ'];
      const groups = [];
      let n = num;
      while (n > 0) {
        groups.push(n % 1000);
        n = Math.floor(n / 1000);
      }

      let parts = [];
      for (let i = groups.length - 1; i >= 0; i--) {
        const grp = groups[i];
        if (grp === 0) {
          if (i === 3 && groups.length > 4 && groups[4] > 0) {
            parts.push('tỷ');
          }
          continue;
        }
        const hasHigher = parts.length > 0;
        const text = readGroup(grp, hasHigher, zeroTenWord);
        parts.push(text + units[i]);
      }
      return parts.join(' ').replace(/\\s+/g, ' ').trim();
    }

    function convertAndDisplay() {
      const rawDigits = (document.getElementById('num-input').value || '').replace(/[^0-9]/g, '');
      const outputEl = document.getElementById('words-output');
      if (!rawDigits) {
        outputEl.innerText = 'Vui lòng nhập số hợp lệ lớn hơn hoặc bằng 0.';
        return;
      }
      if (rawDigits.length > 15) {
        outputEl.innerText = 'Vui lòng nhập số không quá 15 chữ số (tối đa 999.999.999.999.999).';
        return;
      }
      const val = Number(rawDigits);
      const zeroTenWord = document.getElementById('zero-ten-word').value || 'lẻ';
      let readStr = numberToWords(val, zeroTenWord);

      const suffix = document.getElementById('currency-suffix').value;
      if (suffix === 'VND') readStr += ' đồng';
      else if (suffix === 'VND_CHAN') readStr += ' đồng chẵn';
      else if (suffix === 'USD') readStr += ' đô la Mỹ';

      if (document.getElementById('capitalize-first').checked && readStr.length > 0) {
        readStr = readStr.charAt(0).toUpperCase() + readStr.slice(1);
      }
      outputEl.innerText = readStr;
    }

    document.querySelectorAll('.ft-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.getElementById('num-input').value = btn.getAttribute('data-num');
        convertAndDisplay();
      });
    });
    document.getElementById('num-input').addEventListener('input', convertAndDisplay);
    document.getElementById('currency-suffix').addEventListener('change', convertAndDisplay);
    document.getElementById('zero-ten-word').addEventListener('change', convertAndDisplay);
    document.getElementById('capitalize-first').addEventListener('change', convertAndDisplay);
    document.getElementById('copy-words-btn').addEventListener('click', () => {
      const txt = document.getElementById('words-output').innerText;
      if (!txt) return;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(txt).then(() => {
          const btn = document.getElementById('copy-words-btn');
          btn.innerHTML = '<i class="fa-solid fa-check"></i> Đã Sao Chép!';
          setTimeout(() => { btn.innerHTML = '<i class="fa-solid fa-copy"></i> Sao Chép Kết Quả'; }, 1800);
        });
      }
    });
    convertAndDisplay();
    """

    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="Tiện Ích Kế Toán",
        page_title=f"{keyword} - Lên Tới Hàng Trăm Nghìn Tỷ | VinaTools",
        meta_desc="Đọc số tiền bằng chữ tiếng Việt chuẩn kế toán, hóa đơn GTGT và chứng từ ngân hàng: hỗ trợ tới 999.999.999.999.999 (trăm nghìn tỷ) với quy tắc lẻ/linh, mốt, tư, lăm.",
        meta_keywords="đọc số thành chữ, chuyển số thành chữ kế toán, đọc số hàng nghìn tỷ",
        subtitle="Đọc chính xác chữ số lên tới 999.999.999.999.999 (hàng trăm nghìn tỷ đồng) theo đúng quy tắc kế toán (lẻ/linh, mốt, tư, lăm).",
        tool_html=tool_html,
        tool_js=tool_js,
        extra_head=SHARED_FINTECH_CSS,
        nav_badge="Chuẩn Kế Toán",
    )


def build_address_parser(keyword, slug, config):
    tool_html = """
    <div class="ft-grid" style="max-width: 1080px;">
      <div class="ft-card">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 14px;">
          <h2 style="font-size: 1.25rem; margin: 0;"><i class="fa-solid fa-map-location-dot" style="color: #00a8ff;"></i> Nhập Danh Sách Địa Chỉ (1 Địa Chỉ / Dòng)</h2>
          <button type="button" id="fill-sample-addr-btn" class="ft-preset-btn"><i class="fa-solid fa-wand-magic-sparkles"></i> Điền dữ liệu mẫu</button>
        </div>

        <textarea id="raw-address" rows="4" class="ft-textarea" placeholder="Mỗi dòng 1 địa chỉ. Ví dụ:&#10;Số 12 Đường Lê Lợi, Phường Bến Nghé, Quận 1, TP.HCM&#10;Tòa nhà FPT, Phố Duy Tân, Phường Dịch Vọng Hậu, Quận Cầu Giấy, Hà Nội">Số 12 Đường Lê Lợi, Phường Bến Nghé, Quận 1, TP.HCM&#10;198 Trần Quang Khải, Phường Lý Thái Tổ, Quận Hoàn Kiếm, Hà Nội</textarea>

        <div class="ft-actions">
          <button type="button" id="parse-addr-btn" class="btn btn-primary" style="flex: 1;"><i class="fa-solid fa-magnifying-glass-location"></i> Tách &amp; Chuẩn Hóa Hàng Loạt</button>
          <button type="button" id="export-addr-csv-btn" class="btn btn-secondary"><i class="fa-solid fa-file-csv"></i> Xuất File CSV (.csv)</button>
        </div>
      </div>

      <div id="result-panel" class="ft-card" style="display: none;">
        <h3 style="font-size: 1.1rem; color: #34d399; margin-bottom: 14px;"><i class="fa-solid fa-circle-check"></i> Chi Tiết Địa Chỉ Đầu Tiên &amp; Bảng Kết Quả Hàng Loạt (<span id="addr-count">0</span> dòng)</h3>

        <div class="ft-grid-2col" style="margin-bottom: 18px;">
          <div>
            <label class="ft-label">Số nhà / Tên đường</label>
            <input type="text" id="res-street" class="ft-input" readonly>
          </div>
          <div>
            <label class="ft-label">Phường / Xã / Thị trấn</label>
            <input type="text" id="res-ward" class="ft-input" readonly>
          </div>
          <div>
            <label class="ft-label">Quận / Huyện / Thị xã / TP thuộc tỉnh</label>
            <input type="text" id="res-district" class="ft-input" readonly>
          </div>
          <div>
            <label class="ft-label">Tỉnh / Thành phố trực thuộc TW</label>
            <input type="text" id="res-province" class="ft-input" readonly>
          </div>
        </div>

        <div style="overflow-x: auto;">
          <table id="bulk-address-table" class="ft-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Số nhà, Đường</th>
                <th>Phường / Xã</th>
                <th>Quận / Huyện</th>
                <th>Tỉnh / Thành phố</th>
              </tr>
            </thead>
            <tbody id="bulk-address-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>
    """

    tool_js = """
    const PROVINCES = [
      'Thành phố Hồ Chí Minh', 'TP. Hồ Chí Minh', 'TP.HCM', 'TP HCM', 'TPHCM', 'Hồ Chí Minh', 'Sài Gòn',
      'Thành phố Hà Nội', 'TP. Hà Nội', 'TP Hà Nội', 'Hà Nội',
      'Thành phố Đà Nẵng', 'TP. Đà Nẵng', 'Đà Nẵng',
      'Thành phố Hải Phòng', 'TP. Hải Phòng', 'Hải Phòng',
      'Thành phố Cần Thơ', 'TP. Cần Thơ', 'Cần Thơ',
      'Bình Dương', 'Đồng Nai', 'Bà Rịa - Vũng Tàu', 'Bà Rịa Vũng Tàu', 'Vũng Tàu',
      'Long An', 'Tiền Giang', 'Bến Tre', 'Trà Vinh', 'Vĩnh Long', 'Đồng Tháp',
      'An Giang', 'Kiên Giang', 'Hậu Giang', 'Sóc Trăng', 'Bạc Liêu', 'Cà Mau',
      'Tây Ninh', 'Bình Phước', 'Lâm Đồng', 'Đà Lạt', 'Đắk Nông', 'Đắk Lắk', 'Gia Lai', 'Kon Tum',
      'Khánh Hòa', 'Nha Trang', 'Phú Yên', 'Bình Định', 'Quảng Ngãi', 'Quảng Nam', 'Thừa Thiên Huế', 'Huế',
      'Quảng Trị', 'Quảng Bình', 'Hà Tĩnh', 'Nghệ An', 'Thanh Hóa', 'Ninh Bình', 'Nam Định', 'Thái Bình',
      'Hà Nam', 'Hưng Yên', 'Hải Dương', 'Quảng Ninh', 'Bắc Giang', 'Bắc Ninh', 'Vĩnh Phúc',
      'Phú Thọ', 'Thái Nguyên', 'Tuyên Quang', 'Yên Bái', 'Lạng Sơn', 'Cao Bằng', 'Bắc Kạn', 'Hà Giang',
      'Hòa Bình', 'Sơn La', 'Điện Biên', 'Lai Châu', 'Lào Cai', 'Ninh Thuận', 'Bình Thuận'
    ];
    let parsedRows = [];

    function normalizeProvince(p) {
      const low = p.toLowerCase();
      if (low.includes('hồ chí minh') || low.includes('hcm') || low.includes('sài gòn')) return 'Thành phố Hồ Chí Minh';
      if (low.includes('hà nội')) return 'Thành phố Hà Nội';
      if (low.includes('đà nẵng')) return 'Thành phố Đà Nẵng';
      if (low.includes('hải phòng')) return 'Thành phố Hải Phòng';
      if (low.includes('cần thơ')) return 'Thành phố Cần Thơ';
      return p;
    }

    function parseSingleAddress(raw) {
      let clean = raw.trim();
      let province = '', district = '', ward = '', street = '';

      for (const prov of PROVINCES) {
        const esc = prov.replace(/[-/\\\\^$*+?.()|[\\]{}]/g, '\\\\$&');
        const reEnd = new RegExp(',?\\\\s*' + esc + '$', 'i');
        const m = clean.match(reEnd);
        if (m) {
          province = normalizeProvince(prov);
          clean = clean.slice(0, m.index).replace(/,\\s*$/, '').trim();
          break;
        }
      }
      if (!province) {
        for (const prov of PROVINCES) {
          const esc = prov.replace(/[-/\\\\^$*+?.()|[\\]{}]/g, '\\\\$&');
          const reAny = new RegExp(',?\\\\s*' + esc, 'i');
          const m = clean.match(reAny);
          if (m) {
            province = normalizeProvince(prov);
            clean = clean.replace(m[0], '').replace(/,\\s*$/, '').trim();
            break;
          }
        }
      }

      const parts = clean.split(',').map(s => s.trim()).filter(Boolean);
      const distRe = /^(Quận|Huyện|Thị\\s*xã|Thành\\s*phố|Q\\.|H\\.|TX\\.|TP\\.)\\s*/i;
      const wardRe = /^(Phường|Xã|Thị\\s*trấn|P\\.|X\\.)\\s*/i;

      if (parts.length > 0 && distRe.test(parts[parts.length - 1])) {
        district = parts.pop();
      }
      if (parts.length > 0 && wardRe.test(parts[parts.length - 1])) {
        ward = parts.pop();
      }
      street = parts.join(', ');
      return { raw, street, ward, district, province };
    }

    function runAddressParse() {
      const lines = (document.getElementById('raw-address').value || '')
        .split(/\\r?\\n/)
        .map(s => s.trim())
        .filter(Boolean);
      if (lines.length === 0) return;

      parsedRows = lines.map(parseSingleAddress);
      const first = parsedRows[0];
      document.getElementById('res-street').value = first.street || '';
      document.getElementById('res-ward').value = first.ward || '';
      document.getElementById('res-district').value = first.district || '';
      document.getElementById('res-province').value = first.province || '';
      document.getElementById('addr-count').innerText = parsedRows.length;

      const tbody = document.getElementById('bulk-address-tbody');
      tbody.innerHTML = '';
      parsedRows.forEach((r, idx) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${idx + 1}</td><td>${r.street || '-'}</td><td>${r.ward || '-'}</td><td>${r.district || '-'}</td><td>${r.province || '-'}</td>`;
        tbody.appendChild(tr);
      });
      document.getElementById('result-panel').style.display = 'block';
    }

    document.getElementById('parse-addr-btn').addEventListener('click', runAddressParse);
    document.getElementById('fill-sample-addr-btn').addEventListener('click', () => {
      document.getElementById('raw-address').value = [
        'Số 12 Đường Lê Lợi, Phường Bến Nghé, Quận 1, TP.HCM',
        '198 Trần Quang Khải, Phường Lý Thái Tổ, Quận Hoàn Kiếm, Hà Nội',
        'Số 10 Tân Trào, Phường Tân Phú, Quận 7, Thành phố Hồ Chí Minh'
      ].join('\\n');
      runAddressParse();
    });
    document.getElementById('export-addr-csv-btn').addEventListener('click', () => {
      if (parsedRows.length === 0) runAddressParse();
      const esc = (v) => '"' + String(v || '').replace(/"/g, '""') + '"';
      const rows = [['STT', 'Dia chi goc', 'So nha / Duong', 'Phuong / Xa', 'Quan / Huyen', 'Tinh / Thanh pho']];
      parsedRows.forEach((r, idx) => rows.push([idx + 1, esc(r.raw), esc(r.street), esc(r.ward), esc(r.district), esc(r.province)]));
      const csv = rows.map(r => r.join(',')).join('\\n');
      const blob = new Blob(['\\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'dia-chi-chuan-hoa.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
    runAddressParse();
    """

    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="Tiện Ích Dữ Liệu",
        page_title=f"{keyword} - Tách Hàng Loạt & Xuất CSV | VinaTools",
        meta_desc="Phân tách hàng loạt địa chỉ hành chính Việt Nam (1 dòng/địa chỉ) thành 4 cấp: Số nhà/đường, Phường/Xã, Quận/Huyện, Tỉnh/Thành phố và xuất CSV ngay lập tức.",
        meta_keywords="tách địa chỉ việt nam, chuẩn hóa địa chỉ hàng loạt, xuất csv địa chỉ",
        subtitle="Phân tách hàng loạt danh sách địa chỉ thô (mỗi dòng 1 địa chỉ) thành 4 trường chuẩn hành chính và xuất tệp CSV dùng ngay trong Excel.",
        tool_html=tool_html,
        tool_js=tool_js,
        extra_head=SHARED_FINTECH_CSS,
        nav_badge="Bulk Parser + CSV",
    )


def build_compound_interest_calculator(keyword, slug, config):
    tool_html = """
    <div class="ft-grid ft-grid-2">
      <div class="ft-card no-print">
        <h2 style="font-size: 1.25rem; margin-bottom: 18px;"><i class="fa-solid fa-chart-line" style="color: #00a8ff;"></i> Tham Số Đầu Tư Lãi Kép</h2>
        <div class="ft-grid-2col" style="margin-bottom: 14px;">
          <div>
            <label class="ft-label" for="interest-principal">Vốn Gốc Ban Đầu (VND)</label>
            <input type="number" id="interest-principal" class="ft-input" value="100000000" min="0" step="1000000">
          </div>
          <div>
            <label class="ft-label" for="interest-contrib">Đóng Góp Thêm Hàng Tháng (VND)</label>
            <input type="number" id="interest-contrib" class="ft-input" value="5000000" min="0" step="500000">
          </div>
        </div>
        <div class="ft-grid-2col" style="margin-bottom: 14px;">
          <div>
            <label class="ft-label" for="interest-rate">Lãi Suất Năm (%/năm)</label>
            <input type="number" id="interest-rate" class="ft-input" value="8.0" min="0" step="0.1">
          </div>
          <div>
            <label class="ft-label" for="interest-period">Thời Gian Đầu Tư (Năm)</label>
            <input type="number" id="interest-period" class="ft-input" value="10" min="1" max="50">
          </div>
        </div>
        <div style="margin-bottom: 18px;">
          <label class="ft-label" for="interest-type">Kỳ Hạn Ghép Lãi</label>
          <select id="interest-type" class="ft-select">
            <option value="12" selected>Ghép lãi hàng tháng (12 lần/năm)</option>
            <option value="4">Ghép lãi hàng quý (4 lần/năm)</option>
            <option value="1">Ghép lãi hàng năm (1 lần/năm)</option>
          </select>
        </div>
        <button type="button" id="calc-interest-btn" class="btn btn-primary" style="width: 100%;"><i class="fa-solid fa-calculator"></i> Tính Lịch Biểu Dòng Tiền</button>
      </div>

      <div class="print-report">
        <div class="ft-card">
          <h2 style="font-size: 1.25rem; margin-bottom: 16px;"><i class="fa-solid fa-sack-dollar" style="color: #34d399;"></i> Lịch Biểu Dòng Tiền Tích Lũy</h2>
          <div class="ft-grid-2col" style="margin-bottom: 18px;">
            <div style="padding: 14px; border-radius: 10px; background: rgba(0,168,255,0.08); border: 1px solid rgba(0,168,255,0.25); text-align: center;">
              <div style="font-size: 0.75rem; color: #9ca3af; text-transform: uppercase;">Tổng Giá Trị Cuối Kỳ</div>
              <div id="total-val" style="font-size: 1.3rem; font-weight: 900; color: #38bdf8; margin-top: 4px;">0 đ</div>
            </div>
            <div style="padding: 14px; border-radius: 10px; background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25); text-align: center;">
              <div style="font-size: 0.75rem; color: #9ca3af; text-transform: uppercase;">Tổng Tiền Lãi Sinh Ra</div>
              <div id="interest-val" style="font-size: 1.3rem; font-weight: 900; color: #34d399; margin-top: 4px;">0 đ</div>
            </div>
          </div>

          <div style="overflow-x: auto; max-height: 360px;">
            <table id="interest-table" class="ft-table">
              <thead>
                <tr>
                  <th>Năm</th>
                  <th style="text-align: right;">Tổng vốn góp</th>
                  <th style="text-align: right;">Lãi trong năm</th>
                  <th style="text-align: right;">Số dư cuối năm</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>

          <div class="ft-actions no-print">
            <button type="button" id="export-interest-csv-btn" class="btn btn-primary" style="flex: 1;"><i class="fa-solid fa-file-csv"></i> Tải Bảng Tính CSV (.csv)</button>
            <button type="button" onclick="window.print()" class="btn btn-secondary" style="flex: 1;"><i class="fa-solid fa-print"></i> In / Lưu PDF</button>
          </div>
        </div>
      </div>
    </div>
    """

    tool_js = """
    let scheduleRows = [];
    function fmt(n) { return Math.round(n).toLocaleString('vi-VN') + ' đ'; }

    function calcCompound() {
      const principal = Math.max(0, parseFloat(document.getElementById('interest-principal').value) || 0);
      const monthlyContrib = Math.max(0, parseFloat(document.getElementById('interest-contrib').value) || 0);
      const annualRate = Math.max(0, (parseFloat(document.getElementById('interest-rate').value) || 0) / 100);
      const years = Math.min(50, Math.max(1, parseInt(document.getElementById('interest-period').value, 10) || 1));
      const freq = parseInt(document.getElementById('interest-type').value, 10) || 12;

      const tbody = document.querySelector('#interest-table tbody');
      tbody.innerHTML = '';
      scheduleRows = [];

      let balance = principal;
      let totalContrib = principal;

      for (let y = 1; y <= years; y++) {
        const startBal = balance;
        const startContrib = totalContrib;
        for (let m = 1; m <= 12; m++) {
          balance += monthlyContrib;
          totalContrib += monthlyContrib;
          if (freq === 12) {
            balance *= (1 + annualRate / 12);
          } else if (freq === 4 && m % 3 === 0) {
            balance *= (1 + annualRate / 4);
          } else if (freq === 1 && m === 12) {
            balance *= (1 + annualRate);
          }
        }
        const yearInterest = (balance - startBal) - (totalContrib - startContrib);
        scheduleRows.push({
          year: y,
          totalContrib: Math.round(totalContrib),
          yearInterest: Math.round(yearInterest),
          endBalance: Math.round(balance)
        });
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>Năm ${y}</td><td style="text-align:right;">${fmt(totalContrib)}</td><td style="text-align:right; color:#34d399;">+${fmt(yearInterest)}</td><td style="text-align:right; font-weight:700;">${fmt(balance)}</td>`;
        tbody.appendChild(tr);
      }

      document.getElementById('total-val').innerText = fmt(balance);
      document.getElementById('interest-val').innerText = fmt(balance - totalContrib);
    }

    document.getElementById('calc-interest-btn').addEventListener('click', calcCompound);
    ['interest-principal', 'interest-contrib', 'interest-rate', 'interest-period', 'interest-type'].forEach(id => {
      const el = document.getElementById(id);
      el.addEventListener('input', calcCompound);
      el.addEventListener('change', calcCompound);
    });
    document.getElementById('export-interest-csv-btn').addEventListener('click', () => {
      if (scheduleRows.length === 0) calcCompound();
      const rows = [['Nam', 'Tong von gop (VND)', 'Tien lai trong nam (VND)', 'So du cuoi ky (VND)']];
      scheduleRows.forEach(r => rows.push([r.year, r.totalContrib, r.yearInterest, r.endBalance]));
      const csv = rows.map(r => r.join(',')).join('\\n');
      const blob = new Blob(['\\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'lich-bieu-lai-kep.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
    calcCompound();
    """

    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="FinTech & Đầu Tư",
        page_title=f"{keyword} - Mô Phỏng Tích Lũy & Xuất CSV | VinaTools",
        meta_desc="Công cụ tính lãi kép và lịch biểu dòng tiền theo năm với vốn góp định kỳ hàng tháng, kỳ hạn ghép lãi linh hoạt và xuất trực tiếp bảng tính CSV.",
        meta_keywords="tính lãi kép, lịch biểu dòng tiền, công cụ tính lãi gộp, xuất csv lãi kép",
        subtitle="Mô phỏng tăng trưởng tài sản theo lãi suất kép hàng tháng/quý/năm, hỗ trợ đóng góp định kỳ và tải ngay lịch biểu dòng tiền CSV.",
        tool_html=tool_html,
        tool_js=tool_js,
        extra_head=SHARED_FINTECH_CSS,
        nav_badge="Instant CSV Export",
    )


def build_tax_code_lookup(keyword, slug, config):
    tool_html = """
    <div class="ft-grid" style="max-width: 1020px;">
      <div class="ft-card">
        <div class="ft-tabs">
          <button type="button" id="mst-tab-company" class="ft-tab active"><i class="fa-solid fa-building"></i> Tra Cứu Theo Mã Số Thuế (/api/company)</button>
          <button type="button" id="mst-tab-search" class="ft-tab"><i class="fa-solid fa-magnifying-glass"></i> Tìm Theo Tên Doanh Nghiệp (/api/search)</button>
        </div>

        <div id="mst-panel-company">
          <label class="ft-label" for="mst-input">Nhập Mã Số Thuế Doanh Nghiệp (10 hoặc 13 số)</label>
          <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <input type="text" id="mst-input" class="ft-input" value="0100109106" placeholder="Ví dụ: 0100109106" style="flex: 1; min-width: 220px;">
            <button type="button" id="mst-lookup-btn" class="btn btn-primary"><i class="fa-solid fa-search"></i> Tra Cứu MST</button>
          </div>
          <div class="ft-presets">
            <button type="button" class="ft-preset-btn" data-mst="0100109106">Viettel (0100109106)</button>
            <button type="button" class="ft-preset-btn" data-mst="0101248147">FPT (0101248147)</button>
            <button type="button" class="ft-preset-btn" data-mst="0300588569">Vinamilk (0300588569)</button>
          </div>
        </div>

        <div id="mst-panel-search" style="display: none;">
          <div class="ft-grid-2col" style="margin-bottom: 12px;">
            <div>
              <label class="ft-label" for="search-q-input">Tên Doanh Nghiệp / Từ Khóa</label>
              <input type="text" id="search-q-input" class="ft-input" value="Viettel" placeholder="Ví dụ: Viettel, FPT, Vinamilk...">
            </div>
            <div>
              <label class="ft-label" for="search-province">Tỉnh / Thành Phố</label>
              <select id="search-province" class="ft-select">
                <option value="">Tất cả tỉnh thành</option>
                <option value="hanoi">Hà Nội</option>
                <option value="hcm">TP. Hồ Chí Minh</option>
                <option value="danang">Đà Nẵng</option>
                <option value="binhduong">Bình Dương</option>
              </select>
            </div>
          </div>
          <button type="button" id="mst-search-btn" class="btn btn-primary" style="width: 100%;"><i class="fa-solid fa-magnifying-glass"></i> Tìm Kiếm Doanh Nghiệp</button>
        </div>
      </div>

      <div class="ft-card" id="mst-result-card">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 14px;">
          <h3 style="margin: 0; font-size: 1.15rem;"><i class="fa-solid fa-database" style="color: #34d399;"></i> Kết Quả Từ VietRegistry API</h3>
          <button type="button" id="export-mst-csv-btn" class="btn btn-secondary" style="padding: 8px 14px; font-size: 0.82rem;"><i class="fa-solid fa-file-csv"></i> Xuất CSV</button>
        </div>
        <div id="mst-status-line" style="font-size: 0.84rem; color: #9ca3af; margin-bottom: 12px;">Nhấn nút tra cứu để lấy dữ liệu doanh nghiệp thời gian thực.</div>
        <div id="mst-result-body"></div>
      </div>
    </div>
    """

    tool_js = """
    let mstMode = 'company';
    let lastRegistryRows = [];

    document.getElementById('mst-tab-company').addEventListener('click', () => {
      mstMode = 'company';
      document.getElementById('mst-tab-company').classList.add('active');
      document.getElementById('mst-tab-search').classList.remove('active');
      document.getElementById('mst-panel-company').style.display = 'block';
      document.getElementById('mst-panel-search').style.display = 'none';
    });
    document.getElementById('mst-tab-search').addEventListener('click', () => {
      mstMode = 'search';
      document.getElementById('mst-tab-search').classList.add('active');
      document.getElementById('mst-tab-company').classList.remove('active');
      document.getElementById('mst-panel-search').style.display = 'block';
      document.getElementById('mst-panel-company').style.display = 'none';
    });
    document.querySelectorAll('.ft-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.getElementById('mst-input').value = btn.getAttribute('data-mst');
        lookupByTaxCode();
      });
    });

    function escHtml(v) {
      return String(v || '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
    }

    async function lookupByTaxCode() {
      const code = (document.getElementById('mst-input').value || '').trim();
      const statusEl = document.getElementById('mst-status-line');
      const bodyEl = document.getElementById('mst-result-body');
      if (!code) return;
      statusEl.innerText = 'Đang truy vấn /api/company...';
      bodyEl.innerHTML = '';
      try {
        const resp = await fetch(`/api/company?tax_code=${encodeURIComponent(code)}`);
        const data = await resp.json();
        if (!resp.ok || data.error) {
          statusEl.innerText = 'Lỗi: ' + (data.error || resp.statusText);
          lastRegistryRows = [];
          return;
        }
        statusEl.innerText = 'Nguồn: ' + (data.data_source || 'VietRegistry API');
        lastRegistryRows = [data];
        const statusBadge = data.status === 'active'
          ? '<span class="ft-badge ft-badge-green">Đang hoạt động</span>'
          : '<span class="ft-badge ft-badge-amber">' + escHtml(data.status || 'unknown') + '</span>';
        bodyEl.innerHTML = `
          <div class="ft-row"><span>Tên doanh nghiệp</span><strong>${escHtml(data.name_vietnamese || data.name)}</strong></div>
          <div class="ft-row"><span>Mã số thuế</span><strong>${escHtml(data.tax_code)}</strong></div>
          <div class="ft-row"><span>Trạng thái</span>${statusBadge}</div>
          <div class="ft-row"><span>Đại diện pháp luật</span><strong>${escHtml(data.legal_representative || 'N/A')}</strong></div>
          <div class="ft-row"><span>Địa chỉ trụ sở</span><strong style="text-align:right;">${escHtml(data.address || 'N/A')}</strong></div>
        `;
      } catch (err) {
        statusEl.innerText = 'Không thể kết nối /api/company (hãy kiểm tra triển khai Vercel hoặc chạy local API).';
        lastRegistryRows = [];
      }
    }

    async function searchCompanies() {
      const q = (document.getElementById('search-q-input').value || '').trim();
      const province = document.getElementById('search-province').value;
      const statusEl = document.getElementById('mst-status-line');
      const bodyEl = document.getElementById('mst-result-body');
      if (!q) return;
      statusEl.innerText = 'Đang tìm kiếm qua /api/search...';
      bodyEl.innerHTML = '';
      try {
        const resp = await fetch(`/api/search?q=${encodeURIComponent(q)}&province=${encodeURIComponent(province)}`);
        const data = await resp.json();
        if (!resp.ok || data.error) {
          statusEl.innerText = 'Lỗi: ' + (data.error || resp.statusText);
          lastRegistryRows = [];
          return;
        }
        const results = data.results || [];
        lastRegistryRows = results;
        statusEl.innerText = `Tìm thấy ${results.length} kết quả (${data.note || ''})`;
        if (results.length === 0) {
          bodyEl.innerHTML = '<p style="color:#9ca3af;">Không có doanh nghiệp phù hợp.</p>';
          return;
        }
        let html = '<div style="overflow-x:auto;"><table class="ft-table"><thead><tr><th>MST</th><th>Tên doanh nghiệp</th><th>Địa chỉ</th><th>Trạng thái</th></tr></thead><tbody>';
        results.forEach(r => {
          html += `<tr><td><strong>${escHtml(r.tax_code)}</strong></td><td>${escHtml(r.name)}</td><td>${escHtml(r.address)}</td><td>${escHtml(r.status)}</td></tr>`;
        });
        html += '</tbody></table></div>';
        bodyEl.innerHTML = html;
      } catch (err) {
        statusEl.innerText = 'Không thể kết nối /api/search.';
        lastRegistryRows = [];
      }
    }

    document.getElementById('mst-lookup-btn').addEventListener('click', lookupByTaxCode);
    document.getElementById('mst-search-btn').addEventListener('click', searchCompanies);
    document.getElementById('export-mst-csv-btn').addEventListener('click', () => {
      if (!lastRegistryRows.length) return;
      const esc = (v) => '"' + String(v || '').replace(/"/g, '""') + '"';
      const rows = [['Ma so thue', 'Ten doanh nghiep', 'Dia chi', 'Trang thai']];
      lastRegistryRows.forEach(r => rows.push([esc(r.tax_code), esc(r.name_vietnamese || r.name), esc(r.address), esc(r.status)]));
      const csv = rows.map(r => r.join(',')).join('\\n');
      const blob = new Blob(['\\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'ket-qua-tra-cuu-mst.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
    """

    return render_tool_shell(
        keyword=keyword,
        slug=slug,
        category_label="VietRegistry API",
        page_title=f"{keyword} - Tra Cứu MST & Doanh Nghiệp | VinaTools",
        meta_desc="Tra cứu mã số thuế (MST), người đại diện pháp luật, trạng thái hoạt động và địa chỉ trụ sở doanh nghiệp Việt Nam trực tiếp qua VietRegistry Serverless API.",
        meta_keywords="tra cứu mã số thuế, tìm kiếm doanh nghiệp, vietregistry api, mã số thuế công ty",
        subtitle="Tra cứu trực tiếp thông tin đăng ký doanh nghiệp theo Mã số thuế (/api/company) hoặc tìm kiếm theo tên công ty &amp; tỉnh thành (/api/search).",
        tool_html=tool_html,
        tool_js=tool_js,
        extra_head=SHARED_FINTECH_CSS,
        nav_badge="VietRegistry Live API",
    )
