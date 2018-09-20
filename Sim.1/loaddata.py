from plane import Plane, Arrival
from location import Landmark
import numpy as np
import pickle
import math

SEC_PER_MIN = 60  # Seconds per minute


def loadplane(kml, isManual):
    plane = []

    if isManual:
        # Aiports
        akl = Landmark("Auckland Airport", 174.779962, -37.013383, 4000, kml)
        wlg = Landmark("Wellington Airport",
                       174.807598, -41.3275941, 4000, kml)
        syd = Landmark("Sydney Airport", 151.1753, -33.9399, 4000, kml)
        sin = Landmark("Singaport Airport",103.9915,1.3644,4000,kml)
        zqn = Landmark("Queenstown Aiport",168.7399,-45.0210,4000,kml)

        #plane.append(Plane(name, lng, lat, class_num,apt,kml))
        plane.append(Plane("WLG-AKL0", wlg.lng, wlg.lat, 3, akl, kml))
        plane.append(Plane("AKL-WLG0", akl.lng, akl.lat,3, wlg, kml, pred=plane[0]))
        plane.append(Plane("WLG-AKL1", wlg.lng, wlg.lat, 3, akl, kml, pred=plane[1]))
        #plane.append(Plane("AKL-WLG1", akl.lng, akl.lat,3, wlg, kml, pred=plane[2]))
        #plane.append(Plane("WLG-AKL2", wlg.lng, wlg.lat, 3, akl, kml, pred=plane[3]))
        #plane.append(Plane("AKL-WLG2", akl.lng, akl.lat,3, wlg, kml, pred=plane[4]))
        #plane.append(Plane("WLG-AKL3", wlg.lng, wlg.lat, 3, akl, kml, pred=plane[5]))

        #plane.append(Plane("SYD-AKL0", syd.lng, syd.lat, 2, akl, kml))
        #plane.append(Plane("AKL-SYD0", akl.lng, akl.lat, 2, syd, kml, pred=plane[7]))
        #plane.append(Plane("SYD-AKL1", syd.lng, syd.lat, 2, akl, kml,pred=plane[8]))
        #plane.append(Plane("AKL-SYD1", akl.lng, akl.lat, 2, syd, kml, pred=plane[9]))
        #plane.append(Plane("SYD-AKL2", syd.lng, syd.lat, 2, akl, kml,pred=plane[10]))

        #plane.append(Plane("SIN-SYD-AKL0", sin.lng, sin.lat, 1, syd, kml))
        #plane.append(Plane("SIN-SYD-AKL1", syd.lng, syd.lat, 1, akl, kml,pred=plane[12]))
        
        #plane.append(Plane("ZQN-AKL0", zqn.lng, zqn.lat, 3, akl, kml))
        #plane.append(Plane("AKL-ZQN0", akl.lng, akl.lat, 3, zqn, kml,pred=plane[14]))
        #plane.append(Plane("ZQN-AKL0", zqn.lng, zqn.lat, 3, akl, kml,pred=plane[15]))
        #plane.append(Plane("AKL-ZQN0", akl.lng, akl.lat, 3, zqn, kml,pred=plane[16]))
        
        #plane.append(Plane("Rayner", 175.0, -37.0, 3, akl, kml))
        #plane.append(Plane("Frank", 176.0, -39.0, 2, akl, kml))
        #plane.append(Plane("John", 180.0, -39.5, 4, akl, kml))
        #plane.append(Plane("Joe", 172.0, -36.0, 4, akl, kml))
        #plane.append(Plane("Anne", 173.0, -35.0, 2, akl, kml))
        #plane.append(Plane("Rayner", 174.0, -37.0, 3, akl, kml))
        #plane.append(Plane("Bob", 175.0, -33.0, 4, akl, kml))
        #plane.append(Plane("Emma", 176.4, -38.4, 3, akl, kml))


    else:
        with open("./pkl/parsed_flights.pkl", "rb") as f:
            data = pickle.load(f)

        for pl in data:
            if pl["adj_trail"]:
                first_minute = math.floor(pl["adj_trail"][-1]["ts"]/SEC_PER_MIN)
                start_point = Arrival.get_point(pl["adj_trail"], first_minute)

                # Find the class of the plane
                if pl["class"] == 'H':
                    class_num = 2
                elif pl["class"] == 'M':
                    class_num = 3
                elif pl["class"] == 'L':
                    class_num = 4
                else:
                    raise ValueError(
                        'The class could not be identified for a plane in the pickled data.')

                plane.append(Arrival(
                    pl["id"], start_point["lng"], start_point["lat"], class_num, pl["adj_trail"], kml, arr_time=pl["adj_trail"][-1]["ts"]/SEC_PER_MIN))
    return plane


def loadsep(kml):
    S = np.array([[2, 2, 3, 4],
                  [2, 2, 2, 3],
                  [1, 1, 1, 3],
                  [1, 1, 1, 1]])
    return S
