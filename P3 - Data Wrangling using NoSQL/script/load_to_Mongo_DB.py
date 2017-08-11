# Load Data into MongoDB and Insights

# ### 4.1 We will first convert the xml to a Json.

# For the purpose we can use the code that we prepared in the case study, where we had the below rules:
#
# -	you should process only 2 types of top level tags: "node" and "way"
# -	all attributes of "node" and "way" should be turned into regular key/value pairs, except:
# -	attributes in the CREATED array should be added under a key "created"
# -	attributes for latitude and longitude should be added to a "pos" array, for use in geospacial indexing. Make sure the values inside "pos" array are floats and not strings.
# -	if the second level tag "k" value contains problematic characters, it should be ignored
# -	if the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
# -	if the second level tag "k" value does not start with "addr:", but contains ":", you can process it in a way that you feel is best. For example, you might split it into a two-level dictionary like with "addr:", or otherwise convert the ":" to create a valid key.
# -	if there is a second ":" that separates the type/direction of a street, the tag should be ignored


import codecs
import xml.etree.cElementTree as ET
import pprint
import json
import re

from audit_street_names import update_street_name, mapping
from audit_pincodes import cleanse_invalid_zip_codes

from pymongo import MongoClient

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way":

        node['id'] = element.attrib['id']
        node['type'] = element.tag
        node['visible'] = element.get('visible')
        created = dict()
        created['version'] = element.attrib['version']
        created['changeset'] = element.attrib['changeset']
        created['timestamp'] = element.attrib['timestamp']
        created['user'] = element.attrib['user']
        created['uid'] = element.attrib['uid']
        node['created'] = created
        if "lat" in element.keys() and 'lon' in element.keys():
            pos = []
            pos.append(float(element.attrib['lat']))
            pos.append(float(element.attrib['lon']))
            node['pos'] = pos
        else:
            node['pos'] = None
        addr = {}
        for tag in element.iter("tag"):
            tag_name = tag.attrib['k']

            tag_value = tag.attrib['v']
            if problemchars.search(tag_name):
                # skip the problem chars
                continue
            if 'addr' in tag_name:
                add_key = tag_name.split(':', 1)[1]
                if add_key =='housenumber':
                    addr[add_key] = tag_value
                if add_key == 'street':
                    better_name = update_street_name(tag_value,mapping)
                    addr[add_key] = better_name
                if add_key == 'postcode':
                    better_zipcode = cleanse_invalid_zip_codes(tag_value)
                    addr[add_key] = better_zipcode
            elif tag_name == "name":
                node['name'] = tag_value
            elif tag_name == 'phone':
                node['phone'] = tag_value
            elif tag_name == 'amenity':
                node['amenity'] = tag_value
            elif tag_name == 'cuisine':
                node['cuisine'] = tag_value
            node['address'] = addr

        return node
    else:
        return None


# In[23]:

def process_map(file_in, pretty=False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2) + "\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


def load_to_Mongo(data):
    client = MongoClient("mongodb://localhost:27017")
    db = client.NewYorkOSMDB
    db.drop
    collection = db.NewYorkMap
    # remove any stale data if its present
    db.NewYorkMap.drop()
    # insert the json Map
    collection.insert_many(data)
    print db.NewYorkMap.find_one()
    client.close()

if __name__ == '__main__':
    osm_file = 'C:\\python_workspace\\Data-Analyst-NanoDegree\\P3 - Data Wrangling using NoSQL\\new-york_new-york.osm\\ny_extract_osm1.xml'
    data = process_map(osm_file)
    for i in range(10):
        pprint.pprint(data[i])
    load_to_Mongo(data)