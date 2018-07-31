import numpy as np
import simplekml
import os
import math
from polycircles import polycircles
from subprocess import DEVNULL, STDOUT, check_call

###################################################

### SETTINGS

###################################################

tol = 1e-6 # Tolerance in floating point comparisons
big_m = 1e10
min_num = 50
kml_name = "sim.kml"
solve_jl_name = "sim_solver.jl"

###################################################

### CONSTANTS

###################################################

# Radius of the earth
earth_radius = 6.371e6 # metres

###################################################

### FUNCTIONS

###################################################

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
		self.id_arr = dist(self, apt)/self.speed
		
		self.sch_arr = self.id_arr


	def update(self):
		if dist(self, apt) + tol >= self.sch_arr*self.speed:
			step = np.random.normal(self.speed, self.speed_std)

			if step <= tol + dist(self, apt):
				self.rect += step * (apt.rect - self.rect)/dist(self, apt)
			else:
				self.rect = apt.rect
				self.landed = True

			self.lat,self.lon = rect2earth(self.rect)
			self.id_arr = dist(self, apt)/self.speed
			self.ls.coords.addcoordinates([(self.lon,self.lat)])
			self.pt.coords = [(self.lon,self.lat)]

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

###################################################

### SIMULATION

###################################################

while not all([pl.landed for pl in plane]):
	
	proc_t = []
	id_arr = []
	delay_cost = []
	for pl in plane:
		if not pl.landed:
			id_arr.append(pl.id_arr)
			delay_cost.append(pl.delay_cost)
			proc_row = []
			for next in plane:
				if not next.landed:
					proc_row.append(sep_t[pl.class_num,next.class_num])
			proc_t.append(proc_row)

	np.savetxt("./tmp/arrival_t.txt", id_arr, newline="\n")
	np.savetxt("./tmp/delay_cost.txt", delay_cost, newline="\n")
	np.savetxt("./tmp/proc_t.txt", proc_t, newline="\n")

	with open(os.devnull, 'wb') as devnull:
		check_call(['julia', solve_jl_name], stderr=STDOUT)

	schedule = np.loadtxt("./tmp/schedule.txt").tolist()
	for pl in reversed(plane):
		if not pl.landed:
			if isinstance(schedule, float):
				pl.sch_arr = schedule
			else:
				pl.sch_arr = schedule.pop()

	# Update plane positions based on the schedule
	for pl in plane:
		pl.update()

# Create the file
kml.save(kml_name)
#with open(os.devnull, 'wb') as devnull:
	#check_call(['gnome-maps', kml_name], stdout=DEVNULL, stderr=STDOUT)


