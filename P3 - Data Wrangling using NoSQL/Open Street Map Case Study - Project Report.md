# OpenStreetMap Data Case Study

### Map Area
New York, New York, United States

New York with its combination of land and water areas, provided a good diversity which I was interested in exploring. Also wanted to check what contributions I could plough back to OpenStreetMap.org

[http://overpass-api.de/api/map?bbox=40.6192000,-74.1783000,40.7629000,-73.9201000](http://overpass-api.de/api/map?bbox=40.6192000,-74.1783000,40.7629000,-73.9201000)

<bounds minlat="40.6192000" minlon="-74.1783000" maxlat="40.7629000" maxlon="-73.9201000"/>


## Problems Encountered in the Map

After downloading the dataset and creating a sample, I found the following 2 problems which I will discuss below 

- Over Abbreviated or Inconsistent Street Names
- Inconsistent Zip Codes


### Over abbreviated or Inconsistent Street Names

On parsing the raw xml file, I found inconsistencies in the various Street Names like *Steinway street* , *Washington Ave.*. By applying the correction algorithm in [audit_street_names.py](https://github.com/rramchan12/Data-Analyst-NanoDegree/blob/master/P3%20-%20Data%20Wrangling%20using%20NoSQL/script/audit_street_names.py), I was able to update these names to actual abbreviations like *Steinway Street* and *Washington Avenue*

### Inconsistent Zip Codes

I also saw that there were inconsitent zip codes like *NY 10111*, *07030-5774*. By applying the correctin algorithm in [audit_pincodes.py](https://github.com/rramchan12/Data-Analyst-NanoDegree/blob/master/P3%20-%20Data%20Wrangling%20using%20NoSQL/script/audit_pincodes.py), I corrected these to be more consistent *(10111 and 07030)*

