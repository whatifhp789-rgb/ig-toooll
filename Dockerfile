FROM python:3.12-slim-bookworm

# Install all system dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libdbus-1-3 \
    libexpat1 \
    libx11-6 \
    libxext6 \
    libxcb1 \
    libnspr4 \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and Chromium
RUN pip install --no-cache-dir playwright==1.42.0 && \
    playwright install chromium

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
