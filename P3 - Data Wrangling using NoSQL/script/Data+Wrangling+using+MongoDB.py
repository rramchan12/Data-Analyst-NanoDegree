
# coding: utf-8

# ## Wrangling Open Street Map Data using Python and MongoDB

# ### Details of the Area 

# 1. Location : A small subsection of New York Central, with Water Bodies
# 2. Motivation :  I have never been to New York, but its the subject of many movies. I wanted to understand the topography, and see it through the eyes of an analyst
# 3. DataSet : ny_extract_osm1.xml [link](link)

# ## Objective

# You will choose any area of the world in https://www.openstreetmap.org and use data munging techniques, such as assessing the quality of the data for validity, accuracy, completeness, consistency and uniformity, to clean the OpenStreetMap data for a part of the world that you care about. Finally, you will choose either MongoDB or SQL as the data schema to complete your project.

# ## Reference :

# 1. Udacity "Data Wrangling Using Mongo DB" (Lesson 6)
# 2. Mongo DB Docs 

# ## Steps  : 

# 1. Data Download
# 2. Data Audit
# 3. Data Cleansing/Problem Resolution
# 4. Load Data into MongoDB and Insights 
# 5. Conclusion

# ### Step 1: Data Download

# ### 1.1 Extracting using Python 

# I can extract using the Overpass API using the Co-ordinates that are specified in the code below

# In[1]:

"""I am doing this using the  Browser, and so have commented out this code"""
import urllib
#for the Overpass API Git
#file00 = urllib.URLopener()
#file00.retrieve("http://overpass-api.de/api/map? bbox=77.3901,12.8620,77.7973,13.0815", "P3 - Data Wrangling using NoSQL/new-york_new-york.osm/ny_extract_osm.xml""


# I can also download the predefined extract using MapZen, which can be downloaded using a link
# [https://mapzen.com/data/metro-extracts/metro/bengaluru_india](https://mapzen.com/data/metro-extracts/metro/bengaluru_india/)
# The downloaded data is available in this project itself

# In[72]:

#Imports Master

import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import collections
import pymongo
from pymongo import MongoClient
import os


# In[73]:

#File Master

#osm_file = "P3 - Data Wrangling using NoSQL/bengaluru_india.osm/bengaluru_india.osm"
osm_file = "P3 - Data Wrangling using NoSQL/new-york_new-york.osm/ny_extract_osm1.xml"
os.path.exists(osm_file)


# In[74]:

print 'The size of the OSM file is {}'.format(os.path.getsize(osm_file)/1.0e6)


# ### Step 2 : Data Audit

# 2.1 Count the No of Nodes, Ways, Relations

# In[ ]:

#Using Lesson 6 Will count the no of tags

def count_tags(filename):
    tags = {}
    print filename
    for event,elem in ET.iterparse(filename):
        if elem.tag in tags:
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags
count_tags(osm_file)


# ### 2.2 Create a small sample file, to look at the Output, to Analyse the tags

# In[ ]:

#Print a sample of the OSM File
#Code sample based on Quiz of Data Wrangling using MongoDB

# Print a sample of the file. Here I am printing the first 100 elements

OSM_FILE = osm_file  # Replace this with your osm file
SAMPLE_FILE = "sample.osm"

k = 100 # Parameter: print the first k elements (or every kth element)

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


# print the first  k top level elements
for i, element in enumerate(get_element(OSM_FILE)):
    if i <= k:
        print ET.tostring(element)
'''
# or print every  kth top level elements
for i, element in enumerate(get_element(OSM_FILE)):
    if i % k == 0:
        print ET.tostring(element)
'''
# Also writing the sample file to view it in Sublime text
with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')


# 2.3 Getting any Problem Chars in K, V pairs

# We will iterate over all the data, and for any K, V we will check if the value has only lower, or lower with a : or any other characters. This will help us determine if any data cleansing is required for this data
# 
# We will take a count of this, which we will display below

# import re
# 
# lower = re.compile(r'^([a-z]|_)*$')
# lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
# problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
# 
# def key_type(element, keys):
#     if element.tag == 'tag':
#         for val in element.iter('tag'):
#             k = element.get('k')
#             #search for the "lower"
#             if lower.search(k):
#                 keys['lower'] += 1
#             elif lower_colon.search(k):
#                 keys['lower_colon'] += 1
#             elif problemchars.search(k):
#                 keys['problemchars'] += 1
#             else:
#                 keys['other'] += 1
#     return keys
# 
# def process_map(filename):
#     keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
#     for _, element in ET.iterparse(filename):
#         keys = key_type(element, keys)
# 
#     return keys

