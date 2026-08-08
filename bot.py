import os
import random
import string
import time
import json
import re
import requests
from datetime import datetime
from threading import Thread

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

# ================== INDIAN NAMES DATABASE (40+ AGE) ==================
INDIAN_NAMES = [
    'Amit', 'Raj', 'Vikram', 'Sanjay', 'Anil', 'Sunil', 'Pankaj', 'Manoj', 'Rakesh', 'Suresh',
    'Mahesh', 'Dinesh', 'Chandrakant', 'Vijay', 'Ashok', 'Naresh', 'Rajesh', 'Vinod', 'Kishor',
    'Prakash', 'Ram', 'Shyam', 'Mohan', 'Sohan', 'Gopal', 'Narayan', 'Govind', 'Ravi', 'Subhash',
    'Bhaskar', 'Chandra', 'Devendra', 'Ganesh', 'Hari', 'Indra', 'Jagdish', 'Kamal', 'Lalit',
    'Madhav', 'Narendra', 'Omkar', 'Paras', 'Raghunath', 'Satish', 'Trilok', 'Umesh', 'Vishal',
    'Yogesh', 'Zaveri', 'Anand', 'Bharat', 'Chetan', 'Darshan', 'Eshwar', 'Falgun', 'Girish',
    'Hemant', 'Ishan', 'Jitendra', 'Kailash', 'Lokesh', 'Mukesh', 'Navin', 'Omprakash', 'Punit',
    'Ramesh', 'Sachin', 'Tarun', 'Uma', 'Vasant', 'Wasim', 'Yashwant', 'Ajay', 'Balram',
    'Chaman', 'Deepak', 'Eknath', 'Gautam', 'Harish', 'Iqbal', 'Jatin', 'Kartik'
]

INDIAN_LASTNAMES = [
    'Sharma', 'Verma', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Malhotra', 'Mehra', 'Khanna', 'Kapoor',
    'Agarwal', 'Jain', 'Patel', 'Shah', 'Desai', 'Rao', 'Menon', 'Reddy', 'Nair', 'Pillai',
    'Chatterjee', 'Banerjee', 'Mukherjee', 'Bose', 'Ghosh', 'Das', 'Sen', 'Roy', 'Chowdhury',
    'Pandey', 'Mishra', 'Tiwari', 'Dubey', 'Saxena', 'Tripathi', 'Dwivedi', 'Chand', 'Sood',
    'Gill', 'Bajwa', 'Dhillon', 'Grewal', 'Kaur', 'Sandhu', 'Ahuja', 'Bedi', 'Chadha'
]

# ================== RANDOM INDIAN NAME GENERATOR ==================
def generate_indian_name():
    """40+ year old Indian name with lastname"""
    first = random.choice(INDIAN_NAMES)
    last = random.choice(INDIAN_LASTNAMES)
    return f"{first} {last}"

def generate_username(first_name):
    """Username generate karo - random + age hint"""
    # Clean first name
    clean_name = first_name.split()[0].lower()
    
    # Random 4 digit number
    num = ''.join(random.choices(string.digits, k=4))
    
    # Add age indicator (40+)
    age_suffix = random.choice(['40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50'])
    
    usernames = [
        f"{clean_name}{num}",
        f"{clean_name}_{age_suffix}",
        f"{clean_name}{random.choice(['.','_'])}{num}",
        f"official_{clean_name}{random.randint(10,99)}",
        f"{clean_name}_{random.choice(['1960','1970','1980','1990'])}",
        f"mr_{clean_name}{random.randint(1,9)}",
        f"{clean_name}{random.choice(['ji','bhai'])}{random.randint(10,99)}"
    ]
    
    return random.choice(usernames)

# ================== TELEGRAM BOT SETUP ==================
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ================== GLOBAL VARIABLES ==================
proxies = None
is_processing = False

# ================== PROXY FUNCTIONS ==================
def load_proxy(proxy_string):
    global proxies
    if not proxy_string or proxy_string.strip() == "":
        proxies = None
        return True, "Proxy removed! Using direct connection."
    
    proxy_string = proxy_string.strip()
    
    try:
        proxy_dict = {
            'http': proxy_string,
            'https': proxy_string
        }
        test_resp = requests.get('https://api.telegram.org', proxies=proxy_dict, timeout=10)
        if test_resp.status_code == 200:
            proxies = proxy_dict
            return True, f"✅ Proxy loaded: {proxy_string[:30]}..."
        else:
            return False, "❌ Proxy test failed!"
    except Exception as e:
        return False, f"❌ Proxy error: {str(e)[:50]}"

