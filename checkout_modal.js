/**
 * Checkout Payment Modal & VietQR Integration
 * Fully automated client-side payment flow.
 * Localized completely into Vietnamese with senior-accessible UI/UX.
 */

// We fetch config values dynamically or they are templated in by the generator.
let paymentConfig = {
  bankName: "Techcombank",
  bankId: "TCB",
  accountNumber: "",
  accountName: "",
  apiEndpoint: "/api",
  adsenseClient: ""
};

function initCheckoutConfig(config) {
  const centralApi = paymentConfig.apiEndpoint;
  paymentConfig = { ...paymentConfig, ...config };
  if (centralApi && centralApi.startsWith("http")) {
    paymentConfig.apiEndpoint = centralApi;
  }
}

function showCheckoutModal(amount, memo, onSuccessCallback) {
  // Check if modal container already exists
  let modal = document.getElementById("paywall-checkout-modal");
  
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "paywall-checkout-modal";
    modal.className = "paywall-modal-overlay";
    document.body.appendChild(modal);
  }

  // Format currency for display
  const formattedAmount = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
  
  // URL Encode the Account Name for the VietQR API
  const encodedName = encodeURIComponent(paymentConfig.accountName);
  const encodedMemo = encodeURIComponent(memo);
  
  // Generate VietQR Image URL
  const qrUrl = `https://img.vietqr.io/image/${paymentConfig.bankId}-${paymentConfig.accountNumber}-qr_only.png?amount=${amount}&addInfo=${encodedMemo}&accountName=${encodedName}`;

  // Modal inner HTML using global styling classes
  modal.innerHTML = `
    <div class="glass-panel paywall-card" style="position: relative; border-radius: var(--radius-md); box-shadow: 0 20px 50px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.15);">
      <button id="close-checkout-btn" style="position: absolute; top: 16px; right: 16px; background: none; border: none; color: var(--text-muted); font-size: 1.8rem; cursor: pointer; transition: var(--transition-smooth);">&times;</button>
      
      <div style="text-align: center; margin-bottom: 20px;">
        <h3 style="margin-bottom: 8px; font-size: 1.4rem; color: #fff; font-family: var(--font-display);"><i class="fa-solid fa-shield-halved" style="color: #10b981; margin-right: 8px;"></i> Thanh Toán An Toàn</h3>
        <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.4;">Vui lòng mở ứng dụng Ngân hàng (App Ngân hàng) quét mã QR bên dưới, hoặc chuyển khoản đúng thông tin.</p>
      </div>

      <img src="${qrUrl}" alt="VietQR" class="qr-code-img" style="border: 8px solid white; border-radius: 8px; margin: 15px auto; width: 220px; height: 220px;">

      <div style="background: rgba(0,0,0,0.4); padding: 18px; border-radius: var(--radius-sm); border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; font-size: 0.95rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
          <span style="color: var(--text-secondary);">Ngân hàng nhận:</span>
          <strong style="color: #fff;">${paymentConfig.bankName}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
          <span style="color: var(--text-secondary);">Số tài khoản:</span>
          <strong style="color: #fff; font-size: 1.05rem;">${paymentConfig.accountNumber}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
          <span style="color: var(--text-secondary);">Số tiền cần chuyển:</span>
          <strong style="color: #f59e0b; font-size: 1.15rem; font-weight: bold;">${formattedAmount}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 4px;">
          <span style="color: var(--text-secondary);">Nội dung ghi chú:</span>
          <strong style="color: #00a8ff; font-size: 1.1rem; border: 1px dashed #00a8ff; padding: 4px 10px; border-radius: 4px; background: rgba(0, 168, 255, 0.1); font-family: monospace;">${memo}</strong>
        </div>
      </div>

      <div class="payment-loader" style="font-size: 0.95rem; font-weight: 500; color: #00a8ff;">
        <div class="spinner"></div>
        <span>Đang chờ bạn quét mã chuyển khoản...</span>
      </div>
    </div>
  `;

  // Display modal
  setTimeout(() => {
    modal.classList.add("active");
  }, 50);

  // Close button functionality
  let isChecking = true;
  const closeBtn = modal.querySelector("#close-checkout-btn");
  closeBtn.onclick = () => {
    isChecking = false;
    modal.classList.remove("active");
  };

  // Poll transaction verification endpoint
  function pollPaymentStatus() {
    if (!isChecking) return;

    const email = localStorage.getItem("userEmail") || "";
    fetch(`${paymentConfig.apiEndpoint}?memo=${encodedMemo}&email=${encodeURIComponent(email)}&t=${Date.now()}`)
      .then(response => response.json())
      .then(data => {
        if (data.status === "completed") {
          isChecking = false;
          // Play success state in UI
          const loaderArea = modal.querySelector(".payment-loader");
          loaderArea.innerHTML = `
            <i class="fa-solid fa-circle-check" style="color: #10b981; font-size: 1.8rem; margin-right: 8px;"></i>
            <span style="color: #10b981; font-weight: bold; font-size: 1.05rem;">Chuyển khoản thành công! Đang tải gói VIP...</span>
          `;
          if (data.apiKey || data.downloadToken) {
            localStorage.setItem("vipToken", data.apiKey || data.downloadToken);
          }
          setTimeout(() => {
            modal.classList.remove("active");
            updateUserNavStatus();
            if (onSuccessCallback) onSuccessCallback(data.downloadToken || data);
          }, 1500);
        } else {
          // Poll again in 3 seconds
          setTimeout(pollPaymentStatus, 3000);
        }
      })
      .catch(err => {
        console.error("Payment poll error:", err);
        setTimeout(pollPaymentStatus, 3000);
      });
  }

  // Start polling
  pollPaymentStatus();
}

