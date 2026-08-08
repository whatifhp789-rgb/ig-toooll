import os
import random
import string
import time
import names
import requests
import telebot

rd, gn, lgn, yw, lrd, be, pe = '\033[00;31m', '\033[00;32m', '\033[01;32m', '\033[01;33m', '\033[01;31m', '\033[94m', '\033[01;35m'
cn, k, g = '\033[00;36m', '\033[90m', '\033[38;5;130m'
true = f'{rd}[{lgn}+{rd}]{gn} '
false = f'{rd}[{lrd}-{rd}] '
SUCCESS = f'{rd}[{lgn}+{rd}]{gn} '
ERROR = f'{rd}[{lrd}-{rd}]{rd} '

os.system('cls' if os.name == 'nt' else 'clear')

mport os

# input() ki jagah environment variable se token lein
TELEGRAM_TOKEN = os.getenv("8438829745:AAGKGPAFcGr6P-M6YrxQpZ7FQmmg9LnGsoc")
CHAT_ID = input(f'{true}{yw}📱 7431786238: ')
os.system('cls' if os.name == 'nt' else 'clear')
import webbrowser
webbrowser.open("https://t.me/BlackHatFrozen")

print("""\033[97;1m
\x1b[1;30m☆~:*:\x1b[1;31m☆~:*:\x1b[1;32m☆~:*:\x1b[1;33m☆~:{ \x1b[1;91m\x1b[1;100m< Frozen X PokiePy >\033[0;m\x1b[1;93m\033[97;1m }\x1b[1;30m☆~:*:\x1b[1;31m☆~:*:\x1b[1;34m☆~:*:
   OWNER:- \x1b[1;31m @DarkFrozenOwner\x1b[1;37m
   TOOL :- \x1b[1;36m Instagram Auto Account Creator
   Channel :-\x1b[1;34m @DarkFrozenGaming , @Pokie_Toolz\x1b[1;37m
   version :- \x1b[1;33m4.0\x1b[1;37m
   TOOL :-\x1b[1;38m FREE\x1b[1;37m
\033[1;97m\033[97;1m
\x1b[1;30m☆~:*:\x1b[1;31m☆~:*:\x1b[1;32m☆~:*:\x1b[1;33m☆~:{ \x1b[1;91m\x1b[1;100m< Frozen X PokiePy >\033[0;m\x1b[1;93m\033[97;1m }\x1b[1;30m☆~:*:\x1b[1;31m☆~:*:\x1b[1;34m☆~:*:""")
logop = f'''⠀\x1b[38;5;22m⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣴⣶⣶⣾⣿⣿⣿⣿⣿⣿⣷⣶⣶⣦⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⣿⡿⠿⠿⢿⠛⠋⠉⠉⠙⠛⠛⠛⠿⠿⢿⣿⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣾⣿⣿⣿⡿⢿⠹⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⢿⣿⣿⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⡿⠛⣿⣯⣀⣀⠀⠙⢿⣦⣄⣀⡀⢀⣴⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⠟⠁⠀⠀⠈⠙⣛⣿⣿⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⠋⠀⣠⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣶⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣷⣄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣴⣿⣿⠟⠁⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠋⠙⠛⢿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣦⠀⠀⠀⠀⠀
⠀⠀⠀⢀⣾⣿⣿⣯⣀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣾⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣷⡀⠀⠀⠀
⠀⠀⢀⣾⣿⡿⠁⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣤⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣷⡀⠀⠀
⠀⠀⣾⣿⣿⠁⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⠁⠀⠀⠈⠙⠻⣿⣿⣿⣿⣿⡿⠿⣿⣶⣤⣴⣶⣦⡀⠀⠀⠀⠈⢿⣿⣷⠀⠀
⠀⣸⣿⣿⠃⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣄⠀⠀⠀⠈⠙⢿⣿⣿⣶⣶⣿⣿⣿⣿⣿⣿⡓⠀⠀⠀⠀⠘⣿⣿⣇⠀
⢀⣿⣿⡏⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡝⢿⣿⣿⣿⣿⠿⠛⠉⠀⠀⠉⠛⠻⢿⣦⣄⠀⠀⠀⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⢹⣿⣿⡀
⢸⣿⣿⠃⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⣿⣦⣄⠀⠀⠀⠀⣿⠿⣯⡙⢻⡏⠀⠀⠀⠀⠀⠀⠈⣿⣿⡇
⣾⣿⣿⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀    @SANJUKlNG⠀⠀⠀⠙⢿⣿⣿⣶⣶⣤⣿⣦⣼⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿
⣿⣿⡏⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠙⠛⠛⠛⠁⢸⣿⡀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿
⣿⣿⡇⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠈⣿⣧⠀⠀⠀⠀⠀⢳⣄⢸⣿⣿
⢿⣿⣿⢀⣤⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⡀⠀⠀⢹⣿⣆⠀⠀⠀⠀⢸⡿⣿⣿⣿
⢸⣿⣿⡄⠉⠛⠉⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⠀⢻⣿⡷⢦⣤⣶⠟⢁⣿⣿⡇
⠘⣿⣿⣇⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠙⢿⣤⣤⣤⡴⣸⣿⣿⠃
⠀⢹⣿⣿⡄⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠈⠉⠁⢠⣿⣿⡏⠀
⠀⠀⢿⣿⣷⡀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⢀⣾⣿⡿⠀⠀
⠀⠀⠈⢿⣿⣷⡀⠀⠀⠀⠀⢸⣿⣿⠛⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⢀⣾⣿⡿⠁⠀⠀
⠀⠀⠀⠈⢿⣿⣷⡄⠀⣀⣀⣸⣿⡇⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⢠⣾⣿⡿⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠻⣿⣿⣦⡈⠛⠛⠋⠀⠀⠀⢹⡟⠀⠈⠉⠉⠛⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⣴⣿⣿⠟⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠙⢿⣿⣷⣄⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣶⣦⣤⣀⣀⡀⠀⠀⠀⠀⣀⣀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠛⠿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠿⠛⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀


⠀⠀'''
print(logop)


