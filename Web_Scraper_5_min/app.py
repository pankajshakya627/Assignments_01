from flask import Flask, render_template
import threading
import random
import redis
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
import json
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# app = Flask(__name__)
app = Flask(__name__, template_folder='templates')


# Redis instance
redis_instance = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Function to introduce random delays between actions
def random_delay(min_delay=5, max_delay=15):
    delay = random.uniform(min_delay, max_delay)
    sleep(delay)

# Function to scroll the page
def simulate_scroll(driver):
    # Scroll down
    driver.execute_script("window.scrollBy(0, 300);")
    random_delay(1, 2)

# Function to scrape data from the URL every 5 minutes and store it in Redis
def scrape_data():
    DRIVER_PATH = r"F:\\My_Work02\\Demo\\Web_Scraper_5_min\\chromedriver.exe"
    url = 'https://www.nseindia.com/'

    # Define your desired User-Agent string
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"

    # Create a dictionary to hold the desired capabilities
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['chrome.page.customHeaders.User-Agent'] = user_agent

    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # To disable images for faster scraping
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-extensions") #disabling extensions
    chrome_options.add_argument("--disable-gpu")  #applicable to windows os only
    chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model

    service = Service(executable_path=DRIVER_PATH)

    while True:
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url=url)

            ids_list = ["tab1_tableGainer", 'tab1_tableLoser']
            data = {}
            for id_ in ids_list:
                simulate_scroll(driver)
                sleep(30)
                try:
                    print(f'//div[@id="{id_}"]')
                    element = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, f'//div[@id="{id_}"]'))
                    )

                    html_content = element.get_attribute('outerHTML')

                    soup = BeautifulSoup(html_content, 'html.parser')
                    tables = soup.find_all('table')
                    # print(tables)

                    for table in tables:
                        headers = [th.text.strip() for th in table.find_all('th')]
                        rows = []
                        for row in table.find_all('tr'):
                            row_data = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
                            rows.append(row_data)

                        df = pd.DataFrame(rows[1:], columns=headers)
                        data[id_] = df.to_dict('records')
                except Exception as e:
                    print(f"Failed to process element with id {id_}: {e}")

            print(f"Scraped data: {data}")  # Print the scraped data
            redis_instance.set('nifty_data', json.dumps(data))
            redis_instance.publish('nifty_data_channel', json.dumps(data))
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            driver.quit()

        sleep(300)  # Wait for 5 minutes

# data_thread = threading.Thread(target=scrape_data)
# data_thread.daemon = True
# data_thread.start()
scrape_data()

def listen_for_data():
    pubsub = redis_instance.pubsub()  # Get a pubsub instance
    pubsub.subscribe('nifty_data_channel')  # Subscribe to the channel

    for message in pubsub.listen():  # Loop indefinitely, listening for new messages
        if message['type'] == 'message':
            data_str = message['data']
            data = json.loads(data_str)
            global nifty_data  # Define as global so it can be updated from within this function
            nifty_data = data  # Update the global variable with the new data

nifty_data = {}  # Global variable to store the data
data_thread = threading.Thread(target=listen_for_data)
data_thread.daemon = True
data_thread.start()


@app.route('/')
def display_data():
    stocks_data = []

    # Extract stock information from nifty_data dictionary
    for table_id, records in nifty_data.items():
        for record in records:
            stocks_data.append({'name': record.get('Symbol'), 'value': record.get('%Chng')})

    return render_template('index.html', stocks_data=stocks_data)

if __name__ == '__main__':
    app.run(debug=True)
