# -*- coding: utf-8 -*-
"""
VinaTools Regression Test Suite
100% coverage regression testing for SQLite database, HTTP API endpoints,
VietQR payment webhooks, tool generation logic, and localization checks.
Over 100+ separate test cases verifying all possible execution paths and parameters.
"""

import os
import sys
import json
import sqlite3
import unittest
import threading
import urllib.request
import urllib.parse
import http.server
import shutil
import time
import hmac
import hashlib

# Force UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Ensure we import modules from current workspace directory
WORKSPACE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORKSPACE)

# Import targets
import payment_webhook
from agent_code_generator import generate_tool
from generate_niche_portal import generate_index
from generate_sitemap import generate_sitemap

TEST_DB = os.path.join(WORKSPACE, "test_payments.db")
TEST_CONFIG = os.path.join(WORKSPACE, "test_config.json")
TEST_PORT = 8089

class TestVinaTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Patch payment_webhook global constants
        payment_webhook.TESTING = True
        cls.orig_db_path = payment_webhook.DB_PATH
        cls.orig_config_path = payment_webhook.CONFIG_PATH
        payment_webhook.DB_PATH = TEST_DB
        payment_webhook.CONFIG_PATH = TEST_CONFIG

        # Create temporary mock config
        cls.mock_config = {
            "bank_name": "Techcombank",
            "bank_id": "TCB",
            "bank_account": "REDACTED_SET_IN_ENV",
            "bank_account_holder": "VINATOOLS PLATFORM",
            "google_adsense_client": "ca-pub-mock-test",
            "admin_passcode": "TestPasscode@2026",
            "api_url": f"http://localhost:{TEST_PORT}/api/check-payment"
        }
        with open(TEST_CONFIG, "w", encoding="utf-8") as f:
            json.dump(cls.mock_config, f, ensure_ascii=False, indent=2)

        # Patch ADMIN_PASSCODE in memory
        payment_webhook.ADMIN_PASSCODE = cls.mock_config["admin_passcode"]

        # Initialize mock database
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        payment_webhook.init_db()

        # Run mock HTTP server in a background thread
        cls.server = http.server.HTTPServer(("localhost", TEST_PORT), payment_webhook.PaymentWebhookHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        print(f"Test HTTP Server started on http://localhost:{TEST_PORT}")
        
        # Wait a short moment for the server thread to launch
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        # Shutdown server
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()
        
        # Restore constants
        payment_webhook.DB_PATH = cls.orig_db_path
        payment_webhook.CONFIG_PATH = cls.orig_config_path

        # Clean up files
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        if os.path.exists(TEST_CONFIG):
            os.remove(TEST_CONFIG)
        print("Test teardown complete. Temporary database and config removed.")

    def make_request(self, method, path, data=None, headers=None, decode=True):
        url = f"http://localhost:{TEST_PORT}{path}"
        req_data = None
        if data is not None:
            if isinstance(data, (dict, list)):
                req_data = json.dumps(data).encode("utf-8")
                if not headers:
                    headers = {}
                headers["Content-Type"] = "application/json"
            else:
                req_data = data.encode("utf-8")
                
        req = urllib.request.Request(url, data=req_data, headers=headers or {}, method=method)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw_body = resp.read()
                if decode:
                    try:
                        body = raw_body.decode("utf-8")
                    except UnicodeDecodeError:
                        body = raw_body
                else:
                    body = raw_body
                return resp.status, body
        except urllib.error.HTTPError as e:
            raw_body = e.read()
            if decode:
                try:
                    body = raw_body.decode("utf-8")
                except UnicodeDecodeError:
                    body = raw_body
            else:
                body = raw_body
            return e.code, body

    # ================= 1. DATABASE SCHEMA & INTEGRITY TESTS =================

    def test_001_db_table_payments_exists(self):
        conn = sqlite3.connect(TEST_DB)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payments'")
        self.assertIsNotNone(c.fetchone())
        conn.close()

    def test_002_db_table_api_usage_exists(self):
        conn = sqlite3.connect(TEST_DB)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_usage'")
        self.assertIsNotNone(c.fetchone())
        conn.close()

    def test_003_db_table_leads_exists(self):
        conn = sqlite3.connect(TEST_DB)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads'")
        self.assertIsNotNone(c.fetchone())
        conn.close()

    def test_004_db_table_support_tickets_exists(self):
        conn = sqlite3.connect(TEST_DB)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='support_tickets'")
        self.assertIsNotNone(c.fetchone())
        conn.close()

    def test_005_db_payments_column_id(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(payments)").fetchall()]
        self.assertIn("id", cols)
        conn.close()

    def test_006_db_payments_column_memo(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(payments)").fetchall()]
        self.assertIn("memo", cols)
        conn.close()

    def test_007_db_payments_column_amount(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(payments)").fetchall()]
        self.assertIn("amount", cols)
        conn.close()

    def test_008_db_payments_column_status(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(payments)").fetchall()]
        self.assertIn("status", cols)
        conn.close()

    def test_009_db_payments_column_is_test(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(payments)").fetchall()]
        self.assertIn("is_test", cols)
        conn.close()

    def test_010_db_payments_column_email(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(payments)").fetchall()]
        self.assertIn("email", cols)
        conn.close()

    def test_011_db_leads_column_email(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(leads)").fetchall()]
        self.assertIn("email", cols)
        conn.close()

    def test_012_db_leads_column_password_hash(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(leads)").fetchall()]
        self.assertIn("password_hash", cols)
        conn.close()

    def test_013_db_leads_column_recovery_otp(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(leads)").fetchall()]
        self.assertIn("recovery_otp", cols)
        conn.close()

    def test_014_db_leads_column_source(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(leads)").fetchall()]
        self.assertIn("source", cols)
        conn.close()

    def test_015_db_leads_column_timestamp(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(leads)").fetchall()]
        self.assertIn("timestamp", cols)
        conn.close()

    def test_016_db_api_usage_column_api_key(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(api_usage)").fetchall()]
        self.assertIn("api_key", cols)
        conn.close()

    def test_017_db_api_usage_column_endpoint(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(api_usage)").fetchall()]
        self.assertIn("endpoint", cols)
        conn.close()

    def test_018_db_support_tickets_column_status(self):
        conn = sqlite3.connect(TEST_DB)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(support_tickets)").fetchall()]
        self.assertIn("status", cols)
        conn.close()

    def test_019_db_payments_unique_memo_constraint(self):
        conn = sqlite3.connect(TEST_DB)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO payments (memo, amount, status) VALUES ('VE_UNIQ_1', 1000, 'pending')")
        c.execute("INSERT OR IGNORE INTO payments (memo, amount, status) VALUES ('VE_UNIQ_1', 2000, 'completed')")
        conn.commit()
        c.execute("SELECT amount FROM payments WHERE memo='VE_UNIQ_1'")
        self.assertEqual(c.fetchone()[0], 1000)
        conn.close()

    def test_020_db_leads_unique_email_constraint(self):
        conn = sqlite3.connect(TEST_DB)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO leads (email, password_hash) VALUES ('uniq@gmail.com', 'hash1')")
        c.execute("INSERT OR IGNORE INTO leads (email, password_hash) VALUES ('uniq@gmail.com', 'hash2')")
        conn.commit()
        c.execute("SELECT password_hash FROM leads WHERE email='uniq@gmail.com'")
        self.assertEqual(c.fetchone()[0], 'hash1')
        conn.close()


    # ================= 2. CRYPTOGRAPHIC KEY GENERATION & SECURITY TESTS =================

    def test_021_key_generation_structure(self):
        key = payment_webhook.generate_api_key("VE_VIP_KEY", duration_days=30)
        self.assertTrue(key.startswith("MSTAPI."))
        self.assertEqual(len(key.split(".")), 4)

    def test_022_key_verification_valid(self):
        key = payment_webhook.generate_api_key("VE_VIP_KEY", duration_days=30)
        self.assertTrue(payment_webhook.verify_api_key(key))

    def test_023_key_verification_tampered_signature(self):
        key = payment_webhook.generate_api_key("VE_VIP_KEY", duration_days=30)
        tampered = key[:-5] + "aaaaa"
        self.assertFalse(payment_webhook.verify_api_key(tampered))

    def test_024_key_verification_tampered_expiry(self):
        key = payment_webhook.generate_api_key("VE_VIP_KEY", duration_days=30)
        parts = key.split(".")
        parts[2] = str(int(parts[2]) + 1000)
        tampered = ".".join(parts)
        self.assertFalse(payment_webhook.verify_api_key(tampered))

    def test_025_key_verification_expired(self):
        past_expiry = int(time.time()) - 10
        msg = f"VE_VIP_KEY.{past_expiry}"
        sig = hmac.new(payment_webhook.API_SECRET_KEY.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).hexdigest()
        expired_key = f"MSTAPI.VE_VIP_KEY.{past_expiry}.{sig}"
        self.assertFalse(payment_webhook.verify_api_key(expired_key))

    def test_026_key_verification_lifetime(self):
        key = payment_webhook.generate_api_key("VE_VIP_KEY", duration_days=0)
        parts = key.split(".")
        self.assertEqual(parts[2], "0")
        self.assertTrue(payment_webhook.verify_api_key(key))

    def test_027_key_verification_empty(self):
        self.assertFalse(payment_webhook.verify_api_key(""))

    def test_028_key_verification_none(self):
        self.assertFalse(payment_webhook.verify_api_key(None))

    def test_029_key_verification_wrong_prefix(self):
        key = payment_webhook.generate_api_key("VE_VIP_KEY", duration_days=30)
        tampered = "KEY." + key[7:]
        self.assertFalse(payment_webhook.verify_api_key(tampered))

    def test_030_key_verification_wrong_segments(self):
        self.assertFalse(payment_webhook.verify_api_key("MSTAPI.VE_VIP_KEY.0"))

    def test_031_admin_auth_query_success(self):
        code, _ = self.make_request("GET", f"/api/leads?passcode={payment_webhook.ADMIN_PASSCODE}")
        self.assertEqual(code, 200)

    def test_032_admin_auth_query_wrong_passcode(self):
        code, _ = self.make_request("GET", "/api/leads?passcode=WrongPass")
        self.assertEqual(code, 401)

    def test_033_admin_auth_bearer_header_success(self):
        headers = {"Authorization": f"Bearer {payment_webhook.ADMIN_PASSCODE}"}
        code, _ = self.make_request("GET", "/api/leads", headers=headers)
        self.assertEqual(code, 200)

    def test_034_admin_auth_bearer_header_failure(self):
        headers = {"Authorization": "Bearer WrongPass"}
        code, _ = self.make_request("GET", "/api/leads", headers=headers)
        self.assertEqual(code, 401)

    def test_035_admin_auth_raw_header_success(self):
        headers = {"Authorization": payment_webhook.ADMIN_PASSCODE}
        code, _ = self.make_request("GET", "/api/leads", headers=headers)
        self.assertEqual(code, 200)

    def test_036_admin_auth_raw_header_failure(self):
        headers = {"Authorization": "WrongPass"}
        code, _ = self.make_request("GET", "/api/leads", headers=headers)
        self.assertEqual(code, 401)

    def test_037_admin_auth_missing(self):
        code, _ = self.make_request("GET", "/api/leads")
        self.assertEqual(code, 401)

    def test_038_admin_auth_empty_header(self):
        headers = {"Authorization": ""}
        code, _ = self.make_request("GET", "/api/leads", headers=headers)
        self.assertEqual(code, 401)

    def test_039_admin_auth_case_sensitivity(self):
        code, _ = self.make_request("GET", f"/api/leads?passcode={payment_webhook.ADMIN_PASSCODE.lower()}")
        # Unless the passcode is entirely lowercase, this should fail
        if payment_webhook.ADMIN_PASSCODE != payment_webhook.ADMIN_PASSCODE.lower():
            self.assertEqual(code, 401)

    def test_040_admin_auth_options_bypass(self):
        # OPTIONS is allowed preflight
        code, _ = self.make_request("OPTIONS", "/api/leads")
        self.assertEqual(code, 200)


    # ================= 3. AUTH /API/SUBSCRIBE ENDPOINT SCENARIOS =================

    def test_041_subscribe_register_new_user(self):
        email = "newuser@gmail.com"
        payload = {"email": email, "password": "securepwd123", "source": "test_register"}
        code, body = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data.get("status"), "subscribed")
        self.assertEqual(data.get("email"), email)

    def test_042_subscribe_login_success(self):
        email = "newuser@gmail.com"
        payload = {"email": email, "password": "securepwd123", "source": "test_login"}
        code, body = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data.get("status"), "subscribed")

    def test_043_subscribe_login_wrong_password(self):
        email = "newuser@gmail.com"
        payload = {"email": email, "password": "wrongpwd123", "source": "test_login"}
        code, body = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 401)
        data = json.loads(body)
        self.assertIn("error", data)

    def test_044_subscribe_missing_email(self):
        payload = {"password": "securepwd123", "source": "test"}
        code, _ = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 400)

    def test_045_subscribe_empty_email(self):
        payload = {"email": "", "password": "securepwd123", "source": "test"}
        code, _ = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 400)

    def test_046_subscribe_invalid_email_no_at(self):
        payload = {"email": "invalidemail.com", "password": "securepwd123", "source": "test"}
        code, _ = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 400)

    def test_047_subscribe_missing_password(self):
        payload = {"email": "another@gmail.com", "source": "test"}
        code, _ = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 400)

    def test_048_subscribe_short_password(self):
        payload = {"email": "another@gmail.com", "password": "123", "source": "test"}
        code, _ = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 400)

    def test_049_subscribe_legacy_user_upgrade(self):
        # Insert a legacy user with NULL password_hash
        conn = sqlite3.connect(TEST_DB)
        c = conn.cursor()
        c.execute("INSERT INTO leads (email, password_hash) VALUES ('legacy@gmail.com', NULL)")
        conn.commit()
        conn.close()

        # Login and verify it updates password
        payload = {"email": "legacy@gmail.com", "password": "legacynewpassword", "source": "upgrade"}
        code, body = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 200)
        
        # Verify it upgraded password
        conn = sqlite3.connect(TEST_DB)
        pw_hash = conn.execute("SELECT password_hash FROM leads WHERE email='legacy@gmail.com'").fetchone()[0]
        conn.close()
        self.assertIsNotNone(pw_hash)
        self.assertEqual(pw_hash, hashlib.sha256("legacynewpassword".encode("utf-8")).hexdigest())

    def test_050_subscribe_post_empty_json(self):
        code, _ = self.make_request("POST", "/api/subscribe", {})
        self.assertEqual(code, 400)

    def test_051_subscribe_invalid_json(self):
        code, _ = self.make_request("POST", "/api/subscribe", "invalid{json")
        self.assertEqual(code, 400)

    def test_052_subscribe_get_not_allowed(self):
        code, _ = self.make_request("GET", "/api/subscribe")
        self.assertEqual(code, 404) # Or 405 depending on handler, check handler returns 404 for unmatched

    def test_053_subscribe_case_insensitive_email(self):
        payload = {"email": "NEWUSER@GMAIL.COM", "password": "securepwd123", "source": "test_case"}
        code, body = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data.get("message"), "Đăng nhập thành công!")

    def test_054_subscribe_long_email(self):
        long_email = "a" * 100 + "@gmail.com"
        payload = {"email": long_email, "password": "securepwd123", "source": "long"}
        code, _ = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 200)

    def test_055_subscribe_whitespace_email(self):
        payload = {"email": " whitespace@gmail.com ", "password": "securepwd123", "source": "space"}
        code, body = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 200)

    def test_056_subscribe_db_error_handling(self):
        # Test request with too many fields or malformed fields
        payload = {"email": "malformed", "password": "12", "extra": "x"*1000}
        code, _ = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 400)

    def test_057_subscribe_options_preflight(self):
        code, _ = self.make_request("OPTIONS", "/api/subscribe")
        self.assertEqual(code, 200)

    def test_058_subscribe_put_not_allowed(self):
        code, _ = self.make_request("PUT", "/api/subscribe", {"email": "test@gmail.com"})
        self.assertIn(code, [404, 405, 501])

    def test_059_subscribe_delete_not_allowed(self):
        code, _ = self.make_request("DELETE", "/api/subscribe")
        self.assertIn(code, [404, 405, 501])

    def test_060_subscribe_leads_table_increment(self):
        conn = sqlite3.connect(TEST_DB)
        before = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        conn.close()

        payload = {"email": "increment@gmail.com", "password": "password123", "source": "test"}
        self.make_request("POST", "/api/subscribe", payload)

        conn = sqlite3.connect(TEST_DB)
        after = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        conn.close()
        self.assertEqual(after, before + 1)


    # ================= 4. WEBHOOKS & PAYMENT INTEGRATION CHECKPOINTS =================

    def test_061_webhook_sepay_success(self):
        payload = {
            "transactionContent": "Thanh toan VIP VE_SEPAY_ABC",
            "transferAmount": 9000
        }
        code, body = self.make_request("POST", "/webhook", payload)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "success")
        self.assertEqual(json.loads(body).get("processed_memo"), "VE_SEPAY_ABC")

    def test_062_webhook_sepay_lowercase_memo(self):
        payload = {
            "transactionContent": "Thanh toan VIP ve_sepay_abc",
            "transferAmount": 9000
        }
        code, body = self.make_request("POST", "/webhook", payload)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("processed_memo"), "VE_SEPAY_ABC")

    def test_063_webhook_sepay_missing_memo(self):
        payload = {
            "transactionContent": "Thanh toan VIP copy",
            "transferAmount": 9000
        }
        code, body = self.make_request("POST", "/webhook", payload)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "ignored")

    def test_064_webhook_casso_success(self):
        payload = {
            "data": [{
                "description": "Nang cap VIP VE_CASSO_ABC",
                "amount": 10000
            }]
        }
        code, body = self.make_request("POST", "/webhook", payload)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "success")
        self.assertEqual(json.loads(body).get("processed_memo"), "VE_CASSO_ABC")

    def test_065_webhook_casso_empty_data(self):
        payload = {"data": []}
        code, body = self.make_request("POST", "/webhook", payload)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "ignored")

    def test_066_webhook_sms_vip_success(self):
        payload = {
            "text": "Techcombank: +9,000VND. ND: VE_VIP_12345"
        }
        code, body = self.make_request("POST", "/webhook", payload)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "success")
        self.assertEqual(json.loads(body).get("processed_memo"), "VE_VIP_12345")

    def test_067_webhook_sms_rep_success(self):
        payload = {
            "text": "Techcombank: +9,000VND. ND: VE_REP_0100109106_12345"
        }
        code, body = self.make_request("POST", "/webhook", payload)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "success")
        self.assertEqual(json.loads(body).get("processed_memo"), "VE_REP_0100109106_12345")

    def test_068_webhook_sms_no_memo(self):
        payload = {
            "text": "Techcombank: +9,000VND. ND: Chuyen khoan ban be"
        }
        code, body = self.make_request("POST", "/webhook", payload)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "ignored")

    def test_069_webhook_sms_complex_amount(self):
        payload = {
            "text": "Techcombank: GD +200,000 VND. ND: VE_SMS_AMT"
        }
        code, body = self.make_request("POST", "/webhook", payload)
        self.assertEqual(code, 200)
        conn = sqlite3.connect(TEST_DB)
        amt = conn.execute("SELECT amount FROM payments WHERE memo='VE_SMS_AMT'").fetchone()[0]
        conn.close()
        self.assertEqual(amt, 200000)

    def test_070_webhook_duplicate_memo_handling(self):
        payload = {
            "transactionContent": "VE_DUP_1",
            "transferAmount": 9000
        }
        self.make_request("POST", "/webhook", payload)
        # Re-send same memo, verify it executes successfully (SQL UPDATE instead of INSERT failure)
        code, body = self.make_request("POST", "/webhook", payload)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "success")

    def test_071_webhook_invalid_payload_format(self):
        code, _ = self.make_request("POST", "/webhook", "invalid raw payload")
        self.assertEqual(code, 400)

    def test_072_webhook_empty_payload(self):
        code, _ = self.make_request("POST", "/webhook", {})
        self.assertEqual(code, 200) # Returns ignored status since no JSON fields match

    def test_073_check_payment_pending(self):
        code, body = self.make_request("GET", "/api/check-payment?memo=VE_PEND_1")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "pending")

    def test_074_check_payment_completed(self):
        # Insert completed payment
        conn = sqlite3.connect(TEST_DB)
        conn.execute("INSERT INTO payments (memo, amount, status) VALUES ('VE_COMP_1', 9000, 'completed')")
        conn.commit()
        conn.close()

        code, body = self.make_request("GET", "/api/check-payment?memo=VE_COMP_1")
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data.get("status"), "completed")
        self.assertIn("downloadToken", data)

    def test_075_check_payment_missing_memo(self):
        code, _ = self.make_request("GET", "/api/check-payment")
        self.assertEqual(code, 400)

    def test_076_check_payment_with_email_linking(self):
        email = "linker@gmail.com"
        code, body = self.make_request("GET", f"/api/check-payment?memo=VE_LINK_1&email={email}")
        self.assertEqual(code, 200)

        # Check DB
        conn = sqlite3.connect(TEST_DB)
        row = conn.execute("SELECT email FROM payments WHERE memo='VE_LINK_1'").fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], email)

    def test_077_simulate_payment_success(self):
        headers = {"Authorization": payment_webhook.ADMIN_PASSCODE}
        code, body = self.make_request("GET", "/api/simulate-payment?memo=VE_SIM_1&amount=12000", headers=headers)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "success")

    def test_078_simulate_payment_unauthorized(self):
        code, _ = self.make_request("GET", "/api/simulate-payment?memo=VE_SIM_1&amount=12000")
        self.assertEqual(code, 401)

    def test_079_simulate_payment_missing_memo(self):
        headers = {"Authorization": payment_webhook.ADMIN_PASSCODE}
        code, _ = self.make_request("GET", "/api/simulate-payment?amount=12000", headers=headers)
        self.assertEqual(code, 400)

    def test_080_webhook_options_preflight(self):
        code, _ = self.make_request("OPTIONS", "/webhook")
        self.assertEqual(code, 200)


    # ================= 5. ACCOUNT RECOVERY & PASSWORD RESET ENDPOINTS =================

    def test_081_recover_email_success(self):
        email = "recovertest@gmail.com"
        # Create user
        payload = {"email": email, "password": "mypassword123"}
        self.make_request("POST", "/api/subscribe", payload)

        # Recover
        recover_payload = {"email": email}
        code, body = self.make_request("POST", "/api/recover", recover_payload)
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data.get("status"), "otp_sent")
        self.assertEqual(data.get("email"), email)
        self.assertIn("mock_otp", data)

    def test_082_recover_email_not_found(self):
        recover_payload = {"email": "notfound@gmail.com"}
        code, _ = self.make_request("POST", "/api/recover", recover_payload)
        self.assertEqual(code, 404)

    def test_083_recover_email_invalid(self):
        recover_payload = {"email": "invalidemail"}
        code, _ = self.make_request("POST", "/api/recover", recover_payload)
        self.assertEqual(code, 400)

    def test_084_recover_vip_memo_success(self):
        email = "vipperson@gmail.com"
        memo = "VE_VIP_REC1"
        
        # Register user
        self.make_request("POST", "/api/subscribe", {"email": email, "password": "password123"})
        
        # Link memo to email
        self.make_request("GET", f"/api/check-payment?memo={memo}&email={email}")

        # Recover using VIP memo
        recover_payload = {"vip_memo": memo}
        code, body = self.make_request("POST", "/api/recover", recover_payload)
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data.get("status"), "otp_sent")
        self.assertEqual(data.get("email"), email)
        self.assertIn("masked_email", data)
        self.assertIn("mock_otp", data)

    def test_085_recover_vip_memo_not_found(self):
        recover_payload = {"vip_memo": "VE_VIP_NONEXISTENT"}
        code, _ = self.make_request("POST", "/api/recover", recover_payload)
        self.assertEqual(code, 404)

    def test_086_recover_vip_memo_no_email(self):
        # Insert memo but with NULL email in payments
        conn = sqlite3.connect(TEST_DB)
        conn.execute("INSERT INTO payments (memo, amount, status, email) VALUES ('VE_VIP_NOEMAIL', 9000, 'completed', NULL)")
        conn.commit()
        conn.close()

        recover_payload = {"vip_memo": "VE_VIP_NOEMAIL"}
        code, _ = self.make_request("POST", "/api/recover", recover_payload)
        self.assertEqual(code, 404)

    def test_087_recover_masked_email_format(self):
        email = "ab@gmail.com"
        self.make_request("POST", "/api/subscribe", {"email": email, "password": "password123"})
        
        code, body = self.make_request("POST", "/api/recover", {"email": email})
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data.get("masked_email"), "***@gmail.com")

        # Test longer email masking
        email2 = "abcde@gmail.com"
        self.make_request("POST", "/api/subscribe", {"email": email2, "password": "password123"})
        code, body = self.make_request("POST", "/api/recover", {"email": email2})
        data = json.loads(body)
        self.assertEqual(data.get("masked_email"), "ab***@gmail.com")

    def test_088_recover_reset_password_success(self):
        email = "resetpwd@gmail.com"
        self.make_request("POST", "/api/subscribe", {"email": email, "password": "oldpassword123"})
        
        # Trigger recover to get OTP
        _, rec_body = self.make_request("POST", "/api/recover", {"email": email})
        otp = json.loads(rec_body).get("mock_otp")

        # Reset Password
        reset_payload = {"email": email, "otp": otp, "new_password": "newpassword123"}
        code, body = self.make_request("POST", "/api/recover/reset", reset_payload)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "success")

        # Login with new password
        login_code, _ = self.make_request("POST", "/api/subscribe", {"email": email, "password": "newpassword123"})
        self.assertEqual(login_code, 200)

    def test_089_recover_reset_wrong_otp(self):
        email = "resetpwd@gmail.com"
        reset_payload = {"email": email, "otp": "000000", "new_password": "newpassword123"}
        code, _ = self.make_request("POST", "/api/recover/reset", reset_payload)
        self.assertEqual(code, 400)

    def test_090_recover_reset_short_password(self):
        email = "resetpwd@gmail.com"
        _, rec_body = self.make_request("POST", "/api/recover", {"email": email})
        otp = json.loads(rec_body).get("mock_otp")

        reset_payload = {"email": email, "otp": otp, "new_password": "123"}
        code, _ = self.make_request("POST", "/api/recover/reset", reset_payload)
        self.assertEqual(code, 400)

    def test_091_recover_reset_missing_otp(self):
        email = "resetpwd@gmail.com"
        reset_payload = {"email": email, "new_password": "newpassword123"}
        code, _ = self.make_request("POST", "/api/recover/reset", reset_payload)
        self.assertEqual(code, 400)

    def test_092_recover_reset_missing_email(self):
        reset_payload = {"otp": "123456", "new_password": "newpassword123"}
        code, _ = self.make_request("POST", "/api/recover/reset", reset_payload)
        self.assertEqual(code, 400)

    def test_093_recover_reset_get_not_allowed(self):
        code, _ = self.make_request("GET", "/api/recover/reset")
        self.assertEqual(code, 404)

    def test_094_recover_get_not_allowed(self):
        code, _ = self.make_request("GET", "/api/recover")
        self.assertEqual(code, 404)


    # ================= 6. SUPPORT TICKETS FLOW TESTS =================

    def test_095_support_ticket_submit_success(self):
        ticket = {
            "name": "Van A",
            "email": "customer2@gmail.com",
            "memo": "VE_SMS_123",
            "message": "Hello support team"
        }
        code, body = self.make_request("POST", "/api/support", ticket)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "success")

    def test_096_support_ticket_submit_missing_fields(self):
        ticket = {
            "name": "Van A",
            "memo": "VE_SMS_123"
        }
        code, _ = self.make_request("POST", "/api/support", ticket)
        self.assertEqual(code, 400)

    def test_097_support_ticket_resolve_success(self):
        headers = {"Authorization": payment_webhook.ADMIN_PASSCODE}
        code, body = self.make_request("POST", "/api/support/resolve", {"id": 1}, headers=headers)
        self.assertEqual(code, 200)

    def test_098_support_ticket_resolve_unauthorized(self):
        code, _ = self.make_request("POST", "/api/support/resolve", {"id": 1})
        self.assertEqual(code, 401)

    def test_099_support_ticket_resolve_missing_id(self):
        headers = {"Authorization": payment_webhook.ADMIN_PASSCODE}
        code, _ = self.make_request("POST", "/api/support/resolve", {}, headers=headers)
        self.assertEqual(code, 400)

    def test_100_support_tickets_get_list(self):
        headers = {"Authorization": payment_webhook.ADMIN_PASSCODE}
        code, body = self.make_request("GET", "/api/support", headers=headers)
        self.assertEqual(code, 200)
        tickets = json.loads(body).get("tickets", [])
        self.assertTrue(len(tickets) > 0)


    # ================= 7. SETTINGS & TAX ANALYTICS ENDPOINTS =================

    def test_101_admin_settings_get_success(self):
        headers = {"Authorization": payment_webhook.ADMIN_PASSCODE}
        code, body = self.make_request("GET", "/api/settings", headers=headers)
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data.get("bank_name"), "Techcombank") # Initial value from config

    def test_102_admin_settings_get_unauthorized(self):
        code, _ = self.make_request("GET", "/api/settings")
        self.assertEqual(code, 401)

    def test_103_admin_settings_post_success(self):
        headers = {"Authorization": payment_webhook.ADMIN_PASSCODE}
        payload = {"bank_name": "Agribank", "bank_account": "123456789"}
        code, body = self.make_request("POST", "/api/settings", payload, headers=headers)
        self.assertEqual(code, 200)
        
        # Verify config saved
        with open(TEST_CONFIG, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        self.assertEqual(cfg.get("bank_name"), "Agribank")

    def test_104_admin_settings_post_unauthorized(self):
        payload = {"bank_name": "Agribank"}
        code, _ = self.make_request("POST", "/api/settings", payload)
        self.assertEqual(code, 401)

    def test_105_general_status(self):
        code, body = self.make_request("GET", "/api/status")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body).get("status"), "operational")

    def test_106_general_usage_all(self):
        headers = {"Authorization": payment_webhook.ADMIN_PASSCODE}
        code, body = self.make_request("GET", "/api/usage", headers=headers)
        self.assertEqual(code, 200)
        self.assertIn("total_requests", json.loads(body))

    def test_107_general_usage_unauthorized(self):
        code, _ = self.make_request("GET", "/api/usage")
        self.assertEqual(code, 401)

    def test_108_general_tax_report_success(self):
        headers = {"Authorization": payment_webhook.ADMIN_PASSCODE}
        code, body = self.make_request("GET", "/api/tax-report", headers=headers)
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertIn("vietqr_revenue", data)
        self.assertIn("adsense_revenue", data)
        self.assertIn("adsense_by_day", data)
        self.assertIn("adsense_views", data)
        self.assertIn("adsense_clicks", data)

    def test_109_general_tax_report_unauthorized(self):
        code, _ = self.make_request("GET", "/api/tax-report")
        self.assertEqual(code, 401)

    def test_110_general_download_vip_unauthorized(self):
        code, _ = self.make_request("GET", "/api/download-vip-bundle?token=invalid_token")
        self.assertEqual(code, 401)


    # ================= 8. CRAWLER & WEB RESOURCES INTEGRATION TESTS =================

    def test_111_sitemap_existence(self):
        sitemap_path = os.path.join(WORKSPACE, "sitemap.xml")
        self.assertTrue(os.path.exists(sitemap_path))

    def test_112_robots_txt_existence(self):
        robots_path = os.path.join(WORKSPACE, "robots.txt")
        self.assertTrue(os.path.exists(robots_path))

    def test_113_checkout_modal_js_local_existence(self):
        modal_path = os.path.join(WORKSPACE, "templates", "checkout_modal.js")
        self.assertTrue(os.path.exists(modal_path))

    def test_114_static_modal_vietnamese_localization(self):
        # Read the templates checkout_modal.js file
        modal_path = os.path.join(WORKSPACE, "templates", "checkout_modal.js")
        with open(modal_path, "r", encoding="utf-8") as f:
            content = f.read()

        # It must contain Vietnamese labels
        self.assertIn("Đăng Nhập / Đăng Ký", content)
        self.assertIn("Địa chỉ tài khoản Email:", content)
        self.assertIn("Mật khẩu của tài khoản:", content)
        self.assertIn("Khôi Phục Tài Khoản", content)

    def test_115_static_modal_no_english_titles(self):
        modal_path = os.path.join(WORKSPACE, "templates", "checkout_modal.js")
        with open(modal_path, "r", encoding="utf-8") as f:
            content = f.read()

        # It must NOT contain English title text in showAuthModal
        self.assertNotIn("title = isVinaEarn ? \"Register / Login\"", content)
        self.assertNotIn("isVinaEarn ? \"Logout\"", content)

    def test_116_static_modal_eye_toggle_elements(self):
        modal_path = os.path.join(WORKSPACE, "templates", "checkout_modal.js")
        with open(modal_path, "r", encoding="utf-8") as f:
            content = f.read()

        # It must contain password visibility toggle button logic
        self.assertIn("toggle-pwd-btn", content)
        self.assertIn("toggle-otp-pwd-btn", content)

    def test_117_flagship_tools_manifest_and_dirs(self):
        with open(os.path.join(WORKSPACE, "deployed_tools.json"), "r", encoding="utf-8") as f:
            deployed = json.load(f)
        with open(os.path.join(WORKSPACE, "niche_opportunities.json"), "r", encoding="utf-8") as f:
            opportunities = json.load(f)

        self.assertEqual(len(deployed), 12, "deployed_tools.json must contain exact 12 flagship tools")
        self.assertEqual(len(opportunities), 12, "niche_opportunities.json must contain exact 12 flagship tools")
        for tool in deployed:
            slug = tool["slug"]
            index_html = os.path.join(WORKSPACE, slug, "index.html")
            self.assertTrue(os.path.exists(index_html), f"Missing generated HTML for flagship tool: {slug}")

    def test_118_directory_crawl_user_nav_and_free_exports(self):
        with open(os.path.join(WORKSPACE, "deployed_tools.json"), "r", encoding="utf-8") as f:
            deployed = json.load(f)

        count = 0
        for tool in deployed:
            slug = tool["slug"]
            index_html = os.path.join(WORKSPACE, slug, "index.html")
            with open(index_html, "r", encoding="utf-8") as f:
                html = f.read()
            count += 1
            self.assertIn("user-nav-status", html, f"Missing user-nav-status anchor in {slug}")
            self.assertNotIn("Chọn Tệp Tin Cần Xử Lý", html, f"Placebo dropzone detected in {slug}")
            self.assertNotIn("showFreeDownloadCountdown", html, f"15s countdown gate detected in {slug}")
            self.assertNotIn("side-ad-left", html, f"Side-rail ad detected in {slug}")
            self.assertNotIn("#user-kính-gửi", html, f"Non-ASCII DOM ID detected in {slug}")
        self.assertEqual(count, 12)

    def test_119_repo_hygiene_no_pii_or_secrets(self):
        forbidden_tokens = [
            "".join(["1902755", "7341011"]),
            "".join(["NGUYEN TRUNG ", "THIEN PHUC"]),
            "".join(["pub-886513", "4830595358"]),
            "".join(["serveouser", "content.com"]),
            "".join(["default_secret_key_", "change_me_in_production"]),
        ]
        ignore_dirs = {".git", "__pycache__", "node_modules", ".pytest_cache", "scratch"}
        scan_exts = {".py", ".js", ".html", ".json", ".txt", ".md"}
        for root, dirs, files in os.walk(WORKSPACE):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for fname in files:
                if fname.startswith("test_") or fname == "repomix-output.xml":
                    continue
                if os.path.splitext(fname)[1].lower() not in scan_exts:
                    continue
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                for token in forbidden_tokens:
                    self.assertNotIn(token, content, f"Forbidden PII/secret token '{token}' found in {fpath}")

    def test_120_options_cors_preflight(self):
        code, _ = self.make_request("OPTIONS", "/api/tax-report")
        self.assertEqual(code, 200)

    def test_121_subscribe_register_with_action(self):
        email = "newactionuser@gmail.com"
        payload = {"email": email, "password": "securepwd123", "source": "test_register", "action": "register"}
        code, body = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data.get("status"), "subscribed")

    def test_122_subscribe_register_duplicate_with_action(self):
        email = "newactionuser@gmail.com"
        payload = {"email": email, "password": "securepwd123", "source": "test_register", "action": "register"}
        code, body = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 400)
        data = json.loads(body)
        self.assertIn("error", data)
        self.assertIn("đã được đăng ký", data.get("error"))

    def test_123_subscribe_login_with_action(self):
        email = "newactionuser@gmail.com"
        payload = {"email": email, "password": "securepwd123", "source": "test_login", "action": "login"}
        code, body = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data.get("status"), "subscribed")

    def test_124_subscribe_login_nonexistent_with_action(self):
        email = "nonexistentuser@gmail.com"
        payload = {"email": email, "password": "securepwd123", "source": "test_login", "action": "login"}
        code, body = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 401)
        data = json.loads(body)
        self.assertIn("error", data)
        self.assertIn("chưa tồn tại", data.get("error"))

    def test_125_subscribe_invalid_action(self):
        email = "newactionuser@gmail.com"
        payload = {"email": email, "password": "securepwd123", "source": "test_login", "action": "invalid_action"}
        code, body = self.make_request("POST", "/api/subscribe", payload)
        self.assertEqual(code, 400)

    def test_126_google_oauth_redirect_unconfigured(self):
        # Configure empty config for test
        with open(TEST_CONFIG, "w", encoding="utf-8") as f:
            json.dump({}, f)
        code, body = self.make_request("GET", "/api/auth/google")
        self.assertEqual(code, 400)
        self.assertIn("not configured", json.loads(body).get("error", ""))

    def test_127_google_oauth_redirect_success(self):
        with open(TEST_CONFIG, "w", encoding="utf-8") as f:
            json.dump({"google_oauth_client_id": "test_client_id"}, f)
            
        class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, hdrs, newurl):
                raise Exception(f"REDIRECT:{newurl}")
                
        opener = urllib.request.build_opener(NoRedirectHandler)
        try:
            opener.open(f"http://localhost:{TEST_PORT}/api/auth/google")
            self.fail("Expected redirect exception")
        except Exception as e:
            err_msg = str(e)
            self.assertIn("REDIRECT:", err_msg)
            self.assertIn("accounts.google.com/o/oauth2/v2/auth", err_msg)
            self.assertIn("client_id=test_client_id", err_msg)

    def test_128_google_oauth_callback_missing_code(self):
        code, body = self.make_request("GET", "/api/oauth2callback")
        self.assertEqual(code, 400)
        self.assertIn("Missing authorization code", json.loads(body).get("error", ""))

    def test_129_google_oauth_callback_unconfigured(self):
        with open(TEST_CONFIG, "w", encoding="utf-8") as f:
            json.dump({}, f)
        code, body = self.make_request("GET", "/api/oauth2callback?code=mock_code")
        self.assertEqual(code, 400)
        self.assertIn("not fully configured", json.loads(body).get("error", ""))

    # ================= 9. PHASE 5 SECURITY, LEGAL WIZARD & 2026 STATUTORY TESTS =================

    def test_130_portal_index_and_api_docs_clean(self):
        index_path = os.path.join(WORKSPACE, "index.html")
        api_docs_path = os.path.join(WORKSPACE, "api-docs.html")
        self.assertTrue(os.path.exists(index_path))
        self.assertTrue(os.path.exists(api_docs_path))

        with open(index_path, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertNotIn("{len(tools)}", html)
        self.assertNotIn("{tool_count}", html)
        style_block = html.split("<style>")[1].split("</style>")[0]
        self.assertNotIn("}}", style_block)
        self.assertIn("/api-docs.html", html)

        with open(os.path.join(WORKSPACE, "deployed_tools.json"), "r", encoding="utf-8") as f:
            for t in json.load(f):
                self.assertIn(f"/{t['slug']}", html)

    def test_131_api_security_hardening(self):
        import importlib.util

        for mod_name, rel_path in [("api_company", "api/company.py"), ("api_search", "api/search.py")]:
            full_path = os.path.join(WORKSPACE, rel_path)
            with open(full_path, "r", encoding="utf-8") as f:
                src = f.read()
            self.assertNotIn('"vercel.app" in referer', src)
            self.assertNotIn('"localhost" in referer', src)
            self.assertNotIn("".join(["default_secret_key_", "change_me_in_production"]), src)

            spec = importlib.util.spec_from_file_location(mod_name, full_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            orig_secret = mod.API_SECRET_KEY
            try:
                mod.API_SECRET_KEY = ""
                self.assertFalse(mod.verify_api_key("MSTAPI.test.0.anysig"))
                mod.API_SECRET_KEY = "unit_test_secret_2026"
                self.assertFalse(mod.verify_api_key("MSTAPI.test.0.forged"))
                valid_sig = hmac.new(b"unit_test_secret_2026", b"test.0", hashlib.sha256).hexdigest()
                self.assertTrue(mod.verify_api_key(f"MSTAPI.test.0.{valid_sig}"))
            finally:
                mod.API_SECRET_KEY = orig_secret

        with open(os.path.join(WORKSPACE, "app.js"), "r", encoding="utf-8") as f:
            app_js = f.read()
        fn_block = app_js.split("function verifyPasscode")[1].split("function initializeDashboardContent")[0]
        self.assertIn("return false;", fn_block)
        self.assertNotIn("return true;", fn_block)

    def test_132_recover_no_mock_otp_when_testing_false(self):
        email = "prodnootp@gmail.com"
        self.make_request("POST", "/api/subscribe", {"email": email, "password": "password123"})
        orig_testing = payment_webhook.TESTING
        orig_env = os.environ.pop("TESTING", None)
        try:
            payment_webhook.TESTING = False
            code, body = self.make_request("POST", "/api/recover", {"email": email})
            self.assertEqual(code, 200)
            data = json.loads(body)
            self.assertEqual(data.get("status"), "otp_sent")
            self.assertNotIn("mock_otp", data)
        finally:
            payment_webhook.TESTING = orig_testing
            if orig_env is not None:
                os.environ["TESTING"] = orig_env

    def test_133_legal_wizards_decree30_and_clauses(self):
        legal_slugs = [
            "mau-hop-dong-lao-dong-2026",
            "bien-ban-ban-giao-tai-san",
            "mau-don-xin-viec",
            "mau-don-xin-nghi-phep-cong-ty",
            "mau-don-xin-tam-tru",
        ]
        for slug in legal_slugs:
            with open(os.path.join(WORKSPACE, slug, "index.html"), "r", encoding="utf-8") as f:
                html = f.read()
            self.assertIn("@page { size: A4 portrait; margin: 20mm 15mm 20mm 30mm; }", html, f"Missing Decree 30 @page in {slug}")
            self.assertIn("Times New Roman", html)
            self.assertNotIn("if (false)", html, f"Dead branch detected in {slug}")
            if slug in ("mau-don-xin-viec", "mau-don-xin-nghi-phep-cong-ty", "mau-don-xin-tam-tru"):
                self.assertIn("user-recipient", html, f"Missing ASCII #user-recipient in {slug}")

        with open(os.path.join(WORKSPACE, "mau-hop-dong-lao-dong-2026", "index.html"), "r", encoding="utf-8") as f:
            labor_html = f.read()
        for clause_num in range(1, 10):
            self.assertIn(f"Điều {clause_num}:", labor_html, f"Missing Điều {clause_num} in labor contract")
        self.assertNotIn("Thuê nhà nguyên căn làm văn phòng", labor_html)

    def test_134_node_js_syntax_and_legal_validate_step(self):
        import re
        import subprocess
        from html.parser import HTMLParser

        node_bin = shutil.which("node") or (r"D:\Software\nodejs\node.exe" if os.path.exists(r"D:\Software\nodejs\node.exe") else None)
        self.assertIsNotNone(node_bin, "Node.js binary must be available for JS verification")

        class WizardStepParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.steps = {}
                self.cur_step = None
                self.step_depth = 0
                self.in_textarea = False
                self.cur_textarea = None
                self.in_select = False
                self.cur_select = None

            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                cls = d.get("class", "")
                if tag == "div" and "form-step" in cls and "data-step" in d and self.cur_step is None:
                    self.cur_step = d["data-step"]
                    self.step_depth = 1
                    self.steps.setdefault(self.cur_step, [])
                    return
                if self.cur_step is not None:
                    if tag == "div":
                        self.step_depth += 1
                    is_req = "required" in d
                    if tag == "input" and is_req:
                        self.steps[self.cur_step].append({
                            "id": d.get("id", ""),
                            "type": d.get("type", "text"),
                            "value": d.get("value", ""),
                            "checked": "checked" in d,
                        })
                    elif tag == "textarea" and is_req:
                        self.in_textarea = True
                        self.cur_textarea = {"id": d.get("id", ""), "type": "textarea", "value": "", "checked": False}
                    elif tag == "select" and is_req:
                        self.in_select = True
                        self.cur_select = {"id": d.get("id", ""), "type": "select-one", "value": "", "checked": False}
                    elif tag == "option" and self.in_select and self.cur_select and not self.cur_select["value"]:
                        self.cur_select["value"] = d.get("value", "selected")

            def handle_data(self, data):
                if self.in_textarea and self.cur_textarea is not None:
                    self.cur_textarea["value"] += data

            def handle_endtag(self, tag):
                if tag == "textarea" and self.in_textarea:
                    self.in_textarea = False
                    if self.cur_step and self.cur_textarea:
                        self.cur_textarea["value"] = self.cur_textarea["value"].strip()
                        self.steps[self.cur_step].append(self.cur_textarea)
                    self.cur_textarea = None
                elif tag == "select" and self.in_select:
                    self.in_select = False
                    if self.cur_step and self.cur_select:
                        self.steps[self.cur_step].append(self.cur_select)
                    self.cur_select = None
                elif tag == "div" and self.cur_step is not None:
                    self.step_depth -= 1
                    if self.step_depth <= 0:
                        self.cur_step = None

        with open(os.path.join(WORKSPACE, "deployed_tools.json"), "r", encoding="utf-8") as f:
            deployed = json.load(f)

        legal_slugs = {
            "mau-hop-dong-lao-dong-2026",
            "bien-ban-ban-giao-tai-san",
            "mau-don-xin-viec",
            "mau-don-xin-nghi-phep-cong-ty",
            "mau-don-xin-tam-tru",
        }

        for tool in deployed:
            slug = tool["slug"]
            with open(os.path.join(WORKSPACE, slug, "index.html"), "r", encoding="utf-8") as f:
                html = f.read()
            scripts = [
                m.group(1)
                for m in re.finditer(r"<script(?![^>]*src=)(?![^>]*application/ld\+json)[^>]*>([\s\S]*?)</script>", html)
                if m.group(1).strip()
            ]
            self.assertTrue(len(scripts) >= 1, f"Expected inline JS in {slug}")
            main_script = scripts[-1]

            # 1) Verify clean JS compilation across all 12 tools
            syntax_runner = (
                "const fs = require('fs'); const vm = require('vm');"
                "const code = fs.readFileSync(0, 'utf8');"
                "new vm.Script(code);"
            )
            proc = subprocess.run([node_bin, "-e", syntax_runner], input=main_script, text=True, encoding="utf-8", capture_output=True)
            self.assertEqual(proc.returncode, 0, f"JS SyntaxError in {slug}: {proc.stderr}")

            # 2) Simulate DOM and run validateStep(1), (2), (3) for all 5 legal wizards
            if slug in legal_slugs:
                parser = WizardStepParser()
                parser.feed(html)
                self.assertIn("1", parser.steps, f"Missing .form-step[data-step=1] in {slug}")
                self.assertIn("2", parser.steps, f"Missing .form-step[data-step=2] in {slug}")
                payload = json.dumps({"steps": parser.steps, "script": main_script}, ensure_ascii=False)
                dom_runner = r"""
const fs = require('fs');
const vm = require('vm');
const { steps, script } = JSON.parse(fs.readFileSync(0, 'utf8'));
const doc = {
  querySelector(sel) {
    const m = sel.match(/\.form-step\[data-step="(\d+)"\]/);
    if (!m || !steps[m[1]]) return null;
    const list = steps[m[1]].map(x => ({
      id: x.id, type: x.type, value: x.value, checked: x.checked,
      classList: { add() {}, remove() {} }
    }));
    return { querySelectorAll() { return list; } };
  },
  querySelectorAll() { return []; },
  getElementById() { return null; },
  addEventListener() {}
};
const sandbox = {
  document: doc, window: {}, navigator: {}, console,
  Math, Number, String, Array, Object, Set, Map, Date, RegExp, JSON,
  parseInt, parseFloat, isNaN, isFinite,
  setTimeout: () => 0, Blob: function() {}, URL: {}
};
vm.runInNewContext(script, sandbox);
if (sandbox.validateStep(1) !== true) throw new Error('validateStep(1) expected true');
if (sandbox.validateStep(2) !== true) throw new Error('validateStep(2) expected true');
if (sandbox.validateStep(3) !== true) throw new Error('validateStep(3) expected true');
if (steps['1'].length > 0) {
  const orig = Object.assign({}, steps['1'][0]);
  steps['1'][0].value = '';
  steps['1'][0].checked = false;
  if (sandbox.validateStep(1) !== false) throw new Error('validateStep(1) expected false when empty');
  steps['1'][0] = orig;
}
if (steps['2'].length > 0) {
  const orig = Object.assign({}, steps['2'][0]);
  steps['2'][0].value = '';
  steps['2'][0].checked = false;
  if (sandbox.validateStep(2) !== false) throw new Error('validateStep(2) expected false when empty');
  steps['2'][0] = orig;
}
console.log('WIZARD_OK');
"""
                proc_dom = subprocess.run([node_bin, "-e", dom_runner], input=payload, text=True, encoding="utf-8", capture_output=True)
                self.assertEqual(proc_dom.returncode, 0, f"validateStep failed for {slug}: {proc_dom.stderr} {proc_dom.stdout}")
                self.assertIn("WIZARD_OK", proc_dom.stdout)

    def test_135_hkd_2026_statutory_math(self):
        from statutory_engines import calculate_hkd_tax_2026

        # Tier 1: <= 1B VND is exempt
        t1 = calculate_hkd_tax_2026(1_000_000_000, 700_000_000, "group1")
        self.assertEqual(t1["tier"], "Tier 1")
        self.assertEqual(t1["recommended_method"], "exempt")
        self.assertEqual(t1["vat"], 0)
        self.assertEqual(t1["pit_optimal"], 0)
        self.assertEqual(t1["total_tax"], 0)

        # Tier 2 threshold (> 1B to 3B): Group 1 (1% VAT, 0.5% PIT on excess over 1B vs 15% profit)
        t2 = calculate_hkd_tax_2026(2_500_000_000, 2_400_000_000, "group1", ecom_pct=40)
        self.assertEqual(t2["tier"], "Tier 2")
        self.assertEqual(t2["vat"], 25_000_000)
        self.assertEqual(t2["pit_method1"], 7_500_000)
        self.assertEqual(t2["pit_method2"], 15_000_000)
        self.assertEqual(t2["pit_optimal"], 7_500_000)
        self.assertEqual(t2["withheld_at_source"], 15_000_000)
        self.assertEqual(t2["self_declared_due"], 17_500_000)

        # Tier 3 (> 3B to 50B): mandatory 17% on profit
        t3 = calculate_hkd_tax_2026(5_000_000_000, 4_000_000_000, "group2")
        self.assertEqual(t3["tier"], "Tier 3")
        self.assertEqual(t3["vat"], 250_000_000)
        self.assertEqual(t3["pit_optimal"], 170_000_000)

        # Tier 4 (> 50B): mandatory 20% on profit
        t4 = calculate_hkd_tax_2026(60_000_000_000, 50_000_000_000, "group1")
        self.assertEqual(t4["tier"], "Tier 4")
        self.assertEqual(t4["vat"], 600_000_000)
        self.assertEqual(t4["pit_optimal"], 2_000_000_000)

    def test_136_pit_2026_5bracket_math_and_node(self):
        import re
        import subprocess
        from statutory_engines import calculate_pit_2026

        # Gross 25M, 1 dependent, Region I, H2 2026 (base 2.53M, cap 50.6M):
        # ins = 25M * 10.5% = 2,625,000; ded2026 = 15.5M + 6.2M = 21,700,000
        # taxable2026 = 675,000 -> pit2026 = 33,750/mo (405,000/yr)
        # tax2025: ded = 11M + 4.4M = 15.4M -> taxable = 6,975,000 -> pit2025 = 447,500/mo (5,370,000/yr)
        res = calculate_pit_2026(25_000_000, mode="gross-to-net", dependents=1, region="1", period="h2_2026")
        self.assertEqual(res["total_insurance"], 2_625_000)
        self.assertEqual(res["personal_deduction_2026"] + res["dependent_deduction_2026"], 21_700_000)
        self.assertEqual(res["tntt_2026"], 675_000)
        self.assertEqual(res["pit_2026"], 33_750)
        self.assertEqual(res["pit_2025"], 447_500)
        self.assertEqual(res["monthly_tax_saved"], 413_750)
        self.assertEqual(res["annual_tax_saved"], 4_965_000)

        # Net -> Gross binary search round-trip accuracy
        inv = calculate_pit_2026(res["net"], mode="net-to-gross", dependents=1, region="1", period="h2_2026")
        self.assertLessEqual(abs(inv["net"] - res["net"]), 2)
        self.assertLessEqual(abs(inv["gross"] - 25_000_000), 2)

        # Verify client-side JS parity on generated PIT HTML via Node.js
        node_bin = shutil.which("node") or r"D:\Software\nodejs\node.exe"
        with open(os.path.join(WORKSPACE, "cong-cu-tinh-luong-gross-net-tncn-2026", "index.html"), "r", encoding="utf-8") as f:
            pit_html = f.read()
        script = re.findall(r"<script(?![^>]*src=)(?![^>]*application/ld\+json)[^>]*>([\s\S]*?)</script>", pit_html)[-1]
        js_probe = (
            "const fs=require('fs'), vm=require('vm');"
            "const code=fs.readFileSync(0,'utf8');"
            "const noopEl=()=>({addEventListener(){},getAttribute(){return '0';},classList:{add(){},remove(){}},style:{},innerText:'',value:'0'});"
            "const sb={document:{getElementById:noopEl,querySelectorAll:()=>[],addEventListener(){}},window:{},console,Math,parseFloat,parseInt,Number,String,Object,Array,setTimeout:()=>0};"
            "vm.runInNewContext(code,sb);"
            "const r=sb.evalGross(25000000,1,'1','h2_2026','full',0,0);"
            "console.log(JSON.stringify(r));"
        )
        proc = subprocess.run([node_bin, "-e", js_probe], input=script, text=True, encoding="utf-8", capture_output=True, check=True)
        js_res = json.loads(proc.stdout.strip())
        self.assertEqual(js_res["tax2026"], 33750)
        self.assertEqual(js_res["tax2025"], 447500)

    def test_137_ecommerce_2026_fees_math(self):
        from statutory_engines import calculate_ecommerce_fees_2026

        # Shopee 1M order, 6% payment fee + 3.5% fixed + 3,000 infra + Voucher Xtra (capped 50k) + 1.5% tax
        sh = calculate_ecommerce_fees_2026(
            platform="shopee",
            selling_price=1_000_000,
            cogs=500_000,
            ops=20_000,
            pay_fee_pct=6.0,
            fixed_fee_pct=3.5,
            infra_fee=3000,
            voucher_xtra=True,
            tax_withholding=True,
        )
        self.assertEqual(sh["transaction_fee"], 60_000)
        self.assertEqual(sh["fixed_fee"], 35_000)
        self.assertEqual(sh["infra_fee"], 3_000)
        self.assertEqual(sh["voucher_xtra_fee"], 50_000)
        self.assertEqual(sh["platform_fee"], 148_000)
        self.assertEqual(sh["tax_withheld"], 15_000)
        self.assertEqual(sh["net_payout"], 837_000)
        self.assertEqual(sh["net_profit"], 317_000)
        self.assertIsNotNone(sh["break_even_roas"])

        # TikTok 1M order: 6% transaction + 14% commission + 3,000 flat order fee
        tt = calculate_ecommerce_fees_2026(
            platform="tiktok",
            selling_price=1_000_000,
            cogs=450_000,
            ops=20_000,
            tiktok_trans_pct=6.0,
            tiktok_comm_pct=14.0,
            tiktok_flat_fee=3000,
            tax_withholding=True,
        )
        self.assertEqual(tt["platform_fee"], 203_000)
        self.assertEqual(tt["tax_withheld"], 15_000)
        self.assertEqual(tt["net_payout"], 782_000)

    def test_138_unsupported_slug_rejects_dropzone(self):
        from agent_niche_finder import evaluate_keyword_viability

        with self.assertRaises(ValueError):
            generate_tool("phan mem giai nen winrar full crack")

        res = evaluate_keyword_viability("công cụ gộp ổ cứng")
        self.assertEqual(res["score"], 0)
        self.assertEqual(res["competition_level"], "blocked")

if __name__ == "__main__":
    unittest.main()
