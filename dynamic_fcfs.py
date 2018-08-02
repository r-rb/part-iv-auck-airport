import numpy as np
import pprint as pp
import random
from copy import deepcopy
# Dynamic programming implementation
    # Using FCFS within classes -> cost function is a function of class
    # Allows for a polynomial time as a function of planes
# R = number of runways
# W = number of classes
# States are:
    # (k_H,k_M,k_L,((O_1,w_1,......,O_R))

# Algorithm

def valid(state,cl,r,cl_info):

    if state[cl] + 1 <= cl_info["max"][cl]:

        targ                = cl_info["targets"][cl][state[cl]]
        rop                 = state["rop"][r]
        t                   = targ if rop[0] == -1 else \
                                max(targ,rop[1] + cl_info["sep"][rop[0]][cl])
        
        new_state               = deepcopy(state)
        new_state[cl]           += 1
        new_state["prev"]       = rop[0]
        new_state["rop"][r]     = (cl,t)
        new_state["cost"]       += cl_info["cost"][cl] * (t - targ)
        new_state["sched"].append((cl,t,r,t-targ))
    
        return t,new_state

    return None,None
    
def get_states(cl,r,stage,cl_info):

    set_states = []

    for state in stage:
        # print("#################")
        # print ('BEFORE')
        # print("#################")
        # print(state)

        t,new_state = valid(state,cl,r,cl_info)

        # print("#################")
        # print ('AFTER')
        # print("#################")
        # print(state)

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

    # test the landing of all classes
    for cl in cl_info["classes"]:
        for r in range(0,R):
            new_states.extend(get_states(cl,r,stage,cl_info))

    #pp.pprint(new_states)
    return new_states

def dp_fcfs(targ,w_class,cost,sep,R = 1):
               
    cl_info             = {"cost":cost,"sep":sep}
    cl_info["classes"]  = list(sorted(set(w_class)))
    cl_info["max"]      = {k: w_class.count(k) for k in w_class}
    cl_info["total"]    = len(cl_info["classes"])
    cl_info["targets"]  = {cl:sorted([t for t,c in zip(targ,w_class) if c == cl]) for cl in cl_info["classes"]} 

    #pp.pprint(cl_info)   
    # Number of each class
    n_stages            = len(targ) + 1
    stages              = [None] * n_stages

    # Intial state
    init                = {k: 0 for k in cl_info["classes"]}
    init["rop"]         = {i:(-1,-1) for i in range(0,R)}
    init["cost"]        = 0
    init["prev"]        = None
    init["sched"] = [(-1,-1,-1)]

    stages[0]= [init]

    pp.pprint(stages[0])

    for n,stage in enumerate(stages):
        if n < len(targ):
            new_states = expand(stage,cl_info,R)
            stages[n+1] = new_states
            print('STAGE ' + str(n) )
    
    print(len(stages[-1]))
    
    # Backtrack

    # return a landing order

    min_st  = min(stages[-1],key = lambda st : st["cost"])

    pp.pprint(stages[-1])

    return True

if __name__ == '__main__':

    # test case with unit spaced arrivals and randomised seperation and arrival times
    n = 20
    R = 2 
    targets         = [i+1 for i in range(0,n)]
    wake_classes    = [str(i+1) for i in range(0,n)]
    cost = {k:random.randint(1,1) for k in set(wake_classes)}
    sep = {k:{k1:random.randint(2,2) for k1 in set(wake_classes)} for k in set(wake_classes)}

    dp_fcfs(targets,wake_classes,cost,sep,R)






