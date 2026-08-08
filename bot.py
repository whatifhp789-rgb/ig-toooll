import os
import random
import string
import time
import json
import re
import requests
from datetime import datetime

# ================== SOCKS PROXY SUPPORT ==================
try:
    import socks
    import socket
    SOCKS_AVAILABLE = True
except:
    SOCKS_AVAILABLE = False
    print("⚠️ SOCKS support nahi hai. Install: pip install PySocks")

# ================== ZETA COLORS ==================
rd, gn, lgn, yw, lrd, be, pe = '\033[00;31m', '\033[00;32m', '\033[01;32m', '\033[01;33m', '\033[01;31m', '\033[94m', '\033[01;35m'
cn, k, g = '\033[00;36m', '\033[90m', '\033[38;5;130m'
true = f'{rd}[{lgn}+{rd}]{gn} '
false = f'{rd}[{lrd}-{rd}] '
SUCCESS = true
ERROR = false

os.system('cls' if os.name == 'nt' else 'clear')

# ================== TELEGRAM CREDENTIALS ==================
TELEGRAM_TOKEN = "8914036332:AAHA4FB4jau6BahjOSDEQIYPmtkSwRqKluE"
CHAT_ID = "7431786238"

# ================== INDIAN NAMES ==================
INDIAN_NAMES = [
    'Amit', 'Raj', 'Vikram', 'Sanjay', 'Anil', 'Sunil', 'Pankaj', 'Manoj', 'Rakesh', 'Suresh',
    'Mahesh', 'Dinesh', 'Chandrakant', 'Vijay', 'Ashok', 'Naresh', 'Rajesh', 'Vinod', 'Kishor',
    'Prakash', 'Ram', 'Shyam', 'Mohan', 'Sohan', 'Gopal', 'Narayan', 'Govind', 'Ravi', 'Subhash',
    'Bhaskar', 'Chandra', 'Devendra', 'Ganesh', 'Hari', 'Indra', 'Jagdish', 'Kamal', 'Lalit',
    'Madhav', 'Narendra', 'Omkar', 'Paras', 'Raghunath', 'Satish', 'Trilok', 'Umesh', 'Vishal',
    'Yogesh', 'Anand', 'Bharat', 'Chetan', 'Darshan', 'Girish', 'Hemant', 'Ishan', 'Jitendra',
    'Kailash', 'Lokesh', 'Mukesh', 'Navin', 'Omprakash', 'Punit', 'Ramesh', 'Sachin', 'Tarun',
    'Ajay', 'Balram', 'Chaman', 'Deepak', 'Eknath', 'Gautam', 'Harish', 'Jatin', 'Kartik'
]

INDIAN_LASTNAMES = [
    'Sharma', 'Verma', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Malhotra', 'Mehra', 'Khanna', 'Kapoor',
    'Agarwal', 'Jain', 'Patel', 'Shah', 'Desai', 'Rao', 'Menon', 'Reddy', 'Nair', 'Pillai',
    'Chatterjee', 'Banerjee', 'Mukherjee', 'Bose', 'Ghosh', 'Das', 'Sen', 'Roy', 'Chowdhury',
    'Pandey', 'Mishra', 'Tiwari', 'Dubey', 'Saxena', 'Tripathi', 'Dwivedi', 'Sood', 'Gill',
    'Bajwa', 'Dhillon', 'Grewal', 'Sandhu', 'Ahuja', 'Bedi', 'Chadha'
]

# ================== GLOBAL VARIABLES ==================
proxies = None
proxy_type = None  # http, https, socks4, socks5
is_processing = False

