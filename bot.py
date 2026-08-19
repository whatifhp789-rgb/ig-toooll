#!/usr/bin/env python3
# Telegram Bot for Instagram Signup Automation

import os
import sys
import json
import time
import random
import threading
import requests
import logging
import sqlite3
import base64
from io import BytesIO
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

load_dotenv()

# ========== CONFIG ==========
BOT_TOKEN = os.getenv("8760264279:AAHOWTl_pokPjXbQgo25Et8gIy8ISkjJTkE")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN not set")
    sys.exit(1)

OWNER_IDS = [int(x.strip()) for x in os.getenv("8754004223", "").split(",") if x.strip()]
if not OWNER_IDS:
    print("❌ OWNER_IDS not set")
    sys.exit(1)

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
DB_FILE = "bot_state.db"

# Instagram config
INSTA_URL = os.getenv("INSTA_URL", "https://www.instagram.com/accounts/emailsignup/")
EMAIL = os.getenv("EMAIL")
PHONE = os.getenv("PHONE", "")
FULL_NAME = os.getenv("FULL_NAME", "").strip()
PASSWORD = os.getenv("PASSWORD")
PROXY_SERVER = os.getenv("PROXY_SERVER")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")

NAV_TIMEOUT = 30000
ELEMENT_TIMEOUT = 10000

# ========== LOGGING ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== RANDOM INDIAN NAME GENERATOR ==========
INDIAN_FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Pranav", "Dhruv",
    "Krishna", "Shaurya", "Aryan", "Ishaan", "Reyansh", "Ayaan", "Ananya",
    "Diya", "Ishita", "Aadhya", "Myra", "Sara", "Anvi", "Vedika", "Kavya",
    "Riya", "Anika", "Sana", "Ira", "Alisha", "Tara", "Zara", "Arya",
    "Rohan", "Kabir", "Amit", "Rahul", "Priya", "Neha", "Pooja", "Sneha"
]

INDIAN_SURNAMES = [
    "Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Joshi", "Rao",
    "Reddy", "Nair", "Menon", "Pillai", "Iyer", "Mishra", "Tripathi", "Dubey",
    "Pandey", "Chaudhary", "Yadav", "Saini", "Jain", "Mehta", "Shah", "Desai"
]

def random_indian_name():
    first = random.choice(INDIAN_FIRST_NAMES)
    last = random.choice(INDIAN_SURNAMES)
    return f"{first} {last}"

def generate_username(full_name):
    base = full_name.replace(" ", "").lower()
    return f"{base}{random.randint(100, 999)}"

if not FULL_NAME:
    FULL_NAME = random_indian_name()
    logger.info(f"Auto-generated name: {FULL_NAME}")
USERNAME = generate_username(FULL_NAME)

