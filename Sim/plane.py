import numpy as np
import simplekml
import math
from coordinates import rect2earth
from location import Location, dist

tol = 1e-6 # Tolerance in floating point comparisons
SEC_PER_MIN = 60 # Seconds per minute

class Plane(Location):
    def __init__(self, name, lng, lat, class_num,apt,kml,delay_cost = 1,speed=83300.0,max_delay = 10,swap_time = 10):
        Location.__init__(self, name, lng, lat)
        self.pt = kml.newpoint(name=name,coords = [(lng,lat)])
        self.ls = kml.newlinestring(name=name+"path",coords = [(lng,lat)])
        self.class_num = class_num
        self.delay_cost = delay_cost
        self.landed = False
        self.speed = speed
        self.max_delay = max_delay
        self.swap_time = swap_time
        self.apt = apt
        self.id_arr = dist(self, apt[-1])/self.speed
        self.eta = self.id_arr

    def update(self,log_name):
        if not self.landed:
            if dist(self, self.apt[-1]) + tol>= self.eta*self.speed:
                step = self.speed

                if step <= tol + dist(self, self.apt[-1]):
                    self.rect += step * (self.apt[-1].rect - self.rect)/dist(self, self.apt[-1])
                elif len(self.apt) == 1:
                    self.rect = self.apt[-1].rect
                    self.landed = True
                    with open(log_name, 'a') as file:
                        file.write(self.name+" has landed\n")
                else:
                    self.rect = self.apt[-1].rect
                    self.apt.pop()          
                    self.id_arr = self.swap_time + dist(self, self.apt[-1])/self.speed
                    self.eta = self.id_arr      
                    with open(log_name, 'a') as file:
                        file.write(self.name+" has landed\n")

                self.lat,self.lng = rect2earth(self.rect)
                self.id_arr = dist(self, self.apt[-1])/self.speed
                self.ls.coords.addcoordinates([(self.lng,self.lat)])
                self.pt.coords = [(self.lng,self.lat)]
            else:
                with open(log_name, 'a') as file:
                    file.write(self.name+" has been delayed by an estimated "+str(math.ceil(self.eta - dist(self, self.apt[[-1]])/self.speed))+" minute(s)\n")

class Arrival(Plane):
    def __init__(self, name, lng, lat, class_num,eta,trail,kml,delay_cost = 1,speed=83300.0,max_delay=10,swap_time = 10):
        Plane.__init__(self, name, lng, lat, class_num,None,kml,delay_cost,speed,max_delay,swap_time)
        self.eta = eta
        self.trail = trail

    @staticmethod
    def get_point(trail,minute):    
        for idx,point in enumerate(trail):
            # Step through the points on the trail from the end to the beginning
            if point["ts"]/SEC_PER_MIN <= minute + 1:
                # If the plane has already arrived, then return the point where it arrived.
                if idx == 0:
                    return point
                else:
                    # Otherwise, interpolate between the points on the trail.
                    pt0 = point
                    pt1 = trail[idx-1]
                   
                    return {k:np.interp(minute*SEC_PER_MIN,[pt0["ts"],pt1["ts"]],[pt0[k],pt1[k]]) for k in point}
        # If the plane has not started a trail yet, just return None.
        return None

    
