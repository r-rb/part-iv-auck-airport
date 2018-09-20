import math
import numpy as np
import coordinates
import simplekml

earth_radius = 6.371e6  # metres


class Plane:

    def __init__(self, flight_id, weight_class, eta, delay_cost=1, max_delay=36000):
        self.id = flight_id
        self.weight_class = weight_class
        self.delay = 0
        self.appearance_time = None
        self.eta = eta
        self.done = False
        self.delay_cost = delay_cost
        self.max_delay = max_delay

    def update(self, *args):
        pass


class Arrival(Plane):

    def __init__(self, flight_id, weight_class, eta, trail, lng, lat, kml, delay_cost=1):

        Plane.__init__(self, flight_id, weight_class, eta, delay_cost)
        self.appearance_time = trail[-1]["ts"]
        self.trail = trail
        self.lng = lng
        self.lat = lat
        self.kml = kml

    def interpolate_trail(self, t):

        max_targ = (t+1) * 60

        # trail is sorted in descending order of time
        for idx, entry in enumerate(self.trail):

            if entry["ts"] + self.delay <= max_targ:

                if idx == 0:
                    return entry
                else:
                    v1 = entry
                    v0 = self.trail[idx-1]
                    t1 = v1["ts"] + self.delay - t * 60
                    t0 = v0["ts"] + self.delay - t * 60
                    return {k: np.interp(0, [t0, t1], [v0[k], v1[k]]) for k in entry}

        return False

    def delay_by(self, sch):

        self.delay += sch

        if sch:
            print("plane with id: " + self.id +
                  ' is delayed by a further ' + str(sch) + ' seconds')

    def update(self, t):

        if (t+1) * 60 >= self.delay + self.eta:
            self.done = True
            print("plane with id " + self.id + " has landed at time: "
                  + str(self.delay + self.eta) + ' during period: ' + str(t*60))
            return

        new_coords = self.interpolate_trail(t+1)

        if new_coords:
            self.lng = new_coords["lng"]
            self.lat = new_coords["lat"]
