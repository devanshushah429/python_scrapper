from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from pymongo import MongoClient
import json
import re
from lxml import html
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_mongo_client(connection_string):
    return MongoClient(connection_string)

def get_db_and_collection(client, database_name, collection_name):
    db = client[database_name]
    collection = db[collection_name]
    return db, collection

def get_xpath_inner_text(tree, xpath):
    try:
        elements = tree.xpath(xpath)
        if elements:
            strings = [element.text_content() for element in elements]
            result_str = " ".join(strings)
            return re.sub(r"\s+", " ", result_str).strip()
        return None
    except Exception as e:
        logging.error(f"Error in get_xpath_inner_text: {e}")
        return None

def get_xpath_attribute(tree, xpath, attribute):
    try:
        elements = tree.xpath(xpath)
        if elements:
            if attribute == "innerHTML":
                return html.tostring(elements[0], method='html', encoding='unicode')
            return elements[0].get(attribute)
        return None
    except Exception as e:
        logging.error(f"Error in get_xpath_attribute: {e}")
        return None

def get_multiple_xpath_attribute(tree, xpath, attribute):
    try:
        elements = tree.xpath(xpath)
        return [element.get(attribute) for element in elements]
    except Exception as e:
        logging.error(f"Error in get_multiple_xpath_attribute: {e}")
        return None

def get_multiple_xpath_inner_text(tree, xpath):
    try:
        elements = tree.xpath(xpath)
        return [re.sub(r"\s+", " ", element.text_content()).strip() for element in elements]
    except Exception as e:
        logging.error(f"Error in get_multiple_xpath_inner_text: {e}")
        return None

def get_xpath_attribute_from_element(element, xpath=None, attribute=None):
    try:
        if not xpath:
            if attribute == "innerHTML":
                return html.tostring(element, method='html', encoding='unicode')
            return element.get(attribute)

        result_elements = element.xpath(xpath)

        if result_elements:
            return result_elements[0].get(attribute)
        
        return None
    except Exception as e:
        logging.error(f"Error in get_xpath_attribute_from_element: {e}")
        return None

def get_xpath_inner_text_from_element(element, xpath):
    try:
        if not xpath:
            return element.text_content().strip()
        result_elements = element.xpath(xpath)
        if result_elements:
            return result_elements[0].text_content().strip()
        return None
    except Exception as e:
        logging.error(f"Error in get_xpath_inner_text_from_element: {e}")
        return None

def scrape_details_page(driver, url, xpaths):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        tree = html.fromstring(driver.page_source)

        details_data = {}
        for key, xpath in xpaths["details_page"]["inner_text_xpath_dictionary"].items():
            details_data[key] = get_xpath_inner_text(tree, xpath)

        for key, (xpath, attribute) in xpaths["details_page"]["attribute_dictionary"].items():
            details_data[key] = get_xpath_attribute(tree, xpath, attribute)

        for key, (xpath, attribute) in xpaths["details_page"]["multile_attribute_dictionary"].items():
            details_data[key] = get_multiple_xpath_attribute(tree, xpath, attribute)

        for key, xpath in xpaths["details_page"]["multiple_inner_text_dictionary"].items():
            details_data[key] = get_multiple_xpath_inner_text(tree, xpath)

        return details_data
    except Exception as e:
        logging.error(f"Error in scrape_details_page: {e}")
        return {}

def fetch_block_data(driver, page_url, xpaths):
    try:
        driver.get(page_url)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        tree = html.fromstring(driver.page_source)
        block_xpath = xpaths["block_xpath"]
        elements = tree.xpath(block_xpath)

        blocks_data = []
        for element in elements:
            try:
                block_details = {"page_url": page_url}

                for key, value in xpaths["block_details"]["inner_text_xpath_dictionary"].items():
                    block_details[key] = get_xpath_inner_text_from_element(element, value)

                for key, value in xpaths["block_details"]["attribute_dictionary"].items():
                    if key == "url":
                        block_details[key] = xpaths["base_url"] + get_xpath_attribute_from_element(element, value[0], value[1])
                    else:
                        block_details[key] = get_xpath_attribute_from_element(element, value[0], value[1])

                blocks_data.append(block_details)
            except Exception as e:
                logging.error(f"Error processing block data: {e}")
                continue

        return blocks_data
    except Exception as e:
        logging.error(f"Error in fetch_block_data: {e}")
        return []

def process_page(page_url, path_to_chromedriver, xpaths, collection):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service(path_to_chromedriver)
    new_driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        blocks_data = fetch_block_data(new_driver, page_url, xpaths)
        all_data = []

        for block_data in blocks_data:
            details_page_data = scrape_details_page(new_driver, block_data.get("url"), xpaths)
            logging.info(f"Processing block data: {block_data}")
            data = {
                "time_stamp": datetime.now(),
                "url": block_data.get("url"),
                "details": details_page_data
            }

            del block_data["url"]
            data["block_data"] = block_data
            all_data.append(data)

        if all_data:
            collection.insert_many(all_data)
    except Exception as e:
        logging.error(f"Error in process_page: {e}")
        return all_data
    finally:
        new_driver.quit()

def main():
    path_to_chromedriver = "C:\\Program Files\\chromedriver-win64\\chromedriver.exe"
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    service = Service(path_to_chromedriver)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    with open("xpaths.json") as f:
        xpaths = json.load(f)

    source_url = xpaths["source_url"]
    next_button_xpath = xpaths["next_button_xpath"]

    client = get_mongo_client(xpaths["connection_string"])
    db, collection = get_db_and_collection(client, xpaths["database_name"], xpaths["collection_name"])

    try:
        driver.get(source_url)

        while True:
            current_page_url = driver.current_url
            logging.info(f"Processing page: {current_page_url}")

            try:
                process_page(current_page_url, path_to_chromedriver, xpaths, collection)

                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, next_button_xpath))
                )

                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                driver.execute_script("arguments[0].click();", next_button)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@class,'article')]"))
                )

            except Exception as e:
                logging.error(f"Error during pagination: {e}")
                break

    finally:
        driver.quit()
        client.close()

if __name__ == "__main__":
    main()
