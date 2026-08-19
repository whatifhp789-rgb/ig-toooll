#!/usr/bin/env python3
# Instagram Account Creator Bot – With Proxy Management & Validation

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
BOT_TOKEN = "8760264279:AAHhaHYLObOhbe9NPWGk91k0OiXqDuDCHO4"          # <-- Put your bot token
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
    # Also keep user sessions and photos? We'll keep those in memory for now.
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

def validate_proxy(proxy_str):
    """Check if proxy is alive by making a request to ipinfo.io through it."""
    try:
        proxies = {"http": proxy_str, "https": proxy_str}
        # Use a short timeout
        response = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=10)
        if response.status_code == 200:
            return True, "Proxy is alive."
        else:
            return False, f"Proxy returned status {response.status_code}."
    except Exception as e:
        return False, f"Proxy error: {str(e)}"

def get_random_proxy():
    proxies = get_all_proxies()
    if proxies:
        return random.choice(proxies)
    return None

# ============================================================
#  🧑 INDIAN NAMES & DOB
# ============================================================
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

def random_dob():
    age = random.randint(30, 80)
    year = 2026 - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return day, month, year

# ============================================================
#  🤖 BOT SETUP
# ============================================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

bot = telebot.TeleBot(BOT_TOKEN)
user_sessions = {}
user_photos = {}

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_random_delay():
    return random.randint(10, 30)

# ============ HEADER FETCH (WITH FALLBACK APP ID) ============
DEFAULT_APP_ID = "936619743392459"

def get_headers():
    """Fetch fresh headers; use default app id if scraping fails."""
    while True:
        try:
            an_agent = get_random_user_agent()
            proxy_str = get_random_proxy()
            proxies = None
            if proxy_str:
                proxies = {"http": proxy_str, "https": proxy_str}

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

            appid = DEFAULT_APP_ID
            try:
                appid = response1.text.split('APP_ID":"')[1].split('"')[0]
            except:
                pass
            rollout = "1"
            try:
                rollout = response1.text.split('rollout_hash":"')[1].split('"')[0]
            except:
                pass

            headers = {
                'authority': 'www.instagram.com',
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded',
                'cookie': f'dpr=3; csrftoken={r["csrftoken"]}; mid={r["mid"]}; ig_did={r["ig_did"]}',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/accounts/emailsignup/',
                'user-agent': an_agent,
                'x-csrftoken': r["csrftoken"],
                'x-ig-app-id': str(appid),
                'x-instagram-ajax': str(rollout),
                'x-web-device-id': r["ig_did"],
            }
            return headers, proxies
        except Exception as e:
            print(f"Header fetch error: {e}")
            time.sleep(5)

# ============ API FUNCTIONS ============
def send_verification_email(headers, email, proxies):
    try:
        device_id = headers['cookie'].split('mid=')[1].split(';')[0]
        data = {'device_id': device_id, 'email': email}
        response = requests.post(
            'https://www.instagram.com/api/v1/web/accounts/send_verify_email/',
            headers=headers, data=data, proxies=proxies, timeout=30
        )
        if response.status_code == 200 and 'email_sent":true' in response.text:
            return True, response.text, headers
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:500]}", headers
    except Exception as e:
        return False, str(e), headers

def validate_otp(headers, email, code, proxies):
    try:
        device_id = headers['cookie'].split('mid=')[1].split(';')[0]
        data = {'code': code, 'device_id': device_id, 'email': email}
        response = requests.post(
            'https://www.instagram.com/api/v1/web/accounts/check_confirmation_code/',
            headers=headers, data=data, proxies=proxies, timeout=30
        )
        return response
    except Exception:
        return None

def upload_profile_pic(sessionid, csrftoken, photo_path, proxies):
    try:
        url = 'https://www.instagram.com/accounts/web_change_profile_picture/'
        headers = {
            'cookie': f'sessionid={sessionid}; csrftoken={csrftoken};',
            'x-csrftoken': csrftoken,
            'referer': 'https://www.instagram.com/accounts/edit/',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': get_random_user_agent(),
        }
        with open(photo_path, 'rb') as f:
            files = {'profile_pic': f}
            resp = requests.post(url, headers=headers, files=files, proxies=proxies, timeout=30)
        if resp.status_code == 200 and '"changed_profile":true' in resp.text:
            return True
        else:
            return False
    except Exception as e:
        print(f"DP upload error: {e}")
        return False

