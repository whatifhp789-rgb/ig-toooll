#!/usr/bin/env python3
# Telegram Bot for Instagram Signup – Single‑Page Form, Proxy, CAPTCHA

import os, sys, json, time, random, threading, requests, logging, sqlite3
from io import BytesIO
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from datetime import datetime

# ====== CHANGE THESE TWO LINES ONLY ======
BOT_TOKEN = "8760264279:AAHH7DdJpFCpF7ohl_AnwajqjUxvyegDpyA"
OWNER_IDS = [8754004223]
# =======================================

FIXED_PASSWORD = "qwerty9900"
INSTA_URL = "https://www.instagram.com/accounts/emailsignup/"
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
    c.execute('CREATE TABLE IF NOT EXISTS user_creds (chat_id INTEGER PRIMARY KEY, email TEXT, phone TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS user_proxies (chat_id INTEGER PRIMARY KEY, proxy TEXT)')
    conn.commit()
    conn.close()

def get_credential(chat_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT email, phone FROM user_creds WHERE chat_id=?", (chat_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"email": row[0], "phone": row[1]}
    return {"email": None, "phone": None}

def set_email(chat_id, email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    creds = get_credential(chat_id)
    phone = creds.get("phone")
    c.execute("REPLACE INTO user_creds (chat_id, email, phone) VALUES (?, ?, ?)", 
              (chat_id, email, phone))
    conn.commit()
    conn.close()

def set_phone(chat_id, phone):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    creds = get_credential(chat_id)
    email = creds.get("email")
    c.execute("REPLACE INTO user_creds (chat_id, email, phone) VALUES (?, ?, ?)", 
              (chat_id, email, phone))
    conn.commit()
    conn.close()

def get_proxy(chat_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT proxy FROM user_proxies WHERE chat_id=?", (chat_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_proxy(chat_id, proxy):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO user_proxies (chat_id, proxy) VALUES (?, ?)", (chat_id, proxy))
    conn.commit()
    conn.close()

def del_proxy(chat_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM user_proxies WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()

# -------------------- Random generators --------------------
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

def generate_username():
    letters = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(4,5)))
    digits = ''.join(random.choices('0123456789', k=random.randint(2,3)))
    return f"{letters}_{digits}"

def random_dob():
    age = random.randint(30, 70)
    year = datetime.now().year - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return day, month, year

# -------------------- Proxy validation --------------------
def parse_proxy(proxy_str):
    proxy_str = proxy_str.strip()
    protocol = 'http'
    rest = proxy_str
    if '://' in proxy_str:
        protocol, rest = proxy_str.split('://', 1)
        if protocol not in ['http', 'https', 'socks5']:
            return None
    user, passwd = None, None
    if '@' in rest:
        userpass, hostport = rest.split('@', 1)
        if ':' in userpass:
            user, passwd = userpass.split(':', 1)
        else:
            user, passwd = userpass, ''
    else:
        hostport = rest
    if ':' not in hostport:
        return None
    host, port = hostport.split(':', 1)
    if not port.isdigit():
        return None
    server = f"{protocol}://{host}:{port}"
    proxy_dict = {"server": server}
    if user:
        proxy_dict["username"] = user
    if passwd:
        proxy_dict["password"] = passwd
    return proxy_dict

def validate_proxy(proxy_str):
    parsed = parse_proxy(proxy_str)
    if not parsed:
        return False, "Invalid proxy format."
    server = parsed["server"]
    auth = ""
    if parsed.get("username"):
        auth = f"{parsed['username']}:{parsed.get('password','')}@"
    proxy_url = server.replace('://', f'://{auth}')
    proxies = {'http': proxy_url, 'https': proxy_url}
    try:
        resp = requests.get('https://www.instagram.com', proxies=proxies, timeout=10)
        if resp.status_code == 200:
            return True, "Proxy is alive."
        else:
            return False, f"Proxy returned status {resp.status_code}."
    except Exception as e:
        return False, f"Proxy error: {str(e)}"

# -------------------- Telegram helpers --------------------
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

def answer_callback_query(callback_query_id, text=None, show_alert=False):
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
        payload["show_alert"] = show_alert
    return call_telegram("answerCallbackQuery", **payload)

def edit_message_text(chat_id, message_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return call_telegram("editMessageText", **payload)

# -------------------- Automation --------------------
class AutomationSession:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.otp_event = threading.Event()
        self.otp_value = None
        self.captcha_event = threading.Event()
        self.captcha_value = None
        self.running = False
        self.result = None
        self.awaiting_credential = None

sessions = {}
sessions_lock = threading.Lock()

def start_browser(proxy_str=None):
    logger.info("🔄 Starting Playwright...")
    playwright = sync_playwright().start()
    proxy = None
    if proxy_str:
        parsed = parse_proxy(proxy_str)
        if parsed:
            proxy = parsed
            logger.info(f"Using proxy: {proxy_str}")
        else:
            logger.warning(f"Invalid proxy string, ignoring.")
    logger.info("🔄 Launching Chromium (headless)...")
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
    logger.info("✅ Browser ready.")
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
    logger.info("🧩 CAPTCHA detected – sending screenshot...")
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

    creds = get_credential(chat_id)
    email = creds.get("email")
    phone = creds.get("phone")
    if not email and not phone:
        send_message(chat_id, "❌ No email or phone set. Use /start to choose.")
        session.running = False
        return

    if email:
        login_value = email
        login_type = "email"
    else:
        login_value = phone
        login_type = "phone"

    full_name = random_indian_name()
    username = generate_username()
    password = FIXED_PASSWORD
    day, month, year = random_dob()

    proxy_str = get_proxy(chat_id)
    if proxy_str:
        logger.info(f"Using stored proxy: {proxy_str}")
    else:
        logger.info("No proxy, direct connection.")

    try:
        playwright, browser, page = start_browser(proxy_str)
        send_message(chat_id, "🚀 Browser launched. Starting signup...")

        # Navigate
        logger.info("🌐 Navigating to Instagram signup page...")
        page.goto(INSTA_URL, timeout=NAV_TIMEOUT)
        page.wait_for_load_state("networkidle")

        if detect_captcha(page):
            if not handle_captcha_telegram(page, session):
                raise Exception("CAPTCHA failed")
            page.wait_for_load_state("networkidle")

        # --- Fill all fields (single-page form) ---
        logger.info("📝 Filling email/phone...")
        email_phone_input = page.locator('input[name="emailOrPhone"]')
        if email_phone_input.is_visible():
            email_phone_input.fill(login_value)
            logger.info(f"Filled email/phone with {login_value}")
        else:
            email_input = page.locator('input[name="email"]')
            if email_input.is_visible() and email:
                email_input.fill(email)
            phone_input = page.locator('input[name="phone"]')
            if phone_input.is_visible() and phone:
                phone_input.fill(phone)

        logger.info("📝 Filling password...")
        pwd_input = page.locator('input[name="password"]')
        if pwd_input.is_visible():
            pwd_input.fill(password)
        else:
            raise Exception("Password field not found.")

        logger.info("📝 Filling date of birth...")
        # Day
        day_input = page.locator('input[name="day"]')
        if day_input.is_visible():
            day_input.fill(str(day))
        else:
            day_select = page.locator('select[name="day"]')
            if day_select.is_visible():
                day_select.select_option(str(day))
            else:
                day_input = page.locator('input[placeholder*="Day"]')
                if day_input.is_visible():
                    day_input.fill(str(day))
                else:
                    raise Exception("Day field not found.")
        # Month
        month_input = page.locator('input[name="month"]')
        if month_input.is_visible():
            month_input.fill(str(month))
        else:
            month_select = page.locator('select[name="month"]')
            if month_select.is_visible():
                month_select.select_option(str(month))
            else:
                month_input = page.locator('input[placeholder*="Month"]')
                if month_input.is_visible():
                    month_input.fill(str(month))
                else:
                    raise Exception("Month field not found.")
        # Year
        year_input = page.locator('input[name="year"]')
        if year_input.is_visible():
            year_input.fill(str(year))
        else:
            year_input = page.locator('input[placeholder*="Year"]')
            if year_input.is_visible():
                year_input.fill(str(year))
            else:
                year_select = page.locator('select[name="year"]')
                if year_select.is_visible():
                    year_select.select_option(str(year))
                else:
                    raise Exception("Year field not found.")

        logger.info("📝 Filling full name...")
        name_input = page.locator('input[name="fullName"]')
        if name_input.is_visible():
            name_input.fill(full_name)
        else:
            raise Exception("Full name field not found.")

        logger.info("📝 Filling username...")
        username_input = page.locator('input[name="username"]')
        if username_input.is_visible():
            username_input.fill(username)
        else:
            raise Exception("Username field not found.")

        send_message(chat_id, f"✅ Form filled.\nEmail/Phone: {login_value}\nName: {full_name}\nUsername: {username}\nDOB: {day}/{month}/{year}")
        logger.info("All fields filled.")

        # Submit the form
        logger.info("🔘 Clicking Submit...")
        submit_btn = page.locator('button[type="submit"]:visible')
        if submit_btn.is_visible():
            submit_btn.click()
            logger.info("Clicked submit button.")
        else:
            submit_btn = page.get_by_text("Submit", exact=True)
            if submit_btn.is_visible():
                submit_btn.click()
                logger.info("Clicked 'Submit' text.")
            else:
                submit_btn = page.get_by_text("Sign up", exact=True)
                if submit_btn.is_visible():
                    submit_btn.click()
                    logger.info("Clicked 'Sign up' text.")
                else:
                    submit_btn = page.locator('form button:visible')
                    if submit_btn.is_visible():
                        submit_btn.click()
                        logger.info("Clicked any visible button in form.")
                    else:
                        raise Exception("Submit button not found.")

        page.wait_for_load_state("networkidle")
        if detect_captcha(page):
            if not handle_captcha_telegram(page, session):
                raise Exception("CAPTCHA after submit")
            page.wait_for_load_state("networkidle")

        # Wait for OTP page
        logger.info("⏳ Waiting for OTP page...")
        otp_input = page.locator('input[name="code"]')
        otp_input.wait_for(timeout=ELEMENT_TIMEOUT)

        session.otp_event.clear()
        send_message(chat_id, "🔑 OTP sent to your " + login_type + ". Reply with 6-digit code.")
        if not session.otp_event.wait(timeout=120):
            raise TimeoutError("OTP timeout")
        otp = session.otp_value
        if not otp:
            raise ValueError("OTP empty")

        otp_input.fill(otp)
        verify_btn = page.locator('button[type="submit"]:visible')
        if verify_btn.is_visible():
            verify_btn.click()
            logger.info("Clicked verify button.")
        else:
            verify_btn = page.get_by_text("Verify", exact=True)
            if verify_btn.is_visible():
                verify_btn.click()
                logger.info("Clicked 'Verify' text.")
            else:
                raise Exception("Verify button not found.")

        page.wait_for_load_state("networkidle")
        if detect_captcha(page):
            if not handle_captcha_telegram(page, session):
                raise Exception("CAPTCHA after OTP")
            page.wait_for_load_state("networkidle")

        # Final result
        try:
            page.wait_for_url("**/accounts/emailsignup/**", timeout=5000, state='detached')
            page.wait_for_load_state("networkidle")
            url = page.url
            if "instagram.com" in url and "/accounts/" not in url:
                result_msg = f"✅ SUCCESS – Account created for {full_name} (Username: {username})"
                session.result = "success"
                logger.info("✅ SUCCESS")
            else:
                error = page.locator('text="Something went wrong"')
                if error.is_visible():
                    result_msg = "❌ FAILED – Error message"
                    logger.error("❌ FAILED: error message displayed.")
                else:
                    result_msg = "❌ FAILED – Unknown"
                    logger.error("❌ FAILED: unknown issue.")
                session.result = "failed"
        except PlaywrightTimeout:
            result_msg = "⚠️ Timeout – incomplete"
            session.result = "failed"
            logger.error("⏰ Timeout waiting for redirect.")

        send_message(chat_id, result_msg)

    except Exception as e:
        logger.error(f"Automation error: {e}", exc_info=True)
        send_message(chat_id, f"❌ Error: {str(e)}")
        session.result = "failed"
    finally:
        if 'browser' in locals():
            browser.close()
        if 'playwright' in locals():
            playwright.stop()
        session.running = False
        send_message(chat_id, "🏁 Finished.")

# -------------------- Handlers --------------------
def handle_start(chat_id, message_id=None):
    keyboard = {
        "inline_keyboard": [
            [{"text": "📧 Signup with Email", "callback_data": "choose_email"}],
            [{"text": "📱 Signup with Phone", "callback_data": "choose_phone"}]
        ]
    }
    creds = get_credential(chat_id)
    status = ""
    if creds["email"]:
        status += f"\n📧 Email: {creds['email']}"
    if creds["phone"]:
        status += f"\n📱 Phone: {creds['phone']}"
    proxy = get_proxy(chat_id)
    if proxy:
        status += f"\n🔑 Proxy: {proxy}"
    if status:
        status = "\nCurrent credentials:" + status + "\nChoose option to change or start."
    else:
        status = "\nChoose an option to set your email or phone."
    if message_id:
        edit_message_text(chat_id, message_id, "🤖 **Instagram Signup**" + status, reply_markup=keyboard)
    else:
        send_message(chat_id, "🤖 **Instagram Signup**" + status, reply_markup=keyboard)

def handle_callback_query(cq):
    chat_id = cq.get('message', {}).get('chat', {}).get('id')
    if not chat_id:
        return
    data = cq.get('data', '')
    message_id = cq.get('message', {}).get('message_id')
    callback_id = cq.get('id')
    frm = cq.get('from', {})
    user_id = frm.get('id')

    if user_id not in OWNER_IDS:
        answer_callback_query(callback_id, "❌ Not authorized.", show_alert=True)
        return

    if data == "choose_email":
        answer_callback_query(callback_id, "Please send your email address.")
        with sessions_lock:
            session = sessions.get(chat_id)
            if not session:
                session = AutomationSession(chat_id)
                sessions[chat_id] = session
            session.awaiting_credential = "email"
        send_message(chat_id, "📧 Please send your email address (e.g., user@example.com)")

    elif data == "choose_phone":
        answer_callback_query(callback_id, "Please send your phone number with country code.")
        with sessions_lock:
            session = sessions.get(chat_id)
            if not session:
                session = AutomationSession(chat_id)
                sessions[chat_id] = session
            session.awaiting_credential = "phone"
        send_message(chat_id, "📱 Please send your phone number with country code (e.g., +911234567890)")

    else:
        answer_callback_query(callback_id, "Unknown option.")

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

    with sessions_lock:
        session = sessions.get(chat_id)
    if session and session.awaiting_credential:
        cred_type = session.awaiting_credential
        if cred_type == "email":
            if '@' not in text or '.' not in text:
                send_message(chat_id, "❌ Invalid email. Please send again or /cancel")
                return
            set_email(chat_id, text)
            send_message(chat_id, f"✅ Email set to: {text}")
            session.awaiting_credential = None
            send_message(chat_id, "🚀 Starting signup automatically...")
            thread = threading.Thread(target=run_automation, args=(chat_id,), daemon=True)
            thread.start()
            return
        elif cred_type == "phone":
            if not text.startswith('+') or not text[1:].isdigit():
                send_message(chat_id, "❌ Invalid phone. Use country code, e.g., +911234567890")
                return
            set_phone(chat_id, text)
            send_message(chat_id, f"✅ Phone set to: {text}")
            session.awaiting_credential = None
            send_message(chat_id, "🚀 Starting signup automatically...")
            thread = threading.Thread(target=run_automation, args=(chat_id,), daemon=True)
            thread.start()
            return

    if text.startswith('/'):
        cmd = text.split()[0].lower()
        if cmd == '/start':
            handle_start(chat_id)
        elif cmd == '/addproxy':
            parts = text.split(maxsplit=1)
            if len(parts) < 2 or not parts[1]:
                send_message(chat_id, "Usage: /addproxy <proxy_string>\nExamples:\n  http://user:pass@ip:port\n  socks5://ip:port\n  ip:port (assumes http)")
                return
            proxy_str = parts[1].strip()
            ok, msg = validate_proxy(proxy_str)
            if not ok:
                send_message(chat_id, f"❌ Proxy validation failed: {msg}")
                return
            set_proxy(chat_id, proxy_str)
            send_message(chat_id, f"✅ Proxy added successfully!\n{proxy_str}")
        elif cmd == '/removeproxy':
            del_proxy(chat_id)
            send_message(chat_id, "✅ Proxy removed.")
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
        elif cmd == '/setphone':
            parts = text.split(maxsplit=1)
            if len(parts) < 2 or not parts[1]:
                send_message(chat_id, "Usage: /setphone <+911234567890>")
                return
            new_phone = parts[1].strip()
            if not new_phone.startswith('+') or not new_phone[1:].isdigit():
                send_message(chat_id, "❌ Invalid phone number.")
                return
            set_phone(chat_id, new_phone)
            send_message(chat_id, f"✅ Phone set to: {new_phone}")
        elif cmd == '/status':
            creds = get_credential(chat_id)
            proxy = get_proxy(chat_id)
            msg = "📊 Current status:\n"
            if creds["email"]:
                msg += f"📧 Email: {creds['email']}\n"
            if creds["phone"]:
                msg += f"📱 Phone: {creds['phone']}\n"
            if proxy:
                msg += f"🔑 Proxy: {proxy}\n"
            if not creds["email"] and not creds["phone"]:
                msg += "❌ No credential set. Use /start to choose."
            send_message(chat_id, msg)
        elif cmd == '/cancel':
            if session and session.awaiting_credential:
                session.awaiting_credential = None
                send_message(chat_id, "✅ Cancelled credential input.")
            else:
                send_message(chat_id, "No pending action.")
        else:
            send_message(chat_id, "Unknown command. Available:\n/start\n/addproxy <proxy>\n/removeproxy\n/setemail\n/setphone\n/status\n/cancel")
    else:
        send_message(chat_id, "Use commands or /start to begin.")

# -------------------- Polling --------------------
def polling_loop():
    offset = 0
    logger.info("Polling loop started.")
    while True:
        try:
            payload = {"timeout": 30, "offset": offset, "allowed_updates": json.dumps(["message", "callback_query"])}
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
                    elif 'callback_query' in update:
                        handle_callback_query(update['callback_query'])
            if data.get('result'):
                last = data['result'][-1]['update_id']
                if last >= offset:
                    offset = last + 1
        except Exception as e:
            logger.error(f"Poll exception: {e}")
            time.sleep(5)

# -------------------- Main --------------------
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
