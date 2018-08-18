from plane import Plane, Arrival
from location import Landmark
import numpy as np
import pickle
import math

SEC_PER_MIN = 60 # Seconds per minute

def loadplane(kml, isManual):
    plane = []

    if isManual:
        # Aiports
        akl = Landmark("Auckland Airport", 174.779962, -37.013383, 4000, kml)
        wlg = Landmark("Wellington Airport", 174.807598, -41.3275941, 4000, kml)

        #plane.append(Plane("Rayner", 170.0, -35.0, 1, apt, kml))
        #plane.append(Plane("Nathan", 176.0, -39.0, 2, apt, kml))
        #plane.append(Plane("John", 180.0, -39.5, 4, apt, kml))
        #plane.append(Plane("Joe", 172.0, -36.0, 5, apt, kml))
        #plane.append(Plane("Anne", 173.0, -35.0, 2, apt, kml))
        #plane.append(Plane("AKL-WLG1", 174.80759839999996, -41.3275941, 1, [akl,wlg,akl,wlg,akl], kml))
        plane.append(Plane("AKL-WLG2", 174.78, -40, 1, [akl,wlg,akl,wlg,akl], kml))
    else:
        with open("./pkl/parsed_flights.pkl", "rb") as f:
            data = pickle.load(f)

        for pl in data:
            if pl["adj_trail"]:
                first_minute = math.floor(pl["adj_trail"][-1]["ts"]/SEC_PER_MIN)
                start_point = Arrival.get_point(pl["adj_trail"],first_minute)

                # Find the class of the plane
                if pl["class"]=='H':
                    class_num = 2
                elif pl["class"]=='M':
                    class_num = 3
                elif pl["class"]=='L':
                    class_num = 4
                else:
                    raise ValueError('The class could not be identified for a plane in the pickled data.')

                plane.append(Arrival(pl["id"], start_point["lng"], start_point["lat"], class_num, pl["adj_trail"], kml))
    return plane

def loadsep(kml):
    S = np.array([  [2,2,3,4],
                    [2,2,2,3],
                    [0,0,0,3],
                    [0,0,0,0]   ])
    return S
