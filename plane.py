import math
import numpy as np
class Plane:

    def __init__(self,flight_id,weight_class,eta,delay_cost = 1):
        self.flight_id = flight_id
        self.weight_class = weight_class
        self.delay = 0
        self.appearance_time = None
        self.eta = eta
        self.done = False
        self.delay_cost = delay_cost

    def update(self):
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

earth_radius = 6.371e6 # metres

# Convert geospatial earth coordinates to cartesian rectangular coordinates
def earth2rect(lon, lat):
	theta = np.deg2rad(lat)
	phi = np.deg2rad(lon)
	R = earth_radius
	x = R*np.cos(theta)*np.cos(phi)
	y = R*np.cos(theta)*np.sin(phi)
	z = R*np.sin(theta)
	return np.array([x,y,z])

# Convert rectangular coordinates back to geospatial earth coordinates
def rect2earth(coords):
	x = coords[0]
	y = coords[1]
	z = coords[2]
	R = earth_radius
	lat = np.rad2deg( math.asin(z/R) )
	lon = np.rad2deg( math.atan2(y,x) )
	return (lat, lon)
