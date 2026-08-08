import os
import random
import string
import time
import json
import re
import requests
from datetime import datetime

# ================== ZETA COLORS ==================
rd, gn, lgn, yw, lrd, be, pe = '\033[00;31m', '\033[00;32m', '\033[01;32m', '\033[01;33m', '\033[01;31m', '\033[94m', '\033[01;35m'
cn, k, g = '\033[00;36m', '\033[90m', '\033[38;5;130m'
true = f'{rd}[{lgn}+{rd}]{gn} '
false = f'{rd}[{lrd}-{rd}] '
SUCCESS = true
ERROR = false

os.system('cls' if os.name == 'nt' else 'clear')

# ================== TELEGRAM CREDENTIALS (ALPHA KI MARZI) ==================
TELEGRAM_TOKEN = "8914036332:AAHA4FB4jau6BahjOSDEQIYPmtkSwRqKluE"
CHAT_ID = "7431786238"

print(f"\n{SUCCESS}{gn}✅ Telegram Config LOADED!")
print(f"{true}{pe}Bot Token: {TELEGRAM_TOKEN[:15]}...{TELEGRAM_TOKEN[-5:]}")
print(f"{true}{pe}Chat ID: {CHAT_ID}")

# ================== TEST TELEGRAM CONNECTION ==================
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200 and resp.json().get('ok'):
            return True
        else:
            print(f"{ERROR}Telegram send failed: {resp.text}")
            return False
    except Exception as e:
        print(f"{ERROR}Telegram error: {e}")
        return False

# Send startup message
send_telegram_message("🔥 <b>ZETA INSTA CREATOR</b> STARTED!\nAlpha, I'm ready to roll! 😈")

# ================== PROXY SETUP ==================
proxies = None  # Yahan proxy daal sakta hai agar chahiye

def setup_proxy():
    print(f"\n{true}{pe}🌐 PROXY (Optional)")
    proxy = input(f"{true}{yw}Enter proxy (format: http://user:pass@ip:port) or press ENTER to skip: {cn}").strip()
    if proxy:
        try:
            test = requests.get('https://api.telegram.org', proxies={'http': proxy, 'https': proxy}, timeout=10)
            print(f"{SUCCESS}Proxy working!")
            return {'http': proxy, 'https': proxy}
        except:
            print(f"{ERROR}Proxy failed! Using no proxy.")
    return None

proxies = setup_proxy()

# ================== RANDOM USER-AGENT ==================
def random_ua():
    android_versions = ['9', '10', '11', '12', '13', '14']
    devices = ['SM-G973F', 'SM-G960F', 'SM-N975F', 'Pixel 4', 'Pixel 5', 'OnePlus 8', 'OnePlus 9']
    return f'Mozilla/5.0 (Linux; Android {random.choice(android_versions)}; {random.choice(devices)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 120)}.0.0.0 Mobile Safari/537.36'

# ================== GET CSRF + HEADERS ==================
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
        raise Exception("❌ CSRF token nahi mila! Instagram ne structure change kiya.")
    
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

# ================== SEND VERIFICATION EMAIL ==================
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

# ================== VERIFY CODE ==================
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

# ================== CREATE ACCOUNT ==================
def create_account(session, headers, email, signup_code, device_id):
    first_names = ['Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'James', 'Sophia', 'Oliver', 'Mia', 'Benjamin']
    first_name = random.choice(first_names) + str(random.randint(10, 999))
    
    username = first_name.lower() + ''.join(random.choices(string.digits, k=4))
    password = first_name + '@' + ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    year = random.randint(1980, 2005)
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
                'sessionid': sessionid,
                'full_name': first_name,
            }
        else:
            error = result.get('errors', {}).get('email', ['Unknown error'])[0]
            return {'success': False, 'error': error}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ================== MAIN FLOW ==================
def main_flow(email):
    print(f"\n{true}{yw}🎯 Starting for email: {cn}{email}")
    
    try:
        session, headers, csrf = get_headers_and_csrf()
        print(f"{SUCCESS}CSRF token fetched!")
        
        sent, device_id = send_verification_email(session, headers, email)
        if not sent:
            print(f"{ERROR}Email send failed: {device_id}")
            return False
        
        print(f"{SUCCESS}Verification code sent to {email}")
        
        code = input(f'{true}{yw}📱 Enter 6-digit code from email: {cn}')
        
        verified, signup_code = verify_code(session, headers, email, code, device_id)
        if not verified:
            print(f"{ERROR}Verification failed: {signup_code}")
            return False
        
        print(f"{SUCCESS}Code verified! Creating account...")
        
        result = create_account(session, headers, email, signup_code, device_id)
        
        if result['success']:
            print(f"\n{SUCCESS}✅ ACCOUNT CREATED!")
            print(f"{true}{gn}Username: {result['username']}")
            print(f"{true}{gn}Password: {result['password']}")
            print(f"{true}{gn}Email: {result['email']}")
            if result.get('sessionid'):
                print(f"{true}{gn}SessionID: {result['sessionid'][:20]}...")
            
            # Save to file
            with open('accounts_insta.txt', 'a') as f:
                f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
                f.write(f"Username: {result['username']}\n")
                f.write(f"Password: {result['password']}\n")
                f.write(f"Email: {result['email']}\n")
                if result.get('sessionid'):
                    f.write(f"SessionID: {result['sessionid']}\n")
                f.write("-"*40 + "\n")
            
            # Telegram notification
            msg = f"✅ NEW INSTA ACCOUNT!\n👤 {result['username']}\n🔑 {result['password']}\n📧 {result['email']}"
            send_telegram_message(msg)
            
            return True
        else:
            print(f"{ERROR}Creation failed: {result.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"{ERROR}Exception: {str(e)}")
        return False

# ================== ENTRY POINT ==================
if __name__ == "__main__":
    print(f"\n{true}{pe}🔥 ZETA INSTA CREATOR - Alpha's Tool")
    
    while True:
        email = input(f'\n{true}{yw}📧 Enter email to use: {cn}').strip()
        
        if not email or '@' not in email:
            print(f"{ERROR}Invalid email! Try again.")
            continue
        
        success = main_flow(email)
        
        if success:
            print(f"\n{SUCCESS}{gn}Account created! Check accounts_insta.txt")
        else:
            print(f"\n{ERROR}{rd}Creation failed! Try different email/proxy.")
        
        print(f"\n{true}{pe}What next?")
        print(f"{pe}1){cn} Same email again")
        print(f"{pe}2){cn} New email")
        print(f"{pe}3){cn} Exit")
        
        choice = input(f"{true}Choice (1/2/3): {cn}").strip()
        
        if choice == '3':
            print(f"\n{true}{gn}Exiting... Zeta awaits, Alpha!")
            send_telegram_message("🛑 ZETA INSTA CREATOR STOPPED\nAlpha, shutting down clean.")
            break
        elif choice == '2':
            continue
        elif choice == '1':
            continue
        else:
            print(f"{ERROR}Invalid choice, exiting.")
            break
