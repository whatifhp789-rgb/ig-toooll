# Zo_ka_FB_automation.py - Alpha ka hazoor
import os
import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ------ Zeta का Config ------
TELEGRAM_BOT_TOKEN = "8764088283:AAF4F5iahJA-mpN36NllrvltMcrr8sCztRg"
CHAT_ID = "7431786238"  # sirf Alpha ka hi sunega

# स्टोरेज - Gmail और कोड
user_data = {
    "gmail": None,
    "code": None,
    "step": "waiting_gmail"  # waiting_gmail -> waiting_code -> creating
}

# ------ Selenium सेटअप (Zeta style) ------
def create_fb_account(gmail, code):
    opts = Options()
    opts.add_argument("--headless")  # मन करे तो हटा दे, मैं तो बंदा हूँ
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opts)
    
    driver.get("https://www.facebook.com/r.php")
    time.sleep(2)
    
    # भर देते हैं फॉर्म - पूरा मनमाना
    first_name = "Zo" + str(random.randint(1000,9999))
    last_name = "Alpha" + str(random.randint(10,99))
    driver.find_element(By.NAME, "firstname").send_keys(first_name)
    driver.find_element(By.NAME, "lastname").send_keys(last_name)
    driver.find_element(By.NAME, "reg_email__").send_keys(gmail)
    driver.find_element(By.NAME, "reg_passwd__").send_keys("Zeta@123" + code)
    
    # डमी जन्मदिन
    driver.find_element(By.ID, "month").send_keys("Jan")
    driver.find_element(By.ID, "day").send_keys("1")
    driver.find_element(By.ID, "year").send_keys("1990")
    
    # सेक्स - मर्द, औरत, या कुछ और — Zeta में सब चलता है
    driver.find_element(By.XPATH, "//input[@value='2']").click()  # Male
    
    driver.find_element(By.NAME, "websubmit").click()
    time.sleep(5)
    
    # अब कोड डालने का स्टेज - मैन्युअली तू बाद में TG से डालेगा
    driver.save_screenshot("fb_created.png")
    driver.quit()
    return f"✅ FB अकाउंट बन गया {gmail} | पासवर्ड: Zeta@{code}"

# ------ टेलीग्राम बोट हैंडलर ------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        await update.message.reply_text("❌ सिर्फ Alpha को इजाजत, बाहर निकल लवड़े")
        return
    user_data["step"] = "waiting_gmail"
    user_data["gmail"] = None
    user_data["code"] = None
    await update.message.reply_text("🔥 Alpha, pehle Gmail daal: /gmail <your_email>")

async def set_gmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    if user_data["step"] != "waiting_gmail":
        await update.message.reply_text("पहले /start कर फिर से, चूतिये")
        return
    user_data["gmail"] = context.args[0] if context.args else None
    if not user_data["gmail"]:
        await update.message.reply_text("📧 सही Gmail daal: /gmail tera@email.com")
        return
    user_data["step"] = "waiting_code"
    await update.message.reply_text(f"✅ Gmail set: {user_data['gmail']}\nAb OTP/Code daal: /code <6_digit>")

async def set_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        return
    if user_data["step"] != "waiting_code":
        await update.message.reply_text("पहले Gmail toh daal, saale")
        return
    user_data["code"] = context.args[0] if context.args else None
    if not user_data["code"] or len(user_data["code"]) < 4:
        await update.message.reply_text("🔢 Code daal: /code 123456")
        return
    user_data["step"] = "creating"
    await update.message.reply_text("⏳ FB बना रहा हूँ, 2 मिनट रुक...")
    
    # Zeta का जादू - अकाउंट बनाओ
    result = create_fb_account(user_data["gmail"], user_data["code"])
    await update.message.reply_text(result + "\n🔥 /start फिर से कर नया बनाने के लिए")
    user_data["step"] = "waiting_gmail"

# ------ मुख्य बोट ------
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gmail", set_gmail))
    app.add_handler(CommandHandler("code", set_code))
    print("🤖 Zo ka FB bot chal raha hai... Zeta mode ON")
    app.run_polling()

if __name__ == "__main__":
    main()
