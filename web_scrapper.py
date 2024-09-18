from  util.lxml_handler.xpath_extractor import XPathExtractor
from util.lxml_handler.html_parser import HTMLParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import json
import logging
from database.mongo_db_handler import MongoDBHandler
from util.selenium_handler.selenium_web_page_scrapper import SeleniumWebPageScrapper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_details_page(selenium_web_page_scraper: SeleniumWebPageScrapper, url, xpaths):
    try:
        selenium_web_page_scraper.load_url(url)
        tree = HTMLParser(selenium_web_page_scraper.get_page_source()).parse()

        xpath_extractor = XPathExtractor(tree)
        details_data = {}
        for key, xpath in xpaths["details_page"]["inner_text_xpath_dictionary"].items():
            details_data[key] = xpath_extractor.get_xpath_inner_text(xpath)

        for key, (xpath, attribute) in xpaths["details_page"]["attribute_dictionary"].items():
            details_data[key] = xpath_extractor.get_xpath_attribute(xpath, attribute)

        for key, (xpath, attribute) in xpaths["details_page"]["multile_attribute_dictionary"].items():
            details_data[key] = xpath_extractor.get_multiple_xpath_attribute(xpath, attribute)

        for key, xpath in xpaths["details_page"]["multiple_inner_text_dictionary"].items():
            details_data[key] = xpath_extractor.get_multiple_xpath_inner_text(xpath)

        return details_data
    except Exception as e:
        logging.error(f"Error in scrape_details_page: {e}")
        return {}

def fetch_block_data(selenium_web_page_scraper:SeleniumWebPageScrapper, page_url, xpaths):
    try:
        selenium_web_page_scraper.load_url(page_url)
        tree = HTMLParser(selenium_web_page_scraper.get_page_source()).parse()
        block_xpath = xpaths["block_xpath"]
        elements = tree.xpath(block_xpath)

        xpath_extractor = XPathExtractor(tree)
        blocks_data = []
        for element in elements:
            try:
                block_details = {"page_url": page_url}

                for key, value in xpaths["block_details"]["inner_text_xpath_dictionary"].items():
                    block_details[key] = xpath_extractor.get_xpath_inner_text_from_element(element, value)

                for key, value in xpaths["block_details"]["attribute_dictionary"].items():
                    if key == "url":
                        block_details[key] = xpaths["base_url"] + xpath_extractor.get_xpath_attribute_from_element(element, value[0], value[1])
                    else:
                        block_details[key] = xpath_extractor.get_xpath_attribute_from_element(element, value[0], value[1])

                blocks_data.append(block_details)
            except Exception as e:
                logging.error(f"Error processing block data: {e}")
                continue

        return blocks_data
    except Exception as e:
        logging.error(f"Error in fetch_block_data: {e}")
        return []

def process_page(page_url, path_to_chromedriver, xpaths):

    mongo_db_handler = MongoDBHandler(xpaths["connection_string"], xpaths["database_name"], xpaths["collection_name"])
    selenium_web_page_scrapper = SeleniumWebPageScrapper(path_to_chromedriver)

    try:
        blocks_data = fetch_block_data(selenium_web_page_scrapper, page_url, xpaths)
        all_data = []

        for block_data in blocks_data:
            details_page_data = scrape_details_page(selenium_web_page_scrapper, block_data.get("url"), xpaths)
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
            mongo_db_handler.insert_many(all_data)
    except Exception as e:
        logging.error(f"Error in process_page: {e}")
        return all_data
    finally:
        selenium_web_page_scrapper.quit_driver()

def main():
    path_to_chromedriver = "C:\\Program Files\\chromedriver-win64\\chromedriver.exe"
    selenium_web_page_scrapper = SeleniumWebPageScrapper(path_to_chromedriver)

    with open("xpaths.json") as f:
        xpaths = json.load(f)

    source_url = xpaths["source_url"]
    next_button_xpath = xpaths["next_button_xpath"]

    try:
        selenium_web_page_scrapper.load_url(source_url)

        while True:
            current_page_url = selenium_web_page_scrapper.get_current_url()
            logging.info(f"Processing page: {current_page_url}")

            try:
                process_page(current_page_url, path_to_chromedriver, xpaths)

                next_button = WebDriverWait(selenium_web_page_scrapper.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, next_button_xpath))
                )

                selenium_web_page_scrapper.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                selenium_web_page_scrapper.driver.execute_script("arguments[0].click();", next_button)
                WebDriverWait(selenium_web_page_scrapper.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@class,'article')]"))
                )

            except Exception as e:
                logging.error(f"Error during pagination: {e}")
                break

    finally:
        selenium_web_page_scrapper.quit_driver()

if __name__ == "__main__":
    main()
