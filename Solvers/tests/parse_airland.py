import math
import pprint as pp
import numpy as np

def parse_airland(which,line_width = 8):    
    with open("./airland_files/airland"+str(which)+".txt",'r') as f:
        n_flights = int(f.readline().split()[0])
        rest = [s.strip() for s in f.readlines()]

    appearance_times = [None] * n_flights
    early_times = [None] * n_flights
    target_times = [None] * n_flights
    latest_times = [None] * n_flights
    cost_early = [None] * n_flights
    cost_late = [None] * n_flights
    proc_times = [[None]] * n_flights

    chunk_width = 1 + math.ceil(n_flights/line_width)
    assert(len(rest) == (chunk_width * n_flights))

    chunk_list = [rest[chunk_width*i:chunk_width*(i+1)] for i in range(0,n_flights)]

    for idx,chunk in enumerate(chunk_list):
        appearance_times[idx],early_times[idx],target_times[idx],\
            latest_times[idx],cost_early[idx],cost_late[idx] = tuple([float(c) for c in chunk[0].split()])
        proc_row = []

        for c in chunk[1::]:
            proc_row.extend([float(x) for x in c.split()])
        
        proc_row[idx] = 0
        proc_times[idx] = proc_row

    max_delays = [l-t for t,l in zip(target_times,latest_times)]

    pp.pprint(n_flights)

    np.savetxt("./appearance_t.txt", appearance_times, newline="\n")
    np.savetxt("./early_t.txt", early_times, newline="\n")
    np.savetxt("./target_t.txt", target_times, newline="\n")
    np.savetxt("./latest_t.txt",latest_times, newline="\n")
    np.savetxt("./cost_early.txt", cost_early, newline="\n")
    np.savetxt("./cost_late.txt", cost_late, newline="\n")
    np.savetxt("./proc_t.txt", proc_times, newline="\n")
    np.savetxt("./max_delays.txt", max_delays, newline="\n")

parse_airland(8)