function showAuthModal(onSuccessCallback) {
  let modal = document.getElementById("auth-checkout-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "auth-checkout-modal";
    modal.className = "paywall-modal-overlay";
    document.body.appendChild(modal);
  }

  // Define dynamic content in 100% warm Vietnamese optimized for older/non-technical users
  const title = "Đăng Ký / Đăng Nhập Thành Viên";
  const desc = "Tạo tài khoản hoặc đăng nhập nhanh bằng Email và Mật khẩu của bạn để quản lý các công cụ, khóa tài nguyên và tải các tài liệu pháp lý.";
  
  // Inject the modal with custom styled sub-views (Login/Register, Forgot Panel, OTP Panel)
  modal.innerHTML = `
    <style>
      .auth-input-wrapper {
        position: relative;
        margin-bottom: 18px;
      }
      .auth-label {
        display: block; 
        font-size: 0.95rem; 
        color: #d1d5db; 
        margin-bottom: 6px; 
        font-weight: bold;
      }
      .auth-input-field {
        width: 100%; 
        box-sizing: border-box; 
        font-size: 1.05rem !important; 
        padding: 12px 16px !important;
        border-radius: 8px !important;
        background: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: white !important;
      }
      .auth-input-field:focus {
        border-color: #00a8ff !important;
        box-shadow: 0 0 0 4px rgba(0, 168, 255, 0.2) !important;
      }
      .auth-toggle-pwd {
        position: absolute; 
        right: 14px; 
        top: 40px; 
        cursor: pointer; 
        color: #9ca3af; 
        font-size: 1.1rem;
        z-index: 10;
        padding: 4px;
      }
      .auth-tab-btn {
        flex: 1;
        padding: 12px;
        font-size: 0.9rem;
        font-weight: bold;
        background: rgba(255,255,255,0.05);
        color: #9ca3af;
        border: 1px solid rgba(255,255,255,0.08);
        cursor: pointer;
        transition: all 0.2s ease;
      }
      .auth-tab-btn.active {
        background: rgba(0, 168, 255, 0.15);
        color: #00a8ff;
        border-color: #00a8ff;
      }
      .auth-help-box {
        background: rgba(245,158,11,0.08); 
        border: 1px solid rgba(245,158,11,0.2); 
        padding: 14px; 
        border-radius: 8px; 
        font-size: 0.88rem; 
        color: #f59e0b; 
        margin-top: 15px; 
        line-height: 1.5;
        text-align: justify;
      }
      .auth-help-box a {
        color: #00a8ff;
        text-decoration: underline;
        font-weight: bold;
      }
      .auth-link {
        color: #00a8ff; 
        font-size: 0.95rem; 
        display: block; 
        text-align: center; 
        margin-top: 15px; 
        text-decoration: underline;
        font-weight: 500;
      }
      .auth-link:hover {
        color: #38bdf8;
      }
    </style>
    
    <div class="glass-panel paywall-card" style="position: relative; padding: 35px 30px; max-width: 460px; border-radius: var(--radius-md); box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
      <button id="close-auth-btn" style="position: absolute; top: 16px; right: 16px; background: none; border: none; color: var(--text-muted); font-size: 1.8rem; cursor: pointer; transition: var(--transition-smooth); z-index: 100;">&times;</button>
      
      <!-- SUB-PANEL 1: LOGIN/REGISTRATION -->
      <div id="auth-main-panel">
        <div style="text-align: center; margin-bottom: 24px;">
          <h3 style="margin-bottom: 10px; font-size: 1.4rem; color: #fff; font-family: var(--font-display);"><i class="fa-solid fa-user-shield" style="color: #00a8ff; margin-right: 8px;"></i> Đăng Nhập / Đăng Ký</h3>
          <p style="color: var(--text-secondary); font-size: 0.92rem; line-height: 1.5;">Đăng nhập hoặc đăng ký tài khoản để bắt đầu sử dụng.</p>
        </div>

        <div style="display: flex; gap: 4px; margin-bottom: 24px; border-radius: 8px; overflow: hidden; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 4px;">
          <button id="auth-tab-login" class="auth-tab-btn active" style="border-radius: 6px;">Đăng Nhập</button>
          <button id="auth-tab-register" class="auth-tab-btn" style="border-radius: 6px;">Đăng Ký</button>
        </div>

        <div class="auth-input-wrapper">
          <label class="auth-label" for="auth-email-input">Địa chỉ tài khoản Email:</label>
          <input type="email" id="auth-email-input" class="auth-input-field" placeholder="Ví dụ: nguyenvan@gmail.com" required>
        </div>

        <div class="auth-input-wrapper">
          <label class="auth-label" for="auth-password-input">Mật khẩu của tài khoản:</label>
          <input type="password" id="auth-password-input" class="auth-input-field" placeholder="Nhập mật khẩu (tối thiểu 6 ký tự)" required>
          <i class="fa-solid fa-eye auth-toggle-pwd" id="toggle-pwd-btn"></i>
        </div>
        
        <div id="auth-error-msg" style="color: #ef4444; font-size: 0.9rem; margin-bottom: 15px; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); padding: 10px 14px; border-radius: 6px; display: none; line-height: 1.4;"></div>

        <button id="submit-auth-btn" class="btn btn-primary" style="width: 100%; padding: 14px; font-size: 1.05rem; font-weight: bold; border-radius: 8px; background: linear-gradient(135deg, #00a8ff 0%, #a855f7 100%);">
          Đăng Nhập Ngay
        </button>

        <a href="javascript:void(0)" id="go-to-recovery-btn" class="auth-link">Quên Email hoặc Mật khẩu? Khôi phục tại đây</a>
      </div>

      <!-- SUB-PANEL 2: ACCOUNT RECOVERY CHOOSE -->
      <div id="auth-recovery-panel" style="display: none;">
        <div style="text-align: center; margin-bottom: 20px;">
          <h3 style="margin-bottom: 8px; font-size: 1.35rem; color: #fff;"><i class="fa-solid fa-key" style="color: #f59e0b; margin-right: 8px;"></i> Khôi Phục Tài Khoản</h3>
          <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.4;">Vui lòng chọn hình thức khôi phục tài khoản phù hợp bên dưới.</p>
        </div>

        <div style="display: flex; gap: 4px; margin-bottom: 20px; border-radius: 8px; overflow: hidden;">
          <button id="tab-recover-email-btn" class="auth-tab-btn active" style="border-top-left-radius: 8px; border-bottom-left-radius: 8px;">Quên Mật Khẩu (Nhớ Email)</button>
          <button id="tab-recover-vip-btn" class="auth-tab-btn" style="border-top-right-radius: 8px; border-bottom-right-radius: 8px;">Quên cả Email & Mật Khẩu</button>
        </div>

        <!-- Mode A: Forgot Password (email known) -->
        <div id="recover-mode-email-section">
          <div class="auth-input-wrapper">
            <label class="auth-label" for="recover-email-input">Nhập địa chỉ Email tài khoản:</label>
            <input type="email" id="recover-email-input" class="auth-input-field" placeholder="Ví dụ: nguyenvan@gmail.com">
          </div>
          <button id="submit-recover-email-btn" class="btn btn-primary" style="width: 100%; padding: 12px; font-size: 1rem; border-radius: 6px; background: #00a8ff;">
            Gửi mã OTP qua Email
          </button>
        </div>

        <!-- Mode B: Forgot both (VIP transaction code lookup) -->
        <div id="recover-mode-vip-section" style="display: none;">
          <div class="auth-input-wrapper">
            <label class="auth-label" for="recover-vip-input">Mã thanh toán VIP Techcombank:</label>
            <input type="text" id="recover-vip-input" class="auth-input-field" placeholder="Ví dụ: VE_VIP_123456" style="text-transform: uppercase;">
            <p style="color: var(--text-muted); font-size: 0.82rem; margin-top: 6px; line-height: 1.3;">Nhập đúng mã ghi chú trong lịch sử chuyển khoản ngân hàng của bạn khi mua gói dịch vụ.</p>
          </div>
          <button id="submit-recover-vip-btn" class="btn btn-primary" style="width: 100%; padding: 12px; font-size: 1rem; border-radius: 6px; background: #a855f7;">
            Tìm kiếm bằng mã chuyển khoản VIP
          </button>
        </div>

        <div class="auth-help-box">
          <strong>Lưu ý đối với tài khoản Miễn Phí:</strong> Vì bạn chưa nâng cấp VIP, tài khoản thường không gắn liền với thông tin thanh toán. Bạn chỉ cần bấm <a href="javascript:void(0)" id="register-new-free-lnk">Đăng ký tài khoản Miễn phí mới</a> để sử dụng công cụ ngay lập tức (chỉ mất 10 giây).
        </div>

        <div id="recovery-error-msg" style="color: #ef4444; font-size: 0.9rem; margin-top: 15px; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); padding: 10px 14px; border-radius: 6px; display: none;"></div>

        <a href="javascript:void(0)" id="back-to-login-btn" style="color: var(--text-muted); font-size: 0.9rem; display: block; text-align: center; margin-top: 20px; text-decoration: none;"><i class="fa-solid fa-arrow-left"></i> Quay lại Đăng Nhập / Đăng Ký</a>
      </div>

      <!-- SUB-PANEL 3: OTP VERIFICATION & RESET -->
      <div id="auth-otp-panel" style="display: none;">
        <div style="text-align: center; margin-bottom: 20px;">
          <h3 style="margin-bottom: 8px; font-size: 1.35rem; color: #fff;"><i class="fa-solid fa-user-check" style="color: #10b981; margin-right: 8px;"></i> Xác Minh & Đổi Mật Khẩu</h3>
          <p id="otp-panel-desc" style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;"></p>
        </div>

        <div class="auth-input-wrapper">
          <label class="auth-label" for="otp-input">Mã xác minh 6 số (OTP):</label>
          <input type="text" id="otp-input" class="auth-input-field" placeholder="Nhập 6 chữ số nhận được" maxlength="6" style="text-align: center; font-size: 1.25rem !important; letter-spacing: 4px;">
        </div>

        <div class="auth-input-wrapper">
          <label class="auth-label" for="otp-new-password-input">Đặt mật khẩu mới:</label>
          <input type="password" id="otp-new-password-input" class="auth-input-field" placeholder="Nhập mật khẩu mới (tối thiểu 6 ký tự)" required>
          <i class="fa-solid fa-eye auth-toggle-pwd" id="toggle-otp-pwd-btn"></i>
        </div>

        <div id="otp-error-msg" style="color: #ef4444; font-size: 0.9rem; margin-bottom: 15px; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); padding: 10px 14px; border-radius: 6px; display: none;"></div>

        <button id="submit-otp-reset-btn" class="btn btn-primary" style="width: 100%; padding: 12px; font-size: 1rem; border-radius: 6px; background: linear-gradient(135deg, #10b981 0%, #00a8ff 100%);">
          Xác Nhận Đặt Lại Mật Khẩu
        </button>

        <a href="javascript:void(0)" id="back-to-login-from-otp-btn" style="color: var(--text-muted); font-size: 0.9rem; display: block; text-align: center; margin-top: 20px; text-decoration: none;"><i class="fa-solid fa-arrow-left"></i> Hủy bỏ & Quay lại Đăng Nhập</a>
      </div>
    </div>
  `;

  // Display modal
  setTimeout(() => {
    modal.classList.add("active");
  }, 50);

  // Grab panel views
  const mainPanel = modal.querySelector("#auth-main-panel");
  const recoveryPanel = modal.querySelector("#auth-recovery-panel");
  const otpPanel = modal.querySelector("#auth-otp-panel");

  // Main login inputs
  const emailInput = modal.querySelector("#auth-email-input");
  const passwordInput = modal.querySelector("#auth-password-input");
  const submitBtn = modal.querySelector("#submit-auth-btn");
  const errorMsg = modal.querySelector("#auth-error-msg");
  const togglePwdBtn = modal.querySelector("#toggle-pwd-btn");

  // Recovery views elements
  const tabRecoverEmailBtn = modal.querySelector("#tab-recover-email-btn");
  const tabRecoverVipBtn = modal.querySelector("#tab-recover-vip-btn");
  const recoverEmailSection = modal.querySelector("#recover-mode-email-section");
  const recoverVipSection = modal.querySelector("#recover-mode-vip-section");
  
  const recoverEmailInput = modal.querySelector("#recover-email-input");
  const recoverVipInput = modal.querySelector("#recover-vip-input");
  const submitRecoverEmailBtn = modal.querySelector("#submit-recover-email-btn");
  const submitRecoverVipBtn = modal.querySelector("#submit-recover-vip-btn");
  const recoveryErrorMsg = modal.querySelector("#recovery-error-msg");

  // OTP view elements
  const otpInput = modal.querySelector("#otp-input");
  const otpNewPasswordInput = modal.querySelector("#otp-new-password-input");
  const submitOtpResetBtn = modal.querySelector("#submit-otp-reset-btn");
  const otpErrorMsg = modal.querySelector("#otp-error-msg");
  const otpPanelDesc = modal.querySelector("#otp-panel-desc");
  const toggleOtpPwdBtn = modal.querySelector("#toggle-otp-pwd-btn");

  let activeRecoveredEmail = "";

  // Common Modal Close
  const closeBtn = modal.querySelector("#close-auth-btn");
  closeBtn.onclick = () => {
    modal.classList.remove("active");
  };

  // 1. Password Visibility Toggle
  togglePwdBtn.onclick = () => {
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      togglePwdBtn.classList.remove("fa-eye");
      togglePwdBtn.classList.add("fa-eye-slash");
    } else {
      passwordInput.type = "password";
      togglePwdBtn.classList.remove("fa-eye-slash");
      togglePwdBtn.classList.add("fa-eye");
    }
  };

  toggleOtpPwdBtn.onclick = () => {
    if (otpNewPasswordInput.type === "password") {
      otpNewPasswordInput.type = "text";
      toggleOtpPwdBtn.classList.remove("fa-eye");
      toggleOtpPwdBtn.classList.add("fa-eye-slash");
    } else {
      otpNewPasswordInput.type = "password";
      toggleOtpPwdBtn.classList.remove("fa-eye-slash");
      toggleOtpPwdBtn.classList.add("fa-eye");
    }
  };

  // 2. Navigation between Panels
  modal.querySelector("#go-to-recovery-btn").onclick = () => {
    mainPanel.style.display = "none";
    recoveryPanel.style.display = "block";
    recoveryErrorMsg.style.display = "none";
  };

  modal.querySelector("#back-to-login-btn").onclick = () => {
    recoveryPanel.style.display = "none";
    mainPanel.style.display = "block";
    errorMsg.style.display = "none";
  };

  modal.querySelector("#back-to-login-from-otp-btn").onclick = () => {
    otpPanel.style.display = "none";
    mainPanel.style.display = "block";
    errorMsg.style.display = "none";
  };

  modal.querySelector("#register-new-free-lnk").onclick = () => {
    recoveryPanel.style.display = "none";
    mainPanel.style.display = "block";
    emailInput.value = "";
    passwordInput.value = "";
    if (authTabRegister) {
      authTabRegister.click();
    }
    emailInput.focus();
  };

  // 3. Tab switching in Recovery Panel
  tabRecoverEmailBtn.onclick = () => {
    tabRecoverEmailBtn.classList.add("active");
    tabRecoverVipBtn.classList.remove("active");
    recoverEmailSection.style.display = "block";
    recoverVipSection.style.display = "none";
    recoveryErrorMsg.style.display = "none";
  };

  tabRecoverVipBtn.onclick = () => {
    tabRecoverVipBtn.classList.add("active");
    tabRecoverEmailBtn.classList.remove("active");
    recoverVipSection.style.display = "block";
    recoverEmailSection.style.display = "none";
    recoveryErrorMsg.style.display = "none";
  };

  // 4. Handle Login/Registration Submission and Tab Switching
  let activeAuthTab = "login";
  const authTabLogin = modal.querySelector("#auth-tab-login");
  const authTabRegister = modal.querySelector("#auth-tab-register");

  authTabLogin.onclick = () => {
    activeAuthTab = "login";
    authTabLogin.classList.add("active");
    authTabRegister.classList.remove("active");
    submitBtn.innerText = "Đăng Nhập Ngay";
    errorMsg.style.display = "none";
  };

  authTabRegister.onclick = () => {
    activeAuthTab = "register";
    authTabRegister.classList.add("active");
    authTabLogin.classList.remove("active");
    submitBtn.innerText = "Đăng Ký Tài Khoản";
    errorMsg.style.display = "none";
  };

  submitBtn.onclick = () => {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    if (!email || !email.includes("@")) {
      errorMsg.innerText = "Địa chỉ email không hợp lệ. Vui lòng kiểm tra lại xem có thiếu ký tự '@' hay gõ sai không nhé!";
      errorMsg.style.color = "#ef4444";
      errorMsg.style.background = "rgba(239,68,68,0.1)";
      errorMsg.style.borderColor = "rgba(239,68,68,0.2)";
      errorMsg.style.display = "block";
      return;
    }

    if (!password || password.length < 6) {
      errorMsg.innerText = "Mật khẩu phải chứa ít nhất 6 ký tự để bảo đảm an toàn cho tài khoản của bạn.";
      errorMsg.style.color = "#ef4444";
      errorMsg.style.background = "rgba(239,68,68,0.1)";
      errorMsg.style.borderColor = "rgba(239,68,68,0.2)";
      errorMsg.style.display = "block";
      return;
    }

    errorMsg.style.display = "none";
    submitBtn.disabled = true;
    submitBtn.innerText = "Đang xử lý thông tin...";

    const baseApiUrl = paymentConfig.apiEndpoint.replace('/api/check-payment', '');
    const subscribeUrl = `${baseApiUrl}/api/subscribe`;

    fetch(subscribeUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, password: password, source: "vinatools", action: activeAuthTab })
    })
    .then(res => {
      if (!res.ok) {
        return res.json().then(errData => { throw new Error(errData.error || "Giao dịch không thành công"); });
      }
      return res.json();
    })
    .then(data => {
      submitBtn.disabled = false;
      submitBtn.innerText = activeAuthTab === "login" ? "Đăng Nhập Ngay" : "Đăng Ký Tài Khoản";
      
      localStorage.setItem("userEmail", email);
      modal.classList.remove("active");
      
      // Update navigation bar
      updateUserNavStatus();
      
      if (onSuccessCallback) {
        onSuccessCallback(email);
      }
    })
    .catch(err => {
      console.error("Auth error:", err);
      submitBtn.disabled = false;
      submitBtn.innerText = activeAuthTab === "login" ? "Đăng Nhập Ngay" : "Đăng Ký Tài Khoản";
      errorMsg.innerText = err.message || "Lỗi kết nối mạng hoặc mật khẩu không chính xác. Vui lòng thử lại!";
      errorMsg.style.color = "#ef4444";
      errorMsg.style.background = "rgba(239,68,68,0.1)";
      errorMsg.style.borderColor = "rgba(239,68,68,0.2)";
      errorMsg.style.display = "block";
    });
  };

  // Helper function to transition to OTP reset screen
  function openOtpPanel(email, maskedEmail) {
    activeRecoveredEmail = email;
    recoveryPanel.style.display = "none";
    otpPanel.style.display = "block";
    otpErrorMsg.style.display = "none";
    otpInput.value = "";
    otpNewPasswordInput.value = "";
    
    otpPanelDesc.innerHTML = `Mã xác minh (OTP) đã được gửi đến hộp thư của bạn: <strong style="color: #00a8ff;">${maskedEmail}</strong>. Vui lòng nhập mã và thiết lập mật khẩu mới bên dưới.`;
  }

  // 5. Submit Recover Password by Email
  submitRecoverEmailBtn.onclick = () => {
    const email = recoverEmailInput.value.trim();
    if (!email || !email.includes("@")) {
      recoveryErrorMsg.innerText = "Vui lòng điền đúng địa chỉ Email tài khoản của bạn.";
      recoveryErrorMsg.style.display = "block";
      return;
    }

    recoveryErrorMsg.style.display = "none";
    submitRecoverEmailBtn.disabled = true;
    submitRecoverEmailBtn.innerText = "Đang gửi mã...";

    const baseApiUrl = paymentConfig.apiEndpoint.replace('/api/check-payment', '');
    const recoverUrl = `${baseApiUrl}/api/recover`;

    fetch(recoverUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email })
    })
    .then(res => {
      if (!res.ok) {
        return res.json().then(errData => { throw new Error(errData.error || "Có lỗi xảy ra"); });
      }
      return res.json();
    })
    .then(data => {
      submitRecoverEmailBtn.disabled = false;
      submitRecoverEmailBtn.innerText = "Gửi mã OTP qua Email";
      openOtpPanel(data.email, data.masked_email);
    })
    .catch(err => {
      submitRecoverEmailBtn.disabled = false;
      submitRecoverEmailBtn.innerText = "Gửi mã OTP qua Email";
      recoveryErrorMsg.innerText = err.message || "Lỗi kết nối mạng. Không tìm thấy tài khoản email này.";
      recoveryErrorMsg.style.display = "block";
    });
  };

  // 6. Submit Recover Account by VIP Transaction Memo
  submitRecoverVipBtn.onclick = () => {
    const vipMemo = recoverVipInput.value.trim().toUpperCase();
    if (!vipMemo || !vipMemo.startsWith("VE_")) {
      recoveryErrorMsg.innerText = "Mã chuyển khoản VIP không đúng định dạng. Mã thường bắt đầu bằng chữ VE (ví dụ: VE_VIP_123456).";
      recoveryErrorMsg.style.display = "block";
      return;
    }

    recoveryErrorMsg.style.display = "none";
    submitRecoverVipBtn.disabled = true;
    submitRecoverVipBtn.innerText = "Đang xác thực...";

    const baseApiUrl = paymentConfig.apiEndpoint.replace('/api/check-payment', '');
    const recoverUrl = `${baseApiUrl}/api/recover`;

    fetch(recoverUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ vip_memo: vipMemo })
    })
    .then(res => {
      if (!res.ok) {
        return res.json().then(errData => { throw new Error(errData.error || "Mã VIP không tồn tại"); });
      }
      return res.json();
    })
    .then(data => {
      submitRecoverVipBtn.disabled = false;
      submitRecoverVipBtn.innerText = "Tìm kiếm bằng mã chuyển khoản VIP";
      openOtpPanel(data.email, data.masked_email);
    })
    .catch(err => {
      submitRecoverVipBtn.disabled = false;
      submitRecoverVipBtn.innerText = "Tìm kiếm bằng mã chuyển khoản VIP";
      recoveryErrorMsg.innerText = err.message || "Mã giao dịch VIP không tồn tại hoặc tài khoản chưa liên kết thành công.";
      recoveryErrorMsg.style.display = "block";
    });
  };

  // 7. OTP Submit and Reset Password
  submitOtpResetBtn.onclick = () => {
    const otp = otpInput.value.trim();
    const newPwd = otpNewPasswordInput.value.trim();

    if (!otp || otp.length < 6) {
      otpErrorMsg.innerText = "Vui lòng nhập đúng 6 chữ số mã OTP xác minh.";
      otpErrorMsg.style.display = "block";
      return;
    }

    if (!newPwd || newPwd.length < 6) {
      otpErrorMsg.innerText = "Mật khẩu mới của bạn phải có độ dài tối thiểu là 6 ký tự.";
      otpErrorMsg.style.display = "block";
      return;
    }

    otpErrorMsg.style.display = "none";
    submitOtpResetBtn.disabled = true;
    submitOtpResetBtn.innerText = "Đang cập nhật mật khẩu...";

    const baseApiUrl = paymentConfig.apiEndpoint.replace('/api/check-payment', '');
    const resetUrl = `${baseApiUrl}/api/recover/reset`;

    fetch(resetUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: activeRecoveredEmail, otp: otp, new_password: newPwd })
    })
    .then(res => {
      if (!res.ok) {
        return res.json().then(errData => { throw new Error(errData.error || "Giao dịch lỗi"); });
      }
      return res.json();
    })
    .then(data => {
      submitOtpResetBtn.disabled = false;
      submitOtpResetBtn.innerText = "Xác Nhận Đặt Lại Mật Khẩu";
      
      // Redirect to main panel
      otpPanel.style.display = "none";
      mainPanel.style.display = "block";
      
      // Auto fill the email
      emailInput.value = activeRecoveredEmail;
      passwordInput.value = "";
      errorMsg.innerText = "Đặt lại mật khẩu thành công! Bạn hãy đăng nhập bằng mật khẩu mới vừa thiết lập nhé.";
      errorMsg.style.color = "#10b981";
      errorMsg.style.background = "rgba(16,185,129,0.1)";
      errorMsg.style.borderColor = "rgba(16,185,129,0.2)";
      errorMsg.style.display = "block";
    })
    .catch(err => {
      submitOtpResetBtn.disabled = false;
      submitOtpResetBtn.innerText = "Xác Nhận Đặt Lại Mật Khẩu";
      otpErrorMsg.innerText = err.message || "Mã xác nhận OTP không đúng hoặc đã hết hạn.";
      otpErrorMsg.style.display = "block";
    });
  };
}

