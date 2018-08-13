import numpy as np
import simplekml
import math
from coordinates import rect2earth
from location import Location, dist

tol = 1e-6 # Tolerance in floating point comparisons

class Plane(Location):
	def __init__(self, name, lon, lat, class_num, delay_cost,apt,kml):
		Location.__init__(self, name, lon, lat)
		self.pt = kml.newpoint(name=name,coords = [(lon,lat)])
		self.ls = kml.newlinestring(name=name+"path",coords = [(lon,lat)])
		self.class_num = class_num
		self.delay_cost = delay_cost
		self.landed = False
		self.speed = 83300.0
		self.speed_std  = 20
		self.max_delay = 10
		self.apt = apt
		self.id_arr = dist(self, apt)/self.speed
		self.sch_arr = self.id_arr


	def update(self,log_name):
		if not self.landed:
			if dist(self, self.apt) + tol>= self.sch_arr*self.speed:
				step = np.random.normal(self.speed, self.speed_std)

				if step <= tol + dist(self, self.apt):
					self.rect += step * (self.apt.rect - self.rect)/dist(self, self.apt)
				else:
					self.rect = self.apt.rect
					self.landed = True
					with open(log_name, 'a') as file:
						file.write(self.name+" has landed\n")

				self.lat,self.lon = rect2earth(self.rect)
				self.id_arr = dist(self, self.apt)/self.speed
				self.ls.coords.addcoordinates([(self.lon,self.lat)])
				self.pt.coords = [(self.lon,self.lat)]
			else:
				with open(log_name, 'a') as file:
					file.write(self.name+" has been delayed by an estimated "+str(math.ceil(self.sch_arr - dist(self, self.apt)/self.speed))+" minute(s)\n")
