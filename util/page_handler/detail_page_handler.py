from util.lxml_handler.xpath_extractor import XPathExtractor
from util.requests_handler.requests_services import RequestsServices
from util.lxml_handler.html_parser import HTMLParser
from util.selenium_handler.selenium_services import SeleniumServices
from selenium.webdriver.support.ui import WebDriverWait

class DetailPageHandler:
    def __init__(self, url, xpaths):
        self.url = url
        self.xpaths = xpaths

    def scrape_details_page_using_requests(self):
        """This function uses requests to get the page source. And then get the details accordingly with xpaths."""
        try:
            self.page_source = RequestsServices(self.url).get_page_source_by_url_using_requests()
            if self.page_source is None:
                return {}
            return self.scrape_page_details()
        except Exception as e:
            print(f"Error in scrape_details_page: {e}")
            return {}

    def scrape_details_page_using_selenium_chromedriver(self,selenium_services:SeleniumServices):
        """"This function uses selenium to get the page source. And then get the details accordingly with xpaths."""
        try:
            selenium_services.load_url(self.url)
            WebDriverWait(selenium_services.driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            self.page_source = selenium_services.get_page_source()
            if self.page_source is None:
                return {}
            return self.scrape_page_details()
        except Exception as e:
            print(f"Error in scrape_details_page: {e}")
            return {}
        
    def scrape_page_details(self):
        try:
            tree = HTMLParser(self.page_source).parse()
            details_data = {}
            xpath_extractor = XPathExtractor(tree)

            for key, xpath in self.xpaths["details_page"]["inner_text_xpath_dictionary"].items():
                details_data[key] = xpath_extractor.get_xpath_inner_text(xpath)

            for key, (xpath, attribute) in self.xpaths["details_page"]["attribute_dictionary"].items():
                details_data[key] = xpath_extractor.get_xpath_attribute(xpath, attribute)

            for key, (xpath, attribute) in self.xpaths["details_page"]["multile_attribute_dictionary"].items():
                details_data[key] = xpath_extractor.get_multiple_xpath_attribute(xpath, attribute)

            for key, xpath in self.xpaths["details_page"]["multiple_inner_text_dictionary"].items():
                details_data[key] = xpath_extractor.get_multiple_xpath_inner_text(xpath)
            return details_data
        except Exception as e:
            print("Exception e" +{e})
            return  {}
