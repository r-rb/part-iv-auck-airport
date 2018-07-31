import numpy as np
import pprint as pp
import json
import pickle
import simplekml

# Script should prep all the time values
with open("./out/parsed_flights.pkl","rb") as f:
    data = pickle.load(f)

kml=simplekml.Kml()

for fl in data:
    new_path = kml.newlinestring(name=fl["id"])
    for f in reversed(fl["adj_trail"]):
        new_path.coords.addcoordinates([(f["lng"],f["lat"])])

kml.save("paths.kml")

        