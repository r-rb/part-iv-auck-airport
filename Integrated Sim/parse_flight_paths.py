import numpy as np
import pprint as pp
import json
import pickle

# Script should prep all the time values
with open("./data/flight_data.pkl","rb") as f:
    fl_data = pickle.load(f)
start_time = fl_data["start"]

icao_info = open('aircraft_code.txt','r').readlines()

icao_lookup = {x.split('\t')[1].strip() : x.split('\t')[-1].strip() for x in icao_info}

data = []

for fl_id,fl in fl_data["data"].items():
    try:
        weight_class = icao_lookup[fl["aircraft"]["model"]["code"]]
    except KeyError:
        weight_class = 'M'

    landed = None

    # check if landed
    if fl["time"]["real"]["arrival"] is not None:
        landed = int(fl["time"]["real"]["arrival"]) - int(start_time)

    # only update the trail if its not landed
    trail =[]
    for t in fl["trail"]:
        del_t = int(t['ts']) - int(start_time) 
        if del_t >= 0:
            if landed is None:
                t['ts'] = del_t
                trail.append(t)
            elif del_t <=landed:
                t['ts'] = del_t
                trail.append(t)

    new_field = {"id": fl_id,
                "class": weight_class,
                "adj_trail": trail,
                "has_landed": landed if landed else None}
    
    
    data.append(new_field)

    if landed:
        pp.pprint(new_field)

with open("./out/parsed_flights.pkl","wb") as f:
    pickle.dump(data,f)


###################################################################
#                           SCHEMA:
#       ID       CLASS      TRAIL (ADJUSTED)              LANDED           
#      1detr5g     M         {   lon:(float) ,              TS
#                                lat:(float) ,
#                               adj_time:TS - start_time,
#                               speed: (float)  }
###################################################################


    
    



