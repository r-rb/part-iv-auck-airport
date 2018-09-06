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
        return Inf32
    end

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
    stagetable = Array{Dict{Int64,State}}(1, S) # All the valid and non-dominated states for this stage

    println("==============================================================================")
    println("Inputted target times  -> $targets \n")

    # ???
    function samedependency(s1, s2)
        for d in dependentflights
            if (s1.schedule[d][1] * s2.schedule[d][1]) < 0
                return false
            end
        end
        return true
    end

    # Find all successor states, where on the next stage we land f on runway r
    function generatestates(state::State, f, r)

        # If this flight has not already been scheduled:
        if state.schedule[f][2] == -1

            # Initialise a time where if a dependency for flight f exists 
            # then flight f must be scheduled after it.
            dependencytime = 0

            # Check if there is an dependency
            if dependency[f] != 0

                # Check if the dependency has been satisfied, return if it hasn't
                if state.schedule[dependency[f]][1] == -1
                    return [(-1, -1)]
                end
                
                # flight f must be scheduled after dependencytime
                dependencytime = state.schedule[dependency[f]][1] + turnovertime
            end
            
            # Initialise an array of successors to add to 
            newstates = Array{Tuple{Float32,State}}(0)
            
            # Get the previous time and index of the previous flight on the runway r.
            prev, precedingflight = state.rop[r]
            precedingflight = precedingflight == -1 ? f : precedingflight # if precedingflight = -1 then f is the first flight on the runway

            # This is time when flight f must land after to meet wake seperation constraints
            seperationtime = prev + proctimes[precedingflight,f]

            # Return the difference between the most restrictive constraint and the target times:
            # These can be earliest arrival time, dependencytime and separationtime
            delaywidth = targets[f] - max(dependencytime,seperationtime,earlytimes[f])

            # If the delaywidth is negative then there are no early arrivals as the target time 
            # is earlier than the time f
            delaywidth = delaywidth < 0 ? 0 : delaywidth
            
            # Values to offset target time by to early arrvials
            kvals = Float32[k for k = 0:floor(Int,delaywidth)]
            append!(kvals,delaywidth) # append the 

            for k in kvals
                new_schedule, new_rop, new_cost  = copy(state.schedule), copy(state.rop), copy(state.cost)
                new_assigntime = max(dependencytime,seperationtime,targets[f] - k)
                addedcost = fcost(new_assigntime, targets[f], earlytimes[f], maxdelays[f],cost_early[f],cost_late[f])
                if addedcost == Inf32
                    push!(newstates,(-1.0,State(new_schedule,Inf32,new_rop)))
                    continue
                end
                new_schedule[f] = (new_assigntime, r)
                new_cost = new_cost + addedcost
                new_rop[r] = (new_assigntime, f)
                new_state = State(new_schedule, new_cost, new_rop)
                push!(newstates,(new_assigntime,new_state))
            end
            return newstates
        end

        return [(-1, -1)]
    end

    function expand!()
        new_idx = 1 # Key for state in this stage (n+1)
        stagetable[n + 1] = Dict{Int64,State}() # Initialise state container

        # Go trough all combinations of flight-to-runway assignments
        for f = 1:F
            for r = 1:R
                setofstates = Dict{Int64,State}() # Candidate states to add to the stage's state container

                # Consider the last stage's states
                for i = 1:length(stagetable[n])
                    # Generate a list of all successor states from state i
                    newstates = generatestates(stagetable[n][i], f, r)

                    # Go through those successors
                    for st in newstates
                        t, new_state  = st
                        explored = false

                        # If t is -1, then either we haven't scheduled flight f 
                        if t != -1
                            for (idx, state) in setofstates
                                if t == state.rop[r][1] && samedependency(new_state, state)
                                    explored = true
                                    if new_state.cost < state.cost
                                        setofstates[idx] = new_state
                                    end
                                end
                            end
                            if !explored
                                setofstates[new_idx] = new_state
                                new_idx += 1
                            end
                        end
                    end          
                end
                merge!(stagetable[n + 1], setofstates)
            end
        end
    end

    # Initial stage's state
    init_state = State([(-1.0, -1) for i = 1:F], 0.0, [(-1.0, -1) for i = 1:R]) # -1 means "as of yet, undecided".
    stagetable[1] = Dict(1 => init_state)

    # Main loop
    for n = 1:F
        println(n) # Stage number report
        expand!()
        stagetable[n] = Dict{Int64,State}() # We don't need to keep old stages in memory    
    end

    #println(stagetable[end])
    
    min_cost_key = reduce((x, y) -> stagetable[end][x].cost <= stagetable[end][y].cost ? x : y, keys(stagetable[end]))
             
    println("Optimal schedule times -> $(stagetable[end][min_cost_key].schedule)")
    println("Optimal schedule cost  -> $(stagetable[end][min_cost_key].cost) \n")

    minsched = [x[1] for x in stagetable[end][min_cost_key].schedule]

    # writedlm("./tmp/schedule.txt", minsched)

end

@time solvedp(earlytimes,targets,dependency,proctimes,maxdelays,fcost,cost_early,cost_late,runways)
