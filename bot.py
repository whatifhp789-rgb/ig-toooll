#!/usr/bin/env python3
# Instagram Account Creator Bot – Rate Limit Bypass + Proxy Management

import os
import random
import string
import time
import names
import requests
import telebot
import json
import sqlite3

# ============================================================
#  🔐 YOUR BOT CREDENTIALS
# ============================================================
BOT_TOKEN = "8760264279:AAFmr6hb-Uspz1pKR3xclQHP8aFsfF-4-yY"          # <-- Put your bot token
OWNER_IDS = [8754004223]                    # <-- Put your Telegram user ID(s)
# ============================================================

# ============================================================
#  🗃️ DATABASE SETUP (for proxies)
# ============================================================
DB_FILE = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS proxies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proxy TEXT UNIQUE,
        added_at INTEGER
    )''')
    conn.commit()
    conn.close()

def add_proxy_to_db(proxy):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO proxies (proxy, added_at) VALUES (?, ?)", (proxy, int(time.time())))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def remove_proxy_from_db(proxy):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM proxies WHERE proxy = ?", (proxy,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def get_all_proxies():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT proxy FROM proxies")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def clear_all_proxies():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM proxies")
    conn.commit()
    conn.close()

# ============================================================
#  🌐 PROXY PARSER & VALIDATOR (Universal)
# ============================================================
def parse_proxy(proxy_str):
    proxy_str = proxy_str.strip()
    if proxy_str.startswith(('http://', 'https://', 'socks5://')):
        return proxy_str
    parts = proxy_str.split(':')
    if len(parts) == 4:
        ip, port, user, passwd = parts
        return f"http://{user}:{passwd}@{ip}:{port}"
    if '@' in proxy_str:
        return f"http://{proxy_str}"
    if ':' in proxy_str:
        return f"http://{proxy_str}"
    return proxy_str

def validate_proxy(proxy_str):
    parsed = parse_proxy(proxy_str)
    try:
        proxies = {"http": parsed, "https": parsed}
        # Try multiple endpoints
        test_urls = [
            "https://httpbin.org/ip",
            "https://api.ipify.org?format=json",
            "https://www.instagram.com"
        ]
        for url in test_urls:
            try:
                response = requests.get(url, proxies=proxies, timeout=10)
                if response.status_code == 200:
                    return True, "Proxy is alive."
            except:
                continue
        # If none succeeded, try a HEAD request
        try:
            response = requests.head("https://www.google.com", proxies=proxies, timeout=10)
            if response.status_code < 400:
                return True, "Proxy is alive (HEAD check)."
        except:
            pass
        # All failed
        return False, "Proxy is not responding to any test endpoint."
    except Exception as e:
        return False, f"Proxy validation error: {str(e)}"

def get_random_proxy():
    proxies = get_all_proxies()
    if proxies:
        return random.choice(proxies)
    return None

# ============================================================
#  🌐 PROXY LIST – Legacy (not used, replaced by DB)
# ============================================================
# PROXY_LIST = [...]  # removed, now using database

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]

# ============================================================
#  🤖 BOT SETUP
# ============================================================
def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_random_delay():
    return random.randint(5, 15)  # seconds

bot = telebot.TeleBot(BOT_TOKEN)
user_sessions = {}

# ============ CORE FUNCTIONS ============

def get_headers():
    """Fetch fresh headers with a random user-agent and proxy from database."""
    while True:
        try:
            an_agent = get_random_user_agent()
            # Use a proxy from database
            proxy_str = get_random_proxy()
            local_proxies = None
            if proxy_str:
                parsed = parse_proxy(proxy_str)
                local_proxies = {"http": parsed, "https": parsed}

            # Get cookies using a request with the proxy
            r = requests.get(
                'https://www.instagram.com/api/v1/web/accounts/login/ajax/',
                headers={'user-agent': an_agent},
                proxies=local_proxies,
                timeout=30
            ).cookies

            response1 = requests.get(
                'https://www.instagram.com/',
                headers={'user-agent': an_agent},
                proxies=local_proxies,
                timeout=30
            )
            appid = response1.text.split('APP_ID":"')[1].split('"')[0]
            rollout = response1.text.split('rollout_hash":"')[1].split('"')[0]

            headers = {
                'authority': 'www.instagram.com',
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded',
                'cookie': f'dpr=3; csrftoken={r["csrftoken"]}; mid={r["mid"]}; ig_did={r["ig_did"]}',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/accounts/signup/email/',
                'user-agent': an_agent,
                'x-csrftoken': r["csrftoken"],
                'x-ig-app-id': str(appid),
                'x-instagram-ajax': str(rollout),
                'x-web-device-id': r["ig_did"],
            }
            # Also return the proxy used (for logging)
            return headers, local_proxies
        except Exception:
            time.sleep(2)

def generate_username(firstname):
    base = firstname.lower().replace(" ", "")
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{base}_{suffix}"

def send_verification_email(headers, email, proxies):
    try:
        device_id = headers['cookie'].split('mid=')[1].split(';')[0]
        data = {'device_id': device_id, 'email': email}
        response = requests.post(
            'https://www.instagram.com/api/v1/accounts/send_verify_email/',
            headers=headers, data=data, proxies=proxies, timeout=30
        )
        if response.status_code == 200 and 'email_sent":true' in response.text:
            return True, response.text
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:500]}"
    except Exception as e:
        return False, str(e)

def validate_otp(headers, email, code, proxies):
    try:
        device_id = headers['cookie'].split('mid=')[1].split(';')[0]
        data = {'code': code, 'device_id': device_id, 'email': email}
        response = requests.post(
            'https://www.instagram.com/api/v1/accounts/check_confirmation_code/',
            headers=headers, data=data, proxies=proxies, timeout=30
        )
        return response
    except Exception:
        return None

def create_instagram_account(headers, email, signup_code, chat_id, proxies):
    firstname = names.get_first_name()
    username = generate_username(firstname)
    password = f"{firstname.strip()}@{random.randint(100, 999)}"

    data = {
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{password}',
        'email': email,
        'username': username,
        'first_name': firstname,
        'month': random.randint(1, 12),
        'day': random.randint(1, 28),
        'year': random.randint(1990, 2001),
        'client_id': headers['cookie'].split('mid=')[1].split(';')[0],
        'seamless_login_enabled': '1',
        'tos_version': 'row',
        'force_sign_up_code': signup_code,
    }

    # Exponential backoff variables
    wait_time = 30  # start with 30 seconds

    for attempt in range(1, 10):  # up to 10 attempts
        try:
            # Add random delay before request
            delay = get_random_delay()
            time.sleep(delay)

            if attempt > 1:
                # Get fresh headers and a new proxy
                headers, proxies = get_headers()
                data['client_id'] = headers['cookie'].split('mid=')[1].split(';')[0]
                # Also regenerate username/password if needed
                if attempt > 3:
                    firstname = names.get_first_name()
                    username = generate_username(firstname)
                    password = f"{firstname.strip()}@{random.randint(100, 999)}"
                    data['username'] = username
                    data['enc_password'] = f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{password}'

            response = requests.post(
                'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/',
                headers=headers, data=data, proxies=proxies, timeout=30
            )

            full_response = response.text
            status_code = response.status_code

            # If rate limited, wait exponentially
            if status_code == 429:
                bot.send_message(chat_id, f"⏳ Rate limited. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                wait_time *= 2  # double the wait time for next time
                continue

            if '"account_created":true' in full_response:
                sessionid = response.cookies.get('sessionid')
                csrftoken = headers['x-csrftoken']
                cookie_dict = response.cookies.get_dict()
                cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
                full_cookies = f"{headers['cookie']}; sessionid={sessionid}; {cookie_str}"

                result_msg = (
                    f"✅ **Account Created Successfully!**\n"
                    f"👤 Username: `{username}`\n"
                    f"🔑 Password: `{password}`\n"
                    f"📧 Email: `{email}`\n"
                    f"🍪 Cookies:\n`{full_cookies}`"
                )
                bot.send_message(chat_id, result_msg, parse_mode="Markdown")
                return True

            # Handle specific errors
            if '"error_type":"username_is_taken"' in full_response:
                username = generate_username(firstname + random.choice(string.ascii_lowercase))
                data['username'] = username
                continue
            elif '"error_type":"bad_password"' in full_response:
                password = f"{firstname.strip()}@{random.randint(100, 999)}"
                data['enc_password'] = f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{password}'
                continue
            elif '"error_type":"signup_code_expired"' in full_response:
                bot.send_message(chat_id, "⏰ Signup code expired. Resending OTP...")
                new_headers, new_proxies = get_headers()
                success, msg = send_verification_email(new_headers, email, new_proxies)
                if success:
                    bot.send_message(chat_id, f"✅ New OTP sent to `{email}`. Please reply with the new code.", parse_mode="Markdown")
                    user_sessions[chat_id] = {
                        'state': 'waiting_otp',
                        'email': email,
                        'headers': new_headers,
                        'signup_code': None,
                        'proxies': new_proxies,
                    }
                    return False
                else:
                    bot.send_message(chat_id, f"❌ Failed to resend OTP: {msg}")
                    return False

            # Unknown error – show full response
            error_msg = f"Status: {status_code}\nResponse: {full_response[:800]}"
            bot.send_message(chat_id, f"❌ Attempt {attempt} failed.\nError: {error_msg}")
            # Continue to next attempt with fresh headers

        except Exception as e:
            bot.send_message(chat_id, f"❌ Exception: {str(e)}")
            time.sleep(10)

    bot.send_message(chat_id, "❌ All attempts failed. Try again later with a new proxy or email.")
    return False

# ============================================================
#  🧰 PROXY MANAGEMENT COMMANDS
# ============================================================
@bot.message_handler(commands=['addproxy'])
def handle_addproxy(message):
    chat_id = message.chat.id
    if OWNER_IDS and chat_id not in OWNER_IDS:
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(message, "❌ Usage: `/addproxy <proxy>`\nSupported: `ip:port:user:pass` or `user:pass@ip:port` or `ip:port`")
        return
    proxy_str = parts[1].strip()
    ok, msg = validate_proxy(proxy_str)
    if not ok:
        bot.reply_to(message, f"⚠️ Proxy validation warning: {msg}\nStill adding proxy (you can test later).")
    if add_proxy_to_db(proxy_str):
        bot.reply_to(message, f"✅ Proxy added successfully!\n{proxy_str}")
    else:
        bot.reply_to(message, f"⚠️ Proxy already exists in the list.")

@bot.message_handler(commands=['removeproxy'])
def handle_removeproxy(message):
    chat_id = message.chat.id
    if OWNER_IDS and chat_id not in OWNER_IDS:
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(message, "❌ Usage: `/removeproxy <proxy_string>`")
        return
    proxy_str = parts[1].strip()
    if remove_proxy_from_db(proxy_str):
        bot.reply_to(message, f"✅ Proxy removed: {proxy_str}")
    else:
        bot.reply_to(message, f"❌ Proxy not found in the list.")

@bot.message_handler(commands=['listproxies'])
def handle_listproxies(message):
    chat_id = message.chat.id
    if OWNER_IDS and chat_id not in OWNER_IDS:
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    proxies = get_all_proxies()
    if not proxies:
        bot.reply_to(message, "📭 No proxies stored.")
        return
    msg = "📋 **Stored Proxies:**\n" + "\n".join([f"• {p}" for p in proxies])
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['clearproxies'])
def handle_clearproxies(message):
    chat_id = message.chat.id
    if OWNER_IDS and chat_id not in OWNER_IDS:
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    clear_all_proxies()
    bot.reply_to(message, "🗑️ All proxies cleared.")

# ============================================================
#  🚀 ACCOUNT CREATION COMMANDS
# ============================================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    if OWNER_IDS and chat_id not in OWNER_IDS:
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    bot.reply_to(message,
        "🤖 **Instagram Account Creator Bot**\n\n"
        "📌 **Proxy Management:**\n"
        "/addproxy <proxy> – add a working proxy\n"
        "/removeproxy <proxy> – remove a proxy\n"
        "/listproxies – list all saved proxies\n"
        "/clearproxies – remove all proxies\n\n"
        "🚀 **Create Account:**\n"
        "/create <email> – start account creation\n\n"
        "Example: `/create test@example.com`"
    )

@bot.message_handler(commands=['create'])
def handle_create(message):
    chat_id = message.chat.id
    if OWNER_IDS and chat_id not in OWNER_IDS:
        bot.reply_to(message, "⛔ Unauthorized.")
        return

    if chat_id in user_sessions and user_sessions[chat_id].get('state') == 'waiting_otp':
        bot.reply_to(message, "⏳ You have a pending OTP. Please enter the code.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(message, "❌ Please provide an email.\nExample: `/create test@example.com`")
        return
    email = parts[1].strip()

    bot.reply_to(message, f"🔄 Starting for `{email}` ...", parse_mode="Markdown")

    # Try up to 3 times to send OTP
    for attempt in range(3):
        headers, proxies = get_headers()
        success, response_text = send_verification_email(headers, email, proxies)
        if success:
            bot.send_message(chat_id, f"✅ OTP sent to `{email}`. Reply with the 6‑digit code.", parse_mode="Markdown")
            user_sessions[chat_id] = {
                'state': 'waiting_otp',
                'email': email,
                'headers': headers,
                'signup_code': None,
                'proxies': proxies,
            }
            return
        else:
            if attempt < 2:
                bot.send_message(chat_id, f"⚠️ OTP sending failed (attempt {attempt+1}). Retrying...")
                time.sleep(10)
            else:
                bot.send_message(chat_id, f"❌ Failed to send OTP after 3 attempts.\nError: {response_text}")
                return

@bot.message_handler(func=lambda msg: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.reply_to(message, "ℹ️ Use `/create <email>` to start.")
        return

    session = user_sessions[chat_id]
    if session.get('state') == 'waiting_otp':
        otp = message.text.strip()
        if not otp.isdigit() or len(otp) != 6:
            bot.reply_to(message, "❌ Enter a valid 6‑digit OTP.")
            return

        headers = session['headers']
        email = session['email']
        proxies = session.get('proxies')
        response = validate_otp(headers, email, otp, proxies)

        if response and 'status":"ok' in response.text:
            signup_code = response.json().get('signup_code')
            if signup_code:
                bot.send_message(chat_id, "✅ OTP validated. Creating account...")
                # clear OTP state
                del user_sessions[chat_id]
                # start creation (may re-add session if signup expires)
                create_instagram_account(headers, email, signup_code, chat_id, proxies)
            else:
                bot.send_message(chat_id, "❌ No signup_code received.")
                del user_sessions[chat_id]
        else:
            bot.reply_to(message, "❌ Invalid OTP. Try again or /create.")
    else:
        bot.reply_to(message, "ℹ️ Use `/create <email>` to start.")

# ============================================================
#  🏁 MAIN
# ============================================================
if __name__ == "__main__":
    init_db()
    print("🤖 Bot started with proxy rotation, anti-rate-limit, and proxy management.")
    bot.infinity_polling()
