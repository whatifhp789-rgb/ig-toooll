import os
import random
import string
import time
import re
import requests
from datetime import datetime

# ================== SELENIUM WITH AUTO DRIVER ==================
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Auto download ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# ================== TELEGRAM CREDENTIALS ==================
TELEGRAM_TOKEN = "8914036332:AAHA4FB4jau6BahjOSDEQIYPmtkSwRqKluE"
CHAT_ID = "7431786238"

# ================== INDIAN NAMES ==================
INDIAN_FIRST = [
    'Amit', 'Raj', 'Vikram', 'Sanjay', 'Anil', 'Sunil', 'Pankaj', 'Manoj', 'Rakesh', 'Suresh',
    'Mahesh', 'Dinesh', 'Vijay', 'Ashok', 'Naresh', 'Rajesh', 'Vinod', 'Kishor', 'Prakash', 'Ram',
    'Shyam', 'Mohan', 'Sohan', 'Gopal', 'Narayan', 'Govind', 'Ravi', 'Subhash', 'Bhaskar', 'Chandra',
    'Devendra', 'Ganesh', 'Hari', 'Indra', 'Jagdish', 'Kamal', 'Lalit', 'Madhav', 'Narendra', 'Omkar',
    'Paras', 'Raghunath', 'Satish', 'Trilok', 'Umesh', 'Vishal', 'Yogesh', 'Anand', 'Bharat', 'Chetan',
    'Darshan', 'Girish', 'Hemant', 'Ishan', 'Jitendra', 'Kailash', 'Lokesh', 'Mukesh', 'Navin', 'Punit',
    'Ramesh', 'Sachin', 'Tarun', 'Ajay', 'Balram', 'Chaman', 'Deepak', 'Eknath', 'Gautam', 'Harish',
    'Jatin', 'Kartik', 'Lakshman', 'Murlidhar', 'Nikhil', 'Pradeep', 'Rahul', 'Siddharth', 'Tushar'
]

INDIAN_LAST = [
    'Sharma', 'Verma', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Malhotra', 'Mehra', 'Khanna', 'Kapoor',
    'Agarwal', 'Jain', 'Patel', 'Shah', 'Desai', 'Rao', 'Menon', 'Reddy', 'Nair', 'Pillai',
    'Chatterjee', 'Banerjee', 'Mukherjee', 'Bose', 'Ghosh', 'Das', 'Sen', 'Roy', 'Chowdhury',
    'Pandey', 'Mishra', 'Tiwari', 'Dubey', 'Saxena', 'Tripathi', 'Dwivedi', 'Sood', 'Gill',
    'Bajwa', 'Dhillon', 'Grewal', 'Sandhu', 'Ahuja', 'Bedi', 'Chadha', 'Mehta', 'Kohli'
]

# ================== TELEGRAM BOT SETUP ==================
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ================== GLOBALS ==================
proxies = None
is_processing = False
driver = None

# ================== NAME GENERATORS ==================
def generate_indian_name():
    first = random.choice(INDIAN_FIRST)
    last = random.choice(INDIAN_LAST)
    return first, last, f"{first} {last}"

def generate_username(first_name):
    clean = first_name.lower()
    nums = ''.join(random.choices(string.digits, k=4))
    suffixes = ['', '_', '.', 'official_', 'mr_']
    suffix = random.choice(suffixes)
    return f"{suffix}{clean}{nums}" if suffix else f"{clean}{nums}"

def generate_password(first_name):
    specials = ['@', '#', '$', '&']
    return first_name + random.choice(specials) + ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# ================== CHROME DRIVER SETUP (AUTO) ==================
def setup_driver():
    """Auto install ChromeDriver + Setup"""
    chrome_options = Options()
    
    # Headless mode off for debugging
    # chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Random user agent
    chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 120)}.0.0.0 Safari/537.36')
    
    # Proxy if set
    if proxies:
        chrome_options.add_argument(f'--proxy-server={proxies}')
    
    # 🔥 AUTO INSTALL + SERVICE
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

