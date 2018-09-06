# OR Library Case
targets = vec(readdlm("./tests/target_t.txt", Float32))
proctimes = readdlm("./tests/proc_t.txt", Float32)

dependency = UInt8[0 for t = 1:length(targets)]
earlytimes = vec(readdlm("./tests/early_t.txt", Float32))
maxdelays = vec(readdlm("./tests/max_delays.txt", Float32))
cost_early = vec(readdlm("./tests/cost_early.txt", Float32))
cost_late = vec(readdlm("./tests/cost_late.txt", Float32))

runways = convert(UInt8, 1)

# Objective function
function fcost(t, target, earliest, max_delay=100, coeff_early=1, coeff_late= 1, deg=1)
    if (t > target + max_delay) | (t < earliest)
        # Just a flag to show that the cost function is undefined/infinite
        return -1
    end

    # Piecewise linear objective
    if t <= target
        return coeff_early * (target - t)
    else
        return coeff_late * (t - target)
    end
end

struct State
    schedule::Array{Tuple{Float32,Int8}} # [(t1,r1),(t2,r2),...,(tf,rf)]
    cost::Float32 # Cost of this state
    rop::Array{Tuple{Float32,Int8}} #ROP: Runway occupation profile [(t1,pl1),(t2,pl2),...,(tr,plr)], where (most recent time, plane).
end

