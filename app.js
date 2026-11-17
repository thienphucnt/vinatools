/* ==========================================================================
   VinaEarn AI - Registry API Console Logic
   ========================================================================== */

// Shared App State
const APP_STATE = {
  activeTab: 'overview',
  bankConfig: {
    bankCode: 'techcombank',
    accountNo: 'REDACTED_SET_IN_ENV',
    accountName: 'VINATOOLS PLATFORM',
    commissionGoal: 50000000,
    autoRenew: true,
    sandboxPublic: true,
    taxAlert: true
  }
};

// Initialize app when DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  initAuth();
  initRouter();
  
  // Format current local time in Vietnam
  updateVietnamTime();
  setInterval(updateVietnamTime, 1000);
  
  // Check AdSense connection success from redirect callback
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('adsense_connected')) {
    alert("Google AdSense đã được kết nối thành công và bắt đầu đồng bộ dữ liệu doanh thu thực tế!");
    window.history.replaceState({}, document.title, window.location.pathname);
  }
});

// --------------------------------------------------------------------------
// Authentication System & Session Management
// --------------------------------------------------------------------------
function getAdminPasscode() {
  return localStorage.getItem("vinaearn_admin_passcode") || "";
}

function adminFetch(url, options = {}) {
  const passcode = getAdminPasscode();
  if (!options.headers) {
    options.headers = {};
  }
  options.headers["Authorization"] = `Bearer ${passcode}`;
  
  return fetch(url, options).then(res => {
    if (res.status === 401) {
      localStorage.removeItem("vinaearn_admin_passcode");
      const overlay = document.getElementById("login-overlay");
      if (overlay) overlay.style.display = "flex";
      const errMsg = document.getElementById("login-error");
      if (errMsg) {
        errMsg.innerText = "Phiên làm việc hết hạn hoặc mật mã sai.";
        errMsg.style.display = "block";
      }
      throw new Error("Unauthorized");
    }
    return res;
  });
}

function initAuth() {
  const overlay = document.getElementById("login-overlay");
  const form = document.getElementById("login-form");
  const passcodeField = document.getElementById("login-passcode");
  const errorEl = document.getElementById("login-error");
  const logoutBtn = document.getElementById("btn-logout");

  const storedPasscode = localStorage.getItem("vinaearn_admin_passcode");

  if (storedPasscode) {
    verifyPasscode(storedPasscode)
      .then(success => {
        if (success) {
          overlay.style.display = "none";
          initializeDashboardContent();
        } else {
          localStorage.removeItem("vinaearn_admin_passcode");
          overlay.style.display = "flex";
          if (passcodeField) passcodeField.focus();
        }
      });
  } else {
    overlay.style.display = "flex";
    if (passcodeField) passcodeField.focus();
  }

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const inputVal = passcodeField.value.trim();
      if (!inputVal) return;

      verifyPasscode(inputVal)
        .then(success => {
          if (success) {
            localStorage.setItem("vinaearn_admin_passcode", inputVal);
            overlay.style.display = "none";
            errorEl.style.display = "none";
            initializeDashboardContent();
          } else {
            errorEl.style.display = "block";
            passcodeField.value = "";
            passcodeField.focus();
          }
        });
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      localStorage.removeItem("vinaearn_admin_passcode");
      window.location.reload();
    });
  }
}

function verifyPasscode(passcode) {
  const localApiUrl = getLocalApiUrl();
  return fetch(`${localApiUrl}/api/tax-report`, {
    headers: { "Authorization": `Bearer ${passcode}` }
  })
  .then(res => {
    return res.status !== 401;
  })
  .catch(err => {
    console.warn("Auth check failed:", err);
    return false;
  });
}

function initializeDashboardContent() {
  initDashboard();
  initKeysTab();
  initSeoPages();
  initSettings();
}

// --------------------------------------------------------------------------
// Routing System
// --------------------------------------------------------------------------
function initRouter() {
  const navLinks = document.querySelectorAll(".nav-item");
  const tabContents = document.querySelectorAll(".tab-content");

  navLinks.forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetTab = link.getAttribute("data-tab");
      
      // Update active nav link
      navLinks.forEach(item => item.classList.remove("active"));
      link.classList.add("active");
      
      // Update active tab panel
      tabContents.forEach(tab => {
        tab.classList.remove("active");
        if (tab.id === `${targetTab}-tab`) {
          tab.classList.add("active");
        }
      });
      
      APP_STATE.activeTab = targetTab;

      if (targetTab === 'tax') {
        loadTaxReport();
      }
      if (targetTab === 'usage') {
        loadUsageAnalytics();
        loadLeadsList();
      }
      if (targetTab === 'support') {
        loadSupportTickets();
      }
      if (targetTab === 'feedback') {
        loadFeedbacks();
      }
    });
  });
}

function updateVietnamTime() {
  const options = {
    timeZone: 'Asia/Ho_Chi_Minh',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  };
  const formatter = new Intl.DateTimeFormat('vi-VN', options);
  const timeString = formatter.format(new Date());
  
  const vnTimeEl = document.getElementById("vietnam-time");
  if (vnTimeEl) {
    vnTimeEl.innerText = `${timeString} (ICT)`;
  }
}

// --------------------------------------------------------------------------
// Tab: Dashboard Overview
// --------------------------------------------------------------------------
function initDashboard() {
  loadOverviewStats();
}