# ================== SELENIUM SIGNUP FLOW ==================
def create_account_selenium(email, update, context):
    """Full signup flow using Selenium"""
    global driver, is_processing
    
    try:
        # Setup driver with auto install
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🔄 Downloading/Setting up ChromeDriver... (first time takes 10-15 sec)"
        )
        
        driver = setup_driver()
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🌐 Opening Instagram signup page..."
        )
        
        # Go to signup page
        driver.get("https://www.instagram.com/accounts/emailsignup/")
        time.sleep(3)
        
        # Check if captcha appears
        try:
            captcha_element = driver.find_element(By.XPATH, "//div[contains(@class, 'captcha')]")
            if captcha_element:
                screenshot_path = f"captcha_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                
                with open(screenshot_path, 'rb') as f:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=f,
                        caption=f"🔐 <b>CAPTCHA DETECTED!</b>\n\nPlease solve manually in browser.\nClick READY after solving.",
                        parse_mode='HTML'
                    )
                os.remove(screenshot_path)
                context.user_data['waiting_for_captcha'] = True
                return False
        except:
            pass
        
        # Generate name
        first_name, last_name, full_name = generate_indian_name()
        username = generate_username(first_name)
        password = generate_password(first_name)
        
        # Age - 40+
        year = random.randint(1975, 1984)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        
        # Fill form
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📝 Filling signup form...\n🇮🇳 Name: {full_name}"
        )
        
        # Find and fill fields
        try:
            # Email
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "emailOrPhone"))
            )
            email_field.send_keys(email)
            time.sleep(1)
            
            # Full name
            name_field = driver.find_element(By.NAME, "fullName")
            name_field.send_keys(full_name)
            time.sleep(1)
            
            # Username
            username_field = driver.find_element(By.NAME, "username")
            username_field.send_keys(username)
            time.sleep(1)
            
            # Password
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            time.sleep(1)
            
            # Click next
            next_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
            next_button.click()
            time.sleep(3)
            
        except Exception as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Form fill error: {str(e)[:100]}"
            )
            driver.quit()
            is_processing = False
            return False
        
        # Check if captcha appeared after next
        try:
            captcha_element = driver.find_element(By.XPATH, "//div[contains(@class, 'captcha')]")
            if captcha_element:
                screenshot_path = f"captcha_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                with open(screenshot_path, 'rb') as f:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=f,
                        caption=f"🔐 <b>CAPTCHA DETECTED!</b>\n\nPlease solve manually.",
                        parse_mode='HTML'
                    )
                os.remove(screenshot_path)
                context.user_data['waiting_for_captcha'] = True
                return False
        except:
            pass
        
        # Wait for date of birth page
        try:
            # Month
            month_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "month"))
            )
            month_dropdown.send_keys(str(month))
            time.sleep(1)
            
            # Day
            day_field = driver.find_element(By.NAME, "day")
            day_field.send_keys(str(day))
            time.sleep(1)
            
            # Year
            year_field = driver.find_element(By.NAME, "year")
            year_field.send_keys(str(year))
            time.sleep(1)
            
            # Next
            next_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
            next_button.click()
            time.sleep(3)
            
        except Exception as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ DOB fill error: {str(e)[:100]}"
            )
            driver.quit()
            is_processing = False
            return False
        
        # Check for captcha again
        try:
            captcha_element = driver.find_element(By.XPATH, "//div[contains(@class, 'captcha')]")
            if captcha_element:
                screenshot_path = f"captcha_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                with open(screenshot_path, 'rb') as f:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=f,
                        caption=f"🔐 <b>CAPTCHA DETECTED!</b>\n\nPlease solve manually.",
                        parse_mode='HTML'
                    )
                os.remove(screenshot_path)
                context.user_data['waiting_for_captcha'] = True
                return False
        except:
            pass
        
        # Check if OTP was sent
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ <b>OTP SENT!</b> ✅\n\n"
                 f"📧 Verification code sent to:\n"
                 f"<code>{email}</code>\n\n"
                 f"📱 Please enter the 6-digit code NOW:",
            parse_mode='HTML'
        )
        
        # Save driver for later use
        context.user_data['driver'] = driver
        context.user_data['email'] = email
        context.user_data['password'] = password
        context.user_data['username'] = username
        context.user_data['full_name'] = full_name
        context.user_data['age'] = 2026 - year
        context.user_data['waiting_for_code'] = True
        
        return True
        
    except Exception as e:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)[:200]}"
        )
        if driver:
            driver.quit()
        is_processing = False
        return False

# ================== VERIFY CODE AND FINISH ==================
def verify_and_finish(code, update, context):
    """Verify OTP code and complete signup"""
    global driver, is_processing
    
    try:
        driver = context.user_data.get('driver')
        email = context.user_data.get('email')
        password = context.user_data.get('password')
        username = context.user_data.get('username')
        full_name = context.user_data.get('full_name')
        age = context.user_data.get('age')
        
        if not driver:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Session expired! Click READY again."
            )
            is_processing = False
            return False
        
        # Find OTP input field
        try:
            otp_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "verificationCode"))
            )
            otp_field.send_keys(code)
            time.sleep(1)
            
            # Submit
            submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
            submit_button.click()
            time.sleep(5)
            
        except Exception as e:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ OTP submit error: {str(e)[:100]}"
            )
            driver.quit()
            is_processing = False
            return False
        
        # Check if account created
        try:
            # Wait for success or profile page
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/accounts/edit/')]"))
            )
            
            # Account created!
            result = {
                'success': True,
                'username': username,
                'password': password,
                'email': email,
                'full_name': full_name,
                'age': age,
            }
            
            # Save account
            with open('accounts_insta.txt', 'a') as f:
                f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
                f.write(f"Name: {full_name}\n")
                f.write(f"Username: {username}\n")
                f.write(f"Password: {password}\n")
                f.write(f"Email: {email}\n")
                f.write(f"Age: {age}\n")
                f.write("-"*40 + "\n")
            
            msg = (
                f"✅ <b>ACCOUNT CREATED!</b>\n\n"
                f"🇮🇳 {full_name}\n"
                f"👤 <code>{username}</code>\n"
                f"🔑 <code>{password}</code>\n"
                f"📧 {email}\n"
                f"🎂 {age} years\n\n"
                f"✅ Saved in accounts_insta.txt"
            )
            
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=msg,
                parse_mode='HTML'
            )
            
            driver.quit()
            is_processing = False
            return True
            
        except TimeoutException:
            # Check if there's an error
            try:
                error_msg = driver.find_element(By.XPATH, "//div[contains(@class, 'error')]")
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Error: {error_msg.text}\n\n💡 Try different email or proxy."
                )
            except:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Unknown error. Try again with different email/proxy."
                )
            
            driver.quit()
            is_processing = False
            return False
            
    except Exception as e:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)[:200]}"
        )
        if driver:
            driver.quit()
        is_processing = False
        return False

