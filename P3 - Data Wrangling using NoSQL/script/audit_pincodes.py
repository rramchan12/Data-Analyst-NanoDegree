#First we will extract the pin codes, and based on the  sampling, we  will put in a logic to extract the errors.


from collections import defaultdict
import xml.etree.cElementTree as ET
import re

def list_zipcode(invalid_zipcode, zipcode, categorized_master_list_zipcodes):
    initial_digits = zipcode[0:2]

    """
    Create an initial set of the expectation and find out outliers
    Ref : https://www.unitedstateszipcodes.org/ny/
            Shows list of valid zip codes for New York
    """
    if not initial_digits.isdigit():
        invalid_zipcode[initial_digits].add(zipcode)

    elif int(initial_digits) not in [10, 11, 12, 13, 14]:
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
                    list_zipcode(invalid_zipcodes, tag.attrib['v'], categorized_master_list_zipcodes)

    return invalid_zipcodes, categorized_master_list_zipcodes


# Most of the data looks correct, and some standardizations can be applied
#
# 1.	Remove the leading NY for all the valid 5 digit codes
# 2. 	Trim the data after the leading '-' or ';' character as it might be non standard information
#
# There is some data which looks incorrect, like zip codes which start with NJ, or codes which start with 07. Since the data itself is incorrect, no standardizations can be applied


def cleanse_invalid_zip_codes(zipcode):
    alpha = re.findall('[a-zA-Z]*', zipcode)
    if alpha:
        first_few_letters = alpha[0]

        if first_few_letters == 'NJ':
            # We wont correct NJ Data
            return zipcode
        else:
            converted_zip_code = re.findall(r'\d+', zipcode)
            if converted_zip_code:
                if converted_zip_code.__len__() > 0:
                    # This is a - seperated code
                    return converted_zip_code[0]
                else:
                    return converted_zip_code
            else:
                # All is well
                return zipcode


if __name__ == '__main__':
    osm_file = 'C:\\python_workspace\\Data-Analyst-NanoDegree\\P3 - Data Wrangling using NoSQL\\new-york_new-york.osm\\ny_extract_osm1.xml'
    invalid_zipcodes, categorized_master_list_zipcodes = filter_invalid_zipcodes(osm_file)
    for zip_category, zip_codes in categorized_master_list_zipcodes.iteritems():
        for zip_code in zip_codes:
            better_code = cleanse_invalid_zip_codes(zip_code)
            print zip_code, "=>", better_code