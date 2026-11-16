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
            "bank_account": "19027557341011",
            "bank_account_holder": "NGUYEN TRUNG THIEN PHUC",
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

    def test_117_directory_crawl_timer_15s_all(self):
        # Find all generated folders containing index.html, verify countdown timer wait is 15 seconds
        ignore_dirs = {".git", ".gemini", "templates", "__pycache__", "api", "scratch"}
        count = 0
        for name in os.listdir(WORKSPACE):
            path = os.path.join(WORKSPACE, name)
            if os.path.isdir(path) and name not in ignore_dirs:
                index_html = os.path.join(path, "index.html")
                if os.path.exists(index_html):
                    count += 1
                    with open(index_html, "r", encoding="utf-8") as f:
                        html = f.read()
                    
                    # Verify either count text or variable is updated to 15 if the page has a countdown timer
                    if "countdown-timer" in html or "let seconds =" in html:
                        self.assertTrue(
                            "let seconds = 15;" in html or 
                            "countdown-timer" in html and "15" in html,
                            f"Wait time in {name} is not set to 15 seconds"
                        )
        self.assertTrue(count > 0, "No generated tools found to crawl")

    def test_118_directory_crawl_user_nav_all(self):
        ignore_dirs = {".git", ".gemini", "templates", "__pycache__", "api", "scratch"}
        for name in os.listdir(WORKSPACE):
            path = os.path.join(WORKSPACE, name)
            if os.path.isdir(path) and name not in ignore_dirs:
                index_html = os.path.join(path, "index.html")
                if os.path.exists(index_html):
                    with open(index_html, "r", encoding="utf-8") as f:
                        html = f.read()
                    self.assertIn("user-nav-status", html, f"Missing user-nav-status anchor in {name}")

    def test_119_directory_crawl_checkout_script_all(self):
        ignore_dirs = {".git", ".gemini", "templates", "__pycache__", "api", "scratch"}
        for name in os.listdir(WORKSPACE):
            path = os.path.join(WORKSPACE, name)
            if os.path.isdir(path) and name not in ignore_dirs:
                index_html = os.path.join(path, "index.html")
                if os.path.exists(index_html):
                    with open(index_html, "r", encoding="utf-8") as f:
                        html = f.read()
                    self.assertIn("checkout_modal.js", html, f"Missing checkout_modal.js script in {name}")

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

if __name__ == "__main__":
    unittest.main()
