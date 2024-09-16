from lxml import etree

class XMLParser:
    def __init__(self, xml_string):
        self.xml_string = xml_string
        self.tree = None

    def parse(self):
        try:
            self.tree = etree.fromstring(self.xml_string)
        except etree.XMLSyntaxError as e:
            print(f"XML Syntax Error: {e}")
        return self.tree