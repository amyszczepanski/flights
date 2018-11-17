# flights 
tracking local flights with my piaware

Here's an explanation of how I made this. If you want to use this with your own 
[piaware](https://flightaware.com/adsb/), you'll need to change various things 
that I've hardcoded (such as the longitude/latitude bounding box for San Diego 
County, etc.). This comes in two parts: The scripts that run on the piaware to 
collect and organize the data, and the web page that displays the data.

There is a Python script that reads the information that comes out of dump1090 and
saves some of it in a sqlite3 database. There is another Python script that reads
from the database every day and converts the data into GeoJSON. Every day the new
data is transfered to an AWS S3 bucket. In the S3 bucket, I also have GeoJSON files
describing the geography of San Diego County and an HTML file that uses d3.js to
visualize the paths of the planes.

Since San Diego has so many planes coming to the airport (and since my piaware lives
about 3 miles from the airport), I'm only looking at planes that are reporting altitudes
over 25,000 feet.

# Collecting the data from the piaware

First I needed to upgrade and install some software.

## Things that I had to install on the piaware
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install sqlite3
sudo apt-get install python-pip
sudo pip install geojson
sudo apt-get install git
pip install awscli --upgrade --user
```

## Creating the sqlite3 database flights.db

I save the data in a sqlite3 database that I've named flights.db. The path to my
database is hard-coded in my two Python scripts.

```
CREATE TABLE positions (
    observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    hexcode VARCHAR(6),
    altitude INTEGER,
    latitude NUMERIC,
    longitude NUMERIC,
    );
```

## Setting up AWS CLI

Using IAM, I set up a user with programmatic access to my S3 bucket. This way I don't
need to save the secret credentials in any of my scripts.

```
aws configure
```

## Getting everything running on the piaware

The script `flights.py` is sort of pretending that it is a daemon. I launched it with
`nohup python flights.py &`. Every now and then I check to see if it's still running.

I set a cron that runs `parse.py` every morning at 5am. I also set a cron to run the
AWS command line tool to copy `flights_today.json` to my S3 bucket every morning at
6am.

# Displaying the data on the web

I used [d3.js](https://d3js.org) to display the paths of the flights. I got the geography
of San Diego County from the US Census and then used 
[ogr2ogr](https://www.gdal.org/ogr2ogr.html) to convert the shapefiles to GeoJSON.