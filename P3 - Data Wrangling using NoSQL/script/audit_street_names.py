# So 2174 users have contributed to the map data. This is a good number to start.

# ### Step 3: Data Cleansing

# ### 3.1 Eliminating Variation in Street Names
#
#

# This is local data set, from the Asia Region. So the standard correction algorithm will not work. First we will find the various street names, based on this we will decide the approach to eliminate variation.

# In[16]:
from collections import defaultdict
import re
import xml.etree.cElementTree as ET
import pprint


street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = {}


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def get_street_names(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    value = tag.attrib['v']
                    m = street_type_re.search(value)
                    if m:
                        street_type = m.group()
                        street_types[street_type].add(value)

    return street_types

# We can now define a prelimnary mapping file. Do note that, there are a number of non standard names in the street names list. These will not be corrected, but the mapping file will work for all the standard names, where there are variations

# In[14]:

mapping = {'Ave': 'Avenue',
           'ave': 'Avenue',
           'Blvd': 'Boulevard',
           'Dr': 'Drive',
           'Ln': 'Lane',
           'Pkwy': 'Parkway',
           'Rd': 'Road',
           'Rd.': 'Road',
           'St': 'Street',
           'St.': 'Street',
           'ST': 'Street',
           'street': "Street",
           'Ct': "Court",
           'Cir': "Circle",
           'Cr': "Court",
           'ave': 'Avenue',
           'Hwg': 'Highway',
           'Hwy': 'Highway',
           'Sq': "Square",
           "Steet" : "Street",
           'steet' : 'Street',
           'st'   : 'Street'}


# In[20]:

def update_street_name(name, mapping):
    m = street_type_re.search(name)
    better_name = name

    if m:
        if m.group() in mapping.keys():
            better_street_type = mapping[m.group()]
            better_name = street_type_re.sub(better_street_type, name)

    return better_name



if __name__ == '__main__':
    osm_file = 'C:\\python_workspace\\Data-Analyst-NanoDegree\\P3 - Data Wrangling using NoSQL\\new-york_new-york.osm\\ny_extract_osm1.xml'
    street_types = get_street_names(osm_file)
    street_types.keys()
    print '**************************MODIFIED STREET NAMES**************************'
    for street_type, ways in street_types.iteritems():
        for name in ways:
            better_name = update_street_name(name, mapping)
            print name, "=>", better_name