function logoutUser() {
  localStorage.removeItem("userEmail");
  localStorage.removeItem("vipToken");
  location.reload();
}

function updateUserNavStatus() {
  const container = document.getElementById("user-nav-status");
  if (!container) return;

  const email = localStorage.getItem("userEmail");
  const isVip = localStorage.getItem("vipToken");

  if (email) {
    if (isVip) {
      container.innerHTML = `
        <span style="display: flex; align-items: center; gap: 6px; color: #f59e0b; font-weight: bold; background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2); padding: 4px 10px; border-radius: 6px; font-size: 0.85rem;">
          <i class="fa-solid fa-crown"></i> VIP THÀNH VIÊN
        </span>
        <span style="color: var(--text-main); font-weight: 500; font-size: 0.85rem; max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${email}</span>
        <a href="javascript:void(0)" onclick="logoutUser()" style="color: var(--text-muted); text-decoration: none; font-size: 0.82rem; margin-left: 8px; display: flex; align-items: center; gap: 4px; transition: var(--transition-smooth);" onmouseover="this.style.color='white'" onmouseout="this.style.color='var(--text-muted)'">
          <i class="fa-solid fa-right-from-bracket"></i> Đăng Xuất
        </a>
      `;
    } else {
      container.innerHTML = `
        <span style="display: flex; align-items: center; gap: 6px; color: #10b981; font-weight: bold; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); padding: 4px 10px; border-radius: 6px; font-size: 0.8rem;">
          THÀNH VIÊN THƯỜNG
        </span>
        <span style="color: var(--text-main); font-weight: 500; font-size: 0.85rem; max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${email}</span>
        <a href="javascript:void(0)" onclick="logoutUser()" style="color: var(--text-muted); text-decoration: none; font-size: 0.82rem; margin-left: 8px; display: flex; align-items: center; gap: 4px; transition: var(--transition-smooth);" onmouseover="this.style.color='white'" onmouseout="this.style.color='var(--text-muted)'">
          <i class="fa-solid fa-right-from-bracket"></i> Đăng Xuất
        </a>
      `;
    }
  } else {
    // Show login/register button
    container.innerHTML = `
      <button onclick="showAuthModal()" class="btn" style="padding: 10px 20px; font-size: 0.9rem; font-weight: bold; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); color: white; cursor: pointer; border-radius: 8px; transition: var(--transition-smooth); display: inline-flex; align-items: center; gap: 6px;">
        <i class="fa-solid fa-user-plus"></i> Đăng Ký / Đăng Nhập
      </button>
    `;
  }
}

