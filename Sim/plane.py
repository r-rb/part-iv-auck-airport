import numpy as np
import simplekml
import math
from coordinates import rect2earth, earth2rect
from location import Location, dist

tol = 1e-6 # Tolerance in floating point comparisons
SEC_PER_MIN = 60 # Seconds per minute

class Plane(Location):
    def __init__(self, name, lng, lat, class_num,apt,kml,delay_cost = 1,speed=1300.0,max_delay = 1000,swap_time = 10):
        Location.__init__(self, name, lng, lat)
        self.pt = kml.newpoint(name=name,coords = [(lng,lat)]) # Create the kml point entity
        self.ls = kml.newlinestring(name=name+"path",coords = [(lng,lat)]) # Create the list of points the plane has visited.
        self.class_num = class_num
        self.delay_cost = delay_cost
        self.landed = False
        self.speed = speed
        self.max_delay = max_delay
        self.swap_time = swap_time
        self.apt = apt
        if apt:
            self.id_arr = dist(self, apt[-1])/self.speed # The ideal arrival time were we to travel at speed at the way to the airport
            self.eta = self.id_arr
        self.delay = 0

    def update(self,log_name,minute):
        if not self.landed:
            if dist(self, self.apt[-1]) + tol >= self.eta*self.speed:
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

                self.lng,self.lat = rect2earth(self.rect)
                self.id_arr = dist(self, self.apt[-1])/self.speed
                self.ls.coords.addcoordinates([(self.lng,self.lat)])
                self.pt.coords = [(self.lng,self.lat)]
            else:
                self.set_delay(dist(self, self.apt[-1])/self.speed - self.eta,log_name)

    def set_delay(self, delay,log_name):
        self.delay = delay
        with open(log_name, 'a') as file:
            file.write(self.name+" is estimated to be delayed by "+str(delay)+" minute(s)\n")

class Arrival(Plane):
    def __init__(self, name, lng, lat, class_num,trail,kml,delay_cost = 1,speed=1300.0,max_delay=1000):
        Plane.__init__(self, name, lng, lat, class_num,None,kml,delay_cost,speed,max_delay,0)
        self.final_dest = Location(name+" end",trail[0]["lng"],trail[0]["lat"])
        self.id_arr = dist(self, self.final_dest)/self.speed
        self.eta = trail[-1]["ts"]
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

    def update(self, log_name, minute):
        if (self.delay + self.eta)/SEC_PER_MIN <= minute + 1:
            self.landed = True
            self.rect = self.final_dest.rect
            self.lng,self.lat = rect2earth(self.rect)
            with open(log_name, 'a') as file:
                file.write(self.name+" has landed\n")
        else:
            new_point = Arrival.get_point(self.trail,minute+1)
            self.set_delay(dist(self, self.final_dest)/self.speed - self.eta,log_name)
            if new_point:
                self.lng = new_point["lng"]
                self.lat = new_point["lat"]
                self.rect = earth2rect(self.lng, self.lat)
        self.id_arr = dist(self, self.final_dest)/self.speed
        self.ls.coords.addcoordinates([(self.lng,self.lat)])
        self.pt.coords = [(self.lng,self.lat)]