def create_instagram_account(headers, email, signup_code, chat_id, proxies):
    full_name = random_indian_name()
    firstname = full_name.split()[0]
    username = generate_username(firstname)
    password = f"{firstname.strip()}@{random.randint(100, 999)}"
    day, month, year = random_dob()

    data = {
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{password}',
        'email': email,
        'username': username,
        'first_name': full_name,
        'month': month,
        'day': day,
        'year': year,
        'client_id': headers['cookie'].split('mid=')[1].split(';')[0],
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
                headers, proxies = get_headers()
                data['client_id'] = headers['cookie'].split('mid=')[1].split(';')[0]
                if attempt > 3:
                    full_name = random_indian_name()
                    firstname = full_name.split()[0]
                    username = generate_username(firstname)
                    password = f"{firstname.strip()}@{random.randint(100, 999)}"
                    data['first_name'] = full_name
                    data['username'] = username
                    data['enc_password'] = f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{password}'

            response = requests.post(
                'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/',
                headers=headers, data=data, proxies=proxies, timeout=30
            )

            if response.status_code == 429:
                bot.send_message(chat_id, f"⏳ Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2
                continue

            if '"account_created":true' in response.text:
                sessionid = response.cookies.get('sessionid')
                csrftoken = headers['x-csrftoken']
                cookie_dict = response.cookies.get_dict()
                cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
                full_cookies = f"{headers['cookie']}; sessionid={sessionid}; {cookie_str}"

                dp_uploaded = False
                if chat_id in user_photos and os.path.exists(user_photos[chat_id]):
                    dp_uploaded = upload_profile_pic(sessionid, csrftoken, user_photos[chat_id], proxies)

                result_msg = (
                    f"✅ **Account Created Successfully!**\n"
                    f"👤 Name: {full_name}\n"
                    f"👤 Username: `{username}`\n"
                    f"🔑 Password: `{password}`\n"
                    f"📧 Email: `{email}`\n"
                    f"📅 DOB: {day}/{month}/{year}\n"
                    f"🖼️ DP Uploaded: {'✅' if dp_uploaded else '❌'}\n"
                    f"🍪 Cookies:\n`{full_cookies}`"
                )
                bot.send_message(chat_id, result_msg, parse_mode="Markdown")
                return True

            # Error handling
            if '"error_type":"username_is_taken"' in response.text:
                username = generate_username(firstname + random.choice(string.ascii_lowercase))
                data['username'] = username
                continue
            elif '"error_type":"bad_password"' in response.text:
                password = f"{firstname.strip()}@{random.randint(100, 999)}"
                data['enc_password'] = f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{password}'
                continue
            elif '"error_type":"signup_code_expired"' in response.text:
                bot.send_message(chat_id, "⏰ Signup code expired. Resending OTP...")
                new_headers, new_proxies = get_headers()
                success, msg, _ = send_verification_email(new_headers, email, new_proxies)
                if success:
                    bot.send_message(chat_id, f"✅ New OTP sent to `{email}`. Please reply with the new code.", parse_mode="Markdown")
                    user_sessions[chat_id] = {
                        'state': 'waiting_otp',
                        'email': email,
                        'headers': new_headers,
                        'proxies': new_proxies,
                    }
                    return False
                else:
                    bot.send_message(chat_id, f"❌ Failed to resend OTP: {msg}")
                    return False

            error_msg = response.text[:800]
            bot.send_message(chat_id, f"❌ Attempt {attempt} failed.\nError: {error_msg}")
            time.sleep(5)

        except Exception as e:
            bot.send_message(chat_id, f"❌ Exception: {str(e)}")
            time.sleep(10)

    bot.send_message(chat_id, "❌ All attempts failed. Try again later.")
    return False

def generate_username(firstname):
    base = firstname.lower().replace(" ", "")
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{base}_{suffix}"

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
        bot.reply_to(message, "❌ Usage: `/addproxy http://user:pass@ip:port` or `socks5://ip:port`")
        return
    proxy_str = parts[1].strip()

    # Validate the proxy
    ok, msg = validate_proxy(proxy_str)
    if not ok:
        bot.reply_to(message, f"❌ Proxy validation failed: {msg}")
        return

    # Store it
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
#  📷 DP SETUP
# ============================================================
@bot.message_handler(commands=['setdp'])
def handle_setdp(message):
    chat_id = message.chat.id
    if OWNER_IDS and chat_id not in OWNER_IDS:
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    bot.reply_to(message, "📸 Please send a photo with caption `/setdp` to set it as your profile picture.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    if OWNER_IDS and chat_id not in OWNER_IDS:
        return
    caption = message.caption or ""
    if "/setdp" not in caption:
        return
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/dp_{chat_id}.jpg"
    with open(file_path, 'wb') as f:
        f.write(downloaded_file)
    user_photos[chat_id] = file_path
    bot.reply_to(message, "✅ Profile picture saved! It will be used for your next account creation.")

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
        "📸 **Profile Picture:**\n"
        "/setdp – send a photo with this caption to save it\n\n"
        "🚀 **Create Account:**\n"
        "/create <email> – start account creation\n\n"
        "Example: `/create test@gmail.com`"
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

    for attempt in range(5):
        headers, proxies = get_headers()
        success, response_text, headers = send_verification_email(headers, email, proxies)
        if success:
            bot.send_message(chat_id, f"✅ OTP sent to `{email}`. Reply with the 6‑digit code.", parse_mode="Markdown")
            user_sessions[chat_id] = {
                'state': 'waiting_otp',
                'email': email,
                'headers': headers,
                'proxies': proxies,
            }
            return
        else:
            if "Status: 404" in response_text:
                bot.send_message(chat_id, f"⚠️ OTP failed (404). Refreshing headers and retrying...")
                time.sleep(5)
                continue
            else:
                if attempt < 4:
                    bot.send_message(chat_id, f"⚠️ OTP failed (attempt {attempt+1}). Retrying...")
                    time.sleep(10)
                else:
                    bot.send_message(chat_id, f"❌ Failed to send OTP after multiple attempts.\n{response_text}")
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

        headers = session_data['headers']
        email = session_data['email']
        proxies = session_data.get('proxies')
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
    print("🤖 Bot started with proxy management and Indian names.")
    bot.infinity_polling()
