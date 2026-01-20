import time
import pywhatkit as kit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from deepseek import DeepSeek  # Replace with appropriate AI API

# Configure DeepSeek AI (Replace with actual API key)
deepseek = DeepSeek(api_key="sk-847377f5ee3b4b769666698abc380e09")

# Configure Selenium WebDriver
chrome_driver_path = r"C:\Users\raake\Documents\chrome_driver"  # Update with your actual path
service = Service(chrome_driver_path)
driver = webdriver.C
hrome(service=service)

# Open WhatsApp Web
driver.get("https://web.whatsapp.com/")
input("Scan the QR code in WhatsApp Web and press Enter to continue...")

# Group name (must match exactly)
group_name = "My WhatsApp Group"

# Function to navigate to the group chat
def open_group():
    search_box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
    search_box.send_keys(group_name)
    time.sleep(2)
    search_box.send_keys(Keys.ENTER)

# Function to get latest messages
def get_latest_messages():
    messages = driver.find_elements(By.XPATH, "//div[contains(@class,'message-in')]")
    last_messages = [msg.text for msg in messages[-5:]]  # Get last 5 messages
    return last_messages

# Function to analyze if a message is argumentative
def is_argumentative(message):
    prompt = f"Classify this message as 'argumentative' or 'neutral':\n{message}"
    response = deepseek.chat(prompt)
    return "argumentative" in response.lower()

# Function to send a warning message
def send_warning(user):
    warning_msg = f"Hey {user}, please maintain a respectful conversation."
    kit.sendwhatmsg_instantly(user, warning_msg)
    print(f"Warning sent to {user}")

# Main monitoring loop
open_group()
while True:
    messages = get_latest_messages()
    for msg in messages:
        if is_argumentative(msg):
            user_phone = "+yy"  # Replace with detected user's phone number
            send_warning(user_phone)
    time.sleep(5)  # Check every 5 seconds
