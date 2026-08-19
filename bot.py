#!/usr/bin/env python3
# Instagram Account Creator Bot – Hardcoded Credentials

import os
import random
import string
import time
import names
import requests
import telebot

# ============================================================
#  ✏️ EDIT THESE TWO LINES – PUT YOUR VALUES HERE
# ============================================================
BOT_TOKEN = "8760264279:AAGFGJ-Y0s4BKL9ATpuT8lBUZeQ2ntj5fq0"          # <-- Paste your bot token (string)
OWNER_IDS = [8754004223]                    # <-- Paste your Telegram user ID (integer, list)
# ============================================================
# If you want to allow everyone, set OWNER_IDS = []

# Optional: Proxy (if you want to use one)
PROXY_STR = ""   # e.g., "http://user:pass@ip:port" – leave empty if not used

# ============================================================

proxies = None
if PROXY_STR:
    proxies = {"http": PROXY_STR, "https": PROXY_STR}

bot = telebot.TeleBot(BOT_TOKEN)
user_sessions = {}  # chat_id -> state

# ============ CORE FUNCTIONS ============

def get_headers():
    """Fetch fresh headers with cookies."""
    while True:
        try:
            an_agent = (
                f'Mozilla/5.0 (Linux; Android {random.randint(9, 13)}; '
                f'{"".join(random.choices(string.ascii_uppercase, k=3))}{random.randint(111, 999)}) '
                f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36'
            )
            r = requests.get(
                'https://www.instagram.com/api/v1/web/accounts/login/ajax/',
                headers={'user-agent': an_agent},
                proxies=proxies,
                timeout=30
            ).cookies

            response1 = requests.get(
                'https://www.instagram.com/',
                headers={'user-agent': an_agent},
                proxies=proxies,
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
            return headers
        except Exception:
            time.sleep(2)

def generate_username(firstname):
    base = firstname.lower().replace(" ", "")
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{base}_{suffix}"

def send_verification_email(headers, email):
    try:
        device_id = headers['cookie'].split('mid=')[1].split(';')[0]
        data = {'device_id': device_id, 'email': email}
        response = requests.post(
            'https://www.instagram.com/api/v1/accounts/send_verify_email/',
            headers=headers, data=data, proxies=proxies, timeout=30
        )
        return response.text
    except Exception:
        return ""

def validate_otp(headers, email, code):
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

def create_instagram_account(headers, email, signup_code, chat_id):
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

    for attempt in range(3):
        try:
            if attempt > 0:
                headers = get_headers()
                data['client_id'] = headers['cookie'].split('mid=')[1].split(';')[0]

            response = requests.post(
                'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/',
                headers=headers, data=data, proxies=proxies, timeout=30
            )

            if '"account_created":true' in response.text:
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

            if '"error_type":"username_is_taken"' in response.text:
                username = generate_username(firstname + random.choice(string.ascii_lowercase))
                data['username'] = username
                continue
            elif '"error_type":"bad_password"' in response.text:
                password = f"{firstname.strip()}@{random.randint(100, 999)}"
                data['enc_password'] = f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{password}'
                continue
            else:
                error = response.text[:300]
                bot.send_message(chat_id, f"❌ Attempt {attempt+1} failed.\nError: {error}")
                return False

        except Exception as e:
            bot.send_message(chat_id, f"❌ Exception {attempt+1}: {str(e)}")
            time.sleep(3)

    bot.send_message(chat_id, "❌ All attempts failed.")
    return False

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
        "Example: `/create test@example.com`\n\n"
        "You'll receive OTP – reply with the 6‑digit code."
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

    headers = get_headers()
    resp_text = send_verification_email(headers, email)

    if 'email_sent":true' in resp_text:
        bot.send_message(chat_id, f"✅ OTP sent to `{email}`. Reply with the 6‑digit code.", parse_mode="Markdown")
        user_sessions[chat_id] = {
            'state': 'waiting_otp',
            'email': email,
            'headers': headers,
            'signup_code': None,
        }
    else:
        bot.send_message(chat_id, f"❌ Failed to send OTP.\n{resp_text[:200]}")

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
        response = validate_otp(headers, email, otp)

        if response and 'status":"ok' in response.text:
            signup_code = response.json().get('signup_code')
            if signup_code:
                bot.send_message(chat_id, "✅ OTP validated. Creating account...")
                del user_sessions[chat_id]
                create_instagram_account(headers, email, signup_code, chat_id)
            else:
                bot.send_message(chat_id, "❌ No signup_code received.")
                del user_sessions[chat_id]
        else:
            bot.reply_to(message, "❌ Invalid OTP. Try again or /create.")
    else:
        bot.reply_to(message, "ℹ️ Use `/create <email>` to start.")

# ============ MAIN ============
if __name__ == "__main__":
    print("🤖 Bot started polling...")
    bot.infinity_polling()
