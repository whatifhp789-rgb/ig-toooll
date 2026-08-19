#!/usr/bin/env python3
# Instagram Account Creator Bot – API-Based Signup

import os
import random
import string
import time
import names
import requests
import telebot
import json
import re

# ============================================================
#  🔐 YOUR BOT CREDENTIALS
# ============================================================
BOT_TOKEN = "8760264279:AAGFGJ-Y0s4BKL9ATpuT8lBUZeQ2ntj5fq0"          # <-- Put your bot token
OWNER_IDS = [8754004223]                    # <-- Put your Telegram user ID(s)
# ============================================================

# ============================================================
#  🌐 PROXY LIST – Add your proxies here
# ============================================================
PROXY_LIST = [
    # "http://user1:pass1@123.45.67.89:8080",
    # "http://user2:pass2@98.76.54.32:3128",
]
# ============================================================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

proxies = None
proxy_pool = PROXY_LIST.copy()

def get_random_proxy():
    if proxy_pool:
        return random.choice(proxy_pool)
    return None

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_random_delay():
    return random.randint(3, 8)

bot = telebot.TeleBot(BOT_TOKEN)
user_sessions = {}

# ============ CORE API FUNCTIONS ============

def get_csrf_token():
    """Get CSRF token and cookies from Instagram."""
    try:
        an_agent = get_random_user_agent()
        proxy_str = get_random_proxy()
        local_proxies = None
        if proxy_str:
            local_proxies = {"http": proxy_str, "https": proxy_str}

        # First request to get cookies
        session = requests.Session()
        session.headers.update({'user-agent': an_agent})
        if local_proxies:
            session.proxies.update(local_proxies)

        # Get main page to set cookies
        resp = session.get('https://www.instagram.com/')
        if resp.status_code != 200:
            return None, None

        # Get CSRF token from cookies
        csrf_token = session.cookies.get('csrftoken')
        if not csrf_token:
            return None, None

        # Get mid and ig_did
        mid = session.cookies.get('mid', '')
        ig_did = session.cookies.get('ig_did', '')

        # Extract app_id from page
        app_id = None
        match = re.search(r'"APP_ID":"(\d+)"', resp.text)
        if match:
            app_id = match.group(1)

        headers = {
            'authority': 'www.instagram.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': f'csrftoken={csrf_token}; mid={mid}; ig_did={ig_did}',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/accounts/emailsignup/',
            'user-agent': an_agent,
            'x-csrftoken': csrf_token,
            'x-ig-app-id': app_id or '936619743392459',
            'x-instagram-ajax': '1',
            'x-web-device-id': ig_did or '',
        }

        return headers, session
    except Exception as e:
        print(f"CSRF error: {e}")
        return None, None

def send_verification_email_api(email):
    """Send OTP using Instagram's API."""
    try:
        headers, session = get_csrf_token()
        if not headers:
            return False, "Failed to get CSRF token"

        device_id = headers.get('x-web-device-id') or ''.join(random.choices(string.digits, k=16))

        data = {
            'device_id': device_id,
            'email': email,
        }

        response = session.post(
            'https://www.instagram.com/api/v1/web/accounts/send_verify_email/',
            headers=headers,
            data=data,
            timeout=30
        )

        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get('email_sent'):
                # Store session for later use
                return True, response, headers, session
            else:
                return False, resp_json.get('message', 'Unknown error'), None, None
        else:
            return False, f"Status: {response.status_code}", None, None

    except Exception as e:
        return False, str(e), None, None

def validate_otp_api(email, code, headers, session):
    """Validate OTP using Instagram's API."""
    try:
        device_id = headers.get('x-web-device-id') or ''.join(random.choices(string.digits, k=16))

        data = {
            'code': code,
            'device_id': device_id,
            'email': email,
        }

        response = session.post(
            'https://www.instagram.com/api/v1/web/accounts/check_confirmation_code/',
            headers=headers,
            data=data,
            timeout=30
        )

        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get('status') == 'ok':
                signup_code = resp_json.get('signup_code')
                return True, signup_code, headers, session
            else:
                return False, resp_json.get('message', 'Invalid OTP'), headers, session
        else:
            return False, f"Status: {response.status_code}", headers, session

    except Exception as e:
        return False, str(e), headers, session

