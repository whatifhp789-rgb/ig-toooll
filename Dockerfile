# Pehle zaroori packages install karein (gnupg aur curl/wget agar nahi hain toh)
RUN apt-get update && apt-get install -y gnupg wget curl

# Google ki key ko sahi secure folder mein download karein
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg

# Repository list mein keyrings ka path specify karein
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Ab repository update karke Chrome install karein
RUN apt-get update && apt-get install -y google-chrome-stable --no-install-recommends
