import numpy as np
import simplekml
import os
import math
from polycircles import polycircles
from subprocess import DEVNULL, STDOUT, check_call
from coordinates import earth2rect, rect2earth
from solve import solve
from visualize import visualize

###################################################

### SETTINGS

###################################################

tol = 1e-6 # Tolerance in floating point comparisons
kml_name = "sim.kml"
solver_name = "spp"
#solver_name = "mip"
#solver_name = "dp"
log_name = "log.txt"

###################################################

### SET UP KML

###################################################

# File
kml=simplekml.Kml()

###################################################

### SET UP AIRPORT

###################################################

class Location:
	def __init__(self, name, lon, lat):
		self.name = name
		self.lon = lon
		self.lat = lat
		self.rect = earth2rect(lon, lat)

def dist(loc1, loc2):
	return np.linalg.norm(loc1.rect - loc2.rect)

class Landmark(Location):
	def __init__(self, name, lon, lat, rad):
		Location.__init__(self, name, lon, lat)
		self.poly = polycircles.Polycircle(longitude=lon, latitude=lat, radius=rad, number_of_vertices=36)
		self.kml = kml.newpolygon(name=name, outerboundaryis = self.poly.to_kml())
		self.kml.style.polystyle.color = simplekml.Color.changealphaint(200, simplekml.Color.green)

apt = Landmark("Auckland Airport", 174.779962, -37.013383, 4000)

###################################################

### PLANE CLASS

###################################################

class Plane(Location):
	def __init__(self, name, lon, lat, class_num, delay_cost):
		Location.__init__(self, name, lon, lat)
		self.pt = kml.newpoint(name=name,coords = [(lon,lat)])
		self.ls = kml.newlinestring(name=name+"path",coords = [(lon,lat)])
		self.class_num = class_num
		self.delay_cost = delay_cost
		self.landed = False
		self.speed = 83300.0
		self.speed_std  = 20
		self.max_delay = 10
		self.id_arr = dist(self, apt)/self.speed
		self.sch_arr = self.id_arr


	def update(self):
		if not pl.landed:
			if dist(self, apt) + tol>= self.sch_arr*self.speed:
				step = np.random.normal(self.speed, self.speed_std)

				if step <= tol + dist(self, apt):
					self.rect += step * (apt.rect - self.rect)/dist(self, apt)
				else:
					self.rect = apt.rect
					self.landed = True
					with open(log_name, 'a') as file:
						file.write(self.name+" has landed\n")

				self.lat,self.lon = rect2earth(self.rect)
				self.id_arr = dist(self, apt)/self.speed
				self.ls.coords.addcoordinates([(self.lon,self.lat)])
				self.pt.coords = [(self.lon,self.lat)]
			else:
				with open(log_name, 'a') as file:
					file.write(self.name+" has been delayed by an estimated "+str(math.ceil(self.sch_arr - dist(self, apt)/self.speed))+" minute(s)\n")

###################################################

### FAKE DATA OF PLANES

###################################################

sep_t = np.array([	[2,2,3,4],
					[2,2,2,3],
					[0,0,0,3],
					[0,0,0,0]	])

plane = []
plane.append(Plane("Rayner", 170.0, -35.0, 3, 1))
plane.append(Plane("Nathan", 176.0, -39.0, 3, 2))
plane.append(Plane("John", 180.0, -39.5, 0, 4))
plane.append(Plane("Joe", 172.0, -36.0, 0, 5))
plane.append(Plane("Anne", 173.0, -35.0, 1, 2))

###################################################

### SIMULATION

###################################################

minute = 0
while not all([pl.landed for pl in plane]):
	with open(log_name, 'a') as file:
		file.write("Minute "+str(minute)+": \n")

	id_arr = []
	delay_cost = []
	max_delay = []
	class_num = []
	proc_t = []
	for pl in plane:
		if not pl.landed:
			id_arr.append(pl.id_arr)
			delay_cost.append(pl.delay_cost)
			max_delay.append(pl.max_delay)
			class_num.append(pl.class_num+1)
			proc_row = []
			for next in plane:
				if not next.landed:
					proc_row.append(sep_t[pl.class_num,next.class_num])
			proc_t.append(proc_row)

	schedule = solve(id_arr,delay_cost,max_delay,class_num,proc_t,sep_t,solver_name)
	for pl in reversed(plane):
		if not pl.landed:
			pl.sch_arr = schedule.pop()
		pl.update()		

	minute += 1
	# Create the file
	kml.save(kml_name);

	# Visualize the kml file
	visualize(kml_name)


