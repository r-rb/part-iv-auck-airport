import math
import numpy as np
import coordinates
class Plane:

    def __init__(self,flight_id,weight_class,eta,delay_cost = 1,max_delay = 36000):
        self.id          = flight_id
        self.weight_class       = weight_class
        self.delay              = 0
        self.appearance_time    = None
        self.eta                = eta
        self.done               = False
        self.delay_cost         = delay_cost
        self.max_delay          = max_delay

    def update(self,*args):
        pass
    
    def move(self):
        pass
    
    def get_ideal_time(self):
        return self.eta + self.delay

class Arrival(Plane):

    def __init__(self,flight_id,weight_class,eta,trail,lng,lat,delay_cost = 1):
        Plane.__init__(self,flight_id,weight_class,eta,delay_cost)
        self.trail = trail
        self.lng = lng
        self.lat = lat
        self.appearance_time = trail[-1]["ts"]

    def update(self,t):
        new_coords = coordinates.interpolate_trail(t+1,self.trail)
        self.lng = new_coords["lng"]
        self.lat = new_coords["lat"]


earth_radius = 6.371e6 # metres
