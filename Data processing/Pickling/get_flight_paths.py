import requests
import time
import pickle
import json
import re
import pprint as pp
import pandas as pd
import datetime

def httpdate(dt):
    """Return a string representation of a date according to RFC 1123
    (HTTP/1.1).

    The supplied date must be in UTC.

    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
        dt.year, dt.hour, dt.minute, dt.second)

# Returns a list of all flight ids headed toward AKL in the bounding box, at the current time.
def get_flight_ids():
    base_url = "https://data-live.flightradar24.com/zones/fcgi/feed.js"

    params = {
        "bounds" : "-24.95,-49.35,144.10,-166.82",
        "faa": "1",
        "mlat": "1",
        "flarm": "1",
        "adsb": "1",
        "gnd": "1",
        "air": "1",
        "vehicles": "0",
        "estimated": "1",
        "maxage": "14400",
        "gliders": "0",
        "stats": "0"
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "origin": "https://www.flightradar24.com",
        "referer": "https://www.flightradar24.com/data/airports/akl/arrivals",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
    }

    param_str = "&".join("%s=%s" % (k,v) for k,v in params.items())

    r = requests.get(base_url, params = param_str, headers = headers)

    json_keys = list(r.json())

    return [item for item in json_keys if re.search(r'\d',item) \
                        and r.json()[item][12].lower() == "akl"]

# Returns the planes path by flight id or None if the plane hasnt been updated in the past update period.
def get_plane_path(flight_id,last_update = 15):

    base_url = "https://data-live.flightradar24.com/clickhandler/"

    params = {
        "flight" : flight_id,
        "version" : "1.5"
        }

    request_time = datetime.datetime.utcnow()-datetime.timedelta(minutes=last_update)

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language" : "en-US,en;q=0.9",
        "if-modified-since": httpdate(request_time),
        "origin" : "https://www.flightradar24.com",
        "referer" : "https://www.flightradar24.com/ANZ460/1d18f2d0",
        "user-agent" :"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }

    param_str = "&".join("%s=%s" % (k,v) for k,v in params.items())

    r = requests.get(base_url, params = param_str, headers = headers)

    if r.status_code == requests.codes["ok"]:
        return r.json()
    else:
        return None

# Checks if ids are already in the recorded data
def update_records(flight_id_list,recorded_data,last_update = 15):
    for fl_id in flight_id_list:
        fl_data = get_plane_path(fl_id)
        if fl_data is not None:
            recorded_data[fl_id] = fl_data
        
if __name__ == "__main__":
    
    # recording period start
    recording_interval = 1
    start_t = time.time()
    data = {}
    n_max = 360 # number of time periods
    

    for n in range(0,n_max):

        fl_id_list = get_flight_ids()

        update_records(fl_id_list,data,recording_interval)

        recorded = {"start": start_t,
                    "data" : data}
        with open("./data/flight_data.pkl","wb") as f:
            pickle.dump(recorded,f)
        
        pp.pprint("Recorded up to " + str((n+1) * recording_interval) + " minutes worth of data.")

        time.sleep(60 * recording_interval)
    
    
    
        