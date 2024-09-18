from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

class SeleniumServices:
    def __init__(self, path_to_chromedriver):
        self.path_to_chromedriver = path_to_chromedriver
        self.set_driver_headless()

    def set_driver_headless(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(self.path_to_chromedriver)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
    
    def load_url(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

    def get_page_source(self):
        return self.driver.page_source
    
    def quit_driver(self):
        self.driver.quit()
    
    def get_current_url(self):
        return self.driver.current_url