# In[9]:

import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

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


# In[10]:

sc_tag_category = process_map(osm_file)
pprint.pprint(sc_tag_category)


# ### 2.4 Count of Users

# We will get a count of the users, who have updated. This will give us an idea, of how active this section is, and how much variation we can expect on the data.

# In[11]:

# this function will tell us how many unique users have already contributed to the map data

def get_user(element):
    if element.get('uid'):
        uid = element.attrib['uid']
        return uid
    else:
        return None
    
    

def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if get_user(element):
            users.add(get_user(element))

    return users

contributing_users = process_map(osm_file)
len(contributing_users)


# So 2174 users have contributed to the map data. This is a good number to start.

# ### Step 3: Data Cleansing

# ### 3.1 Eliminating Variation in Street Names
# 
# 

# This is local data set, from the Asia Region. So the standard correction algorithm will not work. First we will find the various street names, based on this we will decide the approach to eliminate variation.

# In[16]:

from collections import defaultdict
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

street_types = get_street_names(osm_file)
street_types.keys()


# We can now define a prelimnary mapping file. Do note that, there are a number of non standard names in the street names list. These will not be corrected, but the mapping file will work for all the standard names, where there are variations

# In[14]:

mapping = {'Ave'  : 'Avenue',
           'ave'  : 'Avenue',
           'Blvd' : 'Boulevard',
           'Dr'   : 'Drive',
           'Ln'   : 'Lane',
           'Pkwy' : 'Parkway',
           'Rd'   : 'Road',
           'Rd.'   : 'Road',
           'St'   : 'Street',
           'ST'   : 'Street',
           'street' :"Street",
           'Ct'   : "Court",
           'Cir'  : "Circle",
           'Cr'   : "Court",
           'ave'  : 'Avenue',
           'Hwg'  : 'Highway',
           'Hwy'  : 'Highway',
           'Sq'   : "Square"}


# In[20]:

def update_street_name(name, mapping):

    m = street_type_re.search(name)
    better_name = name
    
    if m:
        if m.group() in mapping.keys():
            better_street_type = mapping[m.group()]
            better_name = street_type_re.sub(better_street_type,name)
            
    return better_name

print '**************************MODIFIED STREET NAMES**************************'
for street_type, ways in street_types.iteritems():
    for name in ways:
        better_name = update_street_name(name, mapping)
        print name, "=>", better_name


# ### 3.2 Eliminating Erroneus Pin Codes

# First we will extract the pin codes, and based on the sampling, we will put in a logic to extract the errors. 

# In[33]:

from collections import defaultdict

def list_zipcode(invalid_zipcode,zipcode, categorized_master_list_zipcodes):
    initial_digits = zipcode[0:2]   
    
    """
    Create an initial set of the expectation and find out outliers
    Ref : https://www.unitedstateszipcodes.org/ny/
            Shows list of valid zip codes for New York
    """
    if not initial_digits.isdigit():
        invalid_zipcode[initial_digits].add(zipcode)   
    
    elif int(initial_digits) not in [10,11,12,13,14]:
        invalid_zipcode[initial_digits].add(zipcode)
   
    categorized_master_list_zipcodes[initial_digits].add(zipcode)
        
def is_zipcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def filter_invalid_zipcodes(osmfile):
    osm_file = open(osmfile, "r")
    invalid_zipcodes = defaultdict(set)
    categorized_master_list_zipcodes = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zipcode(tag):
                    list_zipcode(invalid_zipcodes,tag.attrib['v'], categorized_master_list_zipcodes)

    return invalid_zipcodes, categorized_master_list_zipcodes

invalid_zipcodes, categorized_master_list_zipcodes = filter_invalid_zipcodes(osm_file)


# Most of the data looks correct, and some standardizations can be applied
# 
# 1.	Remove the leading NY for all the valid 5 digit codes
# 2. 	Trim the data after the leading '-' or ';' character as it might be non standard information
# 
# There is some data which looks incorrect, like zip codes which start with NJ, or codes which start with 07. Since the data itself is incorrect, no standardizations can be applied

# In[41]:

def cleanse_invalid_zip_codes(zipcode):           
    alpha = re.findall('[a-zA-Z]*', zipcode)
    if alpha:
        first_few_letters = alpha[0]
        
        if first_few_letters == 'NJ':
            #We wont correct NJ Data
            return zip_code
        else:
            converted_zip_code = re.findall(r'\d+',zip_code)            
            if converted_zip_code:
                if converted_zip_code.__len__() > 0:
                    #This is a - seperated code
                    return converted_zip_code[0]
                else:
                    return converted_zip_code
            else:
                #All is well
                return zip_code

for zip_category, zip_codes in categorized_master_list_zipcodes.iteritems():
    for zip_code in zip_codes:
        better_code = cleanse_invalid_zip_codes(zip_code)
        print zip_code, "=>", better_code


# ### Step 4 : Load Data into MongoDB and Insights

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

# In[22]:

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way":
        # YOUR CODE HERE
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
                #skip the problem chars
                continue
            if 'addr'in tag_name:
                add_key = tag_name.split(':',1)[1]
                if add_key in ('housenumber', 'street'):
                    addr[add_key] = tag_value
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


# In[24]:

#osm_file = 'sample.osm'
data = process_map(osm_file)

for i in range(10):
    pprint.pprint(data[i])


# ### 4.2 Inserting Data into Mongo

# In[25]:

client = MongoClient("mongodb://localhost:27017")

db  = client.NewYorkOSMDB
db.drop
collection = db.NewYorkMap
#remove any stale data if its present
db.NewYorkMap.drop()
#insert the json Map
collection.insert_many(data)

print db.NewYorkMap.find_one()


# In[19]:

collection


# Compute relative sizes

# In[26]:

print 'The JSON File size is {} MB'.format(os.path.getsize(osm_file+'.json')/1.0e6) #1.0e6 is used to convert the bits to bytes


# This is bit more to the original file size ie  511.26328 MB, due to the descriptive JSON format. Without doubt the entire Map is loaded

# ### 4.3 Generating Insights using MongoDB Pipelines

# In[40]:

all = collection.find()
print 'There are totally {} records in the New York Map Collection'.format(all.count())

print 'There are {} unique contributors '.format(len(collection.distinct('created.user')))


# In[46]:

print "The are {} Nodes in this data set".format(collection.find({'type': 'node'}).count())
print "There are {} Ways in this data set".format(collection.find({'type': 'way'}).count())


# ### Pipeline : Top 5 contributors

# In[59]:

group_user =  { '$group' :  { "_id" : "$created.user", "count"  : {"$sum" : 1}}}

sort = { '$sort': { 'count' : -1}}
limit_to = { '$limit' : 5}

users = collection.aggregate([ group_user,sort,limit_to])

pprint.pprint(list(users))


# ### Pipeline : Top 10 Amenities

# In[64]:

match_amenities = { '$match' : {'amenity' : {'$exists' : True}}}
group_amenities = {'$group' : { '_id' : '$amenity', 'count' : {'$sum' : 1}}}
limit_to = { '$limit' : 10}
amenities = collection.aggregate([match_amenities, group_amenities, sort, limit_to])
pprint.pprint(list(amenities))


# ### Pipeline : Top 10 Cuisines of Restaurants in NY

# In[70]:

match_restaurant = { '$match' : {'amenity' : {'$exists' : True}, 'amenity' : 'restaurant'}}
group_cuisine  = { '$group' : { '_id' :  {'Food' : '$cuisine'}, 'count' : {'$sum' : 1}}}
project_food ={'$project' : {'_id' : 0, 'Food' : '$_id.Food', 'foodCount': '$count'}}
sort = { '$sort': { 'foodCount' : -1}}

cuisines = collection.aggregate([match_restaurant,group_cuisine,project_food,sort, limit_to])
pprint.pprint(list(cuisines))


# ### Step 5 : Conclusion

# The map extract of New York, showed a large number of unique users (2136). The top 5 contributers made on the average of 1 Lakh edits (discounting the topmost contributor who made around **9 lakh** edits), which shows that the user are also active. 
# This is reflected in the number of **19 lakh** nodes, **3 lakh** ways in a 500 MB data set.

# ### Improvement Areas

# I initially started with a dataset of my area of residence (Bangalore), which can be seen when looked via the git history. However I soon realised that the data is very sparse, and also not using any specific conventions. 
# In contrast I found the NY Dataset using a set of standard conventions. Such standard conventions are not available in India. If a web based form can be provided, to ensure the conventions are followed, the need for data cleansing would become limited, and can be easily automated. 
# At some other places, data was totally incorrect(eg zip codes). This I could infer, and a basic geo spacific validator can be plugged in, to eliminate the errors at source

# In[ ]:



