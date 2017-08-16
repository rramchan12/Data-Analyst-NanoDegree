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

 

# Data Overview

I then corrected, and converted the data to JSON documents. The attached [sample.osm](https://github.com/rramchan12/Data-Analyst-NanoDegree/blob/master/P3%20-%20Data%20Wrangling%20using%20NoSQL/new-york_new-york.osm/sample.osm) gives an overview of the first hundred nodes on the data set. Running the script for the attached sample gave me the converted [sample.osm.json](https://github.com/rramchan12/Data-Analyst-NanoDegree/blob/master/P3%20-%20Data%20Wrangling%20using%20NoSQL/new-york_new-york.osm/sample.osm.json)

On running this on the original data set, I observed that the original data size of the data was *500 MB*. After conversion of JSON, this data had a size of *520 MB*. I then loaded all this data into MongoDB. The conversion, correction and load scripts are defined the script file [load_to_mongo_db.py](https://github.com/rramchan12/Data-Analyst-NanoDegree/blob/master/P3%20-%20Data%20Wrangling%20using%20NoSQL/script/load_to_Mongo_DB.py). 

## Summary Statistics of the Data Set
Below I am presenting a basic summary of the data set, along with relevant code snippets. More detailed code and explanations are refrenced in  [Data_Wrangling_using_MongoDB.ipynb](https://github.com/rramchan12/Data-Analyst-NanoDegree/blob/master/P3%20-%20Data%20Wrangling%20using%20NoSQL/Data%20Wrangling%20using%20MongoDB.ipynb)

#### No of Records : 2271746 ####
```
len(collection.find())
```

#### No of Nodes : 1925728  ####

```
collection.find({'type': 'node'}).count()
```

#### No of Ways : 346018 ####

```
collection.find({'type': 'way'}).count()
```
#### No of Unique Users in this dataset : 2136 ####

```
len(collection.distinct('created.user')
```
## Data Exploration ## 
I also did some data exploration using Mongo DB pipelines, to get more insights into the data

#### Top 5 contributors to this extract ####

```
group_user =  { '$group' :  { "_id" : "$created.user", "count"  : {"$sum" : 1}}}

sort = { '$sort': { 'count' : -1}}
limit_to = { '$limit' : 5}

users = collection.aggregate([ group_user,sort,limit_to])

pprint.pprint(list(users))
[{u'_id': u'Rub21_nycbuildings', u'count': 939868},
 {u'_id': u'smlevine', u'count': 219859},
 {u'_id': u'lxbarth_nycbuildings', u'count': 170573},
 {u'_id': u'minewman', u'count': 141949},
 {u'_id': u'ediyes_nycbuildings', u'count': 118391}]
 
 ```
 
I could see that user *Rub21_nycbuildings* has a disproportianate share of contributions arount *9 Lakhs*. The average for the others was around *1.5 to 2 lakhs*. Its probable that Rub21_nycbuildings is a Buildings Afficionado

