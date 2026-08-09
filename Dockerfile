FROM python:3.11-slim

# ================== CHROME INSTALL ==================
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ================== CHROMEDRIVER INSTALL (FIXED) ==================
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f1-3 || echo "120.0.6099.109") \
    && echo "✅ Chrome Version: $CHROME_VERSION" \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver-linux64.zip

# ================== PYTHON DEPENDENCIES ==================
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py /app/bot.py

CMD ["python", "/app/bot.py"]