function loadOverviewStats() {
  const localApiUrl = getLocalApiUrl();
  const banner = document.getElementById("connection-warning-banner");

  adminFetch(`${localApiUrl}/api/tax-report`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (banner) banner.style.display = "none";

      // 1. Populate stats cards
      const monthlyRevEl = document.getElementById("stat-monthly");
      const adsenseRevEl = document.getElementById("stat-adsense");
      const headroomEl = document.getElementById("stat-bot-success");
      const scrapersEl = document.getElementById("stat-scrapers");
      const headerRevEl = document.getElementById("header-real-revenue");
      const monthlyTrendEl = document.getElementById("stat-monthly-trend");

      if (monthlyRevEl) monthlyRevEl.innerText = data.vietqr_revenue.toLocaleString('vi-VN') + " đ";
      if (monthlyTrendEl) monthlyTrendEl.innerHTML = `<i class="fa-solid fa-arrow-trend-up"></i> ${data.total_transactions} đơn thành công`;
      if (adsenseRevEl) adsenseRevEl.innerText = data.adsense_revenue.toLocaleString('vi-VN') + " đ";
      
      // Toggle labels based on live AdSense status
      const statAdsenseTitle = document.getElementById("stat-adsense-title");
      const statAdsenseTrendText = document.getElementById("stat-adsense-trend-text");
      const chartLegendAdsense = document.getElementById("chart-legend-adsense");
      const breakdownAdsenseLabel = document.getElementById("breakdown-adsense-label");
      const breakdownAdsenseRowLabel = document.getElementById("breakdown-adsense-row-label");
      const breakdownClicksRowLabel = document.getElementById("breakdown-clicks-row-label");
      const breakdownViewsRowLabel = document.getElementById("breakdown-views-row-label");
      const breakdownAdsenseNote = document.getElementById("breakdown-adsense-note");

      if (data.adsense_is_live) {
        if (statAdsenseTitle) statAdsenseTitle.innerText = "Doanh Thu QC AdSense (Thực Tế Live)";
        if (statAdsenseTrendText) statAdsenseTrendText.innerText = "Đồng bộ live từ Google AdSense API";
        if (chartLegendAdsense) chartLegendAdsense.innerText = "Quảng cáo AdSense (Thực Tế)";
        if (breakdownAdsenseLabel) breakdownAdsenseLabel.innerText = "AdSense (Thực Tế)";
        if (breakdownAdsenseRowLabel) breakdownAdsenseRowLabel.innerText = "QC AdSense (Thực Tế):";
        
        if (breakdownAdsenseNote) {
          breakdownAdsenseNote.innerHTML = `<i class="fa-solid fa-circle-check" style="color: #10b981; margin-right: 4px;"></i> Đã kết nối API Google AdSense thành công. Dữ liệu hiển thị ở trên là doanh thu thực tế live.`;
        }

        // Also update settings status card if present
        const connectionStatus = document.getElementById("adsense-connection-status");
        const connectionIcon = document.getElementById("adsense-connection-icon");
        const connectBtn = document.getElementById("btn-connect-adsense");
        if (connectionStatus) {
          connectionStatus.innerHTML = `Trạng thái: <strong style="color: #10b981;">Đã kết nối thành công</strong> với Google AdSense.<br><span style="font-size: 0.75rem; color: var(--text-muted);">Mã tài khoản (Publisher ID): <strong>${data.adsense_account_id || "Đang lấy..."}</strong></span>`;
        }
        if (connectionIcon) {
          connectionIcon.style.background = "rgba(16, 185, 129, 0.1)";
          connectionIcon.style.color = "#10b981";
        }
        if (connectBtn) {
          connectBtn.innerHTML = '<i class="fa-solid fa-link-slash"></i> Hủy Kết Nối';
          connectBtn.style.background = "#ef4444";
        }
      } else if (data.adsense_token_expired) {
        if (statAdsenseTitle) statAdsenseTitle.innerText = "Doanh Thu QC AdSense (Hết Hạn/Lỗi)";
        if (statAdsenseTrendText) statAdsenseTrendText.innerText = "Kết nối Google API bị lỗi hoặc hết hạn";
        if (chartLegendAdsense) chartLegendAdsense.innerText = "Quảng cáo AdSense (Hết Hạn)";
        if (breakdownAdsenseLabel) breakdownAdsenseLabel.innerText = "AdSense (Hết Hạn)";
        if (breakdownAdsenseRowLabel) breakdownAdsenseRowLabel.innerText = "QC AdSense (Hết Hạn):";
        if (breakdownClicksRowLabel) breakdownClicksRowLabel.innerText = "Lượt click QC (Hết Hạn):";
        if (breakdownViewsRowLabel) breakdownViewsRowLabel.innerText = "Lượt view QC (Hết Hạn):";
        if (breakdownAdsenseNote) {
          breakdownAdsenseNote.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: #f87171; margin-right: 4px;"></i> <strong>Kết nối Google AdSense đã hết hạn hoặc bị lỗi.</strong> Vui lòng đi tới phần <a href="#" onclick="showTab('settings-tab')" style="color: #38bdf8; text-decoration: underline; font-weight: bold;">Cài đặt</a> và nhấn <strong>Kết Nối Ngay</strong> để cấp quyền lại.`;
        }
        
        // Update settings status if elements exist
        const connectionStatus = document.getElementById("adsense-connection-status");
        const connectionIcon = document.getElementById("adsense-connection-icon");
        const connectBtn = document.getElementById("btn-connect-adsense");
        if (connectionStatus) {
          connectionStatus.innerHTML = `Trạng thái: <strong style="color: #f87171;">Kết nối đã hết hạn hoặc bị lỗi</strong>.<br><span style="font-size: 0.75rem; color: var(--text-muted);">Vui lòng nhấn nút bên phải để thực hiện cấp quyền lại bằng tài khoản Google.</span>`;
        }
        if (connectionIcon) {
          connectionIcon.style.background = "rgba(239, 68, 68, 0.1)";
          connectionIcon.style.color = "#ef4444";
        }
        if (connectBtn) {
          connectBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> Cấp Quyền Lại';
          connectBtn.style.background = "var(--accent-secondary)";
          connectBtn.onclick = () => {
            const clientId = document.getElementById("settings-google-client-id").value.trim();
            const clientSecret = document.getElementById("settings-google-client-secret").value.trim();
            if (!clientId || !clientSecret) {
              alert("Vui lòng nhập đầy đủ Google Client ID và Client Secret ở trên rồi bấm lưu lại trước!");
              return;
            }
            window.location.href = `${getLocalApiUrl()}/api/auth/google?redirect_origin=${encodeURIComponent(window.location.origin)}`;
          };
        }
      } else {
        if (statAdsenseTitle) statAdsenseTitle.innerText = "Doanh Thu QC AdSense (Ước Tính Dự Kiến)";
        if (statAdsenseTrendText) statAdsenseTrendText.innerText = "Ước tính từ SEO Search Volume";
        if (chartLegendAdsense) chartLegendAdsense.innerText = "Quảng cáo AdSense (Ước Tính)";
        if (breakdownAdsenseLabel) breakdownAdsenseLabel.innerText = "AdSense (Ước Tính)";
        if (breakdownAdsenseRowLabel) breakdownAdsenseRowLabel.innerText = "QC AdSense (Ước Tính):";
        if (breakdownClicksRowLabel) breakdownClicksRowLabel.innerText = "Lượt click QC (Ước Tính):";
        if (breakdownViewsRowLabel) breakdownViewsRowLabel.innerText = "Lượt view QC (Ước Tính):";
        if (breakdownAdsenseNote) {
          breakdownAdsenseNote.innerHTML = `<i class="fa-solid fa-circle-info" style="margin-right: 4px;"></i> Doanh thu thực tế nhận từ Google AdSense hiện tại là <strong>$0.00 (0 đ)</strong> do website mới triển khai chưa có lượt truy cập thực tế ổn định từ Google. Số liệu hiển thị ở trên là <strong>ước tính tiềm năng thu nhập</strong> dựa trên lượt tìm kiếm từ khóa (Search Volume) của các công cụ SEO đã deploy.`;
        }
      }

      if (headroomEl) headroomEl.innerText = data.remaining_headroom.toLocaleString('vi-VN') + " đ";
      if (scrapersEl) scrapersEl.innerText = data.total_tools_deployed;
      if (headerRevEl) headerRevEl.innerText = data.total_revenue.toLocaleString('vi-VN') + " đ";

      // 2. Populate Activity Log with actual actions
      renderRealActivities(data.transactions, data.tools);

      // 3. Render dynamic weekly revenue chart
      renderRealWeeklyChart(data.transactions, data.adsense_by_day);
      
      // 3.1 Update Revenue Breakdown Card
      const breakdownVietqrVal = document.getElementById("breakdown-vietqr-val");
      const breakdownAdsenseVal = document.getElementById("breakdown-adsense-val");
      const breakdownClicksVal = document.getElementById("breakdown-clicks-val");
      const breakdownViewsVal = document.getElementById("breakdown-views-val");
      
      const breakdownBarVietqr = document.getElementById("breakdown-bar-vietqr");
      const breakdownBarAdsense = document.getElementById("breakdown-bar-adsense");
      
      const breakdownVietqrPct = document.getElementById("breakdown-vietqr-pct");
      const breakdownAdsensePct = document.getElementById("breakdown-adsense-pct");

      const totalRev = data.total_revenue || 1;
      const vietqrPctVal = Math.round((data.vietqr_revenue / totalRev) * 100);
      const adsensePctVal = 100 - vietqrPctVal;

      if (breakdownVietqrVal) breakdownVietqrVal.innerText = (data.vietqr_revenue || 0).toLocaleString('vi-VN') + " đ";
      if (breakdownAdsenseVal) breakdownAdsenseVal.innerText = (data.adsense_revenue || 0).toLocaleString('vi-VN') + " đ";
      if (breakdownClicksVal) breakdownClicksVal.innerText = (data.adsense_clicks || 0).toLocaleString('vi-VN');
      if (breakdownViewsVal) breakdownViewsVal.innerText = (data.adsense_views || 0).toLocaleString('vi-VN');

      if (breakdownBarVietqr) breakdownBarVietqr.style.width = `${vietqrPctVal}%`;
      if (breakdownBarAdsense) breakdownBarAdsense.style.width = `${adsensePctVal}%`;

      if (breakdownVietqrPct) breakdownVietqrPct.innerText = `${vietqrPctVal}%`;
      if (breakdownAdsensePct) breakdownAdsensePct.innerText = `${adsensePctVal}%`;
      
      // 4. Update keys list table
      loadKeysList(data.transactions);
      
      // 5. Update SEO pages
      renderSeoPages(data.tools);
      
      // Update chart timestamp
      const chartTimeEl = document.getElementById("chart-update-time");
      if (chartTimeEl) {
        chartTimeEl.innerText = `Cập nhật lúc: ${new Date().toLocaleTimeString('vi-VN')}`;
      }

      // Fetch total API usage to populate the sidebar footer stat
      adminFetch(`${localApiUrl}/api/usage`)
        .then(res => res.json())
        .then(usageData => {
          const footerCountEl = document.getElementById("footer-actions-count");
          if (footerCountEl) {
            footerCountEl.innerText = (usageData.total_requests || 0).toLocaleString('vi-VN');
          }
        })
        .catch(err => {
          console.warn("Could not load usage for footer:", err);
          const footerCountEl = document.getElementById("footer-actions-count");
          if (footerCountEl) footerCountEl.innerText = "Offline";
        });
    })
    .catch(err => {
      console.warn("Could not load dynamic overview stats:", err);
      if (banner) banner.style.display = "flex";
      renderMockStats();

      // Set fallback message for activity list and weekly chart
      const activityList = document.getElementById("activity-list");
      if (activityList) {
        activityList.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;"><i class="fa-solid fa-circle-exclamation" style="color:#ef4444; margin-right:8px;"></i> Mất kết nối tới Local Webhook Gateway. Hoạt động của Agent không khả dụng.</div>';
      }
      const chartContainer = document.getElementById("overview-chart-container");
      if (chartContainer) {
        chartContainer.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:40px; width:100%;">Mất kết nối tới Local Webhook Gateway. Biểu đồ doanh thu không khả dụng.</div>';
      }
      const footerCountEl = document.getElementById("footer-actions-count");
      if (footerCountEl) footerCountEl.innerText = "Offline";
    });
}

function renderMockStats() {
  const monthlyRevEl = document.getElementById("stat-monthly");
  if (monthlyRevEl) monthlyRevEl.innerText = "0 đ";
  const adsenseRevEl = document.getElementById("stat-adsense");
  if (adsenseRevEl) adsenseRevEl.innerText = "0 đ";
  const headroomEl = document.getElementById("stat-bot-success");
  if (headroomEl) headroomEl.innerText = "1,000,000,000 đ";
}

function renderRealActivities(transactions, tools) {
  const activityList = document.getElementById("activity-list");
  if (!activityList) return;

  const listItems = [];

  // Add payments
  (transactions || []).forEach(tx => {
    if (tx.status === "completed") {
      const actClass = tx.is_test ? 'info' : 'success';
      const prefix = tx.is_test ? '[TEST] ' : '';
      listItems.push({
        icon: 'fa-money-bill-trend-up',
        class: actClass,
        desc: `${prefix}Giao dịch hoàn tất! Nội dung: ${tx.memo}. Nhận: +${tx.amount.toLocaleString('vi-VN')} đ`,
        timestamp: new Date(tx.timestamp.replace(" ", "T")).getTime(),
        timeStr: new Date(tx.timestamp.replace(" ", "T")).toLocaleString('vi-VN')
      });
    }
  });

  // Add tools deployed
  (tools || []).forEach(tool => {
    listItems.push({
      icon: 'fa-share-nodes',
      class: 'info',
      desc: `Đã deploy SEO Tool cho từ khóa: "${tool.keyword}" (Volume: ${tool.estimated_volume})`,
      timestamp: new Date(tool.deployed_at).getTime(),
      timeStr: new Date(tool.deployed_at).toLocaleString('vi-VN')
    });
  });

  // Sort by timestamp descending
  listItems.sort((a, b) => b.timestamp - a.timestamp);

  // Take top 8
  const displayItems = listItems.slice(0, 8);

  activityList.innerHTML = '';
  if (displayItems.length === 0) {
    activityList.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Không có hoạt động nào được ghi nhận.</div>';
    return;
  }

  displayItems.forEach(act => {
    const item = document.createElement("div");
    item.className = `activity-item ${act.class}`;
    item.innerHTML = `
      <div class="activity-icon">
        <i class="fa-solid ${act.icon}"></i>
      </div>
      <div class="activity-details">
        <span class="activity-desc">${act.desc}</span>
        <span class="activity-time">${act.timeStr}</span>
      </div>
    `;
    activityList.appendChild(item);
  });
}

function renderRealWeeklyChart(transactions, adsenseByDay) {
  const chartContainer = document.getElementById("overview-chart-container");
  if (!chartContainer) return;

  const dayNames = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"];
  const daySums = [0, 0, 0, 0, 0, 0, 0];
  const adsenseSums = adsenseByDay || [0, 0, 0, 0, 0, 0, 0];

  (transactions || []).forEach(tx => {
    if (tx.status === "completed" && !tx.is_test) {
      const dt = new Date(tx.timestamp.replace(" ", "T"));
      const day = dt.getDay(); // 0 is Sunday, 1 is Monday
      let index = 0;
      if (day === 0) {
        index = 6; // Sunday
      } else {
        index = day - 1; // Monday to Saturday
      }
      daySums[index] += tx.amount;
    }
  });

  const totalSums = daySums.map((val, idx) => val + adsenseSums[idx]);
  const maxVal = Math.max(...totalSums);
  
  chartContainer.innerHTML = '';
  dayNames.forEach((name, idx) => {
    const vietqrSum = daySums[idx];
    const adsenseSum = adsenseSums[idx];
    const totalSum = vietqrSum + adsenseSum;
    
    const totalPct = maxVal > 0 ? (totalSum / maxVal) * 90 + 5 : 5; // min 5% height
    
    // Proportional inner heights (should add to 100%)
    const adsenseInnerPct = totalSum > 0 ? (adsenseSum / totalSum) * 100 : 0;
    const vietqrInnerPct = totalSum > 0 ? (vietqrSum / totalSum) * 100 : 0;
    
    let formattedVal = '0 đ';
    if (totalSum > 0) {
      formattedVal = (totalSum >= 1000 ? (totalSum/1000).toFixed(0) + 'k' : totalSum) + ' đ';
    }
    
    const barWrapper = document.createElement("div");
    barWrapper.className = "chart-bar-wrapper";
    
    const tooltipText = `Tổng: ${totalSum.toLocaleString('vi-VN')} đ (VIP: ${vietqrSum.toLocaleString('vi-VN')} đ, Ads: ${adsenseSum.toLocaleString('vi-VN')} đ)`;
    
    barWrapper.innerHTML = `
      <div class="chart-bar" style="height: ${totalPct}%; display: flex; flex-direction: column-reverse;" title="${tooltipText}">
        <div class="chart-bar-segment" style="height: ${adsenseInnerPct}%; background: var(--accent-secondary); border-radius: ${vietqrInnerPct > 0 ? '0' : '4px 4px 0 0'}; transition: height 0.5s ease;"></div>
        <div class="chart-bar-segment" style="height: ${vietqrInnerPct}%; background: var(--accent-primary); border-radius: 4px 4px 0 0; transition: height 0.5s ease;"></div>
        <span class="chart-bar-value">${formattedVal}</span>
      </div>
      <span class="chart-label">${name}</span>
    `;
    chartContainer.appendChild(barWrapper);
  });
}

