/* ==========================================================================
   VietRegistry API - Frontend Portal Engine
   Handles sandbox execution, dynamic code snippets, and active UI tabs.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  initEndpointSelector();
  initSandboxSender();
  initCodeSnippets();
  initCheckoutTrigger();
});

// --------------------------------------------------------------------------
// Sandbox Endpoint Input Selector Toggle
// --------------------------------------------------------------------------
function initEndpointSelector() {
  const endpointSelect = document.getElementById("sandbox-endpoint-select");
  const companyGroup = document.getElementById("params-company-group");
  const searchGroup = document.getElementById("params-search-group");

  if (!endpointSelect) return;

  endpointSelect.addEventListener("change", (e) => {
    const val = e.target.value;
    if (val === "company") {
      companyGroup.style.display = "block";
      searchGroup.style.display = "none";
    } else {
      companyGroup.style.display = "none";
      searchGroup.style.display = "block";
    }
    updateSnippets();
  });

  // Attach input listeners to update snippets dynamically as user types
  const taxCodeInput = document.getElementById("param-tax-code");
  const queryInput = document.getElementById("param-search-query");

  if (taxCodeInput) {
    taxCodeInput.addEventListener("input", updateSnippets);
  }
  if (queryInput) {
    queryInput.addEventListener("input", updateSnippets);
  }
}

// --------------------------------------------------------------------------
// Sandbox Ajax Request Sender
// --------------------------------------------------------------------------
function initSandboxSender() {
  const sendBtn = document.getElementById("sandbox-send-btn");
  const endpointSelect = document.getElementById("sandbox-endpoint-select");
  const responseBody = document.getElementById("sandbox-response-body");
  const statusEl = document.getElementById("sandbox-status");

  if (!sendBtn) return;

  sendBtn.addEventListener("click", () => {
    const email = localStorage.getItem("userEmail");
    if (!email) {
      if (window.showAuthModal) {
        window.showAuthModal(() => {
          sendBtn.click();
        });
      } else {
        alert("Vui lòng đăng ký Email miễn phí để sử dụng Sandbox thử nghiệm API.");
      }
      return;
    }

    const acceptTerms = document.getElementById("accept-terms-sandbox");
    if (acceptTerms && !acceptTerms.checked) {
      alert("You must read and agree to the Terms & Conditions and Privacy Policy to use the API sandbox.");
      return;
    }

    const endpoint = endpointSelect.value;
    let url = "";

    if (endpoint === "company") {
      const taxCode = document.getElementById("param-tax-code").value.trim();
      if (!taxCode) {
        alert("Please enter a tax code!");
        return;
      }
      url = `/api/company?tax_code=${encodeURIComponent(taxCode)}`;
    } else {
      const q = document.getElementById("param-search-query").value.trim();
      if (!q) {
        alert("Please enter a search keyword!");
        return;
      }
      url = `/api/search?q=${encodeURIComponent(q)}`;
    }

    // Set loading state
    sendBtn.disabled = true;
    sendBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Sending...`;
    statusEl.innerText = "Status: Querying GDT...";
    statusEl.className = "terminal-status";
    responseBody.innerText = `// Querying the live database / scraping GDT registry records...\n// This might take a few seconds if resolving new data...\n`;

    fetch(url)
      .then(async (response) => {
        const text = await response.text();
        let formatted = text;
        try {
          const parsed = JSON.parse(text);
          formatted = JSON.stringify(parsed, null, 2);
        } catch (e) {
          // Keep as text if not JSON
        }

        responseBody.innerText = formatted;
        
        // Update status badge
        statusEl.innerText = `Status: ${response.status} ${response.statusText}`;
        if (response.ok) {
          statusEl.className = "terminal-status success";
        } else {
          statusEl.className = "terminal-status error";
        }
      })
      .catch((error) => {
        responseBody.innerText = `// Network connection error:\n${error.message}`;
        statusEl.innerText = "Status: Error";
        statusEl.className = "terminal-status error";
      })
      .finally(() => {
        sendBtn.disabled = false;
        sendBtn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Send Request`;
      });
  });
}

// --------------------------------------------------------------------------
// Dynamic Code Snippets & Copy Clipboard logic
// --------------------------------------------------------------------------
let activeCodeTab = "curl";

function initCodeSnippets() {
  const tabs = document.querySelectorAll(".code-tab-btn");
  const panels = document.querySelectorAll(".code-block-panel");
  const copyBtn = document.getElementById("copy-snippet-btn");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      activeCodeTab = tab.getAttribute("data-code-tab");
      panels.forEach(p => {
        p.classList.remove("active");
        if (p.id === `code-${activeCodeTab}`) {
          p.classList.add("active");
        }
      });
    });
  });

  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      let codeText = "";
      if (activeCodeTab === "curl") {
        codeText = document.getElementById("code-curl-text").innerText;
      } else if (activeCodeTab === "js") {
        codeText = document.getElementById("code-js-text").innerText;
      } else if (activeCodeTab === "python") {
        codeText = document.getElementById("code-python-text").innerText;
      }

      navigator.clipboard.writeText(codeText).then(() => {
        const originalHtml = copyBtn.innerHTML;
        copyBtn.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
        setTimeout(() => {
          copyBtn.innerHTML = originalHtml;
        }, 2000);
      });
    });
  }

  // Initial populate
  updateSnippets();
}

function updateSnippets() {
  const endpointSelect = document.getElementById("sandbox-endpoint-select");
  if (!endpointSelect) return;

  const endpoint = endpointSelect.value;
  const baseUrl = window.location.origin === "null" || window.location.origin === "file://" ? "https://vinaearn-ai.vercel.app" : window.location.origin;

  let queryUrl = "";
  let jsFetchCode = "";
  let pythonCode = "";

  if (endpoint === "company") {
    const taxCode = document.getElementById("param-tax-code").value.trim() || "0100109106";
    queryUrl = `${baseUrl}/api/company?tax_code=${taxCode}`;
    
    jsFetchCode = `fetch("${baseUrl}/api/company?tax_code=${taxCode}", {
  headers: {
    "Authorization": "Bearer YOUR_API_KEY"
  }
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error("Error:", error));`;

    pythonCode = `import requests

url = "${baseUrl}/api/company"
params = {"tax_code": "${taxCode}"}
headers = {
    "Authorization": "Bearer YOUR_API_KEY"
}

response = requests.get(url, params=params, headers=headers)
if response.status_code == 200:
    company_data = response.json()
    print(company_data)
else:
    print(f"Error: {response.status_code}")`;
  } else {
    const q = document.getElementById("param-search-query").value.trim() || "cong ty xay dung";
    queryUrl = `${baseUrl}/api/search?q=${encodeURIComponent(q)}`;

    jsFetchCode = `fetch("${baseUrl}/api/search?q=${encodeURIComponent(q)}", {
  headers: {
    "Authorization": "Bearer YOUR_API_KEY"
  }
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error("Error:", error));`;

    pythonCode = `import requests

url = "${baseUrl}/api/search"
params = {"q": "${q}"}
headers = {
    "Authorization": "Bearer YOUR_API_KEY"
}

response = requests.get(url, params=params, headers=headers)
if response.status_code == 200:
    search_results = response.json()
    print(search_results)
else:
    print(f"Error: {response.status_code}")`;
  }

  // Update DOM code text
  document.getElementById("code-curl-text").innerText = `curl -X GET "${queryUrl}" \\\n  -H "Authorization: Bearer YOUR_API_KEY"`;
  document.getElementById("code-js-text").innerText = jsFetchCode;
  document.getElementById("code-python-text").innerText = pythonCode;
}

// --------------------------------------------------------------------------
// Checkout Trigger & Config Initialization
// --------------------------------------------------------------------------
function initCheckoutTrigger() {
  // Initialize bank configuration from config.json details
  if (window.initCheckoutConfig) {
    window.initCheckoutConfig({
      bankName: "techcombank",
      bankId: "TCB",
      accountNumber: "19027557341011",
      accountName: "NGUYEN TRUNG THIEN PHUC"
    });
    
    // Check if there is a localApiUrl override in localStorage
    const localApiUrl = localStorage.getItem("localApiUrl");
    if (localApiUrl) {
      let cleanUrl = localApiUrl.trim();
      if (cleanUrl.endsWith("/")) {
        cleanUrl = cleanUrl.slice(0, -1);
      }
      window.initCheckoutConfig({
        apiEndpoint: `${cleanUrl}/api/check-payment`
      });
    }
  }

  // Config list of available purchase plans
  const plans = [
    { btnId: "buy-vip-btn", price: 99000, memoPrefix: "VE_VIP_" },
    { btnId: "buy-pro-plan-btn", price: 250000, memoPrefix: "VE_PRO_" },
    { btnId: "buy-enterprise-btn", price: 1000000, memoPrefix: "VE_ENT_" },
    { btnId: "buy-bulk-btn", price: 2500000, memoPrefix: "VE_BULK_" }
  ];

  plans.forEach(plan => {
    const btn = document.getElementById(plan.btnId);
    if (btn) {
      btn.addEventListener("click", () => {
        const randomHex = Math.floor(100000 + Math.random() * 900000); // 6 digit random number
        const memo = `${plan.memoPrefix}${randomHex}`;
        
        if (window.showCheckoutModal) {
          window.showCheckoutModal(plan.price, memo, (token) => {
            console.log(`Plan ${plan.btnId} activated successfully. Token/Key:`, token);
            if (plan.btnId === "buy-vip-btn") {
              localStorage.setItem("vipToken", token);
              alert("Chúc mừng! Bạn đã kích hoạt Gói VIP Thành Viên thành công. Toàn bộ 25+ mẫu tài liệu trên VinaTools hiện đã được mở khóa tải MIỄN PHÍ.");
            } else if (plan.btnId === "buy-bulk-btn") {
              alert("Thanh toán thành công! Tệp cơ sở dữ liệu SQLite mẫu (500 doanh nghiệp) đang được tải xuống máy của bạn.");
              window.location.href = "/companies_sample.db";
            } else {
              alert(`Thanh toán thành công! Khóa API của bạn đã được khởi tạo và ký số:\n\n${token}\n\nHãy sao chép khóa này để sử dụng trong header Authorization: Bearer.`);
            }
          });
        } else {
          alert("Hệ thống thanh toán đang tải, vui lòng bấm lại sau ít giây.");
        }
      });
    }
  });
}