def create_instagram_account_api(email, signup_code, headers, session):
    """Create account using Instagram's API."""
    firstname = names.get_first_name()
    username = generate_username(firstname)
    password = f"{firstname.strip()}@{random.randint(100, 999)}"

    device_id = headers.get('x-web-device-id') or ''.join(random.choices(string.digits, k=16))
    client_id = headers.get('cookie', '').split('mid=')[1].split(';')[0] if 'mid=' in headers.get('cookie', '') else device_id

    data = {
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}',
        'email': email,
        'username': username,
        'first_name': firstname,
        'month': random.randint(1, 12),
        'day': random.randint(1, 28),
        'year': random.randint(1990, 2001),
        'client_id': client_id,
        'seamless_login_enabled': '1',
        'tos_version': 'row',
        'force_sign_up_code': signup_code,
    }

    wait_time = 30

    for attempt in range(1, 8):
        try:
            delay = get_random_delay()
            time.sleep(delay)

            if attempt > 1:
                # Get fresh headers
                new_headers, new_session = get_csrf_token()
                if new_headers:
                    headers = new_headers
                    session = new_session
                    data['client_id'] = headers.get('cookie', '').split('mid=')[1].split(';')[0] if 'mid=' in headers.get('cookie', '') else device_id

                if attempt > 3:
                    firstname = names.get_first_name()
                    username = generate_username(firstname)
                    password = f"{firstname.strip()}@{random.randint(100, 999)}"
                    data['username'] = username
                    data['enc_password'] = f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}'

            response = session.post(
                'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/',
                headers=headers,
                data=data,
                timeout=30
            )

            if response.status_code == 429:
                bot.send_message(chat_id, f"⏳ Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2
                continue

            if response.status_code == 200:
                resp_json = response.json()

                if resp_json.get('account_created'):
                    # Success - extract cookies
                    sessionid = session.cookies.get('sessionid', '')
                    csrftoken = headers.get('x-csrftoken', '')
                    cookie_str = f"sessionid={sessionid}; csrftoken={csrftoken}"

                    result_msg = (
                        f"✅ **Account Created Successfully!**\n"
                        f"👤 Username: `{username}`\n"
                        f"🔑 Password: `{password}`\n"
                        f"📧 Email: `{email}`\n"
                        f"🍪 Cookies: `{cookie_str}`"
                    )
                    return True, result_msg

                # Handle specific errors
                error_type = resp_json.get('error_type', '')
                if error_type == 'username_is_taken':
                    username = generate_username(firstname + random.choice(string.ascii_lowercase))
                    data['username'] = username
                    continue
                elif error_type == 'bad_password':
                    password = f"{firstname.strip()}@{random.randint(100, 999)}"
                    data['enc_password'] = f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}'
                    continue
                elif error_type == 'signup_code_expired':
                    return False, "⏰ Signup code expired. Please restart with /create."
                else:
                    return False, f"Error: {resp_json.get('message', 'Unknown error')}"

            else:
                return False, f"Status: {response.status_code}"

        except Exception as e:
            time.sleep(10)

    return False, "All attempts failed. Try again later."

def generate_username(firstname):
    base = firstname.lower().replace(" ", "")
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{base}_{suffix}"

# ============ BOT HANDLERS ============

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    if OWNER_IDS and chat_id not in OWNER_IDS:
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    bot.reply_to(message,
        "🤖 **Instagram Account Creator Bot**\n\n"
        "Send `/create <email>` to start.\n"
        "Example: `/create test@gmail.com`\n\n"
        "Bot uses Instagram's official API for fast creation."
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
        bot.reply_to(message, "❌ Please provide an email.\nExample: `/create test@gmail.com`")
        return
    email = parts[1].strip()

    bot.reply_to(message, f"🔄 Starting for `{email}` ...", parse_mode="Markdown")

    # Try to send OTP
    for attempt in range(3):
        success, result, headers, session = send_verification_email_api(email)
        if success:
            bot.send_message(chat_id, f"✅ OTP sent to `{email}`. Reply with the 6‑digit code.", parse_mode="Markdown")
            user_sessions[chat_id] = {
                'state': 'waiting_otp',
                'email': email,
                'headers': headers,
                'session': session,
            }
            return
        else:
            if attempt < 2:
                bot.send_message(chat_id, f"⚠️ OTP failed (attempt {attempt+1}). Retrying...")
                time.sleep(5)
            else:
                bot.send_message(chat_id, f"❌ Failed to send OTP.\n{result}")
                return

@bot.message_handler(func=lambda msg: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        bot.reply_to(message, "ℹ️ Use `/create <email>` to start.")
        return

    session_data = user_sessions[chat_id]
    if session_data.get('state') == 'waiting_otp':
        otp = message.text.strip()
        if not otp.isdigit() or len(otp) != 6:
            bot.reply_to(message, "❌ Enter a valid 6‑digit OTP.")
            return

        email = session_data['email']
        headers = session_data['headers']
        session = session_data['session']

        success, result, new_headers, new_session = validate_otp_api(email, otp, headers, session)

        if success:
            signup_code = result
            bot.send_message(chat_id, "✅ OTP validated. Creating account...")
            del user_sessions[chat_id]

            # Create account
            created, msg = create_instagram_account_api(email, signup_code, new_headers, new_session)
            bot.send_message(chat_id, msg, parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ {result}")
    else:
        bot.reply_to(message, "ℹ️ Use `/create <email>` to start.")

# ============ MAIN ============
if __name__ == "__main__":
    print("🤖 Bot started with API-based signup...")
    bot.infinity_polling()
