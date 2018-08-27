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

solver_name = "dp"
# solver_name = "mip"
# solver_name = "dp"
log_name = "log.txt"
plotDuring = True
plotAfter = False
isManual = True  # Manual data entry or not


# File
kml = simplekml.Kml()
# AKL airport
akl = Landmark("Auckland Airport", 174.779962, -37.013383, 4000, kml)
plane = loadplane(kml, isManual)
sep_t = loadsep(kml)

minute = 0
while not all([pl.landed for pl in plane]):
    with open(log_name, 'a') as file:
        file.write("Minute "+str(minute)+": \n")
        minute += 1
        if True:  # not (minute % 1):
            valid = [pl for pl in plane if not pl.landed and dist(
                pl, akl) <= 100000000]
            id_arr = [pl.id_arr for pl in valid]
            delay_cost = [pl.delay_cost for pl in valid]
            max_delay = [pl.max_delay for pl in valid]
            class_num = [pl.class_num for pl in valid]
            id_arr = [pl.id_arr for pl in valid]
            depends = [valid.index(pl.pred) if pl.pred else 0 for pl in valid]
            proc_t = [[sep_t[i.class_num-1, k.class_num-1]
                       if i.name != k.name else 0 for k in valid] for i in valid]

            schedule = solve(id_arr, delay_cost, max_delay,
                             class_num, proc_t, sep_t, depends, solver_name)
            for pl in reversed(plane):
                if not pl.landed and dist(pl, akl) <= 100000000:
                    if not isinstance(schedule, float):
                        pl.eta = schedule.pop()
                    else:
                        pl.eta = schedule

        for pl in plane:
            pl.update(log_name, minute)

    # Visualize the kml file
    if plotDuring:
        visualize(kml)
if plotAfter:
    visualize(kml)