proxies = None


def show_thinking(message="Processing", duration=4):
    print(f"\n{true}{cn}{message}", end="", flush=True)
    for i in range(duration):
        time.sleep(1)
        print(".", end="", flush=True)
    print("\n")


def show_ip_info():
    try:
        show_thinking("🌐 Checking your IP", 3)
        ip_data = requests.get("https://ipinfo.io/json", timeout=10).json()
        ip = ip_data.get("ip", "Unknown")
        country = ip_data.get("country", "??")
        city = ip_data.get("city", "")
        region = ip_data.get("region", "")
        print(f"{true}\x1b[1;36m📍Current IP: {ip}")
        print(f"\x1b[1;91m\x1b[1;100m🌍 Location: {country} ({city}, {region}) \n")
    except Exception as e:
        print(f"{false} ❌ Could not fetch IP info: {e}")


show_ip_info()


def get_headers(Country, Language):
    while True:
        try:
            show_thinking("Fetching headers", 2)
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
                'accept-language': f'{Language}-{Country},en-US;q=0.8,en;q=0.7',
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
        except Exception as E:
            print(E)


def Get_UserName(Headers, Name, Email):
    try:
        show_thinking("Getting username suggestion", 7)
        while True:
            data = {'email': Email, 'name': Name + str(random.randint(1, 99))}
            response = requests.post(
                'https://www.instagram.com/api/v1/web/accounts/username_suggestions/',
                headers=Headers, data=data, proxies=proxies, timeout=30
            )
            if 'status":"ok' in response.text:
                print(f"{true} Username generated")
                return random.choice(response.json()['suggestions'])
    except Exception as E:
        print(E)


def Send_SMS(Headers, Email):
    try:
        show_thinking("Sending verification code", 10)
        data = {
            'device_id': Headers['cookie'].split('mid=')[1].split(';')[0],
            'email': Email
        }
        response = requests.post(
            'https://www.instagram.com/api/v1/accounts/send_verify_email/',
            headers=Headers, data=data, proxies=proxies, timeout=30
        )
        return response.text
    except Exception as E:
        print(E)


def Validate_Code(Headers, Email, Code):
    try:
        show_thinking("Validating code", 10)
        data = {
            'code': Code,
            'device_id': Headers['cookie'].split('mid=')[1].split(';')[0],
            'email': Email
        }
        response = requests.post(
            'https://www.instagram.com/api/v1/accounts/check_confirmation_code/',
            headers=Headers, data=data, proxies=proxies, timeout=30
        )
        return response
    except Exception as E:
        print(E)


def get_random_file_from_folder(folder):
    valid_exts = ['.jpg', '.jpeg', '.png']
    files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in valid_exts]
    return os.path.join(folder, random.choice(files)) if files else None


def upload_profile_pic(sessionid, csrftoken, retries=3):
    try:
        folder = 'Profile_pic'
        photo_path = get_random_file_from_folder(folder)
        if not photo_path:
            print(ERROR + "No profile pictures found in folder.")
            return
        url = 'https://www.instagram.com/accounts/web_change_profile_picture/'
        headers = {
            'cookie': f'sessionid={sessionid}; csrftoken={csrftoken};',
            'x-csrftoken': csrftoken,
            'referer': 'https://www.instagram.com/accounts/edit/',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        }
        for attempt in range(1, retries + 1):
            with open(photo_path, 'rb') as f:
                files = {'profile_pic': f}
                resp = requests.post(url, headers=headers, files=files, proxies=proxies)
            if resp.status_code == 200 and '"changed_profile":true' in resp.text:
                print(SUCCESS + f"Profile picture uploaded! [Attempt {attempt}]")
                return
            else:
                print(ERROR + f"Failed to upload profile picture [Attempt {attempt}]: {resp.text}")
    except Exception as e:
        print(ERROR + f"Exception during profile pic upload: {e}")


