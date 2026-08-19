#!/usr/bin/env python3
# Telegram Bot for Instagram Signup – Email via Command, Fixed Password

import os, sys, json, time, random, threading, requests, logging, sqlite3
from io import BytesIO
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ====== CHANGE THESE TWO LINES ======
BOT_TOKEN = "8760264279:AAHOWTl_pokPjXbQgo25Et8gIy8ISkjJTkE"      # <--- put your token
OWNER_IDS = [8754004223]                # <--- put your Telegram user ID (as int)
# ===================================

FIXED_PASSWORD = "qwerty9900@"
INSTA_URL = "https://www.instagram.com/accounts/emailsignup/"
PHONE = ""
FULL_NAME = ""
PROXY_SERVER = PROXY_USER = PROXY_PASS = ""
NAV_TIMEOUT = 30000
ELEMENT_TIMEOUT = 10000

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
DB_FILE = "bot_state.db"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS bot_state (key TEXT PRIMARY KEY, value TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS user_emails (chat_id INTEGER PRIMARY KEY, email TEXT)')
    conn.commit()
    conn.close()

def get_email(chat_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT email FROM user_emails WHERE chat_id=?", (chat_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_email(chat_id, email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO user_emails (chat_id, email) VALUES (?, ?)", (chat_id, email))
    conn.commit()
    conn.close()

# Random Indian name generator
INDIAN_FIRST_NAMES = [
    "Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Pranav","Dhruv",
    "Krishna","Shaurya","Aryan","Ishaan","Reyansh","Ayaan","Ananya",
    "Diya","Ishita","Aadhya","Myra","Sara","Anvi","Vedika","Kavya",
    "Riya","Anika","Sana","Ira","Alisha","Tara","Zara","Arya",
    "Rohan","Kabir","Amit","Rahul","Priya","Neha","Pooja","Sneha"
]
INDIAN_SURNAMES = [
    "Sharma","Verma","Patel","Singh","Kumar","Gupta","Joshi","Rao",
    "Reddy","Nair","Menon","Pillai","Iyer","Mishra","Tripathi","Dubey",
    "Pandey","Chaudhary","Yadav","Saini","Jain","Mehta","Shah","Desai"
]

def random_indian_name():
    return f"{random.choice(INDIAN_FIRST_NAMES)} {random.choice(INDIAN_SURNAMES)}"

def generate_username(full_name):
    base = full_name.replace(" ", "").lower()
    return f"{base}{random.randint(100, 999)}"

# ========== TELEGRAM HELPERS ==========
def call_telegram(method, **kwargs):
    url = f"{API_URL}/{method}"
    try:
        resp = requests.post(url, json=kwargs, timeout=30)
        if resp.status_code != 200:
            logger.error(f"API error {resp.status_code}: {resp.text}")
            return None
        data = resp.json()
        if not data.get('ok'):
            logger.error(f"API error: {data}")
            return None
        return data.get('result')
    except Exception as e:
        logger.error(f"call_telegram exception: {e}")
        return None

def send_message(chat_id, text, parse_mode="HTML", reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return call_telegram("sendMessage", **payload)

def send_photo(chat_id, photo_bytes, caption=None):
    files = {'photo': ('captcha.png', BytesIO(photo_bytes), 'image/png')}
    data = {'chat_id': chat_id}
    if caption:
        data['caption'] = caption
        data['parse_mode'] = 'HTML'
    url = f"{API_URL}/sendPhoto"
    try:
        resp = requests.post(url, data=data, files=files, timeout=30)
        if resp.status_code != 200:
            logger.error(f"Send photo error: {resp.status_code} - {resp.text}")
            return None
        result = resp.json()
        if not result.get('ok'):
            logger.error(f"Send photo error: {result}")
            return None
        return result.get('result')
    except Exception as e:
        logger.error(f"send_photo exception: {e}")
        return None

# ========== AUTOMATION ==========
class AutomationSession:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.otp_event = threading.Event()
        self.otp_value = None
        self.captcha_event = threading.Event()
        self.captcha_value = None
        self.running = False
        self.result = None

sessions = {}
sessions_lock = threading.Lock()

def start_browser():
    playwright = sync_playwright().start()
    proxy = None
    if PROXY_SERVER:
        proxy = {"server": PROXY_SERVER}
        if PROXY_USER and PROXY_PASS:
            proxy["username"] = PROXY_USER
            proxy["password"] = PROXY_PASS
    browser = playwright.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled', '--disable-dev-shm-usage']
    )
    context = browser.new_context(
        proxy=proxy,
        viewport={'width': 1280, 'height': 720},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    return playwright, browser, page

def detect_captcha(page):
    iframes = page.locator('iframe')
    for i in range(iframes.count()):
        src = iframes.nth(i).get_attribute('src') or ''
        if 'captcha' in src.lower() or 'recaptcha' in src.lower() or 'hcaptcha' in src.lower():
            return True
    captcha_elements = page.locator('[class*="captcha"], [id*="captcha"], input[name="captcha"], input[name="verification"]')
    if captcha_elements.count() > 0:
        return True
    return False

def handle_captcha_telegram(page, session):
    screenshot_bytes = page.screenshot(full_page=True)
    session.captcha_event.clear()
    send_photo(session.chat_id, screenshot_bytes, caption="🧩 CAPTCHA detected. Reply with the text.")
    if not session.captcha_event.wait(timeout=120):
        send_message(session.chat_id, "⏰ CAPTCHA timeout.")
        return False
    solution = session.captcha_value
    if not solution:
        return False
    captcha_input = page.locator('input[name="captcha"]')
    if not captcha_input.is_visible():
        captcha_input = page.locator('input[name="verification"]')
    if captcha_input.is_visible():
        captcha_input.fill(solution)
        submit = page.locator('button[type="submit"]:visible')
        if submit.count() > 0:
            submit.click()
        send_message(session.chat_id, "✅ CAPTCHA solved.")
        return True
    else:
        send_message(session.chat_id, "❌ CAPTCHA input not found.")
        return False

def run_automation(chat_id):
    session = sessions.get(chat_id)
    if not session:
        return
    session.running = True
    email = get_email(chat_id)
    if not email:
        send_message(chat_id, "❌ No email set. Use /setemail <email>")
        session.running = False
        return
    password = FIXED_PASSWORD
    full_name = FULL_NAME if FULL_NAME else random_indian_name()
    username = generate_username(full_name)

    try:
        playwright, browser, page = start_browser()
        send_message(chat_id, "🚀 Starting...")

        page.goto(INSTA_URL, timeout=NAV_TIMEOUT)
        page.wait_for_load_state("networkidle")

        if detect_captcha(page):
            if not handle_captcha_telegram(page, session):
                raise Exception("CAPTCHA failed")

        email_phone = page.locator('input[name="emailOrPhone"]')
        if email_phone.is_visible():
            email_phone.fill(email)
        else:
            email_input = page.locator('input[name="email"]')
            if email_input.is_visible():
                email_input.fill(email)
            phone_input = page.locator('input[name="phone"]')
            if phone_input.is_visible() and PHONE:
                phone_input.fill(PHONE)

        name_input = page.locator('input[name="fullName"]')
        if name_input.is_visible():
            name_input.fill(full_name)

        username_input = page.locator('input[name="username"]')
        if username_input.is_visible():
            username_input.fill(username)

        pwd_input = page.locator('input[name="password"]')
        if pwd_input.is_visible():
            pwd_input.fill(password)

        send_message(chat_id, f"✅ Form filled. Email: {email}")

        submit_btn = page.locator('button[type="submit"]')
        if submit_btn.is_visible():
            submit_btn.click()
        else:
            submit_btn = page.get_by_text("Sign up", exact=True)
            if submit_btn.is_visible():
                submit_btn.click()
            else:
                raise Exception("Submit button not found.")

        page.wait_for_load_state("networkidle")
        if detect_captcha(page):
            if not handle_captcha_telegram(page, session):
                raise Exception("CAPTCHA after submit")

        send_message(chat_id, "⏳ Waiting for OTP...")
        otp_input = page.locator('input[name="code"]')
        otp_input.wait_for(timeout=ELEMENT_TIMEOUT)

        session.otp_event.clear()
        send_message(chat_id, "🔑 OTP sent. Reply with 6-digit code.")
        if not session.otp_event.wait(timeout=120):
            raise TimeoutError("OTP timeout")
        otp = session.otp_value
        if not otp:
            raise ValueError("OTP empty")

        otp_input.fill(otp)
        verify_btn = page.locator('button[type="submit"]')
        if verify_btn.is_visible():
            verify_btn.click()
        else:
            verify_btn = page.get_by_text("Verify", exact=True)
            if verify_btn.is_visible():
                verify_btn.click()
            else:
                raise Exception("Verify button not found.")

        try:
            page.wait_for_url("**/accounts/emailsignup/**", timeout=5000, state='detached')
            page.wait_for_load_state("networkidle")
            url = page.url
            if "instagram.com" in url and "/accounts/" not in url:
                result_msg = f"✅ SUCCESS – {full_name} (Username: {username})"
                session.result = "success"
            else:
                error = page.locator('text="Something went wrong"')
                if error.is_visible():
                    result_msg = "❌ FAILED – Error message"
                else:
                    result_msg = "❌ FAILED – Unknown"
                session.result = "failed"
        except PlaywrightTimeout:
            result_msg = "⚠️ Timeout – incomplete"
            session.result = "failed"

        send_message(chat_id, result_msg)

    except Exception as e:
        logger.error(f"Automation error: {e}")
        send_message(chat_id, f"❌ Error: {str(e)}")
        session.result = "failed"
    finally:
        if 'browser' in locals():
            browser.close()
        if 'playwright' in locals():
            playwright.stop()
        session.running = False
        send_message(chat_id, "🏁 Finished.")

# ========== HANDLERS ==========
def handle_message(msg):
    chat_id = msg.get('chat', {}).get('id')
    if not chat_id:
        return
    text = (msg.get('text') or '').strip()
    if not text:
        return

    if chat_id not in OWNER_IDS:
        send_message(chat_id, "❌ Not authorized.")
        return

    reply_to = msg.get('reply_to_message')
    if reply_to:
        with sessions_lock:
            session = sessions.get(chat_id)
        if session:
            if session.otp_event and not session.otp_event.is_set():
                if text.isdigit() and len(text) == 6:
                    session.otp_value = text
                    session.otp_event.set()
                    send_message(chat_id, "✅ OTP received.")
                    return
                else:
                    send_message(chat_id, "❌ OTP must be 6 digits.")
                    return
            if session.captcha_event and not session.captcha_event.is_set():
                session.captcha_value = text
                session.captcha_event.set()
                send_message(chat_id, "✅ CAPTCHA received.")
                return

    if text.startswith('/'):
        cmd = text.split()[0].lower()
        if cmd == '/start':
            with sessions_lock:
                if chat_id in sessions and sessions[chat_id].running:
                    send_message(chat_id, "⏳ Already running.")
                    return
                sessions[chat_id] = AutomationSession(chat_id)
            send_message(chat_id, "🤖 Starting signup...")
            thread = threading.Thread(target=run_automation, args=(chat_id,), daemon=True)
            thread.start()

        elif cmd == '/setemail':
            parts = text.split(maxsplit=1)
            if len(parts) < 2 or not parts[1]:
                send_message(chat_id, "Usage: /setemail <your_email@example.com>")
                return
            new_email = parts[1].strip()
            if '@' not in new_email or '.' not in new_email:
                send_message(chat_id, "❌ Invalid email.")
                return
            set_email(chat_id, new_email)
            send_message(chat_id, f"✅ Email set to: {new_email}")

        elif cmd == '/status':
            with sessions_lock:
                session = sessions.get(chat_id)
            if session and session.running:
                send_message(chat_id, "⏳ Running...")
            else:
                send_message(chat_id, "⏸️ Idle.")
        else:
            send_message(chat_id, "Unknown command. Use /start, /setemail, /status.")
    else:
        send_message(chat_id, "Use commands.")

# ========== POLLING ==========
def polling_loop():
    offset = 0
    logger.info("Polling loop started.")
    while True:
        try:
            payload = {"timeout": 30, "offset": offset, "allowed_updates": json.dumps(["message"])}
            url = f"{API_URL}/getUpdates"
            resp = requests.get(url, params=payload, timeout=35)
            if resp.status_code != 200:
                logger.error(f"getUpdates error: {resp.status_code}")
                time.sleep(5)
                continue
            data = resp.json()
            if not data.get('ok'):
                logger.error(f"getUpdates error: {data}")
                time.sleep(5)
                continue

            for update in data.get('result', []):
                update_id = update['update_id']
                if update_id >= offset:
                    offset = update_id + 1
                    if 'message' in update:
                        handle_message(update['message'])
            if data.get('result'):
                last = data['result'][-1]['update_id']
                if last >= offset:
                    offset = last + 1
        except Exception as e:
            logger.error(f"Poll exception: {e}")
            time.sleep(5)

# ========== MAIN ==========
if __name__ == "__main__":
    init_db()
    call_telegram("deleteWebhook", drop_pending_updates=True)
    time.sleep(1)
    me = call_telegram("getMe")
    if not me:
        logger.error("Invalid token.")
        sys.exit(1)
    logger.info(f"Bot @{me['username']} started.")
    polling_loop()
