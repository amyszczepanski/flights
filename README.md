# flights 
tracking local flights with my piaware

Currently these are notes to myself.

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
```
CREATE TABLE positions (
    observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    hexcode VARCHAR(6),
    altitude INTEGER,
    latitude NUMERIC,
    longitude NUMERIC,
    );
```

## Adding AWS CLI to my path
```
export PATH=~/.local/bin:$PATH
```
