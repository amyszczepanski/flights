import sqlite3
import json
import time
from geojson import LineString, Feature, FeatureCollection

conn = sqlite3.connect('flights.db')
c = conn.cursor()

myFeatures = []

# Find the offset of the first flight of the "day"
c.execute(" \
SELECT strftime('%s', MIN(DATETIME(observed))) - strftime('%s', MIN(DATE(observed)))  \
AS day_offset \
FROM positions \
WHERE observed >= DATE('NOW', '-1 day'); \
")
dayOffset = c.fetchone()[0]

# Now find the collection of hexcodes for the day
c.execute(" \
SELECT DISTINCT(hexcode) \
FROM positions \
WHERE observed >= DATE('NOW', '-1 day'); \
")
allHexcodes = c.fetchall()

# Make the FeatureList: One feature per hexcode
# Properties: hexcode, start, and finish
# LineString is defined by the coordinates

featureList = []

for hexcode in allHexcodes:
    # getting the properties
    c.execute(" \
    SELECT strftime('%s', MIN(DATETIME(observed))) - strftime('%s', MIN(DATE(observed))) \
    AS start_time, \
    strftime('%s', MAX(DATETIME(observed))) - strftime('%s', MIN(DATE(observed))) \
    AS end_time \
    FROM positions \
    WHERE observed >= DATE('NOW', '-1 day') \
    AND hexcode = ?; \
    ", hexcode)
    start, finish = c.fetchone()
    
    # getting the positions and making the LIST of coordinates
    coordList = []
    c.execute(" \
    SELECT longitude, latitude \
    FROM positions \
    WHERE observed >= DATE('NOW', '-1 day') \
    AND hexcode = ? \
    ORDER BY observed ASC; \
    ", hexcode)
    thePositions = c.fetchall()
    for position in thePositions:
        coordList.append(position)
        
    myLS = LineString(coordList)
    myFeature = Feature(geometry=myLS, 
    properties={"hexcode": hexcode[0], "start": start, "finish": finish})
    featureList.append(myFeature)

myGeoJSON = FeatureCollection(featureList)

# One copy to archive; one copy to be overwritten
timestr = time.strftime("/home/pi/flights/flights_%Y%m%d")
myFilename = timestr + '.json'
with open(myFilename, 'w') as outfile:
    json.dump(myGeoJSON, outfile)
with open('/home/pi/flights/flights_today.json', 'w') as outfile:
    json.dump(myGeoJSON, outfile)

conn.close()