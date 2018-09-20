import numpy as np
import os
from subprocess import DEVNULL, STDOUT, check_call

def solve(id_arr, delay_cost, max_delay, class_num, proc_t, sep_t, depends, solver_name):
    np.savetxt("./tmp/arrival_t.txt", id_arr, newline="\n")
    np.savetxt("./tmp/delay_cost.txt", delay_cost, newline="\n")
    np.savetxt("./tmp/max_delay.txt", max_delay, newline="\n")
    np.savetxt("./tmp/class_num.txt", class_num, newline="\n", fmt='%u')
    np.savetxt("./tmp/proc_t.txt", proc_t, newline="\n")
    np.savetxt("./tmp/sep_t.txt", sep_t, newline="\n")
    np.savetxt("./tmp/depends.txt", depends, newline="\n")

    if solver_name == "spp":
        with open(os.devnull, 'wb') as devnull:
            check_call(['julia', '../Solvers/spp_solver.jl'], stderr=STDOUT)
    elif solver_name == "mip":
        with open(os.devnull, 'wb') as devnull:
            check_call(['julia', '../Solvers/mip_solver_full_beasley.jl'], stderr=STDOUT)
    elif solver_name == "dp":
        with open(os.devnull, 'wb') as devnull:
            check_call(['julia', '../Solvers/dp_solver.jl'], stderr=STDOUT)
    else:
        print("Error: specified solver is not configured")
        exit()

    schedule =[float(x) for x in open("./tmp/schedule.txt",'r').readlines()]

    n_flights = len(id_arr)
    endtimes = [None] * n_flights

    stuff = [(schedule[i],class_num[i]-1,i) for i in range(n_flights)]
    stuff.sort(key = lambda x:x[0])
    
    for idx,st in enumerate(stuff):
        if (idx < n_flights -1):
            endtimes[st[-1]] = st[0]+ proc_t[st[2]][stuff[idx + 1][2]]
        else:
           endtimes[st[-1]] =  st[0] + 1
    return schedule,endtimes