# ================== INSTAGRAM FUNCTIONS ==================
def random_ua():
    android_versions = ['9', '10', '11', '12', '13', '14']
    devices = ['SM-G973F', 'SM-G960F', 'SM-N975F', 'Pixel 4', 'Pixel 5', 'OnePlus 8', 'OnePlus 9']
    return f'Mozilla/5.0 (Linux; Android {random.choice(android_versions)}; {random.choice(devices)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 120)}.0.0.0 Mobile Safari/537.36'

def get_headers_and_csrf():
    session = requests.Session()
    ua = random_ua()
    resp = session.get('https://www.instagram.com/', headers={'user-agent': ua}, proxies=proxies)
    
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
        raise Exception("❌ CSRF token nahi mila!")
    
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

def send_verification_email(session, headers, email):
    url = 'https://www.instagram.com/api/v1/accounts/send_verify_email/'
    device_id = ''.join(random.choices(string.hexdigits.lower(), k=32))
    
    data = {
        'email': email,
        'device_id': device_id,
        'flow': 'signup',
    }
    
    resp = session.post(url, headers=headers, data=data, proxies=proxies)
    
    try:
        result = resp.json()
        if result.get('email_sent'):
            return True, device_id
        else:
            return False, result.get('message', 'Unknown error')
    except:
        return False, 'Failed to parse response'

def verify_code(session, headers, email, code, device_id):
    url = 'https://www.instagram.com/api/v1/accounts/check_confirmation_code/'
    
    data = {
        'code': code,
        'device_id': device_id,
        'email': email,
    }
    
    resp = session.post(url, headers=headers, data=data, proxies=proxies)
    
    try:
        result = resp.json()
        if result.get('status') == 'ok':
            return True, result.get('signup_code')
        else:
            return False, result.get('message', 'Invalid code')
    except:
        return False, 'Failed to verify'

def create_account(session, headers, email, signup_code, device_id):
    """Account create karo - INDIAN NAME + 40+ AGE"""
    
    # INDIAN NAME GENERATE
    full_name = generate_indian_name()
    first_name = full_name.split()[0]
    last_name = full_name.split()[1] if len(full_name.split()) > 1 else random.choice(INDIAN_LASTNAMES)
    
    # Username generate - Indian style
    username = generate_username(first_name)
    
    # Password - strong with Indian touch
    password = first_name + '@' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + str(random.randint(10,99))
    
    # AGE: ALWAYS 40+
    year = random.randint(1975, 1984)  # 40-49 years
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    
    url = 'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/'
    
    data = {
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}',
        'email': email,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
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
    
    resp = session.post(url, headers=create_headers, data=data, proxies=proxies)
    
    try:
        result = resp.json()
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
                'first_name': first_name,
                'last_name': last_name,
                'age': 2026 - year,
                'birth_year': year,
                'sessionid': sessionid,
            }
        else:
            error = result.get('errors', {}).get('email', ['Unknown error'])[0]
            return {'success': False, 'error': error}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ================== ACCOUNT CREATION FLOW ==================
def create_account_flow(email, update, context):
    global is_processing
    
    try:
        is_processing = True
        
        # Send status
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⏳ Starting account creation for:\n📧 {email}\n\n🔄 Getting CSRF token..."
        )
        
        session, headers, csrf = get_headers_and_csrf()
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📨 Sending verification code to your email..."
        )
        
        sent, device_id = send_verification_email(session, headers, email)
        if not sent:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Failed to send code!\nError: {device_id}"
            )
            is_processing = False
            return False
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Code sent to {email}\n\n📱 Please check your email and send the 6-digit code here."
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
            text=f"❌ Error: {str(e)}"
        )
        is_processing = False
        return False

