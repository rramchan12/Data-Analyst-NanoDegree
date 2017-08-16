#Print a sample of the OSM File
#Code sample based on Quiz of Data Wrangling using MongoDB

# Print a sample of the file. Here I am printing the first 100 elements



import xml.etree.cElementTree as ET


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
def printNElements(k):
    k =10
    for i, element in enumerate(get_element(OSM_FILE)):
        if i <= k:
            print ET.tostring(element)
    '''
    # or print every  kth top level elements
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            print ET.tostring(element)
    '''
    return None


# Also writing the sample file to view it in Sublime text
# Parameter: print the first k elements (or every kth element)


def createSampleFile(k, OSM_FILE, SAMPLE_FILE):
    with open(SAMPLE_FILE, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ')

        # Write every kth top level element
        for i, element in enumerate(get_element(OSM_FILE)):
            if i % k == 0:
                output.write(ET.tostring(element, encoding='utf-8'))

        output.write('</osm>')
        return None


if __name__ == '__main__':
    sample_file = 'C:\\python_workspace\\Data-Analyst-NanoDegree\\P3 - Data Wrangling using NoSQL\\new-york_new-york.osm\\sample1.osm'
    osm_file = 'C:\\python_workspace\\Data-Analyst-NanoDegree\\P3 - Data Wrangling using NoSQL\\new-york_new-york.osm\\ny_extract_osm1.xml'
    createSampleFile(100, osm_file, sample_file)