function triggerVipUpgrade() {
  const email = localStorage.getItem("userEmail");
  if (!email) {
    showAuthModal(function(registeredEmail) {
      proceedToVipUpgrade();
    });
  } else {
    proceedToVipUpgrade();
  }
}

function proceedToVipUpgrade() {
  const memo = "VE_VIP_" + Math.floor(Date.now() / 1000).toString().slice(-6);
  showCheckoutModal(9000, memo, function(token) {
    localStorage.setItem("vipToken", token);
    alert('Chúc mừng! Bạn đã nâng cấp VIP thành viên thành công.');
    location.reload();
  });
}

function showFreeDownloadCountdown(onComplete) {
  if (typeof onComplete === "function") {
    onComplete();
  }
}

// Add CSS classes dynamically if FontAwesome or modal classes aren't styled
if (typeof window !== "undefined") {
  window.initCheckoutConfig = initCheckoutConfig;
  window.showCheckoutModal = showCheckoutModal;
  window.showAuthModal = showAuthModal;
  window.logoutUser = logoutUser;
  window.updateUserNavStatus = updateUserNavStatus;
  window.triggerVipUpgrade = triggerVipUpgrade;
  window.showFreeDownloadCountdown = showFreeDownloadCountdown;
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", updateUserNavStatus);
  } else {
    updateUserNavStatus();
  }
}