// --------------------------------------------------------------------------
// Tab: API Keys Management
// --------------------------------------------------------------------------
function initKeysTab() {
  const form = document.getElementById("manual-key-form");
  if (!form) return;
  
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const memo = document.getElementById("manual-key-memo").value.trim();
    const amount = document.getElementById("manual-key-amount").value.trim();
    const duration = document.getElementById("manual-key-duration").value;
    
    const localApiUrl = getLocalApiUrl();
    
    // Call simulation endpoint to generate custom manual key
    adminFetch(`${localApiUrl}/api/simulate-payment?memo=${encodeURIComponent(memo)}&amount=${amount}&duration=${duration}`)
      .then(res => res.json())
      .then(data => {
        if (data.status === "success" && data.apiKey) {
          const resultWrapper = document.getElementById("manual-key-result-wrapper");
          const outputEl = document.getElementById("manual-key-output");
          if (resultWrapper && outputEl) {
            outputEl.value = data.apiKey;
            resultWrapper.style.display = "block";
          }
          // Refresh statistics and keys table
          loadOverviewStats();
        } else {
          alert("Lỗi khi tạo khóa: " + (data.error || "Không xác định"));
        }
      })
      .catch(err => {
        console.error(err);
        alert("Không thể kết nối đến Webhook local. Vui lòng kiểm tra cấu hình trong System Settings.");
      });
  });

  // Wire manual key generator copy button
  const copyBtn = document.getElementById("manual-key-copy-btn");
  if (copyBtn) {
    copyBtn.onclick = () => {
      const outputEl = document.getElementById("manual-key-output");
      if (outputEl && outputEl.value) {
        navigator.clipboard.writeText(outputEl.value).then(() => {
          const status = document.getElementById("manual-key-copy-status");
          if (status) {
            status.style.display = "block";
            setTimeout(() => {
              status.style.display = "none";
            }, 2000);
          }
        });
      }
    };
  }
}

