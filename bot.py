#!/usr/bin/env python3
# Instagram Account Creator Bot – Rate Limit Bypass + CAPTCHA Handling

import os
import random
import string
import time
import names
import requests
import telebot
import json
import sqlite3
from io import BytesIO

# ============================================================
#  🔐 YOUR BOT CREDENTIALS
# ============================================================
BOT_TOKEN = "8760264279:AAFmr6hb-Uspz1pKR3xclQHP8aFsfF-4-yY"
OWNER_IDS = [8754004223]
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
#  🌐 PROXY PARSER & VALIDATOR
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
        try:
            response = requests.head("https://www.google.com", proxies=proxies, timeout=10)
            if response.status_code < 400:
                return True, "Proxy is alive (HEAD check)."
        except:
            pass
        return False, "Proxy is not responding to any test endpoint."
    except Exception as e:
        return False, f"Proxy validation error: {str(e)}"

def get_random_proxy():
    proxies = get_all_proxies()
    if proxies:
        return random.choice(proxies)
    return None

# ============================================================
#  USER AGENTS
# ============================================================
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
    return random.randint(5, 15)

bot = telebot.TeleBot(BOT_TOKEN)
user_sessions = {}

# ============ CORE FUNCTIONS ============

def get_headers():
    while True:
        try:
            an_agent = get_random_user_agent()
            proxy_str = get_random_proxy()
            local_proxies = None
            if proxy_str:
                parsed = parse_proxy(proxy_str)
                local_proxies = {"http": parsed, "https": parsed}

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
            return headers, local_proxies
        except Exception:
            time.sleep(2)

def generate_username(firstname):
    base = firstname.lower().replace(" ", "")
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{base}_{suffix}"

# ====== MODIFIED: send_verification_email with CAPTCHA support ======
def send_verification_email(headers, email, proxies, captcha_solution=None, captcha_id=None):
    try:
        device_id = headers['cookie'].split('mid=')[1].split(';')[0]
        data = {'device_id': device_id, 'email': email}
        if captcha_solution and captcha_id:
            data['captcha_solution'] = captcha_solution
            data['captcha_id'] = captcha_id

        response = requests.post(
            'https://www.instagram.com/api/v1/accounts/send_verify_email/',
            headers=headers, data=data, proxies=proxies, timeout=30
        )
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get('email_sent'):
                return True, response.text, None, None
            elif resp_json.get('require_captcha'):
                captcha_url = resp_json.get('captcha_url')
                captcha_id = resp_json.get('captcha_id')
                # If captcha_url is missing, construct from captcha_id
                if not captcha_url and captcha_id:
                    captcha_url = f"https://www.instagram.com/api/v1/accounts/get_captcha/?captcha_id={captcha_id}"
                return False, "require_captcha", captcha_url, captcha_id
            else:
                return False, f"Response: {response.text[:500]}", None, None
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:500]}", None, None
    except Exception as e:
        return False, str(e), None, None

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

    wait_time = 30

    for attempt in range(1, 10):
        try:
            delay = get_random_delay()
            time.sleep(delay)

            if attempt > 1:
                headers, proxies = get_headers()
                data['client_id'] = headers['cookie'].split('mid=')[1].split(';')[0]
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

            if status_code == 429:
                bot.send_message(chat_id, f"⏳ Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2
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
                success, msg, _, _ = send_verification_email(new_headers, email, new_proxies)
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

            error_msg = f"Status: {status_code}\nResponse: {full_response[:800]}"
            bot.send_message(chat_id, f"❌ Attempt {attempt} failed.\nError: {error_msg}")

        except Exception as e:
            bot.send_message(chat_id, f"❌ Exception: {str(e)}")
            time.sleep(10)

    bot.send_message(chat_id, "❌ All attempts failed. Try again later.")
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
        bot.reply_to(message, "❌ Usage: `/addproxy <proxy>`")
        return
    proxy_str = parts[1].strip()
    ok, msg = validate_proxy(proxy_str)
    if not ok:
        bot.reply_to(message, f"⚠️ Proxy validation warning: {msg}\nStill adding proxy (you can test later).")
    if add_proxy_to_db(proxy_str):
        bot.reply_to(message, f"✅ Proxy added successfully!\n{proxy_str}")
    else:
        bot.reply_to(message, f"⚠️ Proxy already exists.")

@bot.message_handler(commands=['removeproxy'])
def handle_removeproxy(message):
    chat_id = message.chat.id
    if OWNER_IDS and chat_id not in OWNER_IDS:
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(message, "❌ Usage: `/removeproxy <proxy>`")
        return
    proxy_str = parts[1].strip()
    if remove_proxy_from_db(proxy_str):
        bot.reply_to(message, f"✅ Proxy removed: {proxy_str}")
    else:
        bot.reply_to(message, f"❌ Proxy not found.")

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
#  🚀 ACCOUNT CREATION WITH CAPTCHA
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
        "/addproxy <proxy> – add a proxy\n"
        "/removeproxy <proxy> – remove a proxy\n"
        "/listproxies – list all proxies\n"
        "/clearproxies – remove all proxies\n\n"
        "🚀 **Create Account:**\n"
        "/create <email> – start account creation\n\n"
        "If CAPTCHA appears, the bot will send the image – just reply with the text you see."
    )

