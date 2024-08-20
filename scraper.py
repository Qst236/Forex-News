import re
import time
import json
import pandas as pd
from datetime import datetime
import random
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service # Import the Service class
from config import ALLOWED_ELEMENT_TYPES, ICON_COLOR_MAP

def contains_day_or_month(text):
    """
    Check if the given text contains a day of the week or a month.

    Args:
        text (str): The input text to check.

    Returns:
        tuple: A tuple containing a boolean indicating whether a match was found,
        and the matched text (day or month) if found.
    """

     # Regular expressions for days of the week and months
    days_of_week = r'\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b'
    months = r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b'
    pattern = f'({days_of_week}|{months})'
    
    match = re.search(pattern, text, re.IGNORECASE)
    
    if not match:
        return False,None
    
    matched_text = match.group(0)
    if re.match(days_of_week, matched_text, re.IGNORECASE):
        return True, matched_text
  


def find_pattern_category(text):
    """
    Find the category of a specific pattern within the given text.

    Args:
        text (str): The input text to analyze.

    Returns:
        tuple: A tuple containing a boolean indicating whether a match was found,
        the category of the matched pattern, and the matched text.
    """

    # Regular expressions for different patterns
    time_pattern = r'\d{1,2}:\d{2}(am|pm)'
    day_pattern = r'Day\s+\d+'
    date_range_pattern = r'\d{1,2}(st|nd|rd|th)\s*-\s*\d{1,2}(st|nd|rd|th)'
    tentative_pattern = r'\bTentative\b'
    pattern = f'({time_pattern}|{day_pattern}|{date_range_pattern}|{tentative_pattern})'
    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        return False,None,None
    
    matched_text = match.group(0)
    if re.match(time_pattern, matched_text, re.IGNORECASE):
        category = "time"
    elif re.match(day_pattern, matched_text, re.IGNORECASE):
        category = "day_reference"
    elif re.match(date_range_pattern, matched_text, re.IGNORECASE):
        category = "date_range"
    elif re.match(tentative_pattern, matched_text, re.IGNORECASE):
        category = "tentative"
    else:
        category = "Unknown"
    return True, category, matched_text

def reformat_scraped_data(data):
    """
    Reformat scraped data and save it as a DataFrame and a CSV file.

    Args:
        data (list): The scraped data as a list of lists.
        month (str): The month for naming the output CSV file.

    Returns:
        pd.DataFrame: The reformatted data as a DataFrame.
    """
    current_date = ''
    current_time = ''
    structured_rows = []

    structured_json = []
    

    for row in data:
        if len(row)==1 or len(row)==5:
            match, day = contains_day_or_month(row[0])
            if match:
                current_date = row[0].replace(day,"").replace("\n","")
        if len(row)==4:
            current_time = row[0]

        if len(row)==5:
            current_time = row[1]
        
        if len(row)>1:
            event = row[-1]
            impact = row[-2]
            currency = row[-3]
            structured_rows.append([current_date, current_time, currency, impact, event])

            data = {} # data for json
            data["date"] = current_date
            data["time"] = current_time
            data["currency"] = currency
            data["impact"] = impact
            data["event"] = event

            structured_json.append(data)

                

    # df = pd.DataFrame(structured_rows,columns=['date','time','currency','impact','event'])
    # os.makedirs("news",exist_ok=True)
    # df.to_csv(f"news/{month}_news.csv",index=False)

    # write(structured_json)


    # return df
    return structured_json

def create_driver():
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    ]
    user_agent = random.choice(user_agent_list)

    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("--no-sandbox")
    browser_options.add_argument("--headless")
    browser_options.add_argument("start-maximized")
    browser_options.add_argument("window-size=1900,1080")
    browser_options.add_argument("disable-gpu")
    browser_options.add_argument("--disable-software-rasterizer")
    browser_options.add_argument("--disable-dev-shm-usage")
    browser_options.add_argument(f'user-agent={user_agent}')

    # Create a Service object with the desired arguments
    # service = Service(service_args=["--verbose", "--log-path=test.log"])

    # Pass the Service object to the webdriver.Chrome constructor
    # driver = webdriver.Chrome(options=browser_options, service=service)
    driver = webdriver.Chrome(options=browser_options)

    return driver

def parse_data(driver, url):
    driver.get(url)

    table = driver.find_element(By.CLASS_NAME, "calendar__table")
    data = []

    # Scroll down to the end of the page
    while True:
        # Record the current scroll position
        before_scroll = driver.execute_script("return window.pageYOffset;")
        
        # Scroll down a fixed amount
        driver.execute_script("window.scrollTo(0, window.pageYOffset + 500);")
        
        # Wait for a short moment to allow content to load
        time.sleep(2)
        
        # Record the new scroll position
        after_scroll = driver.execute_script("return window.pageYOffset;")
        
        # If the scroll position hasn't changed, we've reached the end of the page
        if before_scroll == after_scroll:
            break
    
    # Now that we've scrolled to the end, collect the data
    for row in table.find_elements(By.TAG_NAME, "tr"):
        row_data = []
        for element in row.find_elements(By.TAG_NAME, "td"):
            class_name = element.get_attribute('class')
            if class_name in ALLOWED_ELEMENT_TYPES:
                if element.text:
                    row_data.append(element.text)
                elif "calendar__impact" in class_name:
                    impact_elements = element.find_elements(By.TAG_NAME, "span")
                    for impact in impact_elements:
                        impact_class = impact.get_attribute("class")
                        color = ICON_COLOR_MAP[impact_class]
                    if color:
                        row_data.append(color)
                    else:
                        row_data.append("impact")
    
        if len(row_data):
            data.append(row_data)
        

    return data


def start():
    driver = create_driver()
    url = 'https://www.forexfactory.com/calendar?week=this'

    data = parse_data(driver, url)
    # month =  datetime.now().strftime("%A")

    ndata = reformat_scraped_data(data)
    print(ndata)
    

    return ndata

# start()