function loadKeysList(transactions) {
  const tbody = document.getElementById("keys-list-tbody");
  if (!tbody) return;
  
  const completedTx = (transactions || []).filter(tx => tx.status === "completed" && tx.apiKey);
  
  if (completedTx.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4" style="text-align:center; padding: 30px 0; color:var(--text-muted);">
          Chưa có khóa API nào hoạt động.
        </td>
      </tr>
    `;
    return;
  }
  
  tbody.innerHTML = "";
  completedTx.forEach(tx => {
    const parts = tx.apiKey.split('.');
    let expiryStr = "Lifetime";
    if (parts.length >= 3) {
      const expVal = parseInt(parts[2]);
      if (expVal > 0) {
        expiryStr = new Date(expVal * 1000).toLocaleDateString('vi-VN');
      }
    }
    const regDate = new Date(tx.timestamp.replace(" ", "T")).toLocaleDateString('vi-VN');
    
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="padding:12px; border-bottom:1px solid var(--border-glass); color:white; font-weight:bold;">${tx.memo}</td>
      <td style="padding:12px; border-bottom:1px solid var(--border-glass); color:var(--text-secondary);">${regDate}</td>
      <td style="padding:12px; border-bottom:1px solid var(--border-glass); color:var(--text-secondary);">${expiryStr}</td>
      <td style="padding:12px; border-bottom:1px solid var(--border-glass); font-family:monospace; display:flex; align-items:center; gap:8px;">
        <input type="text" readonly value="${tx.apiKey}" style="background:rgba(0,0,0,0.2); border:1px solid var(--border-glass); padding:4px 8px; border-radius:4px; color:#fff; font-family:monospace; font-size:0.8rem; width:180px;">
        <button class="btn btn-secondary copy-key-btn" data-key="${tx.apiKey}" style="padding:4px 8px; font-size:0.75rem;"><i class="fa-solid fa-copy"></i> Copy</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Wire copy buttons in keys table
  tbody.querySelectorAll(".copy-key-btn").forEach(btn => {
    btn.onclick = () => {
      const key = btn.getAttribute("data-key");
      navigator.clipboard.writeText(key).then(() => {
        const origHtml = btn.innerHTML;
        btn.innerHTML = `<i class="fa-solid fa-check"></i>`;
        setTimeout(() => {
          btn.innerHTML = origHtml;
        }, 1500);
      });
    };
  });
}

// --------------------------------------------------------------------------
// Tab: SEO Landing Pages
// --------------------------------------------------------------------------
function initSeoPages() {
  const localApiUrl = getLocalApiUrl();

  adminFetch(`${localApiUrl}/api/tax-report`)
    .then(res => res.json())
    .then(data => {
      renderSeoPages(data.tools);
    })
    .catch(err => {
      console.warn("Failed to load SEO pages, rendering mock content:", err);
      renderSeoPages([]);
    });
}

function renderSeoPages(tools) {
  const grid = document.getElementById("seo-pages-grid");
  if (!grid) return;
  
  if (!tools || tools.length === 0) {
    grid.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px; grid-column:1/-1;">Không có SEO Tools nào được deploy hoặc server offline.</div>';
    return;
  }
  
  grid.innerHTML = "";
  tools.forEach(tool => {
    const card = document.createElement("div");
    card.className = "glass-panel glass-panel-interactive";
    card.style.padding = "20px";
    card.style.display = "flex";
    card.style.flexDirection = "column";
    card.style.justifyContent = "space-between";
    card.style.height = "100%";
    
    const dateStr = new Date(tool.deployed_at).toLocaleDateString('vi-VN');
    
    card.innerHTML = `
      <div style="flex-grow: 1;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
          <span class="product-badge" style="background: rgba(20, 184, 166, 0.1); color: var(--accent-secondary); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase;">SEO Tool</span>
          <span style="font-size: 0.8rem; color: var(--text-muted);"><i class="fa-solid fa-calendar-days"></i> ${dateStr}</span>
        </div>
        <h4 style="color: white; margin-bottom: 12px; font-size: 1.1rem; line-height: 1.4;">${tool.keyword}</h4>
        
        <div style="display: flex; gap: 16px; margin-bottom: 16px;">
          <div>
            <span style="font-size: 0.75rem; color: var(--text-muted); display: block;">Search Volume</span>
            <span style="color: white; font-weight: bold; font-size: 0.95rem;">${tool.estimated_volume} / thg</span>
          </div>
          <div>
            <span style="font-size: 0.75rem; color: var(--text-muted); display: block;">Niche Score</span>
            <span style="color: #10b981; font-weight: bold; font-size: 0.95rem;">${tool.niche_score}/100</span>
          </div>
        </div>
      </div>
      
      <a href="${tool.url}" target="_blank" class="btn" style="text-decoration: none; text-align: center; display: block; font-size: 0.85rem; padding: 8px 12px; margin-top: auto;">
        <i class="fa-solid fa-up-right-from-square"></i> Xem Landing Page
      </a>
    `;
    grid.appendChild(card);
  });
}

// --------------------------------------------------------------------------
// Tab: Settings
// --------------------------------------------------------------------------
function initSettings() {
  const form = document.getElementById("settings-form");
  if (!form) return;
  
  // Load localApiUrl from localStorage
  const localApiUrlField = document.getElementById("settings-local-api-url");
  if (localApiUrlField) {
    localApiUrlField.value = getLocalApiUrl();
  }
  
  // Fetch current config from backend API
  const localApiUrl = getLocalApiUrl();
  adminFetch(`${localApiUrl}/api/settings`)
    .then(res => {
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return res.json();
    })
    .then(config => {
      // Set settings fields from loaded backend config
      document.getElementById("settings-bank-select").value = (config.bank_name || "techcombank").toLowerCase();
      document.getElementById("settings-account-no").value = config.bank_account || "";
      document.getElementById("settings-account-name").value = config.bank_account_holder || "";
      document.getElementById("settings-commission-goal").value = config.commission_goal || 50000000;
      document.getElementById("settings-adsense-client").value = config.google_adsense_client || "ca-pub-mock";
      document.getElementById("settings-admin-passcode").value = config.admin_passcode || "VinaAdmin@2026Secure";
      
      // Load Google OAuth details
      document.getElementById("settings-google-client-id").value = config.google_oauth_client_id || "";
      document.getElementById("settings-google-client-secret").value = config.google_oauth_client_secret || "";
      
      // Update AdSense Connection Status
      updateAdSenseConnectionStatus(config);
      
      // Update APP_STATE memory
      APP_STATE.bankConfig.bankCode = (config.bank_name || "techcombank").toLowerCase();
      APP_STATE.bankConfig.accountNo = config.bank_account || "";
      APP_STATE.bankConfig.accountName = config.bank_account_holder || "";
      APP_STATE.bankConfig.commissionGoal = config.commission_goal || 50000000;
      
      loadOverviewStats();
    })
    .catch(err => {
      console.error("Failed to load backend settings:", err);
      // Fallback to initial APP_STATE if API fails
      document.getElementById("settings-bank-select").value = APP_STATE.bankConfig.bankCode;
      document.getElementById("settings-account-no").value = APP_STATE.bankConfig.accountNo;
      document.getElementById("settings-account-name").value = APP_STATE.bankConfig.accountName;
      document.getElementById("settings-commission-goal").value = APP_STATE.bankConfig.commissionGoal;
      // CRITICAL: Still wire up the AdSense button even when API is offline
      // Use a stub config — if user previously connected, they can still click Connect
      // The status will show "not connected" honestly since we can't verify
      const connectionStatus = document.getElementById("adsense-connection-status");
      if (connectionStatus) {
        connectionStatus.innerHTML = `Trạng thái: <strong style="color: #f87171;">Không thể tải trạng thái</strong> (Webhook API ngoại tuyến).<br><span style="font-size: 0.75rem; color: var(--text-muted);">Mạng đang cố kết nối lại. Bạn vẫn có thể nhấn nút bên phải để khởi tạo OAuth.</span>`;
      }
      // Wire up the button anyway so it's not a dead element
      updateAdSenseConnectionStatus({});
    });
  
  // Google client_secret.json upload handler
  const jsonUploadInput = document.getElementById("settings-google-json-upload");
  if (jsonUploadInput) {
    jsonUploadInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (!file) return;
      
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const credentials = JSON.parse(event.target.result);
          const config = credentials.web || credentials.installed;
          if (config && config.client_id && config.client_secret) {
            document.getElementById("settings-google-client-id").value = config.client_id;
            document.getElementById("settings-google-client-secret").value = config.client_secret;
            alert("Đã tự động tải cấu hình Client ID và Client Secret từ tệp JSON thành công! Hãy bấm 'Lưu cấu hình' bên dưới để hoàn tất.");
          } else {
            alert("Tệp JSON không đúng định dạng thông tin xác thực Google OAuth 2.0 (thiếu trường 'web' hoặc 'installed').");
          }
        } catch (err) {
          alert("Lỗi khi đọc tệp JSON: " + err.message);
        }
      };
      reader.readAsText(file);
    });
  }

  // Toggles
  document.getElementById("settings-auto-renew").checked = APP_STATE.bankConfig.autoRenew;
  document.getElementById("settings-sandbox-public").checked = APP_STATE.bankConfig.sandboxPublic;
  document.getElementById("settings-tax-alert").checked = APP_STATE.bankConfig.taxAlert;
  
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    
    const bankSelect = document.getElementById("settings-bank-select");
    const bankName = bankSelect.value;
    const bankAccount = document.getElementById("settings-account-no").value.trim();
    const bankAccountHolder = document.getElementById("settings-account-name").value.trim().toUpperCase();
    const commissionGoal = parseInt(document.getElementById("settings-commission-goal").value);
    const adsenseClient = document.getElementById("settings-adsense-client").value.trim();
    const adminPasscode = document.getElementById("settings-admin-passcode").value.trim();
    const googleClientId = document.getElementById("settings-google-client-id").value.trim();
    const googleClientSecret = document.getElementById("settings-google-client-secret").value.trim();
    
    // Update local variables
    APP_STATE.bankConfig.bankCode = bankSelect.value;
    APP_STATE.bankConfig.accountNo = bankAccount;
    APP_STATE.bankConfig.accountName = bankAccountHolder;
    APP_STATE.bankConfig.commissionGoal = commissionGoal;
    
    APP_STATE.bankConfig.autoRenew = document.getElementById("settings-auto-renew").checked;
    APP_STATE.bankConfig.sandboxPublic = document.getElementById("settings-sandbox-public").checked;
    APP_STATE.bankConfig.taxAlert = document.getElementById("settings-tax-alert").checked;
    
    if (localApiUrlField) {
      localStorage.setItem("localApiUrl", localApiUrlField.value.trim());
    }
    
    // Sync to uppercase for name
    document.getElementById("settings-account-name").value = bankAccountHolder;
    
    // Send to backend API
    const savePayload = {
      bank_name: bankName,
      bank_account: bankAccount,
      bank_account_holder: bankAccountHolder,
      commission_goal: commissionGoal,
      google_adsense_client: adsenseClient,
      admin_passcode: adminPasscode,
      google_oauth_client_id: googleClientId,
      google_oauth_client_secret: googleClientSecret
    };
    
    const saveUrl = `${getLocalApiUrl()}/api/settings`;
    
    // Show loading indicator or update passcode in localstorage if updated
    if (adminPasscode !== localStorage.getItem("vinaearn_admin_passcode")) {
      localStorage.setItem("vinaearn_admin_passcode", adminPasscode);
    }
    
    adminFetch(saveUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(savePayload)
    })
    .then(res => {
      alert(res.message || "Cấu hình cài đặt đã được lưu thành công!");
      // Refresh stats
      loadOverviewStats();
    })
    .catch(err => {
      alert("Lỗi khi lưu cấu hình lên máy chủ: " + err.message);
    });
  });
}

function updateAdSenseConnectionStatus(config) {
  const connectionStatus = document.getElementById("adsense-connection-status");
  const connectionIcon = document.getElementById("adsense-connection-icon");
  const connectBtn = document.getElementById("btn-connect-adsense");
  if (!connectBtn) return;
  
  if (config.google_adsense_refresh_token) {
    if (connectionStatus) connectionStatus.innerHTML = `Trạng thái: <strong style="color: #10b981;">Đã kết nối thành công</strong> với Google AdSense.<br><span style="font-size: 0.75rem; color: var(--text-muted);">Mã tài khoản (Publisher ID): <strong>${config.google_adsense_account_id || config.google_adsense_client || "Đang lấy..."}</strong></span>`;
    if (connectionIcon) {
      connectionIcon.style.background = "rgba(16, 185, 129, 0.1)";
      connectionIcon.style.color = "#10b981";
    }
    connectBtn.innerHTML = '<i class="fa-solid fa-link-slash"></i> Hủy Kết Nối';
    connectBtn.style.background = "#ef4444";
    connectBtn.onclick = () => {
      if (confirm("Bạn có chắc chắn muốn ngắt kết nối tài khoản Google AdSense khỏi Dashboard?")) {
        const passcode = localStorage.getItem("vinaearn_admin_passcode") || "VinaAdmin@2026Secure";
        const localApiUrl = getLocalApiUrl();
        fetch(`${localApiUrl}/api/settings`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${passcode}`
          },
          body: JSON.stringify({ disconnect_adsense: true })
        })
        .then(res => res.json())
        .then(data => {
          alert("Đã ngắt kết nối Google AdSense!");
          location.reload();
        })
        .catch(err => alert("Lỗi khi ngắt kết nối: " + err));
      }
    };
  } else {
    if (connectionStatus) connectionStatus.innerText = "Trạng thái: Chưa kết nối tài khoản. Vui lòng nhập thông tin Client ID & Secret ở trên, lưu lại rồi bấm kết nối.";
    if (connectionIcon) {
      connectionIcon.style.background = "rgba(239, 68, 68, 0.1)";
      connectionIcon.style.color = "#ef4444";
    }
    connectBtn.innerHTML = '<i class="fa-solid fa-link"></i> Kết Nối Ngay';
    connectBtn.style.background = "var(--accent-secondary)";
    connectBtn.onclick = () => {
      const clientId = document.getElementById("settings-google-client-id").value.trim();
      const clientSecret = document.getElementById("settings-google-client-secret").value.trim();
      if (!clientId || !clientSecret) {
        alert("Vui lòng nhập đầy đủ Google Client ID và Client Secret ở trên rồi bấm lưu lại trước!");
        return;
      }
      window.location.href = `${getLocalApiUrl()}/api/auth/google?redirect_origin=${encodeURIComponent(window.location.origin)}`;
    };
  }
}

