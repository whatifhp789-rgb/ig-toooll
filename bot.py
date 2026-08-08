import os
import random
import string
import time
import requests
from datetime import datetime

# ================== TELEGRAM CREDENTIALS ==================
TELEGRAM_TOKEN = "8914036332:AAHA4FB4jau6BahjOSDEQIYPmtkSwRqKluE"
CHAT_ID = "7431786238"

# ================== INDIAN NAMES ==================
INDIAN_NAMES = ['Amit', 'Raj', 'Vikram', 'Sanjay', 'Anil', 'Sunil', 'Pankaj', 'Manoj', 'Rakesh', 'Suresh']
INDIAN_LASTNAMES = ['Sharma', 'Verma', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Malhotra', 'Mehra', 'Khanna', 'Kapoor']

# ================== TELEGRAM BOT ==================
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

proxies = None
is_processing = False
user_data_store = {}

# ================== INSTAGRAM PRIVATE API ==================
class InstagramAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Instagram 276.0.0.18.96 Android',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        })
        self.csrf = None
        self.device_id = ''.join(random.choices(string.hexdigits.lower(), k=32))
        
    def get_csrf(self):
        """CSRF token fetch karo"""
        try:
            resp = self.session.get('https://www.instagram.com/')
            for cookie in self.session.cookies:
                if cookie.name == 'csrftoken':
                    self.csrf = cookie.value
                    return True
            return False
        except:
            return False
    
    def send_otp(self, email):
        """OTP send karo"""
        if not self.csrf:
            if not self.get_csrf():
                return False, "CSRF fetch failed"
        
        url = 'https://www.instagram.com/api/v1/accounts/send_verify_email/'
        data = {
            'email': email,
            'device_id': self.device_id,
            'flow': 'signup',
        }
        headers = {
            'x-csrftoken': self.csrf,
            'x-ig-app-id': '936619743392459',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        try:
            resp = self.session.post(url, headers=headers, data=data, timeout=30)
            result = resp.json()
            if result.get('email_sent'):
                return True, self.device_id
            else:
                return False, result.get('message', 'Unknown error')
        except Exception as e:
            return False, str(e)
    
    def verify_code(self, email, code, device_id):
        """OTP verify karo"""
        url = 'https://www.instagram.com/api/v1/accounts/check_confirmation_code/'
        data = {
            'code': code,
            'device_id': device_id,
            'email': email,
        }
        headers = {
            'x-csrftoken': self.csrf,
            'x-ig-app-id': '936619743392459',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        try:
            resp = self.session.post(url, headers=headers, data=data, timeout=30)
            result = resp.json()
            if result.get('status') == 'ok':
                return True, result.get('signup_code')
            else:
                return False, result.get('message', 'Invalid code')
        except Exception as e:
            return False, str(e)
    
    def create_account(self, email, signup_code, device_id):
        """Account create karo"""
        first_name = random.choice(INDIAN_NAMES)
        last_name = random.choice(INDIAN_LASTNAMES)
        username = first_name.lower() + str(random.randint(100, 999))
        password = first_name + '@' + ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        year = random.randint(1975, 1984)
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
        
        headers = {
            'x-csrftoken': self.csrf,
            'x-ig-app-id': '936619743392459',
            'x-requested-with': 'XMLHttpRequest',
            'content-type': 'application/x-www-form-urlencoded',
        }
        
        try:
            resp = self.session.post(url, headers=headers, data=data, timeout=30)
            result = resp.json()
            if result.get('account_created'):
                return {
                    'success': True,
                    'username': username,
                    'password': password,
                    'email': email,
                    'full_name': f"{first_name} {last_name}",
                    'age': 2026 - year,
                }
            else:
                return {'success': False, 'error': result.get('errors', {}).get('email', ['Unknown'])[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# ================== BOT HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ READY - Create Account", callback_data='start_creation')],
        [InlineKeyboardButton("📊 Status", callback_data='status')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🔥 <b>ZETA INSTA - PRIVATE API</b>\n\n"
        f"👑 Alpha, ready!\n"
        f"├ Processing: {'🟢' if is_processing else '🔴'}\n"
        f"├ Name: 🇮🇳 Indian 40+\n"
        f"└ Status: ✅ New API\n\n"
        f"<i>Click READY, send email, get OTP, send code!</i>",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    global is_processing
    
    if query.data == 'start_creation':
        if is_processing:
            await query.edit_message_text("⚠️ Already processing! Wait.")
            return
        
        sample_name = f"{random.choice(INDIAN_NAMES)} {random.choice(INDIAN_LASTNAMES)}"
        await query.edit_message_text(
            f"📧 <b>Start Creation</b>\n\n"
            f"🇮🇳 Sample: {sample_name}\n"
            f"🎂 Age: {random.randint(40, 49)}\n\n"
            f"Send email (with @):",
            parse_mode='HTML'
        )
        context.user_data['waiting_for_email'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_processing
    message = update.message.text
    
    # Email input
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
        is_processing = True
        
        # Create API instance
        api = InstagramAPI()
        context.user_data['api'] = api
        
        await update.message.reply_text(f"⏳ Sending OTP to {email}...")
        
        success, result = api.send_otp(email)
        if not success:
            await update.message.reply_text(f"❌ Failed: {result}\n\n💡 Try different email or proxy.")
            is_processing = False
            return
        
        context.user_data['device_id'] = result
        context.user_data['email'] = email
        context.user_data['waiting_for_code'] = True
        
        await update.message.reply_text(
            f"✅ <b>OTP SENT!</b> ✅\n\n"
            f"📧 Code sent to: <code>{email}</code>\n"
            f"📱 Send 6-digit code NOW:",
            parse_mode='HTML'
        )
        return
    
    # Code input
    if context.user_data.get('waiting_for_code'):
        code = message.strip()
        if len(code) != 6 or not code.isdigit():
            await update.message.reply_text("❌ 6 digits required! Try again.")
            return
        
        api = context.user_data.get('api')
        email = context.user_data.get('email')
        device_id = context.user_data.get('device_id')
        
        if not api or not email or not device_id:
            await update.message.reply_text("❌ Session expired! Click READY again.")
            is_processing = False
            return
        
        context.user_data['waiting_for_code'] = False
        
        await update.message.reply_text("⏳ Verifying code...")
        
        success, signup_code = api.verify_code(email, code, device_id)
        if not success:
            await update.message.reply_text(f"❌ Verification failed: {signup_code}")
            is_processing = False
            return
        
        await update.message.reply_text("⏳ Creating account...")
        
        result = api.create_account(email, signup_code, device_id)
        
        if result['success']:
            with open('accounts_insta.txt', 'a') as f:
                f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
                f.write(f"Name: {result['full_name']}\n")
                f.write(f"Username: {result['username']}\n")
                f.write(f"Password: {result['password']}\n")
                f.write(f"Email: {result['email']}\n")
                f.write(f"Age: {result['age']}\n")
                f.write("-"*40 + "\n")
            
            msg = (
                f"✅ <b>ACCOUNT CREATED!</b>\n\n"
                f"🇮🇳 {result['full_name']}\n"
                f"👤 <code>{result['username']}</code>\n"
                f"🔑 <code>{result['password']}</code>\n"
                f"📧 {result['email']}\n"
                f"🎂 {result['age']} years\n\n"
                f"✅ Saved!"
            )
            await update.message.reply_text(msg, parse_mode='HTML')
        else:
            await update.message.reply_text(f"❌ Failed: {result.get('error', 'Unknown')}")
        
        is_processing = False
        return
    
    await update.message.reply_text("❓ Unknown. /start")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waiting_for_email'] = False
    context.user_data['waiting_for_code'] = False
    global is_processing
    is_processing = False
    await update.message.reply_text("❌ Cancelled. /start")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 <b>STATUS</b>\n\n"
        f"├ Processing: {'🟢' if is_processing else '🔴'}\n"
        f"├ Email: {context.user_data.get('email', 'Not Set')}\n"
        f"└ Waiting: {'📨 Code' if context.user_data.get('waiting_for_code') else '❌'}",
        parse_mode='HTML'
    )

# ================== MAIN ==================
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                     data={'chat_id': CHAT_ID, 'text': "🔥 ZETA INSTA - PRIVATE API!\nAlpha, /start"})
    except:
        pass
    
    print(f"\n✅ Bot Started! (Private API)")
    print(f"Send /start in Telegram!")
    application.run_polling()

if __name__ == "__main__":
    main()
