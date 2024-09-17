from lxml import html

class HTMLParser:
    def __init__(self, html_string):
        """
        Takes the string from and parse it to the tree and then  add
        """
        self.html_string = html_string
        try:
            self.tree = html.fromstring(self.html_string)
        except Exception as e:
            self.tree = None
            print(f"Exception occured while parseing html_string {e}")

    def parse(self):
        """
        Parse the String to HTML
        """
        try:
            return self.tree
        except Exception as e:
            print(f"XML Syntax Error: {e}")