// --------------------------------------------------------------------------
// Tab: Tax Assistant & local webhook reports
// --------------------------------------------------------------------------
function loadTaxReport() {
  const localApiUrl = getLocalApiUrl();

  const tbody = document.getElementById("tax-transactions-tbody");
  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4" style="text-align:center; padding: 30px 0; color:var(--text-muted);">
          <i class="fa-solid fa-circle-notch fa-spin" style="margin-right:8px;"></i> Đang tải dữ liệu từ ${localApiUrl}...
        </td>
      </tr>
    `;
  }

  adminFetch(`${localApiUrl}/api/tax-report`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error ${response.status}`);
      return response.json();
    })
    .then(data => {
      // 1. Populate stats cards
      const totalRevenueEl = document.getElementById("tax-total-revenue");
      const txCountEl = document.getElementById("tax-total-tx-count");
      const remainingHeadroomEl = document.getElementById("tax-remaining-headroom");
      const exemptionStatusEl = document.getElementById("tax-exemption-status");
      
      if (totalRevenueEl) totalRevenueEl.innerText = data.total_revenue.toLocaleString('vi-VN') + " đ";
      if (txCountEl) txCountEl.innerText = `VietQR: ${data.vietqr_revenue.toLocaleString('vi-VN')} đ | AdSense: ${data.adsense_revenue.toLocaleString('vi-VN')} đ`;
      if (remainingHeadroomEl) remainingHeadroomEl.innerText = data.remaining_headroom.toLocaleString('vi-VN') + " đ";
      
      if (exemptionStatusEl) {
        if (data.is_exempt) {
          exemptionStatusEl.innerText = "Được miễn thuế hoàn toàn (< 1 Tỷ VND)";
          exemptionStatusEl.style.color = "#10b981";
        } else {
          exemptionStatusEl.innerText = "Vượt hạn mức, phát sinh nghĩa vụ thuế";
          exemptionStatusEl.style.color = "#ef4444";
        }
      }
      
      // 2. Exemption Progress bar
      const progressTextEl = document.getElementById("tax-progress-text");
      const progressBarEl = document.getElementById("tax-progress-bar");
      
      const percent = Math.min(100, (data.total_revenue / data.exempt_limit) * 100).toFixed(2);
      if (progressTextEl) {
        progressTextEl.innerText = `${percent}% (${data.total_revenue.toLocaleString('vi-VN')} đ / ${data.exempt_limit.toLocaleString('vi-VN')} đ)`;
      }
      if (progressBarEl) {
        progressBarEl.style.width = `${percent}%`;
      }
      
      // 3. Indicators
      const ind27 = document.getElementById("tax-indicator-27");
      const ind28 = document.getElementById("tax-indicator-28");
      const ind33 = document.getElementById("tax-indicator-33");
      const ind34 = document.getElementById("tax-indicator-34");
      
      if (ind27) ind27.innerText = data.total_revenue.toLocaleString('vi-VN') + " đ";
      if (ind28) ind28.innerText = data.total_revenue.toLocaleString('vi-VN') + " đ";
      if (ind33) ind33.innerText = data.etax_vat_due.toLocaleString('vi-VN') + " đ";
      if (ind34) ind34.innerText = data.etax_pit_due.toLocaleString('vi-VN') + " đ";
      
      // Wire indicators Copy buttons
      setupIndicatorCopy("tax-copy-27", data.total_revenue);
      setupIndicatorCopy("tax-copy-28", data.total_revenue);
      setupIndicatorCopy("tax-copy-33", data.etax_vat_due);
      setupIndicatorCopy("tax-copy-34", data.etax_pit_due);
      
      // 4. Transaction log table
      if (tbody) {
        if (data.transactions.length === 0) {
          tbody.innerHTML = `
            <tr>
              <td colspan="4" style="text-align:center; padding: 30px 0; color:var(--text-muted);">
                Chưa ghi nhận giao dịch nào.
              </td>
            </tr>
          `;
        } else {
          tbody.innerHTML = '';
          data.transactions.forEach(tx => {
            const tr = document.createElement("tr");
            const badgeStyle = tx.is_test 
              ? "background:rgba(245,158,11,0.1); color:#f59e0b;" 
              : "background:rgba(16,185,129,0.1); color:#10b981;";
            const badgeText = tx.is_test ? "TEST" : tx.status.toUpperCase();
            
            tr.innerHTML = `
              <td style="padding:12px; border-bottom:1px solid var(--border-glass);">${new Date(tx.timestamp.replace(" ", "T")).toLocaleString('vi-VN')}</td>
              <td style="padding:12px; border-bottom:1px solid var(--border-glass); font-family:monospace; color:var(--accent-secondary); font-weight:bold;">${tx.memo}</td>
              <td style="padding:12px; border-bottom:1px solid var(--border-glass); color:white; font-weight:bold;">${tx.amount.toLocaleString('vi-VN')} đ</td>
              <td style="padding:12px; border-bottom:1px solid var(--border-glass);"><span style="${badgeStyle} padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:bold;">${badgeText}</span></td>
            `;
            tbody.appendChild(tr);
          });
        }
      }
    })
    .catch(err => {
      console.error("Failed to load tax report:", err);
      if (tbody) {
        tbody.innerHTML = `
          <tr>
            <td colspan="4" style="text-align:center; padding: 30px 0; color:var(--error); font-weight:bold;">
              <i class="fa-solid fa-triangle-exclamation" style="color: #ef4444; margin-right:8px;"></i> Không thể kết nối với Webhook API địa phương.<br>
              <span style="font-size:0.8rem; font-weight:normal; color:var(--text-secondary); display:block; margin-top:8px;">Hãy kiểm tra xem server python ở local và tunnel đã chạy chưa, hoặc cập nhật Local Gateway URL ở System Settings.</span>
            </td>
          </tr>
        `;
      }
    });
}

