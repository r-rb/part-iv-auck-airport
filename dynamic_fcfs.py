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
def dominated(state1,state2):
    pass

def transitions(state):
    pass

def valid(state,cl,r,w_max):
    

def set_states(cl,r,stage,w_max):
    for state in stage:
        valid(state,cl,r,w_max)

def expand(stage,pl_classes,cl_max,R):
    
    new_states = []

    # test the landing of all classes
    for cl in pl_classes:
        for r in range(0,R):
            set_states(cl,r,stage)

        

    return new_states

def prune(stage):
    pass

def targeted_time(p_class,idx):
    pass

def dp_fcfs(targ,w_class,cost,d_max = 99999,R = 1):

    classes     = list(sorted(set(w_class)))                # Set of classes
    W           = len(classes)                              # Number of classes
    cl_max       = {k: w_class.count(k) for k in w_class}    # Number of each class
    n_stages    = len(targ) + 1
    stages = [[]] * n_stages

    # Initial state
    init            = {k: 0 for k in classes}
    init["rop"]     = {i:(-1,-1) for i in range(0,R)}
    init["cost"]    = 0
    init["prev"]    = None

    stages[0].append(init)

    for n,stage in enumerate(stages):
        if n < len(targ):
            new_states = expand(stage)
            stages[n+1].extend(new_states,classes,cl_max)

            # Prune dominated states
            prune(stages[n+1])
    
    # Backtrack

    # return a landing order
    return True

if __name__ == '__main__':
    # Sample problem
    targets         =               [1,2,3,4,5,6,7]
    wake_classes    = ['H','M','L','L','H','M','L']
vv
    dp_fcfs(targets,wake_classes,cost,10)






