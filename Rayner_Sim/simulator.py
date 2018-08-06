import numpy as np
import simplekml
import os
import math
from subprocess import DEVNULL, STDOUT, check_call
from test_data import data
import pprint as pp
from plane import Plane,Arrival
from dynamic_fcfs import *
import coordinates

T_MAX = 
T_STEP = 1

cand_list   = []

plane_list  = []

wake_sep = {'H':{'H':3,'M':2,'L':1},'M':{'H':2,'M':10,'L':2},'L':{'H':4,'M':5,'L':2}}

for pl in data:
    t           = math.floor(pl["adj_trail"][-1]["ts"]/60)
    intp        = coordinates.interpolate_trail(t,pl["adj_trail"])
    plane_list.append(Arrival(pl["id"],pl["class"],pl["has_landed"],pl["adj_trail"],intp["lng"],intp["lat"]))
    #pp.pprint(plane_list[-1].appearance_time)


for t in range(0,T_MAX,T_STEP):

    # Update candidate list ( list of planes in the box at time )
    for idx,pl in enumerate(plane_list):
        if pl.appearance_time < (t+1) * 60 and pl not in cand_list and not pl.done:
            print(pl.appearance_time)
            cand_list.append(pl)  

    #print(len(cand_list))
    #assert(1==0)
 
    for idx,pl in enumerate(cand_list):
        if pl.done:
            cand_list.pop(idx)

    # Solve model with current positions and etas
    id_arr      = [pl.eta + pl.delay for pl in cand_list]
    delay_cost  = {pl.id:pl.delay_cost for pl in cand_list}
    class_arr   = [pl.id for pl in cand_list]
    max_delay   = [pl.max_delay for pl in cand_list]
    sep         = {i.id : {k.id: wake_sep[i.weight_class][k.weight_class] * 60 for k in cand_list} for i in cand_list}

    # Update with postions at new times

    print(id_arr)

    pp.pprint(sep)
    
    sched = dp_fcfs(id_arr,class_arr,delay_cost,sep,max_delay,R=1,deg =1)

    for sch in sched:
        if sch[0]:
            for pl in cand_list:
                if pl.id == sch[0]:
                    pl.delay += sch[3]
                    print("plane with id: " + pl.id + ' is delayed by ' + str(sch[3]))

                pl.update(t+1)

    cand_list = []







    