function setupIndicatorCopy(btnId, val) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.onclick = () => {
    navigator.clipboard.writeText(val.toString()).then(() => {
      const origHtml = btn.innerHTML;
      btn.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
      setTimeout(() => {
        btn.innerHTML = origHtml;
      }, 2000);
    });
  };
}

// --------------------------------------------------------------------------
// Tab: API Usage Analytics
// --------------------------------------------------------------------------
const ACTIVE_TUNNEL_URL = "";

function getLocalApiUrl() {
  const localApiUrlField = document.getElementById("settings-local-api-url");
  const isProduction = window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1" && window.location.protocol !== "file:";
  
  if (isProduction) {
    const configuredUrl = ACTIVE_TUNNEL_URL || localStorage.getItem("localApiUrl") || window.location.origin;
    if (localApiUrlField) localApiUrlField.value = configuredUrl;
    return configuredUrl.replace(/\/$/, "");
  }
  
  // In dev, use localhost or whatever is saved
  let localApiUrl = (localApiUrlField ? localApiUrlField.value.trim() : "") || localStorage.getItem("localApiUrl") || "http://localhost:8085";
  if (localApiUrl.endsWith("/")) localApiUrl = localApiUrl.slice(0, -1);
  return localApiUrl;
}

function loadUsageAnalytics() {
  const localApiUrl = getLocalApiUrl();

  adminFetch(`${localApiUrl}/api/usage`)
    .then(res => res.json())
    .then(data => {
      // Stats cards
      const totalEl = document.getElementById("usage-total-requests");
      const h24El = document.getElementById("usage-24h-requests");
      const d7El = document.getElementById("usage-7d-requests");
      
      if (totalEl) totalEl.innerText = (data.total_requests || 0).toLocaleString('vi-VN');
      if (h24El) h24El.innerText = (data.requests_24h || 0).toLocaleString('vi-VN');
      if (d7El) d7El.innerText = (data.requests_7d || 0).toLocaleString('vi-VN');

      // Top endpoints bar chart
      const chartContainer = document.getElementById("usage-endpoints-chart");
      if (chartContainer) {
        const endpoints = data.top_endpoints || [];
        if (endpoints.length === 0) {
          chartContainer.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">No API usage recorded yet.</div>';
        } else {
          const maxCount = Math.max(...endpoints.map(e => e.count));
          chartContainer.innerHTML = '';
          endpoints.forEach(ep => {
            const pct = maxCount > 0 ? (ep.count / maxCount) * 100 : 0;
            const bar = document.createElement('div');
            bar.style.cssText = 'display: flex; align-items: center; gap: 12px;';
            bar.innerHTML = `
              <span style="font-family: monospace; color: var(--accent-secondary); font-weight: bold; min-width: 140px; font-size: 0.85rem;">${ep.endpoint}</span>
              <div style="flex: 1; height: 24px; background: rgba(255,255,255,0.03); border-radius: 4px; overflow: hidden; border: 1px solid var(--border-glass);">
                <div style="width: ${pct}%; height: 100%; background: linear-gradient(90deg, var(--accent-secondary), var(--accent-primary)); border-radius: 4px; transition: width 0.5s ease;"></div>
              </div>
              <span style="color: white; font-weight: bold; min-width: 50px; text-align: right; font-size: 0.9rem;">${ep.count.toLocaleString()}</span>
            `;
            chartContainer.appendChild(bar);
          });
        }
      }

      // Per-key usage table
      const tbody = document.getElementById("usage-keys-tbody");
      if (tbody) {
        const keys = data.keys || [];
        if (keys.length === 0) {
          tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding: 30px 0; color:var(--text-muted);">No API key usage recorded yet.</td></tr>';
        } else {
          tbody.innerHTML = '';
          keys.forEach(k => {
            const tr = document.createElement('tr');
            const lastUsed = k.last_used ? new Date(k.last_used.replace(' ', 'T')).toLocaleString('vi-VN') : 'N/A';
            tr.innerHTML = `
              <td style="padding:12px; border-bottom:1px solid var(--border-glass); font-family:monospace; color:var(--accent-secondary); font-size:0.8rem;">${k.key}</td>
              <td style="padding:12px; border-bottom:1px solid var(--border-glass); color:white; font-weight:bold;">${k.count.toLocaleString()}</td>
              <td style="padding:12px; border-bottom:1px solid var(--border-glass); color:var(--text-secondary);">${lastUsed}</td>
            `;
            tbody.appendChild(tr);
          });
        }
      }
    })
    .catch(err => {
      console.warn("Failed to load usage analytics:", err);
    });

  // Also fetch leads count for the stat card
  adminFetch(`${localApiUrl}/api/leads`)
    .then(res => res.json())
    .then(data => {
      const leadsEl = document.getElementById("usage-total-leads");
      if (leadsEl) leadsEl.innerText = (data.total_leads || 0).toLocaleString('vi-VN');
    })
    .catch(() => {});
}

function loadLeadsList() {
  const localApiUrl = getLocalApiUrl();

  adminFetch(`${localApiUrl}/api/leads`)
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById("usage-leads-tbody");
      if (!tbody) return;

      const leads = data.leads || [];
      if (leads.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding: 30px 0; color:var(--text-muted);">No developer leads captured yet. Share your API portal to start collecting signups.</td></tr>';
        return;
      }

      tbody.innerHTML = '';
      leads.forEach(lead => {
        const tr = document.createElement('tr');
        const signupDate = lead.timestamp ? new Date(lead.timestamp.replace(' ', 'T')).toLocaleString('vi-VN') : 'N/A';
        tr.innerHTML = `
          <td style="padding:12px; border-bottom:1px solid var(--border-glass); color:white; font-weight:bold;">${lead.email}</td>
          <td style="padding:12px; border-bottom:1px solid var(--border-glass); color:var(--text-secondary);">
            <span style="background:rgba(20,184,166,0.1); color:var(--accent-secondary); padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:bold;">${lead.source.toUpperCase()}</span>
          </td>
          <td style="padding:12px; border-bottom:1px solid var(--border-glass); color:var(--text-secondary);">${signupDate}</td>
        `;
        tbody.appendChild(tr);
      });
    })
    .catch(err => {
      console.warn("Failed to load leads:", err);
    });
}

