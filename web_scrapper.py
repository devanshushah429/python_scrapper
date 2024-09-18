from datetime import datetime
import json
import logging
from database.mongo_db_handler import MongoDBHandler
from util.selenium_handler.selenium_services import SeleniumServices
from util.page_handler.detail_page_handler import DetailPageHandler
from util.page_handler.listing_page_handler import ListingPageHandler
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def process_page(selenium_services:SeleniumServices, current_page_url, xpaths):

    mongo_db_handler = MongoDBHandler(xpaths["connection_string"], xpaths["database_name"], xpaths["collection_name"])
    selenium_services.load_url(current_page_url)
    listing_page_handler = ListingPageHandler(current_page_url, xpaths)
    try:
        next_page_url, blocks_data = listing_page_handler.fetch_block_data_selenium_chrome_driver(selenium_services)
        all_data = []

        for block_data in blocks_data:
            details_page_handler = DetailPageHandler(block_data.get("url"), xpaths)
            details_page_data = details_page_handler.scrape_details_page_using_selenium_chromedriver(selenium_services)
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
        return next_page_url
    except Exception as e:
        logging.error(f"Error in process_page: {e}")
        return next_page_url

def main():
    path_to_chromedriver = "C:\\Program Files\\chromedriver-win64\\chromedriver.exe"
    selenium_web_page_scrapper = SeleniumServices(path_to_chromedriver)
    with open("xpaths2.json") as f:
        xpaths = json.load(f)
    source_url = xpaths["source_url"]
    try:
        current_page_url = source_url
        while True:
            logging.info(f"Processing page: {current_page_url}")

            try:
                current_page_url = process_page(selenium_web_page_scrapper, current_page_url, xpaths)
            except Exception as e:
                logging.error(f"Error during pagination: {e}")
                break
    finally:
        selenium_web_page_scrapper.quit_driver()

if __name__ == "__main__":
    main()
