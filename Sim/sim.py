import numpy as np
import simplekml
import os
import math
from subprocess import DEVNULL, STDOUT, check_call
from coordinates import rect2earth
from solve import solve
from visualize import visualize
from location import Location, dist, Landmark
from plane import Plane

###################################################

### SETTINGS

###################################################

solver_name = "spp"
#solver_name = "mip"
#solver_name = "dp"
log_name = "log.txt"

###################################################

### SET UP KML

###################################################

# File
kml=simplekml.Kml()

# Aiport
apt = Landmark("Auckland Airport", 174.779962, -37.013383, 4000, kml)

###################################################

### FAKE DATA OF PLANES

###################################################

sep_t = np.array([	[2,2,3,4],
					[2,2,2,3],
					[0,0,0,3],
					[0,0,0,0]	])

plane = []
plane.append(Plane("Rayner", 170.0, -35.0, 3, 1, apt, kml))
plane.append(Plane("Nathan", 176.0, -39.0, 3, 2, apt, kml))
plane.append(Plane("John", 180.0, -39.5, 0, 4, apt, kml))
plane.append(Plane("Joe", 172.0, -36.0, 0, 5, apt, kml))
plane.append(Plane("Anne", 173.0, -35.0, 1, 2, apt, kml))

###################################################

### SIMULATION

###################################################

minute = 0
while not all([pl.landed for pl in plane]):
	with open(log_name, 'a') as file:
		file.write("Minute "+str(minute)+": \n")
	minute += 1

	id_arr = delay_cost = max_delay = class_num = proc_t = []

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
		pl.update(log_name)

	# Visualize the kml file
	visualize(kml)


