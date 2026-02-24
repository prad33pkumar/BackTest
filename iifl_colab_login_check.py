"""
Google Colab-friendly script to verify whether login to
https://markets.iiflcapital.com/ is successful.

Usage in Colab:
1) Paste this file content into a cell.
2) Run it and enter your credentials when prompted.
3) Complete OTP/2FA manually if asked.
"""

import argparse
import getpass
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

LOGIN_URL = "https://markets.iiflcapital.com/"
TIMEOUT_SECONDS = 40


def build_driver(headless: bool = True) -> webdriver.Chrome:
    """Create a Chrome driver that works well in Google Colab."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def attempt_login(driver: webdriver.Chrome, user_id: str, password: str) -> None:
    """Open login page and try to submit credentials."""
    driver.get(LOGIN_URL)

    wait = WebDriverWait(driver, TIMEOUT_SECONDS)

    # These selectors are generic and may need adjustment if site DOM changes.
    user_box = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[type='text'], input[type='email'], input[name*='user'], input[id*='user']",
            )
        )
    )
    pass_box = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[type='password'], input[name*='pass'], input[id*='pass']",
            )
        )
    )

    user_box.clear()
    user_box.send_keys(user_id)
    pass_box.clear()
    pass_box.send_keys(password)

    login_btn = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "button[type='submit'], input[type='submit'], button[id*='login'], button[name*='login']",
            )
        )
    )
    login_btn.click()


def login_status(driver: webdriver.Chrome) -> tuple[bool, str]:
    """Check whether login succeeded based on URL and page signals."""
    wait = WebDriverWait(driver, TIMEOUT_SECONDS)

    # Give time for redirects / OTP step.
    time.sleep(3)

    current_url = driver.current_url.lower()
    page_text = driver.page_source.lower()

    # Common success signal: redirected away from login page
    if "login" not in current_url and "markets.iiflcapital.com" in current_url:
        return True, f"Redirected to: {driver.current_url}"

    # Generic dashboard signals
    success_selectors = [
        "[href*='logout']",
        "button[id*='logout']",
        "a[href*='portfolio']",
        "a[href*='dashboard']",
    ]
    for selector in success_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            return True, f"Found post-login element: {selector}"

    # If OTP/MFA screen is present, login is partially complete but not fully authenticated yet.
    if any(token in page_text for token in ["otp", "one time password", "2fa", "verification code"]):
        return False, "OTP/2FA step detected. Complete OTP and rerun status check."

    # Explicit failure hints
    if any(token in page_text for token in ["invalid", "incorrect", "failed", "try again"]):
        return False, "Login failed: invalid credentials or rejected attempt."

    # Last attempt: wait for URL change away from known login patterns.
    try:
        wait.until(lambda d: "login" not in d.current_url.lower())
        return True, f"URL changed to: {driver.current_url}"
    except TimeoutException:
        return False, f"Still on login-like page: {driver.current_url}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check IIFL Markets login status")
    parser.add_argument('--user-id', help='IIFL user ID')
    parser.add_argument('--password', help='IIFL password')
    parser.add_argument('--headed', action='store_true', help='Run browser in headed mode (useful outside Colab)')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print("IIFL Market Login Checker")
    user_id = (args.user_id or input("Enter your IIFL user ID: " )).strip()
    password = args.password or getpass.getpass("Enter your password: ")

    driver = build_driver(headless=not args.headed)
    try:
        attempt_login(driver, user_id, password)
        ok, message = login_status(driver)
        print("\n=== RESULT ===")
        if ok:
            print("✅ Login appears successful.")
        else:
            print("❌ Login not confirmed.")
        print(message)
        print(f"Current URL: {driver.current_url}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