# ================== UNIVERSAL PROXY PARSER ==================
def parse_proxy(proxy_string):
    """
    Har type ki proxy parse karega:
    - http://user:pass@ip:port
    - https://user:pass@ip:port
    - socks4://user:pass@ip:port
    - socks5://user:pass@ip:port
    - http://ip:port
    - ip:port (auto-detect)
    """
    proxy_string = proxy_string.strip()
    
    # Agar protocol nahi hai toh http assume karo
    if '://' not in proxy_string:
        proxy_string = 'http://' + proxy_string
    
    # Parse URL
    try:
        from urllib.parse import urlparse
        parsed = urlparse(proxy_string)
        
        protocol = parsed.scheme.lower()
        username = parsed.username
        password = parsed.password
        hostname = parsed.hostname
        port = parsed.port
        
        if not hostname or not port:
            return None, "❌ Invalid format! Need ip:port"
        
        # Proxy dict for requests
        proxy_dict = {}
        
        if protocol in ['http', 'https']:
            proxy_dict['http'] = proxy_string
            proxy_dict['https'] = proxy_string
            return proxy_dict, 'http', f"✅ HTTP Proxy: {hostname}:{port}"
            
        elif protocol in ['socks4', 'socks5']:
            if not SOCKS_AVAILABLE:
                return None, None, "❌ PySocks not installed! Run: pip install PySocks"
            
            # SOCKS proxy ke liye special handling
            proxy_dict['http'] = proxy_string
            proxy_dict['https'] = proxy_string
            return proxy_dict, protocol, f"✅ {protocol.upper()} Proxy: {hostname}:{port}"
            
        else:
            return None, None, f"❌ Unknown protocol: {protocol}. Use http, https, socks4, socks5"
            
    except Exception as e:
        return None, None, f"❌ Parse error: {str(e)[:50]}"

# ================== PROXY TESTER ==================
def test_proxy(proxy_dict, proxy_type_str):
    """Proxy ko test karo - Instagram se connect karke"""
    try:
        test_url = 'https://www.instagram.com/'
        test_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        if proxy_type_str and proxy_type_str.startswith('socks'):
            # SOCKS proxy ke liye requests nahi support karta directly
            # PySocks use karo
            if SOCKS_AVAILABLE:
                import socks
                import socket
                
                # Parse proxy
                from urllib.parse import urlparse
                parsed = urlparse(proxy_dict['http'])
                
                # Set SOCKS proxy
                sock_type = socks.SOCKS5 if 'socks5' in proxy_type_str else socks.SOCKS4
                socks.set_default_proxy(sock_type, parsed.hostname, parsed.port, 
                                       username=parsed.username, password=parsed.password)
                socket.socket = socks.socksocket
                
                # Test connection
                resp = requests.get(test_url, headers=test_headers, timeout=15)
                return resp.status_code == 200
        else:
            # HTTP/HTTPS proxy
            resp = requests.get(test_url, proxies=proxy_dict, headers=test_headers, timeout=15)
            return resp.status_code == 200
            
    except Exception as e:
        print(f"⚠️ Proxy test failed: {str(e)[:50]}")
        return False

# ================== LOAD PROXY ==================
def load_proxy(proxy_string):
    global proxies, proxy_type
    
    if not proxy_string or proxy_string.strip() == "":
        proxies = None
        proxy_type = None
        return True, "✅ Proxy removed! Using direct connection."
    
    # Parse proxy
    proxy_dict, ptype, msg = parse_proxy(proxy_string)
    
    if not proxy_dict:
        return False, msg
    
    # Test proxy
    print(f"🔍 Testing proxy...")
    if test_proxy(proxy_dict, ptype):
        proxies = proxy_dict
        proxy_type = ptype
        return True, f"{msg}\n✅ Proxy working!"
    else:
        return False, f"{msg}\n❌ Proxy test failed! Check credentials or connection."

# ================== TELEGRAM SETUP ==================
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ================== NAME GENERATORS ==================
def generate_indian_name():
    first = random.choice(INDIAN_NAMES)
    last = random.choice(INDIAN_LASTNAMES)
    return f"{first} {last}"

def generate_username(first_name):
    clean_name = first_name.split()[0].lower()
    num = ''.join(random.choices(string.digits, k=4))
    age_suffix = random.choice(['40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50'])
    
    usernames = [
        f"{clean_name}{num}",
        f"{clean_name}_{age_suffix}",
        f"{clean_name}{random.choice(['.','_'])}{num}",
        f"official_{clean_name}{random.randint(10,99)}",
        f"{clean_name}_{random.choice(['1960','1970','1980'])}",
        f"mr_{clean_name}{random.randint(1,9)}",
    ]
    return random.choice(usernames)

