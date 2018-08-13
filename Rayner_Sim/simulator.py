import os
import math
import pickle
import simplekml
import coordinates

import numpy as np
import pprint as pp

from subprocess import DEVNULL, STDOUT, check_call
from plane import Plane, Arrival
from dynamic_fcfs import *

#from test_data import data


T_MAX = 30
T_STEP = 1

cand_list = []

plane_list = []

wake_sep = {'H': {'H': 3, 'M': 2, 'L': 1}, 'M': {
    'H': 2, 'M': 10, 'L': 2}, 'L': {'H': 4, 'M': 5, 'L': 2}}

with open("./out/parsed_flights.pkl", "rb") as f:
    data = pickle.load(f)

for pl in data:
    if pl["adj_trail"]:
        t = math.floor(pl["adj_trail"][-1]["ts"]/60)
        intp = coordinates.interpolate_trail(t, pl["adj_trail"])
        plane_list.append(Arrival(
            pl["id"], pl["class"], pl["has_landed"], pl["adj_trail"], intp["lng"], intp["lat"], None))

print(len(plane_list))
assert(1 == 0)
for t in range(0, T_MAX, T_STEP):

    # Update candidate list ( list of planes in the box at time )
    rm_list = []

    for idx, pl in enumerate(plane_list):
        if pl.appearance_time < 60 * (t+1):
            cand_list.append(pl)
            rm_list.append(idx)

    plane_list = [plane_list[idx] for idx, _ in enumerate(plane_list) if idx not in rm_list]

    # Solve model with current positions and etas
    id_arr = [pl.eta + pl.delay for pl in cand_list]
    delay_cost = {pl.id: pl.delay_cost for pl in cand_list}
    class_arr = [pl.id for pl in cand_list]
    max_delay = [pl.max_delay for pl in cand_list]
    sep = {i.id: {k.id: wake_sep[i.weight_class][k.weight_class] * 60 for k in cand_list} for i in cand_list}

    # Update with postions at new times
    sched = dp_fcfs(id_arr, class_arr, delay_cost, sep, max_delay, R=1, deg=1)

    for sch, pl in zip(sched, cand_list):
        pl.delay_by(sch)
        pl.update(t)

    cand_list = [cd for cd in cand_list if not cd.done]

    #print('\n' + str(len([cd for cd in cand_list if not cd.done])) + '\n')