# ================== TELEGRAM HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ READY - Create Account", callback_data='start_creation')],
        [InlineKeyboardButton("📊 Status", callback_data='status')],
        [InlineKeyboardButton("🔄 Reset", callback_data='reset')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔥 <b>ZETA INSTA - SELENIUM (AUTO DRIVER)</b>\n\n"
        f"👑 Alpha, ready!\n"
        f"├ Processing: {'🟢' if is_processing else '🔴'}\n"
        f"├ Name: 🇮🇳 Indian 40+\n"
        f"└ Driver: ✅ Auto Install\n\n"
        f"<i>Click READY → Send email → Get OTP → Send code</i>",
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
        
        first, last, full = generate_indian_name()
        age = random.randint(40, 49)
        
        await query.edit_message_text(
            f"📧 <b>Start Creation</b>\n\n"
            f"🇮🇳 Sample: {full}\n"
            f"🎂 Age: {age}\n\n"
            f"Send email (with @):",
            parse_mode='HTML'
        )
        context.user_data['waiting_for_email'] = True
        
    elif query.data == 'status':
        waiting_code = context.user_data.get('waiting_for_code', False)
        waiting_captcha = context.user_data.get('waiting_for_captcha', False)
        
        status_msg = (
            f"📊 <b>STATUS</b>\n\n"
            f"├ Processing: {'🟢' if is_processing else '🔴'}\n"
            f"├ Email: {context.user_data.get('email', 'Not Set')}\n"
            f"├ Waiting Code: {'✅' if waiting_code else '❌'}\n"
            f"└ Captcha: {'🔐' if waiting_captcha else '❌'}"
        )
        await query.edit_message_text(status_msg, parse_mode='HTML')
        
    elif query.data == 'reset':
        global driver
        if driver:
            driver.quit()
            driver = None
        context.user_data.clear()
        is_processing = False
        await query.edit_message_text("✅ Reset done! Click READY to start fresh.")

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
        
        await update.message.reply_text("🌐 Starting browser... This may take a few seconds.")
        
        success = create_account_selenium(email, update, context)
        if not success and not context.user_data.get('waiting_for_captcha'):
            is_processing = False
        return
    
    # Captcha solved
    if context.user_data.get('waiting_for_captcha'):
        context.user_data['waiting_for_captcha'] = False
        await update.message.reply_text(
            "✅ Captcha solved! Continuing...\n"
            "Check your email for OTP and send code here."
        )
        driver = context.user_data.get('driver')
        if driver:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "verificationCode"))
                )
                context.user_data['waiting_for_code'] = True
                await update.message.reply_text(
                    f"✅ <b>OTP SENT!</b> ✅\n\n"
                    f"📱 Send 6-digit code NOW:",
                    parse_mode='HTML'
                )
            except:
                await update.message.reply_text(
                    "❌ OTP not found. Click READY again."
                )
                is_processing = False
        return
    
    # Code input
    if context.user_data.get('waiting_for_code'):
        code = message.strip()
        if len(code) != 6 or not code.isdigit():
            await update.message.reply_text("❌ 6 digits required! Try again.")
            return
        
        context.user_data['waiting_for_code'] = False
        
        await update.message.reply_text("⏳ Verifying code & creating account...")
        
        verify_and_finish(code, update, context)
        return
    
    await update.message.reply_text("❓ Unknown. /start for menu.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waiting_for_email'] = False
    context.user_data['waiting_for_code'] = False
    context.user_data['waiting_for_captcha'] = False
    global is_processing, driver
    is_processing = False
    if driver:
        driver.quit()
        driver = None
    await update.message.reply_text("❌ Cancelled. /start")

# ================== MAIN ==================
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                     data={'chat_id': CHAT_ID, 'text': "🔥 ZETA INSTA - AUTO DRIVER!\nAlpha, /start"})
    except:
        pass
    
    print(f"\n✅ Bot Started! (Auto ChromeDriver)")
    print(f"📌 First time will download ChromeDriver (10-15 sec)")
    print(f"Send /start in Telegram!")
    
    application.run_polling()

if __name__ == "__main__":
    main()
