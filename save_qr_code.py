import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--user-data-dir=./chrome_data")  # Change path if needed

# Chrome Driver Path
# chrome_driver_path = r"C:\Users\raake\Documents\chrome_driver"  # Replace with your path
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open WhatsApp Web
driver.get("https://web.whatsapp.com/")
time.sleep(10)  # Wait for user to scan QR manually (first time)

# Save session cookies
with open("whatsapp_cookies.pkl", "wb") as file:
    pickle.dump(driver.get_cookies(), file)

print("Cookies saved! You won't need to scan QR next time.")

# Load session cookies
with open("whatsapp_cookies.pkl", "rb") as file:
    cookies = pickle.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)

# Refresh and continue
driver.refresh()
time.sleep(5)
print("Logged in automatically without QR scan!")