function loadSupportTickets() {
  const localApiUrl = getLocalApiUrl();
  const tbody = document.getElementById("support-tickets-tbody");
  if (!tbody) return;

  tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:20px; color:var(--text-secondary);"><i class="fa-solid fa-spinner fa-spin"></i> Đang tải dữ liệu...</td></tr>`;

  adminFetch(`${localApiUrl}/api/support`)
    .then(res => res.json())
    .then(data => {
      const tickets = data.tickets || [];
      if (tickets.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:30px 0; color:var(--text-muted);"><i class="fa-solid fa-face-smile"></i> Không có yêu cầu hỗ trợ nào cần xử lý.</td></tr>`;
        return;
      }
      tbody.innerHTML = "";
      tickets.forEach(t => {
        const tr = document.createElement("tr");
        tr.style.borderBottom = "1px solid rgba(255,255,255,0.05)";
        
        const statusBadge = t.status === "resolved" 
          ? `<span style="background:rgba(16,185,129,0.1); color:#10b981; padding:2px 8px; border-radius:100px; font-size:0.75rem; font-weight:600;"><i class="fa-solid fa-circle-check"></i> Đã xử lý</span>`
          : `<span style="background:rgba(245,158,11,0.1); color:#f59e0b; padding:2px 8px; border-radius:100px; font-size:0.75rem; font-weight:600;"><i class="fa-solid fa-spinner fa-spin"></i> Chờ xử lý</span>`;

        const actionBtn = t.status === "resolved"
          ? `<button class="btn btn-secondary" style="padding:4px 8px; font-size:0.75rem; background:rgba(255,255,255,0.02); border-color:var(--border-glass);" disabled>Đã xong</button>`
          : `<button class="btn btn-primary" style="padding:4px 8px; font-size:0.75rem;" onclick="resolveSupportTicket(${t.id})">Giải quyết</button>`;

        const ticketDate = t.timestamp ? new Date(t.timestamp.replace(' ', 'T')).toLocaleString('vi-VN') : 'N/A';

        tr.innerHTML = `
          <td style="padding:12px; font-weight:bold; color:#fff;">#${t.id}</td>
          <td style="padding:12px;">
            <div style="font-weight:600; color:#fff;">${escapeHtml(t.name)}</div>
            <div style="font-size:0.8rem; color:var(--text-secondary);">${escapeHtml(t.email)}</div>
          </td>
          <td style="padding:12px;"><code style="color:var(--accent-secondary); font-size:0.85rem;">${escapeHtml(t.memo || 'N/A')}</code></td>
          <td style="padding:12px; max-width:300px; word-wrap:break-word; color:var(--text-main); font-size:0.9rem;">${escapeHtml(t.message)}</td>
          <td style="padding:12px;">${statusBadge}</td>
          <td style="padding:12px; font-size:0.8rem; color:var(--text-muted);">${ticketDate}</td>
          <td style="padding:12px;">${actionBtn}</td>
        `;
        tbody.appendChild(tr);
      });
    })
    .catch(err => {
      console.warn("Failed to load support tickets:", err);
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:20px; color:#ef4444;"><i class="fa-solid fa-circle-exclamation"></i> Lỗi tải dữ liệu. Cổng kết nối API cục bộ đang offline.</td></tr>`;
    });
}

function resolveSupportTicket(id) {
  const localApiUrl = getLocalApiUrl();

  adminFetch(`${localApiUrl}/api/support/resolve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ id })
  })
  .then(res => {
    if (res.ok) {
      loadSupportTickets();
    } else {
      alert("Không thể đánh dấu xử lý vé hỗ trợ này.");
    }
  })
  .catch(err => {
    console.error("Resolve ticket error:", err);
    alert("Không kết nối được với server cục bộ.");
  });
}

function loadFeedbacks() {
  const localApiUrl = getLocalApiUrl();
  const tbody = document.getElementById("feedback-tbody");
  if (!tbody) return;

  tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px; color:var(--text-secondary);"><i class="fa-solid fa-spinner fa-spin"></i> Đang tải dữ liệu...</td></tr>`;

  adminFetch(`${localApiUrl}/api/feedback`)
    .then(res => res.json())
    .then(data => {
      const feedbacks = data.feedbacks || [];
      if (feedbacks.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:30px 0; color:var(--text-muted);"><i class="fa-solid fa-face-smile"></i> Không có ý kiến đóng góp nào.</td></tr>`;
        return;
      }
      tbody.innerHTML = "";
      feedbacks.forEach(f => {
        const tr = document.createElement("tr");
        tr.style.borderBottom = "1px solid rgba(255,255,255,0.05)";
        
        let statusBadge = "";
        if (f.status === "backlogged") {
          statusBadge = `<span style="background:rgba(16,185,129,0.1); color:#10b981; padding:2px 8px; border-radius:100px; font-size:0.75rem; font-weight:600;"><i class="fa-solid fa-circle-check"></i> Đưa vào Backlog</span>`;
        } else if (f.status === "ignored") {
          statusBadge = `<span style="background:rgba(239,68,68,0.1); color:#ef4444; padding:2px 8px; border-radius:100px; font-size:0.75rem; font-weight:600;"><i class="fa-solid fa-ban"></i> Bỏ qua / Spam</span>`;
        } else {
          statusBadge = `<span style="background:rgba(245,158,11,0.1); color:#f59e0b; padding:2px 8px; border-radius:100px; font-size:0.75rem; font-weight:600;"><i class="fa-solid fa-hourglass-half"></i> Chờ đánh giá</span>`;
        }

        const dateStr = f.timestamp ? new Date(f.timestamp.replace(' ', 'T')).toLocaleString('vi-VN') : 'N/A';

        tr.innerHTML = `
          <td style="padding:12px; font-weight:bold; color:#fff;">#${f.id}</td>
          <td style="padding:12px;">
            <div style="font-weight:600; color:#fff;">${escapeHtml(f.name || 'Anonymous')}</div>
            <div style="font-size:0.8rem; color:var(--text-secondary);">${escapeHtml(f.email || 'N/A')}</div>
          </td>
          <td style="padding:12px; max-width:250px; word-wrap:break-word; color:var(--text-main); font-size:0.9rem;">${escapeHtml(f.message)}</td>
          <td style="padding:12px; max-width:300px; word-wrap:break-word; color:var(--text-secondary); font-size:0.85rem;">${escapeHtml(f.assessment || 'Đang chờ Agent đánh giá...')}</td>
          <td style="padding:12px;">${statusBadge}</td>
          <td style="padding:12px; font-size:0.8rem; color:var(--text-muted);">${dateStr}</td>
        `;
        tbody.appendChild(tr);
      });
    })
    .catch(err => {
      console.warn("Failed to load feedbacks:", err);
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px; color:#ef4444;"><i class="fa-solid fa-circle-exclamation"></i> Lỗi tải dữ liệu.</td></tr>`;
    });
}

function escapeHtml(text) {
  if (!text) return "";
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

if (typeof window !== "undefined") {
  window.loadSupportTickets = loadSupportTickets;
  window.resolveSupportTicket = resolveSupportTicket;
  window.loadFeedbacks = loadFeedbacks;
}
