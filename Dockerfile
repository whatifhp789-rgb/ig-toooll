# Python ka official image use kar rahe hain
FROM python:3.10-slim

# System dependencies install kar rahe hain jisme gnupg, wget, curl sab shamil hai
RUN apt-get update && apt-get install -y \
    gnupg \
    gnupg2 \
    gnupg1 \
    wget \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome ki signing key add karne wali command jo pehle fail ho rahi thi
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Working directory set kar rahe hain
WORKDIR /app

# Requirements file copy karke dependencies install kar rahe hain
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki saari files copy kar rahe hain
COPY . .

# Bot ko run karne ki command (jo aapne Procfile me likhi hogi)
CMD ["python", "bot.py"]
