# 1. Sabse pehle base image specify karna zaroori hai
FROM python:3.10-slim

# 2. Phir zaroori packages install karein
RUN apt-get update && apt-get install -y gnupg wget curl

# 3. Google ki key ko secure folder mein download karein
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg

# 4. Repository list mein keyrings ka path add karein
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# 5. Repository update karke Chrome install karein
RUN apt-get update && apt-get install -y google-chrome-stable --no-install-recommends

# (Agar iske neeche aapke baaki ke commands jaise WORKDIR, COPY, ya pip install the, toh unhe iske niche waise hi rehne dena)
