import numpy as np
import pprint as pp
import random
import math
import time
from copy import deepcopy

# Dynamic programming implementation
    # Using FCFS within classes -> cost function is a function of class
    # General case if number of classes == number of planes

def valid(state,cl,r,cl_info):

    if state[cl] + 1 <= cl_info["max"][cl]:

        targ    = cl_info["targets"][cl][state[cl]]
        rop     = state["rop"][r]
        t       = targ if rop[0] == -1 else \
                    max(targ,rop[1] + cl_info["sep"][rop[0]][cl])
        
        new_state           = deepcopy(state)
        new_state[cl]      += 1
        new_state["rop"][r] = (cl,t)
        new_state["cost"]  += cl_info["cost"][cl] * math.pow((t - targ),cl_info["deg"])\
                                if (t-targ)<cl_info["max_delay"][cl] else float("inf")
        new_state["sched"].append((cl,t,r,targ,t-targ,))
    
        return t,new_state

    return None,None
    
def get_states(cl,r,stage,cl_info):
    set_states = []
    for state in stage:
        t,new_state = valid(state,cl,r,cl_info)
        if t is not None:
            added = False
            for idx,st in enumerate(set_states):
                if t == st["rop"][r][1]:
                    if new_state["cost"] < st["cost"]:
                        set_states[idx] = new_state
                    added = True
            if not added:
                set_states.append(new_state)
        else:
            pass

    return set_states


def expand(stage,cl_info,R):
    
    new_states = []

    # test the landing of all class/runway combinations
    for cl in cl_info["classes"]:
        for r in range(0,R):
            new_states.extend(get_states(cl,r,stage,cl_info))

    #pp.pprint(new_states)
    return new_states

def dp_fcfs(targ,w_class,cost,sep,max_delay = None,R = 1,deg = 2):

    #pp.pprint(cl_info)   

    n_planes            = len(targ)
    n_stages            = n_planes + 1
    stages              = [None] * n_stages

    cl_info             = {"cost":cost,"sep":sep, "deg":deg}
    cl_info["classes"]  = list(sorted(set(w_class)))
    cl_info["max"]      = {k: w_class.count(k) for k in w_class}
    cl_info["total"]    = len(cl_info["classes"])
    cl_info["targets"]  = {cl:sorted([t for t,c in zip(targ,w_class) if c == cl]) for cl in cl_info["classes"]} 
    cl_info["max_delay"]= {d:c for c,d in zip(max_delay,cl_info["classes"])}

    #print(cl_info)

    #print(cl_info["max_delay"])

    # Intial state
    init                = {k: 0 for k in cl_info["classes"]}
    init["rop"]         = {i:(-1,-1) for i in range(0,R)}
    init["cost"]        = 0
    init["sched"]       = [(-1,-1,-1,0,None)]

    # Intialise 
    stages[0]           = [init]

    #pp.pprint(stages[0])

    for n,stage in enumerate(stages):
        if n < len(targ):
            new_states  = expand(stage,cl_info,R)
            stages[n+1] = new_states

    #print(len(stages[-1]))
    
    min_st  = min(stages[-1],key = lambda st : st["cost"])

    #assert(sum([ math.pow(s[3],deg) for s in min_st["sched"] ]) == min_st["cost"] )

    # return a schedule which is an array of tuples that look like:
    # (class, time of usage, runway number,targ, deviation from target)

    #print(min_st["cost"])
    sched =  [list(filter(lambda sch: sch[-2] == t,min_st["sched"]))[0][-1] for t in targ]

    return sched

if __name__ == '__main__':

    # Test case with unit spaced arrivals and randomised seperation and costs.
    # This is the general case as number of classes == number of planes

    n = 5  # number of planes
    R = 1   # number of runways
    deg = 1 # degree on deviation from target in objective cost

    targets         = [i+1 for i in range(0,n)]
    plane_classes   = [str(i+1) for i in range(0,n)]
    cost            = {k:random.randint(1,1) for k in set(plane_classes)}
    sep             = {k:{k1:random.randint(2,2) for k1 in set(plane_classes)} for k in set(plane_classes)}

    t0 = time.clock()
    sched           = dp_fcfs(targets,plane_classes,cost,sep,None,R,deg)
    pp.pprint(sched)
    t1 = time.clock()
    pp.pprint(t1 - t0)