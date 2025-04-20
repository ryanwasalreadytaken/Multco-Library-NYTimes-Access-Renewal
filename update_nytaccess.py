"""
Activates 24 hours of New York Times digital provided by the Multnomah County Library
"""
import os
import sys
import urllib
import http.client
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    handlers=[RotatingFileHandler('logs/update.log', maxBytes=10240000, backupCount=3),
              logging.StreamHandler(sys.stdout)],
    )


def pushover(title, message):
    """Receives title, message, and severity variables and generates a pushover alert.
    Disabled in default env.env file. Set ALERTS=true in .env file to enable.
    """
    alerts = os.getenv('ALERTS')
    priority = os.getenv('ALERT_PRIORITY')
    userkey = os.getenv('PUSH_USERKEY')
    token = os.getenv('PUSH_TOKEN')
    conn = http.client.HTTPSConnection("api.pushover.net:443")

    if alerts:
        conn.request("POST", "/1/messages.json",
                     urllib.parse.urlencode({
                         "token": token,
                         "user": userkey,
                         "title": title,
                         "message": message,
                         "priority": priority,
                     }), {"Content-type": "application/x-www-form-urlencoded"})
        response = conn.getresponse()

        if response.status == 200:
            logging.info('Pushover alert sent successfully')
        else:
            logging.error('Pushover alert failed to send')
            logging.error("Server response: %s, %s", {response.status}, {response.reason})

    else:
        logging.warning('Pushover alerts are disabled. Set ALERT=true in .env to enable')


if __name__ == '__main__':
    logging.info('Initializing NYT renewal script...')

    # Load config values from .env
    load_dotenv()
    cardnum = os.getenv('MCL_CARDNUM')
    cardpin = os.getenv('MCL_CARDPIN')
    email = os.getenv('NYT_EMAIL')
    nytpass = os.getenv('NYT_PASS')
    url = os.getenv('URL')

    # Setup and instantiate a Firefox webdriver session
    options = FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)

    try:
        driver.get(url)

        # Login to Multco Library proxy site
        username = driver.find_element(By.NAME, value='user')
        password = driver.find_element(By.NAME, value='pass')
        username.send_keys(cardnum)
        password.send_keys(cardpin, Keys.RETURN)

        # Click continue on NYT terms of service page
        button_text = "Continue"
        continue_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{button_text}']")))
        continue_button.click()

        # Login to NYT
        login = driver.find_element(By.LINK_TEXT, 'Log in')
        login.click()

        # Input creds and submit
        driver.find_element(By.XPATH, "//*[@id='email']").send_keys(email)
        driver.find_element(By.XPATH, "/html/body/div/div/div/div/form/div/div[4]/button").click()
        driver.find_element(By.XPATH, "//*[@id='password']").send_keys(nytpass)
        driver.find_element(By.XPATH, "/html/body/div/div/div/form/div/div[2]/button").click()

        # Close browser
        driver.quit()

        logging.info('NYT access renewal was successful!')

    except Exception as e:
        # Close any hung instances of firefox
        driver.quit()

        hostname = os.uname().nodename
        pushtitle = "NYT Access Renewal Failure"
        pushmessage = f'An error occurred when reactivating on {hostname}:\n\n{e}'

        logging.error(pushmessage, exc_info=True)
        pushover(pushtitle, pushmessage)

sys.exit()