# ================== RANDOM UA ==================
def random_ua():
    android_versions = ['9', '10', '11', '12', '13', '14']
    devices = ['SM-G973F', 'SM-G960F', 'SM-N975F', 'Pixel 4', 'Pixel 5', 'OnePlus 8', 'OnePlus 9']
    return f'Mozilla/5.0 (Linux; Android {random.choice(android_versions)}; {random.choice(devices)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 120)}.0.0.0 Mobile Safari/537.36'

# ================== GET CSRF WITH RETRY ==================
def get_headers_and_csrf(retries=3):
    for attempt in range(retries):
        try:
            session = requests.Session()
            ua = random_ua()
            
            # SOCKS proxy support
            if proxy_type and proxy_type.startswith('socks') and SOCKS_AVAILABLE:
                import socks
                import socket
                from urllib.parse import urlparse
                parsed = urlparse(proxies['http'])
                sock_type = socks.SOCKS5 if 'socks5' in proxy_type else socks.SOCKS4
                socks.set_default_proxy(sock_type, parsed.hostname, parsed.port,
                                       username=parsed.username, password=parsed.password)
                socket.socket = socks.socksocket
                resp = session.get('https://www.instagram.com/', headers={'user-agent': ua}, timeout=30)
            else:
                resp = session.get('https://www.instagram.com/', headers={'user-agent': ua}, proxies=proxies, timeout=30)
            
            if resp.status_code != 200:
                print(f"⚠️ Attempt {attempt+1}: Status {resp.status_code}")
                time.sleep(2)
                continue
            
            csrf = None
            for cookie in session.cookies:
                if cookie.name == 'csrftoken':
                    csrf = cookie.value
                    break
            
            if not csrf:
                match = re.search(r'"csrf_token":"([^"]+)"', resp.text)
                if match:
                    csrf = match.group(1)
            
            if not csrf:
                print(f"⚠️ Attempt {attempt+1}: CSRF not found")
                time.sleep(2)
                continue
            
            app_id = '936619743392459'
            match = re.search(r'"APP_ID":"([^"]+)"', resp.text)
            if match:
                app_id = match.group(1)
            
            headers = {
                'user-agent': ua,
                'x-csrftoken': csrf,
                'x-ig-app-id': app_id,
                'x-requested-with': 'XMLHttpRequest',
                'content-type': 'application/x-www-form-urlencoded',
                'referer': 'https://www.instagram.com/accounts/emailsignup/',
                'origin': 'https://www.instagram.com',
                'accept-language': 'en-US,en;q=0.9',
            }
            
            return session, headers, csrf
            
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed: {str(e)[:50]}")
            time.sleep(2)
    
    raise Exception("❌ CSRF fetch failed after 3 attempts!")

# ================== SEND VERIFICATION EMAIL ==================
def send_verification_email(session, headers, email, retries=3):
    for attempt in range(retries):
        try:
            url = 'https://www.instagram.com/api/v1/accounts/send_verify_email/'
            device_id = ''.join(random.choices(string.hexdigits.lower(), k=32))
            
            data = {
                'email': email,
                'device_id': device_id,
                'flow': 'signup',
            }
            
            if proxy_type and proxy_type.startswith('socks') and SOCKS_AVAILABLE:
                resp = session.post(url, headers=headers, data=data, timeout=30)
            else:
                resp = session.post(url, headers=headers, data=data, proxies=proxies, timeout=30)
            
            try:
                result = resp.json()
            except:
                print(f"⚠️ Attempt {attempt+1}: Invalid JSON: {resp.text[:100]}")
                time.sleep(2)
                continue
            
            if result.get('email_sent'):
                return True, device_id
            else:
                error_msg = result.get('message', 'Unknown error')
                print(f"⚠️ Attempt {attempt+1}: {error_msg}")
                time.sleep(2)
                continue
                
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed: {str(e)[:50]}")
            time.sleep(2)
    
    return False, "Failed after 3 attempts"