function solvedp(earlytimes::Array{Float32},targets::Array{Float32}, dependency::Array{UInt8}, proctimes::Array{Float32,2},maxdelays::Array{Float32},fcost::Function,cost_early::Array{Float32},cost_late::Array{Float32},runways=1::UInt8)
    F = length(targets) # Number of flights
    S = F + 1   # Number of stages. Initial stage only has initial state
    R = runways # Number of runways
    n = 1   # Initialising stage counter
    turnovertime = 10    # Turnaround time for a plane before they can make another flight
    dependentflights = [dependency[i] for i = 1:F if dependency[i] != 0] # Storing flights which do have successors, could have duplicates.
    stagetable = Array{Array{State}}(1, S) # All the valid and non-dominated states for this stage
    println("==============================================================================")
    println("Inputted target times  -> $targets \n")

    function sameflights(s1, s2)
        for f in 1:F
            # If flight f has been scheduled in one schedule but not the other, then the schedules don't have the same flights.
            if (s1.schedule[f][1] * s2.schedule[f][1]) < 0
                return false
            end
        end
        return true
    end

    # Find all successor states, where on the next stage we land f on runway r
    function generatesuccessors(state::State, f, r)
        # If this flight has not already been scheduled:
        if state.schedule[f][2] < 0
            # Enforce earliest arrival time
            mintime = earlytimes[f]

            dep = dependency[f]

            # Check if there is an dependency for flight f
            if dep > 0

                # Check if the dependency has been satisfied, return if it hasn't.
                # Flight f can't be landed, and (-1,-1) is interpreted as "infeasible (f,r) combination"
                if state.schedule[dep][1] < 0
                    return [(-1, -1)]
                end
                
                # Enforce dependencies with turnover time
                mintime = max(mintime,state.schedule[dep][1] + turnovertime)
            end
            
            # The successors
            successors = Array{Tuple{Float32,State}}(0)
            
            # Get the (start) time and index of the most recent flight on the runway r.
            prevtime, precedingflight = state.rop[r]
            # If nothing has been landed on the runway yet, set this flight to be its own predecessor.
            # That's okay, because separation time between a flight and itself is assumed 0 in the inputs.
            if precedingflight < 0
                precedingflight = f
            end

            # Enforce separation constraints
            mintime = max(mintime,prevtime + proctimes[precedingflight,f])

            delaywidth = targets[f] - mintime

            # If targets[f] <= mintime (and so delaywidth is negative), then no early arrivals are possible
            if delaywidth < 0
                delaywidth = 0
            end
            
            # Integer values to offset target time by to early arrvials.
            # Check them in decreasing order (which is increasing arrival time order).
            earlyoffsets = Float32[k for k = delaywidth:-5:0]
            if delaywidth%1 > 0
                earlyoffsets = append!([delaywidth],earlyoffsets) # Add the endpoint, too, if it's fractional
            end

            # Consider each possible earliness by considering the earlyoffsets
            for e in earlyoffsets
                # Initialise state values
                newschedule, newrop, newcost  = copy(state.schedule), copy(state.rop), copy(state.cost)

                # Set the new time to be the target, offset by the earliness e.
                # But if no early arrivals, delaywidth is zero, so will be mintime
                newtime = max(mintime, targets[f] - e)

                # Find the cost of this additional cost by landing (f,r) now (over and above existing state costs)
                addedcost = fcost(newtime, targets[f], earlytimes[f], maxdelays[f],cost_early[f],cost_late[f])
                # If this is -1 (as a flag for invalid), it means that the flight f is late (and so this state is infeasible.)
                # It also means that we do not need to check any smaller earliness values, and so break
                if addedcost < -1
                    break
                end
                
                # Compute new state
                newschedule[f] = (newtime, r)
                newcost += addedcost
                newrop[r] = (newtime, f)
                newstate = State(newschedule, newcost, newrop)

                # Add new state (with new time)
                push!(successors,(newtime,newstate))
            end

            # Return the statelist, unless it's empty in which case return the invalid state list "flag" with -1s
            if length(successors)>0
                return successors
            else   
                return [(-1.0,-1)]
            end
        else
            # If the flight has already been scheduled, there are no successors. Return the invalid state "flag" with -1s
            return [(-1.0, -1)]
        end
    end

    function expand!()
        new_idx = 1 # Key for state in this stage (n+1)
        stagetable[n + 1] = Array{State}(0) # Initialise state container

        # Go trough all combinations of flight-to-runway assignments
        for f = 1:F
            for r = 1:R
                # We are going to only record non-dominated successors, as candidates to add to the next stage (n+1)
                candidates = Array{State}(0)

                # Consider the last stage's states
                for i = 1:length(stagetable[n])
                    # Generate a list of all successor states from state i
                    successors = generatesuccessors(stagetable[n][i], f, r)

                    # Go through those successors
                    for sc in successors
                        newtime, newstate  = sc

                        # If t is -1, then this successor is invalid.
                        if newtime >= 0
                            # Assume a state does not dominate, unless we find later that it does
                            dominates = false

                            # Check for domination in each of the candidates
                            for (idx, rivalstate) in enumerate(candidates)
                                # newstate dominates rivalstate when the newstate time is earlier than t, with better cost for the same flights scheduled
                                if newtime < rivalstate.rop[r][1] && sameflights(newstate, rivalstate) && newstate.cost <= rivalstate.cost
                                    # There are no successors to a deadend state under the generatesuccessors function
                                    deadend = State([(-1.0, 1) for i = 1:F], 0.0, [(-1.0, -1) for i = 1:R])

                                    # If we've dominated before, we don't want to explore the dominating state (newstate) twice, so make a deadend.
                                    # Otherwise, do replace the dominated state, with this new one.
                                    candidates[idx] = dominates ? deadend : newstate

                                    # We have dominated.
                                    dominates = true
                                end
                            end
                            if !dominates
                                # If there is no domination, this is a new state to add to the candidate list.
                                push!(candidates,newstate)
                            end
                        end
                    end          
                end
                # Add the successful candidates (which have not been dominated) to the list of states for stage n+1
                append!(stagetable[n + 1], candidates)
            end
        end
    end

    # Initial stage's state
    init_state = State([(-1.0, -1) for i = 1:F], 0.0, [(-1.0, -1) for i = 1:R]) # -1 means "as of yet, undecided".
    stagetable[1] = State[init_state]

    # Main loop
    for n = 1:F
        println(n) # Stage number report
        expand!()
        stagetable[n] = Array{State}(0) # We don't need to keep old stages in memory    
    end

    #println(stagetable[end])
    
    cheapeststate = reduce((x, y) -> x.cost <= y.cost ? x : y, stagetable[end])
             
    println("Optimal schedule times -> $(cheapeststate.schedule)")
    println("Optimal schedule cost  -> $(cheapeststate.cost) \n")

    minsched = [x[1] for x in cheapeststate.schedule]

    # writedlm("./tmp/schedule.txt", minsched)

end

@time solvedp(earlytimes,targets,dependency,proctimes,maxdelays,fcost,cost_early,cost_late,runways)
