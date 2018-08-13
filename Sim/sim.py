import numpy as np
import simplekml
import os
import math
from subprocess import DEVNULL, STDOUT, check_call
from solve import solve
from visualize import visualize
from location import Location, dist, Landmark
from plane import Plane
from loaddata import loadplane, loadsep

###################################################

### SETTINGS

###################################################

solver_name = "spp"
#solver_name = "mip"
#solver_name = "dp"
log_name = "log.txt"
plotDuring = True
plotAfter = True

###################################################

### SET UP KML

###################################################

# File
kml=simplekml.Kml()

# Aiport
apt = Landmark("Auckland Airport", 174.779962, -37.013383, 4000, kml)

###################################################

### GET DATA

###################################################

plane = loadplane(apt,kml)
sep_t = loadsep(kml)

###################################################

### SIMULATION

###################################################

minute = 0
while not all([pl.landed for pl in plane]):
	with open(log_name, 'a') as file:
		file.write("Minute "+str(minute)+": \n")
	minute += 1

	id_arr,delay_cost,max_delay,class_num,proc_t = [],[],[],[],[]
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
	if plotDuring visualize(kml)
if plotAfter visualize(kml)