# ================== TELEGRAM BOT HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - shows main menu"""
    keyboard = [
        [InlineKeyboardButton("🌐 Load Proxy", callback_data='load_proxy')],
        [InlineKeyboardButton("✅ READY - Start Creating", callback_data='start_creation')],
        [InlineKeyboardButton("📊 Current Status", callback_data='status')],
        [InlineKeyboardButton("🔄 Reset Proxy", callback_data='reset_proxy')],
        [InlineKeyboardButton("🇮🇳 Show Sample Name", callback_data='sample_name')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔥 <b>ZETA INSTA CREATOR - INDIAN EDITION</b>\n\n"
        f"👑 Alpha, welcome to your tool!\n\n"
        f"<b>Current Status:</b>\n"
        f"├ Proxy: {'✅ Loaded' if proxies else '❌ Not Set'}\n"
        f"├ Processing: {'🟢 Active' if is_processing else '🔴 Idle'}\n"
        f"├ Name Style: 🇮🇳 Indian (40+ age)\n"
        f"└ Bot: 🟢 Online\n\n"
        f"<i>Click a button below to start:</i>",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    global is_processing, proxies
    
    if query.data == 'load_proxy':
        await query.edit_message_text(
            "🌐 <b>Load Proxy</b>\n\n"
            "Send me your proxy in this format:\n"
            "<code>http://user:pass@ip:port</code>\n"
            "or\n"
            "<code>http://ip:port</code>\n\n"
            "Type <b>/cancel</b> to cancel.",
            parse_mode='HTML'
        )
        context.user_data['waiting_for_proxy'] = True
        
    elif query.data == 'start_creation':
        if is_processing:
            await query.edit_message_text(
                "⚠️ Already processing! Wait for current operation to complete."
            )
            return
        
        # Show sample name that will be used
        sample_name = generate_indian_name()
        sample_username = generate_username(sample_name.split()[0])
        sample_age = random.randint(40, 49)
        
        await query.edit_message_text(
            f"📧 <b>Start Account Creation</b>\n\n"
            f"🇮🇳 <b>Sample Name:</b> {sample_name}\n"
            f"👤 <b>Sample Username:</b> {sample_username}\n"
            f"🎂 <b>Age:</b> {sample_age} years\n"
            f"📅 <b>Birth Year:</b> {2026 - sample_age}\n\n"
            f"Please send me your email address.\n"
            f"Example: <code>your@email.com</code>\n\n"
            f"Type <b>/cancel</b> to cancel.",
            parse_mode='HTML'
        )
        context.user_data['waiting_for_email'] = True
        
    elif query.data == 'status':
        status_msg = (
            f"📊 <b>CURRENT STATUS</b>\n\n"
            f"├ Proxy: {'✅ Loaded' if proxies else '❌ Not Set'}\n"
            f"├ Processing: {'🟢 Active' if is_processing else '🔴 Idle'}\n"
            f"├ Email: {context.user_data.get('email', 'Not Set')}\n"
            f"├ Name Style: 🇮🇳 Indian (40+)\n"
            f"└ Waiting: {'📨 Code' if context.user_data.get('waiting_for_code') else '❌ None'}\n\n"
            f"<i>Click /start for main menu</i>"
        )
        await query.edit_message_text(status_msg, parse_mode='HTML')
        
    elif query.data == 'reset_proxy':
        proxies = None
        await query.edit_message_text(
            "✅ Proxy reset successfully!\n"
            "Now using direct connection."
        )
        
    elif query.data == 'sample_name':
        name = generate_indian_name()
        username = generate_username(name.split()[0])
        age = random.randint(40, 49)
        
        await query.edit_message_text(
            f"🇮🇳 <b>INDIAN SAMPLE ACCOUNT</b>\n\n"
            f"👤 <b>Name:</b> {name}\n"
            f"🔑 <b>Username:</b> {username}\n"
            f"🎂 <b>Age:</b> {age} years\n"
            f"📅 <b>Birth Year:</b> {2026 - age}\n"
            f"📧 <b>Email:</b> your@email.com\n\n"
            f"<i>This is how your account will look!</i>\n"
            f"Click READY to create one!",
            parse_mode='HTML'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    global proxies, is_processing
    
    message = update.message.text
    user_id = update.effective_chat.id
    
    # Handle proxy input
    if context.user_data.get('waiting_for_proxy'):
        if message.lower() == '/cancel':
            context.user_data['waiting_for_proxy'] = False
            await update.message.reply_text("❌ Cancelled proxy setup.")
            return
        
        success, msg = load_proxy(message)
        context.user_data['waiting_for_proxy'] = False
        
        await update.message.reply_text(f"{msg}\n\nClick /start to continue.")
        return
    
    # Handle email input
    if context.user_data.get('waiting_for_email'):
        if message.lower() == '/cancel':
            context.user_data['waiting_for_email'] = False
            await update.message.reply_text("❌ Cancelled account creation.")
            return
        
        email = message.strip()
        if '@' not in email:
            await update.message.reply_text("❌ Invalid email! Please send a valid email address.")
            return
        
        context.user_data['waiting_for_email'] = False
        context.user_data['email'] = email
        
        # Start creation flow
        success = create_account_flow(email, update, context)
        if success:
            await update.message.reply_text(
                "✅ Check your email for the verification code.\n"
                "Send the 6-digit code here when you receive it."
            )
        return
    
    # Handle code input
    if context.user_data.get('waiting_for_code'):
        code = message.strip()
        if len(code) != 6 or not code.isdigit():
            await update.message.reply_text("❌ Invalid code! Should be 6 digits. Try again.")
            return
        
        context.user_data['waiting_for_code'] = False
        
        # Verify and create account
        session = context.user_data.get('session')
        headers = context.user_data.get('headers')
        email = context.user_data.get('email')
        device_id = context.user_data.get('device_id')
        
        if not all([session, headers, email, device_id]):
            await update.message.reply_text("❌ Session expired! Please click READY again.")
            return
        
        await update.message.reply_text("⏳ Verifying code and creating account...\n🇮🇳 Using Indian name (40+ age)...")
        
        verified, signup_code = verify_code(session, headers, email, code, device_id)
        if not verified:
            await update.message.reply_text(f"❌ Verification failed: {signup_code}")
            is_processing = False
            return
        
        result = create_account(session, headers, email, signup_code, device_id)
        
        if result['success']:
            # Save account
            with open('accounts_insta.txt', 'a') as f:
                f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
                f.write(f"Full Name: {result['full_name']}\n")
                f.write(f"Username: {result['username']}\n")
                f.write(f"Password: {result['password']}\n")
                f.write(f"Email: {result['email']}\n")
                f.write(f"Age: {result['age']}\n")
                f.write(f"Birth Year: {result['birth_year']}\n")
                if result.get('sessionid'):
                    f.write(f"SessionID: {result['sessionid']}\n")
                f.write("-"*50 + "\n")
            
            # Success message
            msg = (
                f"✅ <b>ACCOUNT CREATED SUCCESSFULLY!</b>\n\n"
                f"🇮🇳 <b>Full Name:</b> {result['full_name']}\n"
                f"👤 <b>Username:</b> <code>{result['username']}</code>\n"
                f"🔑 <b>Password:</b> <code>{result['password']}</code>\n"
                f"📧 <b>Email:</b> <code>{result['email']}</code>\n"
                f"🎂 <b>Age:</b> {result['age']} years\n"
                f"📅 <b>Birth Year:</b> {result['birth_year']}\n"
                f"🕐 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
                f"📁 Saved in accounts_insta.txt\n\n"
                f"<i>🇮🇳 Pure Indian account created!</i>"
            )
            
            await update.message.reply_text(msg, parse_mode='HTML')
            
            # Send to Telegram backup
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                data = {
                    'chat_id': CHAT_ID,
                    'text': f"🔥 NEW INDIAN ACCOUNT!\n{result['full_name']}\n@{result['username']}\n{result['password']}\nAge: {result['age']}",
                }
                requests.post(url, data=data)
            except:
                pass
            
        else:
            await update.message.reply_text(f"❌ Account creation failed: {result.get('error', 'Unknown error')}")
        
        is_processing = False
        return
    
    # Default response
    await update.message.reply_text(
        "❓ Unknown command. Click /start to see the menu."
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    context.user_data['waiting_for_proxy'] = False
    context.user_data['waiting_for_email'] = False
    context.user_data['waiting_for_code'] = False
    global is_processing
    is_processing = False
    
    await update.message.reply_text(
        "❌ Cancelled all operations.\nClick /start for menu."
    )

# ================== MAIN ==================
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Send startup
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            'chat_id': CHAT_ID,
            'text': "🔥 ZETA INSTA CREATOR - INDIAN EDITION STARTED!\n🇮🇳 Using Indian names with 40+ age.\nAlpha, /start to begin!",
        }
        requests.post(url, data=data)
    except:
        pass
    
    print(f"\n{SUCCESS}{gn}✅ Bot Started Successfully!")
    print(f"{true}{pe}Bot Token: {TELEGRAM_TOKEN[:15]}...{TELEGRAM_TOKEN[-5:]}")
    print(f"{true}{pe}Chat ID: {CHAT_ID}")
    print(f"{true}{cn}🇮🇳 Using INDIAN Names (40+ Age)")
    print(f"{true}{yw}Send /start in Telegram to begin!")
    
    application.run_polling()

if __name__ == "__main__":
    main()
