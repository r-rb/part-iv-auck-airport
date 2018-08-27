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

    schedule = np.loadtxt("./tmp/schedule.txt").tolist()
    return schedule
