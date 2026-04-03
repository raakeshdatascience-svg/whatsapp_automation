import os
import time
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Config
GROUP_NAME = "Test WhatsApp"
PROFILE_DIR = os.path.abspath("whatsapp_profile")
OUTPUT_FILE = "group_members.csv"
WELCOME_TEMPLATE = "Welcome to the group {group_name}"

# --- Launch browser with cached profile
options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={PROFILE_DIR}")
options.add_argument("--window-size=1920,1080")
# options.headless = True  # Optional after QR login

driver = uc.Chrome(options=options)
driver.get("https://web.whatsapp.com")


def get_search_box(driver):
    """Return the chat search box using whichever selector WhatsApp currently exposes."""
    selectors = [
        'div[data-testid="chat-list-search"] div[contenteditable="true"]',
        'div[contenteditable="true"][data-tab="3"]',
        'div[contenteditable="true"][role="textbox"]',
        "p.selectable-text.copyable-text",
    ]
    last_error = None
    for selector in selectors:
        try:
            return WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        except Exception as exc:
            last_error = exc
            continue
    raise RuntimeError("Unable to locate WhatsApp search box; update selectors") from last_error


def get_members_panel(driver):
    """Return the member list scroll region."""
    selectors = [
        '//div[@role="region"]',
        '//div[@data-animate-modal-body="true"]',
        '//div[@aria-label="Group info"]//div[@aria-label="List"]',
    ]
    last_error = None
    for selector in selectors:
        try:
            return WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
        except Exception as exc:
            last_error = exc
            continue
    raise RuntimeError("Unable to locate members scroll panel; update selectors") from last_error


def get_chat_composer(driver):
    """Return the main chat message composer."""
    selectors = [
        'div[contenteditable="true"][data-tab="10"]',
        'div[contenteditable="true"][data-tab="9"]',
        'div[contenteditable="true"][data-tab="8"]',
        'div[contenteditable="true"][data-tab="6"]',
        'footer div[contenteditable="true"][role="textbox"]',
    ]
    last_error = None
    for selector in selectors:
        try:
            return WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
        except Exception as exc:
            last_error = exc
            continue
    raise RuntimeError("Unable to locate chat composer; update selectors") from last_error


def print_welcome_prompt(driver, group_name):
    """Type and send the welcome message in the active chat."""
    message = WELCOME_TEMPLATE.format(group_name=group_name)
    print(f'Typing welcome message for {group_name!r}: "{message}"')
    composer = get_chat_composer(driver)
    composer.click()
    composer.send_keys(message)
    composer.send_keys(Keys.ENTER)


# --- Wait for WhatsApp Web to load
print("Waiting for WhatsApp Web...")
search_box = get_search_box(driver)

# --- Search for the group
print(f"Searching for group: {GROUP_NAME}")
search_box.click()
search_box.send_keys(GROUP_NAME)
time.sleep(2)
search_box.send_keys(Keys.ENTER)
time.sleep(3)
print_welcome_prompt(driver, GROUP_NAME)

# --- Click group header to open group info
# Click the group title to open Group Info
group_title = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(
        (By.XPATH, '//span[contains(@title, "' + GROUP_NAME + '")]')
    )
)
group_title.click()
time.sleep(2)

def get_phone_numbers():

    # --- Scroll to ensure all members are visible
    panel = get_members_panel(driver)
    for _ in range(5):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", panel)
        time.sleep(1)

    # --- Get list of members (those with clickable profiles)
    members_xpath = '//div[@role="button" and .//span[@dir="auto" and string-length(normalize-space()) > 0]]'
    member_elements = driver.find_elements(By.XPATH, members_xpath)

    print(f"Found {len(member_elements)} member entries")

    # --- Visit each member and extract name and phone

    phone_numbers = []

    for i in range(len(member_elements)):
        try:
            # Re-fetch because DOM reloads after each back
            member_elements = driver.find_elements(By.XPATH, members_xpath)
            member = member_elements[i]
            member.click()
            time.sleep(2)

            # Get name
            name_elems = driver.find_elements(By.XPATH, '//span[@dir="auto"]')
            name = name_elems[0].text.strip() if name_elems else "Unknown"

            # Get number
            try:
                phone_elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[contains(@class,"x1fcfy0u") and contains(text(), "+")]')
                    )
                )
                number = phone_elem.text.strip()
            except:
                number = "Not visible"

            print(f"{i + 1}. {name} - {number}")
            phone_numbers.append((name, number))

            driver.back()
            time.sleep(2)

        except Exception as e:
            print(f"Error with member {i + 1}: {e}")
            driver.back()
            time.sleep(2)
            continue

    # --- Save results to CSV
    with open(OUTPUT_FILE, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Phone Number"])
        writer.writerows(phone_numbers)

    print(f"\nSaved {len(phone_numbers)} members to {OUTPUT_FILE}")
    driver.quit()

def main():
    print_welcome_prompt(GROUP_NAME)
