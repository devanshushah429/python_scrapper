from util.lxml_handler.xpath_extractor import XPathExtractor
from util.requests_handler.web_page_fetcher import WebPageFetcher
from util.lxml_handler.html_parser import HTMLParser
from util.selenium_handler.selenium_web_page_scrapper import SeleniumWebPageScrapper

class ListingPageHandler:
    def __init__(self, page_url, xpaths):
        self.page_url = page_url
        self.xpaths = xpaths

    def fetch_block_data_requests(self):
        try:
            self.tree = HTMLParser(WebPageFetcher(self.page_url).get_page_source_by_url_using_requests()).parse()
            next_page_url, blocks_data = self.fetch_block_data()
            return (next_page_url, blocks_data)
        except Exception as e:
            print(f"Error in fetch_block_data: {e}")
            return ()

    def fetch_block_data_selenium_chrome_driver(self, selenium_web_page_scraper:SeleniumWebPageScrapper):
        try:
            selenium_web_page_scraper.load_url(self.page_url)
            self.tree = HTMLParser(selenium_web_page_scraper.get_page_source()).parse()
            next_page_url, blocks_data = self.fetch_block_data()
            return next_page_url, blocks_data
        except Exception as e:
            print(f"Error in fetch_block_data: {e}")
            return []

    def fetch_block_data(self):
        block_xpath = self.xpaths["block_xpath"]
        xpath_extractor = XPathExtractor(self.tree)
        elements = xpath_extractor.get_elements_using_xpath(block_xpath)
        try:
            next_page_url = xpath_extractor.get_xpath_attribute(self.xpaths["next_button_xpath"], "href")
        except:
            next_page_url = None
        blocks_data = []
        for element in elements:
            try:
                block_details = {"page_url": self.page_url}
                for key, value in self.xpaths["block_details"]["inner_text_xpath_dictionary"].items():
                    block_details[key] = xpath_extractor.get_xpath_inner_text_from_element(element, value)
                for key, value in self.xpaths["block_details"]["attribute_dictionary"].items():
                    if key == "url":
                        block_details[key] = self.xpaths["base_url"] + xpath_extractor.get_xpath_attribute_from_element(element, value[0], value[1])
                    else:
                        block_details[key] = xpath_extractor.get_xpath_attribute_from_element(element, value[0], value[1])
                blocks_data.append(block_details)
            except Exception as e:
                print(f"Error processing block data: {e}")
                continue
        return next_page_url, blocks_data

