from datetime import datetime
from datetime import datetime
import logging
import json
from util.lxml_handler.html_parser import HTMLParser
from util.lxml_handler.xpath_extractor import XPathExtractor
from util.requests_handler.web_page_fetcher import WebPageFetcher
from database.mongo_db_handler import MongoDBHandler
from util.page_handler.requests.detail_page_handler import DetailPageHandler

def fetch_block_data(page_url, xpaths):
    try:
        tree = HTMLParser(WebPageFetcher(page_url).get_page_source_by_url_using_requests()).parse()
        block_xpath = xpaths["block_xpath"]
        xpath_extractor = XPathExtractor(tree)
        elements = xpath_extractor.get_elements_using_xpath(block_xpath)
        try:
            next_page_url = xpath_extractor.get_xpath_attribute(xpaths["next_button_xpath"], "href")
        except:
            next_page_url = None
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
            
        return (next_page_url, blocks_data)
    except Exception as e:
        logging.error(f"Error in fetch_block_data: {e}")
        return ()

def process_page(page_url, xpaths):
    """
    function processes the page and returns the next page url
    """
    try:
        mongo_db_handler = MongoDBHandler(xpaths["connection_string"], xpaths["database_name"], xpaths["collection_name"])
        next_page_url, blocks_data = fetch_block_data(page_url, xpaths)
        all_data = []

        for block_data in blocks_data:
            details_page_handler = DetailPageHandler(block_data.get("url"), xpaths)
            details_page_data = details_page_handler.scrape_details_page()
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
        return next_page_url
    except Exception as e:
        logging.error(f"Error in process_page: {e}")
        return next_page_url

def main():
    
    with open("xpaths.json") as f:
        xpaths = json.load(f)

    source_url = xpaths["source_url"]
    
    try:
        current_page_url = source_url
        while True:
            logging.info(f"Processing page: {current_page_url}")

            try:
                current_page_url = process_page(current_page_url, xpaths)
            except Exception as e:
                logging.error(f"Error during pagination: {e}")
                break
            
    finally:
        pass

if __name__ == "__main__":
    main()