@bot.message_handler(commands=['create'])
def handle_create(message):
    chat_id = message.chat.id
    if OWNER_IDS and chat_id not in OWNER_IDS:
        bot.reply_to(message, "⛔ Unauthorized.")
        return

    if chat_id in user_sessions and user_sessions[chat_id].get('state') in ('waiting_otp', 'waiting_captcha'):
        bot.reply_to(message, "⏳ You have a pending OTP or CAPTCHA. Please complete it first.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(message, "❌ Please provide an email.\nExample: `/create test@example.com`")
        return
    email = parts[1].strip()

    bot.reply_to(message, f"🔄 Starting for `{email}` ...", parse_mode="Markdown")

    headers, proxies = get_headers()
    success, response, captcha_url, captcha_id = send_verification_email(headers, email, proxies)

    if success:
        bot.send_message(chat_id, f"✅ OTP sent to `{email}`. Reply with the 6‑digit code.", parse_mode="Markdown")
        user_sessions[chat_id] = {
            'state': 'waiting_otp',
            'email': email,
            'headers': headers,
            'proxies': proxies,
        }
        return
    elif response == "require_captcha" and captcha_url:
        try:
            captcha_response = requests.get(captcha_url, proxies=proxies, timeout=30)
            if captcha_response.status_code == 200:
                captcha_image = BytesIO(captcha_response.content)
                bot.send_photo(chat_id, captcha_image, caption="🧩 **CAPTCHA Required**\nPlease enter the text you see in the image.\n\nReply with the text.")
                user_sessions[chat_id] = {
                    'state': 'waiting_captcha',
                    'email': email,
                    'headers': headers,
                    'proxies': proxies,
                    'captcha_id': captcha_id,
                    'captcha_url': captcha_url,
                }
                return
            else:
                bot.send_message(chat_id, f"⚠️ Could not download CAPTCHA image. Status: {captcha_response.status_code}")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ Error downloading CAPTCHA: {str(e)}")
        # Fallback: try to get CAPTCHA from get_captcha endpoint
        try:
            fallback_url = 'https://www.instagram.com/api/v1/accounts/get_captcha/'
            fallback_resp = requests.get(fallback_url, headers=headers, proxies=proxies, timeout=30)
            if fallback_resp.status_code == 200:
                captcha_image = BytesIO(fallback_resp.content)
                bot.send_photo(chat_id, captcha_image, caption="🧩 **CAPTCHA Required (fallback)**\nPlease enter the text you see in the image.\n\nReply with the text.")
                user_sessions[chat_id] = {
                    'state': 'waiting_captcha',
                    'email': email,
                    'headers': headers,
                    'proxies': proxies,
                    'captcha_id': None,
                    'captcha_url': None,
                }
                return
            else:
                bot.send_message(chat_id, f"❌ Could not retrieve CAPTCHA from fallback endpoint.")
        except Exception as e:
            bot.send_message(chat_id, f"❌ Fallback CAPTCHA error: {str(e)}")
    else:
        bot.send_message(chat_id, f"❌ Failed to send OTP.\n{response}")

@bot.message_handler(func=lambda msg: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.reply_to(message, "ℹ️ Use `/create <email>` to start.")
        return

    session = user_sessions[chat_id]
    state = session.get('state')

    if state == 'waiting_captcha':
        solution = message.text.strip()
        if not solution:
            bot.reply_to(message, "❌ Please enter the CAPTCHA text.")
            return

        headers = session['headers']
        email = session['email']
        proxies = session.get('proxies')
        captcha_id = session.get('captcha_id')

        # Resend OTP with CAPTCHA solution
        success, response, _, _ = send_verification_email(headers, email, proxies, solution, captcha_id)

        if success:
            bot.send_message(chat_id, f"✅ OTP sent to `{email}`. Reply with the 6‑digit code.", parse_mode="Markdown")
            user_sessions[chat_id] = {
                'state': 'waiting_otp',
                'email': email,
                'headers': headers,
                'proxies': proxies,
            }
        else:
            if response == "require_captcha":
                bot.send_message(chat_id, "❌ CAPTCHA solution incorrect. Please try again with a new image.")
                # Remove session to let user restart
                del user_sessions[chat_id]
            else:
                bot.send_message(chat_id, f"❌ Failed to send OTP after CAPTCHA.\n{response}")
                del user_sessions[chat_id]

    elif state == 'waiting_otp':
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
                del user_sessions[chat_id]
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
    print("🤖 Bot started with CAPTCHA handling, proxy rotation, and anti-rate-limit.")
    bot.infinity_polling()
