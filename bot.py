import os
import random
import string
import time
import logging
from datetime import datetime

# ================== SELENIUM ==================
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# ================== TELEGRAM ==================
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ================== LOGGING ==================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== CONFIG ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN set nahi hai!")
    exit(1)

logger.info(f"✅ Token: {TELEGRAM_TOKEN[:10]}...")

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

# ================== GLOBALS ==================
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

# ================== CHROME DRIVER (DOCKER) ==================
def setup_driver():
    chrome_options = Options()
    
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    logger.info("✅ ChromeDriver started!")
    return driver

# ================== SELENIUM SIGNUP ==================
def create_account_selenium(email, update, context):
    global driver, is_processing
    
    try:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🌐 Opening Instagram signup page..."
        )
        
        driver = setup_driver()
        driver.get("https://www.instagram.com/accounts/emailsignup/")
        time.sleep(3)
        
        first_name, last_name, full_name = generate_indian_name()
        username = generate_username(first_name)
        password = generate_password(first_name)
        year = random.randint(1975, 1984)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📝 Filling form...\n🇮🇳 {full_name}"
        )
        
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "emailOrPhone"))
        )
        email_field.send_keys(email)
        time.sleep(1)
        
        driver.find_element(By.NAME, "fullName").send_keys(full_name)
        time.sleep(1)
        driver.find_element(By.NAME, "username").send_keys(username)
        time.sleep(1)
        driver.find_element(By.NAME, "password").send_keys(password)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]").click()
        time.sleep(3)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "month"))
        ).send_keys(str(month))
        time.sleep(1)
        driver.find_element(By.NAME, "day").send_keys(str(day))
        time.sleep(1)
        driver.find_element(By.NAME, "year").send_keys(str(year))
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]").click()
        time.sleep(3)
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ <b>OTP SENT!</b> ✅\n\n📧 Code sent to: <code>{email}</code>\n📱 Send 6-digit code NOW:",
            parse_mode='HTML'
        )
        
        context.user_data['driver'] = driver
        context.user_data['email'] = email
        context.user_data['password'] = password
        context.user_data['username'] = username
        context.user_data['full_name'] = full_name
        context.user_data['age'] = 2026 - year
        context.user_data['waiting_for_code'] = True
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Signup error: {e}")
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)[:200]}"
        )
        if driver:
            driver.quit()
        is_processing = False
        return False

# ================== VERIFY OTP ==================
def verify_and_finish(code, update, context):
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
        
        otp_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "verificationCode"))
        )
        otp_field.send_keys(code)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]").click()
        time.sleep(5)
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/accounts/edit/')]"))
        )
        
        with open('accounts_insta.txt', 'a') as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
            f.write(f"Name: {full_name}\nUsername: {username}\nPassword: {password}\nEmail: {email}\nAge: {age}\n")
            f.write("-"*40 + "\n")
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ <b>ACCOUNT CREATED!</b>\n\n🇮🇳 {full_name}\n👤 <code>{username}</code>\n🔑 <code>{password}</code>\n📧 {email}\n🎂 {age} years\n\n✅ Saved!",
            parse_mode='HTML'
        )
        
        driver.quit()
        is_processing = False
        return True
        
    except Exception as e:
        logger.error(f"❌ Verify error: {e}")
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
    logger.info(f"✅ /start from {update.effective_user.id}")
    keyboard = [[InlineKeyboardButton("✅ READY - Create Account", callback_data='start_creation')]]
    await update.message.reply_text(
        f"🔥 <b>ZETA INSTA - DOCKER</b>\n\nClick READY → Send email → Get OTP → Send code",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    global is_processing
    
    if query.data == 'start_creation':
        if is_processing:
            await query.edit_message_text("⚠️ Already processing!")
            return
        await query.edit_message_text("📧 Send email (with @):")
        context.user_data['waiting_for_email'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_processing
    msg = update.message.text
    
    if context.user_data.get('waiting_for_email'):
        if '@' not in msg:
            await update.message.reply_text("❌ Invalid email!")
            return
        context.user_data['waiting_for_email'] = False
        is_processing = True
        await update.message.reply_text("🌐 Starting browser...")
        create_account_selenium(msg, update, context)
        return
    
    if context.user_data.get('waiting_for_code'):
        if len(msg) != 6 or not msg.isdigit():
            await update.message.reply_text("❌ 6 digits required!")
            return
        context.user_data['waiting_for_code'] = False
        await update.message.reply_text("⏳ Verifying...")
        verify_and_finish(msg, update, context)
        return
    
    await update.message.reply_text("❓ /start")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    global is_processing, driver
    is_processing = False
    if driver:
        driver.quit()
        driver = None
    await update.message.reply_text("❌ Cancelled.")

# ================== MAIN ==================
def main():
    logger.info("🚀 Starting bot...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("✅ Bot started! Polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
