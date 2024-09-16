import re
import logging
from lxml import html

class XPathExtractor:
    def __init__(self,tree):
        """
        === Constructor ===
        Gives the html tree structure and sets it
        """
        self.tree = tree
    
    def get_xpath_inner_text(self, xpath):
        """
        Finds the element from the given xpath and then get the inner text.
        """
        try:
            elements = self.tree.xpath(xpath)
            multiple_space_regex = r"\s+"
            replacement = " "
            if elements:
                strings = [element.text_content() for element in elements]
                result_str = " ".join(strings)
                return re.sub(multiple_space_regex, replacement, result_str).strip()
            return None
        except Exception as e:
            logging.error(f"Error in get_xpath_inner_text: {e}")
            return None

    def get_xpath_attribute(self, xpath, attribute):
        """
        Finds the element from the given xpath and then get the attribute value
        """
        try:
            elements = self.tree.xpath(xpath)
            if elements:
                if attribute == "innerHTML":
                    return html.tostring(elements[0], method='html', encoding='unicode')
                return elements[0].get(attribute)
            return None
        except Exception as e:
            logging.error(f"Error in get_xpath_attribute: {e}")
            return None

    def get_multiple_xpath_attribute(self, xpath, attribute):
        """
        Finds elements from the xpath and return the array of the attribute value
        """
        try:
            elements = self.tree.xpath(xpath)
            return [element.get(attribute) for element in elements]
        except Exception as e:
            logging.error(f"Error in get_multiple_xpath_attribute: {e}")
            return None

    def get_multiple_xpath_inner_text(self, xpath):
        """
        Finds elements from the given xpath and then return the array of multiple elements inner text
        """
        try:
            elements = self.tree.xpath(xpath)
            return [re.sub(r"\s+", " ", element.text_content()).strip() for element in elements]
        except Exception as e:
            logging.error(f"Error in get_multiple_xpath_inner_text: {e}")
            return None

    def get_xpath_attribute_from_element(self, element, xpath=None, attribute=None):
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

    def get_xpath_inner_text_from_element(self, element, xpath):
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