def convert_to_professional(sessionid, csrftoken, retries=3):
    try:
        url = "https://www.instagram.com/api/v1/business/account/convert_account/"
        headers = {
            'cookie': f'sessionid={sessionid}; csrftoken={csrftoken};',
            'x-csrftoken': csrftoken,
            'referer': 'https://www.instagram.com/accounts/convert_to_professional_account/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'content-type': 'application/x-www-form-urlencoded',
            'x-ig-app-id': '1217981644879628',
            'x-requested-with': 'XMLHttpRequest'
        }

        category_ids = [
            "180164648685982",
            "180410820992720",
            "180504230065143",
            "180213508993482",
            "180144472006690",
            "180559408665151"
        ]
        category_id = random.choice(category_ids)

        data = {
            "category_id": category_id,
            "create_business_id": "true",
            "entry_point": "ig_web_settings",
            "set_public": "true",
            "should_bypass_contact_check": "true",
            "should_show_category": "0",
            "to_account_type": "3",
            "jazoest": "22663"
        }

        for attempt in range(1, retries + 1):
            resp = requests.post(url, headers=headers, data=data, proxies=proxies)
            if resp.status_code == 200 and '\"status\":\"ok\"' in resp.text:
                print(SUCCESS + f"Converted to Professional Account! [Attempt {attempt}]")
                print(true + f"Category ID used: {category_id}")
                return True
            else:
                print(ERROR + f"Failed to convert account [Attempt {attempt}]: {resp.text}")
                time.sleep(2)
        return False
    except Exception as e:
        print(ERROR + f"Exception during conversion: {e}")
        return False


def Create_Acc(Headers, Email, SignUpCode):
    try:
        firstname = names.get_first_name()
        UserName = Get_UserName(Headers, firstname, Email)
        Password = firstname.strip() + '@' + str(random.randint(111, 999))

        show_thinking("Creating account", 5)
        data = {
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{Password}',
            'email': Email,
            'username': UserName,
            'first_name': firstname,
            'month': random.randint(1, 12),
            'day': random.randint(1, 28),
            'year': random.randint(1990, 2001),
            'client_id': Headers['cookie'].split('mid=')[1].split(';')[0],
            'seamless_login_enabled': '1',
            'tos_version': 'row',
            'force_sign_up_code': SignUpCode,
        }

        response = requests.post(
            'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/',
            headers=Headers, data=data, proxies=proxies, timeout=30
        )
        print(f"[RESPONSE]: {response.text}")
        if '"account_created":true' in response.text:
            sessionid = response.cookies['sessionid']
            csrftoken = Headers['x-csrftoken']
            print(f"{true} UserName : {UserName}")
            print(f"{true} PassWord : {Password}")
            print(f"{true} Sessionid : {sessionid}")

            with open('account_insta.txt', 'a') as f:
                f.write(f'UserName: {UserName}\n Password: {Password}\nEmail: {Email}\n')

            
            show_thinking("Uploading Profile Pic", 8)
            upload_profile_pic(sessionid, csrftoken)

            
            show_thinking("Converting to Professional Account", 5)
            convert_to_professional(sessionid, csrftoken)

           
            send_telegram_message(
                f"New Instagram Account Created:\nUsername: {UserName}\nPassword: {Password}\nEmail: {Email}"
            )
        else:
            print(ERROR + "Account not created!")
    except Exception as E:
        print(E)


def send_telegram_message(message):
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    bot.send_message(CHAT_ID, message)


def account_flow_with_email(Email):
    headers = get_headers(Country='US', Language='en')
    ss = Send_SMS(headers, Email)
    print(f'{true}{yw}🍁 An account creation code has been sent to: {cn}{Email}')

    if 'email_sent":true' in ss:
        code = input('👩‍💻 Enter Code : ')
        a = Validate_Code(headers, Email, code)
        if 'status":"ok' in a.text:
            print(f'{true}✅ Good OTP {cn}')
            SignUpCode = a.json()['signup_code']
            Create_Acc(headers, Email, SignUpCode)
        else:
            print(ERROR + "Invalid OTP / verification failed.")
    else:
        print(ERROR + "Failed to send email code.")


if __name__ == "__main__":
    print(f"{rd}Tool {yw}By {lgn}@DarkFrozenOwner✅")

    
    Email = input(f'{true}📧 Enter Your Email:{cn}   ').strip()

    while True:
        
        account_flow_with_email(Email)

        
        print("\n" + true + "What do you want to do next?")
        print(f"{pe}1){cn} Create another account with SAME email ({Email})")
        print(f"{pe}2){cn} Create account with NEW email")
        print(f"{pe}3){cn} Exit")

        choice = input(f"{true}Enter your choice (1/2/3): {cn}").strip()

        if choice == "1":
            
            print(true + f"Using same email again: {Email}")
            continue
        elif choice == "2":
            #
            Email = input(f'{true}📧 Enter NEW Email:{cn}   ').strip()
            continue
        elif choice == "3":
            print(true + "Exiting... Done, TG : @DarkFrozenGaming")
            break
        else:
            print(ERROR + "Invalid choice, exiting for safety.")
            break
