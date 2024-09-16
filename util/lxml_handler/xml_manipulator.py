from lxml import etree

class XMLManipulator:
    def __init__(self, tree):
        self.tree = tree

    def get_elements_by_tag(self, tag):
        return self.tree.findall(tag)

    def add_element(self, parent_tag, new_element_tag, text=''):
        parent = self.tree.find(parent_tag)
        if parent is not None:
            new_element = etree.Element(new_element_tag)
            new_element.text = text
            parent.append(new_element)
        else:
            print(f"Parent tag '{parent_tag}' not found")

    def to_string(self):
        return etree.tostring(self.tree, pretty_print=True).decode()
