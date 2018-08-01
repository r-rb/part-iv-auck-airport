import numpy as np
import pprint as pp

# Dynamic programming implementation
    # Using FCFS within classes -> cost function is a function of class
    # Allows for a polynomial time as a function of planes
# R = number of runways
# W = number of classes
# States are:
    # (k_H,k_M,k_L,((O_1,w_1,......,O_R))

# Algorithm

def valid(state,cl,r,cl_info):

    if state[cl] + 1 < cl_info["max"][cl]:

        targ                = cl_info["targets"][cl][state[cl]]
        rop                 = state["rop"][r]
        t                   = targ if rop[0] == -1 else \
                                max(targ,rop[1] + cl_info["sep"][rop[0]][cl])
        
        new_state           = state
        new_state[cl]       += 1
        new_state["prev"]   = rop[0]
        new_state["rop"][r] = (cl,t)
        new_state["cost"]   += cl_info["cost"][cl] * (t - targ)
    
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

    return set_states


def expand(stage,cl_info,R):
    
    new_states = []

    # test the landing of all classes
    for cl in cl_info["classes"]:
        for r in range(0,R):
            new_states.extend(get_states(cl,r,stage,cl_info))

    return new_states

def dp_fcfs(targ,w_class,cost,sep,R = 1):
               
    cl_info             = {"cost":cost,"sep":sep}
    cl_info["classes"]  = list(sorted(set(w_class)))
    cl_info["max"]      = {k: w_class.count(k) for k in w_class}
    cl_info["total"]    = len(cl_info["classes"])

    cl_info["targets"]  ={cl:[t for t,c in zip(targ,w_class) if c == cl] for cl in cl_info["classes"]} 

    pp.pprint(cl_info)   
    # Number of each class
    n_stages            = len(targ) + 1
    stages              = [[]] * n_stages

    # Initial state
    init                = {k: 0 for k in cl_info["classes"]}
    init["rop"]         = {i:(-1,-1) for i in range(0,R)}
    init["cost"]        = 0
    init["prev"]        = None

    stages[0].append(init)

    for n,stage in enumerate(stages):
        if n < len(targ):
            new_states = expand(stage,cl_info,R)
            stages[n+1].extend(new_states)
            pass
            # Prune dominated states
            # prune(stages[n+1])
    
    # Backtrack
    print(len(stages[-1]))
    # return a landing order
    return True

if __name__ == '__main__':

    # Sample problem
    targets         =               [1,2,3,4,5,6,7]
    wake_classes    = ['H','M','L','L','H','M','L']
    cost = {'H': 1,'M':1,'L':1}
    sep = {'H':{'H': 2,'M':2,'L':2},
                'M':{'H': 2,'M':2,'L':2},
                    'L':{'H': 2,'M':2,'L':2}}

    dp_fcfs(targets,wake_classes,cost,sep,10)