# ========== DATABASE (for offset & processed updates) ==========
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bot_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS processed_updates (
            update_id INTEGER PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def get_offset():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM bot_state WHERE key='offset'")
    row = c.fetchone()
    conn.close()
    return int(row[0]) if row else 0

def set_offset(offset):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO bot_state (key, value) VALUES ('offset', ?)", (str(offset),))
    conn.commit()
    conn.close()

def is_update_processed(update_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM processed_updates WHERE update_id=?", (update_id,))
    row = c.fetchone()
    conn.close()
    return row is not None

def mark_update_processed(update_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO processed_updates (update_id) VALUES (?)", (update_id,))
    conn.commit()
    conn.close()

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
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return call_telegram("sendMessage", **payload)

def send_photo(chat_id, photo_bytes, caption=None, parse_mode="HTML"):
    files = {'photo': ('captcha.png', BytesIO(photo_bytes), 'image/png')}
    data = {'chat_id': chat_id}
    if caption:
        data['caption'] = caption
        data['parse_mode'] = parse_mode
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

# ========== AUTOMATION STATE (per chat) ==========
class AutomationSession:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.otp_event = threading.Event()
        self.otp_value = None
        self.captcha_event = threading.Event()
        self.captcha_value = None
        self.captcha_image_bytes = None
        self.running = False
        self.result = None

sessions = {}  # chat_id -> AutomationSession
sessions_lock = threading.Lock()

# ========== BROWSER & AUTOMATION ==========
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
        args=['--disable-blink-features=AutomationControlled']
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
    """Send screenshot to user and wait for CAPTCHA solution via Telegram."""
    # Capture screenshot
    screenshot_bytes = page.screenshot(full_page=True)
    session.captcha_image_bytes = screenshot_bytes
    session.captcha_event.clear()
    # Send photo with caption asking for CAPTCHA
    send_photo(
        session.chat_id,
        screenshot_bytes,
        caption="🧩 CAPTCHA detected. Please solve and reply with the text you see in the image.\n\nSend the text as a reply to this message.",
        parse_mode="HTML"
    )
    # Wait for solution
    if not session.captcha_event.wait(timeout=120):
        send_message(session.chat_id, "⏰ CAPTCHA timeout. Automation will stop.")
        return False
    solution = session.captcha_value
    if not solution:
        send_message(session.chat_id, "❌ Empty CAPTCHA solution received.")
        return False
    # Find input and fill
    captcha_input = page.locator('input[name="captcha"]')
    if not captcha_input.is_visible():
        captcha_input = page.locator('input[name="verification"]')
    if captcha_input.is_visible():
        captcha_input.fill(solution)
        # click submit button if present
        submit_captcha = page.locator('button[type="submit"]:visible')
        if submit_captcha.count() > 0:
            submit_captcha.click()
        send_message(session.chat_id, "✅ CAPTCHA solved and submitted.")
        return True
    else:
        send_message(session.chat_id, "❌ Could not find CAPTCHA input field after solving.")
        return False

def run_automation(chat_id):
    session = sessions.get(chat_id)
    if not session:
        return
    session.running = True
    session.result = None

    try:
        playwright, browser, page = start_browser()
        send_message(chat_id, "🚀 Browser launched. Starting signup...")

        # Navigate
        page.goto(INSTA_URL, timeout=NAV_TIMEOUT)
        page.wait_for_load_state("networkidle")

        # Check initial CAPTCHA
        if detect_captcha(page):
            if not handle_captcha_telegram(page, session):
                raise Exception("CAPTCHA solving failed")
            page.wait_for_load_state("networkidle")

        # Fill form
        email_phone = page.locator('input[name="emailOrPhone"]')
        if email_phone.is_visible():
            if EMAIL:
                email_phone.fill(EMAIL)
            elif PHONE:
                email_phone.fill(PHONE)
            else:
                raise ValueError("No EMAIL or PHONE provided.")
        else:
            email_input = page.locator('input[name="email"]')
            if email_input.is_visible() and EMAIL:
                email_input.fill(EMAIL)
            phone_input = page.locator('input[name="phone"]')
            if phone_input.is_visible() and PHONE:
                phone_input.fill(PHONE)

        name_input = page.locator('input[name="fullName"]')
        if name_input.is_visible():
            name_input.fill(FULL_NAME)

        username_input = page.locator('input[name="username"]')
        if username_input.is_visible():
            username_input.fill(USERNAME)

        pwd_input = page.locator('input[name="password"]')
        if pwd_input.is_visible():
            pwd_input.fill(PASSWORD)

        send_message(chat_id, "✅ Form filled. Submitting...")

        # Submit
        submit_btn = page.locator('button[type="submit"]')
        if submit_btn.is_visible():
            submit_btn.click()
        else:
            submit_btn = page.get_by_text("Sign up", exact=True)
            if submit_btn.is_visible():
                submit_btn.click()
            else:
                raise Exception("Submit button not found.")

        # Check for post-submit CAPTCHA
        page.wait_for_load_state("networkidle")
        if detect_captcha(page):
            if not handle_captcha_telegram(page, session):
                raise Exception("CAPTCHA solving failed after submit.")
            page.wait_for_load_state("networkidle")

        # Wait for OTP
        send_message(chat_id, "⏳ Waiting for OTP page...")
        otp_input = page.locator('input[name="code"]')
        otp_input.wait_for(timeout=ELEMENT_TIMEOUT)

        # Ask for OTP
        session.otp_event.clear()
        send_message(chat_id, "🔑 OTP sent to your email/phone. Please reply with the 6-digit OTP.")

        if not session.otp_event.wait(timeout=120):
            raise TimeoutError("OTP not provided within 120 seconds.")

        otp = session.otp_value
        if not otp:
            raise ValueError("OTP was empty.")

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

        # Check result
        try:
            page.wait_for_url("**/accounts/emailsignup/**", timeout=5000, state='detached')
            page.wait_for_load_state("networkidle")
            url = page.url
            if "instagram.com" in url and "/accounts/" not in url:
                result_msg = f"✅ SUCCESS – Account created for {FULL_NAME} (Username: {USERNAME})"
                session.result = "success"
            else:
                error = page.locator('text="Something went wrong"')
                if error.is_visible():
                    result_msg = "❌ FAILED – Error message displayed."
                else:
                    result_msg = "❌ FAILED – Unknown issue."
                session.result = "failed"
        except PlaywrightTimeout:
            result_msg = "⚠️ Timeout waiting for redirect – may be incomplete."
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
        send_message(chat_id, "🏁 Automation finished.")

# ========== MESSAGE HANDLER ==========
def handle_message(msg):
    chat_id = msg.get('chat', {}).get('id')
    if not chat_id:
        return
    text = (msg.get('text') or '').strip()
    if not text:
        return

    # Only allow owners
    if chat_id not in OWNER_IDS:
        send_message(chat_id, "❌ You are not authorized to use this bot.")
        return

    # Check if this is a reply to a previous message (for OTP/CAPTCHA)
    reply_to = msg.get('reply_to_message')
    if reply_to:
        # Check if we have a pending request for this chat
        with sessions_lock:
            session = sessions.get(chat_id)
        if session:
            # Check OTP
            if session.otp_event and not session.otp_event.is_set():
                if text.isdigit() and len(text) == 6:
                    session.otp_value = text
                    session.otp_event.set()
                    send_message(chat_id, "✅ OTP received. Continuing...")
                    return
                else:
                    send_message(chat_id, "❌ Invalid OTP. Must be 6 digits.")
                    return
            # Check CAPTCHA
            if session.captcha_event and not session.captcha_event.is_set():
                # Accept any text as CAPTCHA solution
                session.captcha_value = text
                session.captcha_event.set()
                send_message(chat_id, "✅ CAPTCHA solution received. Continuing...")
                return

    # If not a reply, treat as command
    if text.startswith('/'):
        cmd = text.split()[0].lower()
        if cmd == '/start':
            with sessions_lock:
                if chat_id in sessions and sessions[chat_id].running:
                    send_message(chat_id, "⏳ An automation is already running for this chat. Please wait.")
                    return
                sessions[chat_id] = AutomationSession(chat_id)
            send_message(chat_id, "🤖 Starting Instagram signup automation...")
            thread = threading.Thread(target=run_automation, args=(chat_id,), daemon=True)
            thread.start()
        elif cmd == '/status':
            with sessions_lock:
                session = sessions.get(chat_id)
            if session and session.running:
                send_message(chat_id, "⏳ Automation is currently running.")
            else:
                send_message(chat_id, "⏸️ No automation running.")
        elif cmd == '/cancel':
            with sessions_lock:
                session = sessions.get(chat_id)
            if session and session.running:
                # Hard to cancel gracefully, but we can mark result as failed and let it finish
                send_message(chat_id, "❌ Cancelling... (will stop after current step)")
                session.result = "cancelled"
                # We can't easily kill the thread, but we can set a flag
            else:
                send_message(chat_id, "No running automation to cancel.")
        else:
            send_message(chat_id, "Unknown command. Use /start to begin.")
    else:
        send_message(chat_id, "Please use /start to begin, or reply to the bot's message with OTP/CAPTCHA.")

# ========== POLLING LOOP ==========
def polling_loop():
    offset = get_offset()
    logger.info(f"Polling loop started with offset={offset}")
    while True:
        try:
            payload = {
                "timeout": 30,
                "offset": offset,
                "allowed_updates": json.dumps(["message"])
            }
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

            results = data.get('result', [])
            for update in results:
                update_id = update['update_id']
                if is_update_processed(update_id):
                    logger.info(f"Skipping duplicate update {update_id}")
                    continue
                mark_update_processed(update_id)

                if 'message' in update:
                    handle_message(update['message'])

                if update_id >= offset:
                    offset = update_id + 1
                    set_offset(offset)

            if results:
                last_update_id = results[-1]['update_id']
                if last_update_id >= offset:
                    offset = last_update_id + 1
                    set_offset(offset)

        except Exception as e:
            logger.error(f"Polling loop exception: {e}", exc_info=True)
            time.sleep(5)

# ========== MAIN ==========
if __name__ == "__main__":
    init_db()
    # Delete any webhook
    call_telegram("deleteWebhook", drop_pending_updates=True)
    time.sleep(1)

    # Validate bot token
    me = call_telegram("getMe")
    if not me:
        logger.error("Invalid bot token. Exiting.")
        sys.exit(1)
    logger.info(f"Bot @{me['username']} started.")

    polling_loop()