# ================== VERIFY CODE ==================
def verify_code(session, headers, email, code, device_id, retries=3):
    for attempt in range(retries):
        try:
            url = 'https://www.instagram.com/api/v1/accounts/check_confirmation_code/'
            
            data = {
                'code': code,
                'device_id': device_id,
                'email': email,
            }
            
            if proxy_type and proxy_type.startswith('socks') and SOCKS_AVAILABLE:
                resp = session.post(url, headers=headers, data=data, timeout=30)
            else:
                resp = session.post(url, headers=headers, data=data, proxies=proxies, timeout=30)
            
            try:
                result = resp.json()
            except:
                print(f"⚠️ Attempt {attempt+1}: Invalid JSON: {resp.text[:100]}")
                time.sleep(2)
                continue
            
            if result.get('status') == 'ok':
                return True, result.get('signup_code')
            else:
                error_msg = result.get('message', 'Invalid code')
                print(f"⚠️ Attempt {attempt+1}: {error_msg}")
                time.sleep(2)
                continue
                
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1}: {str(e)[:50]}")
            time.sleep(2)
    
    return False, "Verification failed after 3 attempts"

# ================== CREATE ACCOUNT ==================
def create_account(session, headers, email, signup_code, device_id, retries=3):
    for attempt in range(retries):
        try:
            full_name = generate_indian_name()
            first_name = full_name.split()[0]
            username = generate_username(first_name)
            password = first_name + '@' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + str(random.randint(10,99))
            
            year = random.randint(1975, 1984)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            
            url = 'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/'
            
            data = {
                'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}',
                'email': email,
                'username': username,
                'first_name': first_name,
                'month': month,
                'day': day,
                'year': year,
                'device_id': device_id,
                'seamless_login_enabled': '1',
                'tos_version': 'row',
                'force_sign_up_code': signup_code,
            }
            
            create_headers = headers.copy()
            create_headers['content-type'] = 'application/x-www-form-urlencoded'
            create_headers['x-ig-www-claim'] = '0'
            
            if proxy_type and proxy_type.startswith('socks') and SOCKS_AVAILABLE:
                resp = session.post(url, headers=create_headers, data=data, timeout=30)
            else:
                resp = session.post(url, headers=create_headers, data=data, proxies=proxies, timeout=30)
            
            try:
                result = resp.json()
            except:
                print(f"⚠️ Attempt {attempt+1}: Invalid JSON: {resp.text[:100]}")
                time.sleep(3)
                continue
            
            if result.get('account_created'):
                sessionid = None
                for cookie in session.cookies:
                    if cookie.name == 'sessionid':
                        sessionid = cookie.value
                        break
                
                return {
                    'success': True,
                    'username': username,
                    'password': password,
                    'email': email,
                    'full_name': full_name,
                    'age': 2026 - year,
                    'birth_year': year,
                    'sessionid': sessionid,
                }
            else:
                error = result.get('errors', {}).get('email', ['Unknown error'])[0]
                print(f"⚠️ Attempt {attempt+1}: {error}")
                
                if 'challenge' in str(result).lower():
                    print("🔐 Challenge required! Try different proxy")
                    time.sleep(5)
                    continue
                    
                time.sleep(3)
                continue
                
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1}: {str(e)[:50]}")
            time.sleep(3)
    
    return {'success': False, 'error': 'Failed after 3 attempts'}

# ================== ACCOUNT CREATION FLOW ==================
def create_account_flow(email, update, context):
    global is_processing
    
    try:
        is_processing = True
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⏳ Starting for: {email}\n🔄 Getting session (3 retries)..."
        )
        
        session, headers, csrf = get_headers_and_csrf()
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📨 Sending verification code (3 retries)..."
        )
        
        sent, device_id = send_verification_email(session, headers, email)
        if not sent:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Failed to send code!\nError: {device_id}\n\n💡 Try:\n- Different email\n- Different proxy\n- Wait 5 mins"
            )
            is_processing = False
            return False
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Code sent to {email}\n📱 Send 6-digit code here:"
        )
        
        context.user_data['session'] = session
        context.user_data['headers'] = headers
        context.user_data['device_id'] = device_id
        context.user_data['email'] = email
        context.user_data['waiting_for_code'] = True
        
        return True
        
    except Exception as e:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)[:100]}\n\n💡 Try using a different proxy."
        )
        is_processing = False
        return False

