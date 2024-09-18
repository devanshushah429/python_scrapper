from datetime import datetime
from datetime import datetime
import logging
import json
from database.mongo_db_handler import MongoDBHandler
from util.page_handler.detail_page_handler import DetailPageHandler
from util.page_handler.listing_page_handler import ListingPageHandler

def process_page(page_url, xpaths):
    """
    function processes the page and returns the next page url
    """
    try:
        mongo_db_handler = MongoDBHandler(xpaths["connection_string"], xpaths["database_name"], xpaths["collection_name"])
        listing_page_handler = ListingPageHandler(page_url, xpaths)
        next_page_url, blocks_data = listing_page_handler.fetch_block_data_requests()
        all_data = []   

        for block_data in blocks_data:
            details_page_handler = DetailPageHandler(block_data.get("url"), xpaths)
            details_page_data = details_page_handler.scrape_details_page_using_requests()
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
