import pandas as pd
import sqlite3

# Get URL from opendata.swiss
urls = {
    "wind_10min": "https://data.geo.admin.ch/ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min/ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min_de.csv",
    "wind_1s": "https://data.geo.admin.ch/ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min/ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min_de.csv",
}

# Define db
db = "ch_ws_db.sqlite"

# Connect to db
cnx = sqlite3.connect(db)

for key, value in urls.items():

    # Access old data
    try:
        df_old = pd.read_pickle(key + ".pkl")
    except:
        df_old = None

    # Read data from URL, use ISO-8859-1 encode since UTF-8 returns error
    df = pd.read_csv(
        value, sep=";", encoding="ISO-8859-1", skipfooter=3, engine='python'
    )

    # Compare against old data, avoid duplicates
    if df.equals(df_old) == False:
    
        # Create table with stations for overview
        df.to_sql(
            "stations",
            con=cnx,
            if_exists="replace",
        )

        # Create list with station abbreviations
        station_lst = df["Abk."].tolist()

        # For each station make data entries
        for station in station_lst:
            row = df.values == station
            df.loc[row].to_sql(
                station + "_" + key,
                con=cnx,
                if_exists="append",
            )

        # Save data for next run
        df_old = df.to_pickle(key + ".pkl")

# Close db connection
cnx.close()
