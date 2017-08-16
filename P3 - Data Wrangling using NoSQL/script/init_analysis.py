import xml.etree.cElementTree as ET
import pprint
import re


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def count_tags(filename):
    tags = {}
    print filename
    for event,elem in ET.iterparse(filename):
        if elem.tag in tags:
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags


def key_type(element, keys):
    if element.tag == 'tag':
        for val in element.iter('tag'):
            k = element.get('k')
            #search for the "lower"
            if lower.search(k):
                keys['lower'] += 1
            elif lower_colon.search(k):
                keys['lower_colon'] += 1
            elif problemchars.search(k):
                keys['problemchars'] += 1
            else:
                keys['other'] += 1
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys
if __name__ == '__main__':
    osm_file = 'C:\\python_workspace\\Data-Analyst-NanoDegree\\P3 - Data Wrangling using NoSQL\\new-york_new-york.osm\\ny_extract_osm1.xml'
    print '*********************TAG CATEGORIZATION*****************'
    pprint.pprint(count_tags(osm_file))
    print '*****   POSSIBLE PROBLEM CHARS **************'
    pprint.pprint(process_map(osm_file))