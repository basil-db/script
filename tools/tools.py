import xml.etree.ElementTree as ET
import re

def get_PM_info(string, ids):
    tree = ET.ElementTree(ET.fromstring(string))
    root = tree.getroot()
    titles = []
    abstracts = []
    years = []
    for title in root.iter('ArticleTitle'):
        titles.append(title.text)
    for abstract in root.iter('Abstract'):
        for element in list(abstract.iter()):
            if element.tag == 'AbstractText':
                abstracts.append(''.join(element.itertext()))
    for year in root.iter('DateRevised'):
        for x in year:
            if x.tag == 'Year':
                years.append(int(x.text))

    ptype = []
    for types in root.iter('PublicationTypeList'):
        typelist = []
        for type in types.findall('PublicationType'):
            typelist.append(type.text)
        ptype.append(typelist)

    abstracts = ["".join(abstracts)]

    return list(zip(*[ids, titles, abstracts, years, ptype]))

def is_simple_name(name):
    # The pattern assumes that complex names have more than 4 digits or special characters
    pattern = r'[^a-zA-Z\s-]'
    matches = re.findall(pattern, name)
    return len(matches) <= 4