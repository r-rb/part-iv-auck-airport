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
            check_call(['julia', '../Solvers/mip_solver.jl'], stderr=STDOUT)
    elif solver_name == "dp":
        with open(os.devnull, 'wb') as devnull:
            check_call(['julia', '../Solvers/dp_solver.jl'], stderr=STDOUT)
    else:
        print("Error: specified solver is not configured")
        exit()

    schedule =[float(x) for x in open("./tmp/schedule.txt",'r').readlines()]

    # Code to return the ending times of a schedule
    # 0  1   2   3
    # 3, 7 , 5 , 10 
    # 
    # Sort the list
    # 
    n_planes = len(id_arr)
    stuff = [(schedule[i],class_num[i]-1,i) for i in range(n_planes)]
    stuff.sort(key = lambda x:x[0])
    end_times = [st[0] + proc_t[ st[2] ][ stuff[idx + 1 ][ 2 ] ] if (idx < n_planes -1) else st[0] + 1 for idx,st in enumerate(stuff)]

    print(end_times)

    

    return schedule
