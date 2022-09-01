import pandas as pd
import requests
import sqlite3
import time

def get_elevation(lat, long):
    query = ('https://api.open-elevation.com/api/v1/lookup'
             f'?locations={lat},{long}')
    r = requests.get(query).json()  # json object, various ways you can extract value
    # one approach is to use pandas json functionality:
    elevation = pd.json_normalize(r, 'results')['elevation'].values[0]
    return int(elevation)

# CSV URL (manual download)
# https://data.geo.admin.ch/ch.swisstopo-vd.ortschaftenverzeichnis_plz/PLZO_CSV_WGS84.zip

# Read data from URL
df = pd.read_csv(
    "PLZO_CSV_WGS84.csv", sep=";", encoding="utf-8",
)

# Define db
db = "ch_ws_db.sqlite"

# Connect to db
cnx = sqlite3.connect(db)
cur = cnx.cursor()

# Create table with stations for overview
df.to_sql(
    "towns",
    con=cnx,
    if_exists="replace",
)

cur.execute("""ALTER TABLE towns ADD COLUMN Höhe 'integer'""")
cur.execute("""SELECT rowid, e, n FROM towns""")
data = cur.fetchall()

for row in data:
    time.sleep(1) # Do not overload API
    try:
        rowid = row[0]
        height = get_elevation(row[2], row[1])
        cur.execute("""UPDATE towns SET Höhe = ? WHERE rowid = ?""", (height, rowid))
        print(rowid, height)
        cnx.commit()
    except Exception as e:
        print(e)
        pass

cnx.close()