# ================== TELEGRAM HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 Load Proxy", callback_data='load_proxy')],
        [InlineKeyboardButton("✅ READY - Start Creating", callback_data='start_creation')],
        [InlineKeyboardButton("📊 Status", callback_data='status')],
        [InlineKeyboardButton("🔄 Reset Proxy", callback_data='reset_proxy')],
        [InlineKeyboardButton("🇮🇳 Sample Name", callback_data='sample_name')],
        [InlineKeyboardButton("📖 Proxy Help", callback_data='proxy_help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    proxy_status = f"{proxy_type.upper()}" if proxy_type else "❌ Not Set"
    
    await update.message.reply_text(
        f"🔥 <b>ZETA INSTA - UNIVERSAL PROXY</b>\n\n"
        f"👑 Alpha, ready!\n"
        f"├ Proxy: {proxy_status}\n"
        f"├ Processing: {'🟢' if is_processing else '🔴'}\n"
        f"├ Name: 🇮🇳 Indian 40+\n"
        f"└ Retry: 🔄 3 attempts\n\n"
        f"<i>Supports: HTTP, HTTPS, SOCKS4, SOCKS5</i>",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    global is_processing, proxies, proxy_type
    
    if query.data == 'load_proxy':
        await query.edit_message_text(
            "🌐 <b>Load Proxy</b>\n\n"
            "Send proxy in ANY format:\n\n"
            "<code>http://user:pass@1.2.3.4:8080</code>\n"
            "<code>https://1.2.3.4:3128</code>\n"
            "<code>socks5://user:pass@1.2.3.4:1080</code>\n"
            "<code>socks4://1.2.3.4:1080</code>\n"
            "<code>1.2.3.4:8080</code> (auto http)\n\n"
            "Type /cancel to cancel.",
            parse_mode='HTML'
        )
        context.user_data['waiting_for_proxy'] = True
        
    elif query.data == 'proxy_help':
        await query.edit_message_text(
            "📖 <b>PROXY FORMATS</b>\n\n"
            "<b>HTTP:</b>\n"
            "<code>http://user:pass@ip:port</code>\n"
            "<code>http://ip:port</code>\n"
            "<code>ip:port</code>\n\n"
            "<b>HTTPS:</b>\n"
            "<code>https://user:pass@ip:port</code>\n\n"
            "<b>SOCKS4:</b>\n"
            "<code>socks4://user:pass@ip:port</code>\n\n"
            "<b>SOCKS5:</b>\n"
            "<code>socks5://user:pass@ip:port</code>\n\n"
            "💡 <i>Free proxies: https://free-proxy-list.net/</i>",
            parse_mode='HTML'
        )
        
    elif query.data == 'start_creation':
        if is_processing:
            await query.edit_message_text("⚠️ Already processing! Wait.")
            return
        
        sample_name = generate_indian_name()
        sample_username = generate_username(sample_name.split()[0])
        sample_age = random.randint(40, 49)
        
        await query.edit_message_text(
            f"📧 <b>Start Creation</b>\n\n"
            f"🇮🇳 Sample: {sample_name}\n"
            f"👤 Username: {sample_username}\n"
            f"🎂 Age: {sample_age}\n"
            f"🌐 Proxy: {proxy_type.upper() if proxy_type else 'Direct'}\n\n"
            f"Send email (with @):",
            parse_mode='HTML'
        )
        context.user_data['waiting_for_email'] = True
        
    elif query.data == 'status':
        status_msg = (
            f"📊 <b>STATUS</b>\n\n"
            f"├ Proxy: {proxy_type.upper() if proxy_type else '❌ Direct'}\n"
            f"├ Processing: {'🟢' if is_processing else '🔴'}\n"
            f"├ Email: {context.user_data.get('email', 'Not Set')}\n"
            f"├ Retry: 3 attempts\n"
            f"└ Waiting: {'📨 Code' if context.user_data.get('waiting_for_code') else '❌'}"
        )
        await query.edit_message_text(status_msg, parse_mode='HTML')
        
    elif query.data == 'reset_proxy':
        proxies = None
        proxy_type = None
        await query.edit_message_text("✅ Proxy reset! Using direct connection.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global proxies, is_processing, proxy_type
    
    message = update.message.text
    
    if context.user_data.get('waiting_for_proxy'):
        if message.lower() == '/cancel':
            context.user_data['waiting_for_proxy'] = False
            await update.message.reply_text("❌ Cancelled.")
            return
        
        success, msg = load_proxy(message)
        context.user_data['waiting_for_proxy'] = False
        
        if success:
            proxy_type = "socks5" if "socks5" in message.lower() else "socks4" if "socks4" in message.lower() else "http"
        
        await update.message.reply_text(f"{msg}\n\n/start for menu")
        return
    
    if context.user_data.get('waiting_for_email'):
        if message.lower() == '/cancel':
            context.user_data['waiting_for_email'] = False
            await update.message.reply_text("❌ Cancelled.")
            return
        
        email = message.strip()
        if '@' not in email:
            await update.message.reply_text("❌ Invalid email! Try again.")
            return
        
        context.user_data['waiting_for_email'] = False
        context.user_data['email'] = email
        
        success = create_account_flow(email, update, context)
        if success:
            await update.message.reply_text("✅ Code sent! Send 6-digit code:")
        return
    
    if context.user_data.get('waiting_for_code'):
        code = message.strip()
        if len(code) != 6 or not code.isdigit():
            await update.message.reply_text("❌ 6 digits required! Try again.")
            return
        
        context.user_data['waiting_for_code'] = False
        
        session = context.user_data.get('session')
        headers = context.user_data.get('headers')
        email = context.user_data.get('email')
        device_id = context.user_data.get('device_id')
        
        if not all([session, headers, email, device_id]):
            await update.message.reply_text("❌ Session expired! Click READY again.")
            return
        
        await update.message.reply_text("⏳ Verifying & creating... (3 retries)")
        
        verified, signup_code = verify_code(session, headers, email, code, device_id)
        if not verified:
            await update.message.reply_text(f"❌ Verification failed: {signup_code}\n💡 Try with different proxy or email.")
            is_processing = False
            return
        
        result = create_account(session, headers, email, signup_code, device_id)
        
        if result['success']:
            with open('accounts_insta.txt', 'a') as f:
                f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
                f.write(f"Name: {result['full_name']}\n")
                f.write(f"Username: {result['username']}\n")
                f.write(f"Password: {result['password']}\n")
                f.write(f"Email: {result['email']}\n")
                f.write(f"Age: {result['age']}\n")
                f.write(f"Proxy: {proxy_type}\n")
                f.write("-"*40 + "\n")
            
            msg = (
                f"✅ <b>ACCOUNT CREATED!</b>\n\n"
                f"🇮🇳 {result['full_name']}\n"
                f"👤 <code>{result['username']}</code>\n"
                f"🔑 <code>{result['password']}</code>\n"
                f"📧 {result['email']}\n"
                f"🎂 {result['age']} years\n"
                f"🌐 Proxy: {proxy_type.upper() if proxy_type else 'Direct'}\n\n"
                f"✅ Saved!"
            )
            
            await update.message.reply_text(msg, parse_mode='HTML')
            
        else:
            await update.message.reply_text(
                f"❌ Failed: {result.get('error', 'Unknown')}\n\n"
                f"💡 Fixes:\n"
                f"• Load different proxy\n"
                f"• Different email\n"
                f"• Wait 5 minutes\n"
                f"• Try SOCKS5 proxy"
            )
        
        is_processing = False
        return
    
    await update.message.reply_text("❓ Unknown. /start for menu.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waiting_for_proxy'] = False
    context.user_data['waiting_for_email'] = False
    context.user_data['waiting_for_code'] = False
    global is_processing
    is_processing = False
    await update.message.reply_text("❌ Cancelled. /start")

# ================== MAIN ==================
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            'chat_id': CHAT_ID,
            'text': "🔥 ZETA INSTA - UNIVERSAL PROXY SUPPORT!\nHTTP, HTTPS, SOCKS4, SOCKS5 - Sab chalega!\nAlpha, /start",
        }
        requests.post(url, data=data)
    except:
        pass
    
    print(f"\n{SUCCESS}✅ Bot Started! (Universal Proxy Support)")
    print(f"{true}🌐 HTTP | HTTPS | SOCKS4 | SOCKS5")
    print(f"{true}🇮🇳 Indian names | 40+ age | 3 retries")
    print(f"{true}Send /start in Telegram!")
    
    application.run_polling()

if __name__ == "__main__":
    main()
