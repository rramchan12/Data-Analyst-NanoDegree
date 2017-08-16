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
## Additional Data Exploration ## 
I also did some data exploration using Mongo DB pipelines, to get more insights into the data

#### Top 5 contributors and their respective contributions ####

```
group_user =  { '$group' :  { "_id" : "$created.user", "count"  : {"$sum" : 1}}}

sort = { '$sort': { 'count' : -1}}
limit_to = { '$limit' : 5}

users = collection.aggregate([ group_user,sort,limit_to])
pprint.pprint(list(users))
```
```

[{u'_id': u'Rub21_nycbuildings', u'count': 939868},
 {u'_id': u'smlevine', u'count': 219859},
 {u'_id': u'lxbarth_nycbuildings', u'count': 170573},
 {u'_id': u'minewman', u'count': 141949},
 {u'_id': u'ediyes_nycbuildings', u'count': 118391}]
 
 ```
 
I could see that user *Rub21_nycbuildings* has a disproportianate share of contributions arount *9 Lakhs*. The average for the others was around *1.5 to 2 lakhs*. Its probable that Rub21_nycbuildings is a Buildings Afficionado

#### Top 10 Amenities ####

```
match_amenities = { '$match' : {'amenity' : {'$exists' : True}}}
group_amenities = {'$group' : { '_id' : '$amenity', 'count' : {'$sum' : 1}}}
limit_to = { '$limit' : 10}
amenities = collection.aggregate([match_amenities, group_amenities, sort, limit_to])
pprint.pprint(list(amenities))

```
```
[{u'_id': u'bicycle_parking', u'count': 3408},
 {u'_id': u'restaurant', u'count': 1894},
 {u'_id': u'place_of_worship', u'count': 970},
 {u'_id': u'parking', u'count': 902},
 {u'_id': u'cafe', u'count': 668},
 {u'_id': u'school', u'count': 636},
 {u'_id': u'fast_food', u'count': 467},
 {u'_id': u'bar', u'count': 390},
 {u'_id': u'bicycle_rental', u'count': 388},
 {u'_id': u'bench', u'count': 338}]
 
 ```
The bicycle parkings are much more than any other amenities, which made sense, as I intentionally selected an area near the shore, for the extract. So possibly its  a bicycle friendly area. Restaurants are second in count, which also seems in line with the topography.

#### Top 10 Cuisines ####

```
match_restaurant = { '$match' : {'amenity' : {'$exists' : True}, 'amenity' : 'restaurant'}}
group_cuisine  = { '$group' : { '_id' :  {'Food' : '$cuisine'}, 'count' : {'$sum' : 1}}}
project_food ={'$project' : {'_id' : 0, 'Food' : '$_id.Food', 'foodCount': '$count'}}
sort = { '$sort': { 'foodCount' : -1}}

cuisines = collection.aggregate([match_restaurant,group_cuisine,project_food,sort, limit_to])
pprint.pprint(list(cuisines))
```
```

{u'Food': None, u'foodCount': 710},
 {u'Food': u'italian', u'foodCount': 119},
 {u'Food': u'american', u'foodCount': 92},
 {u'Food': u'pizza', u'foodCount': 87},
 {u'Food': u'mexican', u'foodCount': 86},
 {u'Food': u'chinese', u'foodCount': 62},
 {u'Food': u'japanese', u'foodCount': 56},
 {u'Food': u'thai', u'foodCount': 46},
 {u'Food': u'french', u'foodCount': 43},
 {u'Food': u'indian', u'foodCount': 40} 
 ```
 
 This was a bit dissapointing, as the top cuisine turned out to be the uncategorized ones. This is a data error, and there is scope for correction of the data at source here. 
 
 ## Conclusion ##
 
 The New York Data Set was pretty standard. In spite of having close to `2136` users, who contributed for when we sampled merely 500 MB of data. One thing that struck me was that convention was pretty standardised. Eg Street, Avenue etc. Most of the errors were just human errors. These can be weeded at source by introducing data entry Validations. One way to do that is to use a Web Form, which validates against these standard conventions. That way we have a standardised data set.
 
 ### Challenges ###
This approach would not work if the street names itself were not standardised. For a lot of countries, this is true. Addresses in  India, do not follow a specific pattern. Eg Lane, Avenue, Street might not even figure in the address set. There will be some elements which are present eg Landmark, State, City and Zip Code, but there will not be standard definitions of the same. 
We should first try to standardise the mandatory elements, for such data sets. Lets take the case of Landmark
Using ML Algorithsm, Based on a large number of croudsourced addresses, we can define a set of pivot points, which are landmarks. We will standardize the definitions of these Landmarks, which are  and prepopulated in the web forms, and manual entry is not allowed . Thus an accurate description of the same, in standard terms can be input in all the addresses. The same approach can then be extended to all the non standard fields, by scaling the algorithm.
 
