# targets = readdlm("../Sim/tmp/arrival_t.txt", Float32)
# maxdelay = readdlm("../Sim/tmp/max_delay.txt", Float32)
# classes = readdlm("../Sim/tmp/class_num.txt", UInt8)

# Targets for the flights
# planes = 10
# targets = Float32[i for i = 1:planes]

# # Index of flights that to be processed before the corresponding flight as the same plane is being used.
# dependency = UInt8[0,1,0,0]

# # Processing times
# proctimes = convert(Array{Float32,2},  [0 3 3 3;
#                                         3 0 3 3;
#                                         3 3 0 3;
#                                         3 3 3 0])

# targets = vec(readdlm("./tmp/arrival_t.txt", Float32))
# proctimes = readdlm("./tmp/proc_t.txt", Float32)
# println(proctimes)
# classes = convert(Array{UInt8,1}, vec(readdlm("./tmp/class_num.txt", Float32)))
#dependency = UInt8[0,0,0,0,0]
#dependency = convert(Array{UInt8,1}, vec(readdlm("./tmp/depends.txt", Float32)))
flights =  3
runways = convert(UInt8, 1)

targets = Float32[t for t = 1:flights]
dependency = UInt8[0 for t = 1:flights]

earlytimes = Float32[max(0,t-3) for t = 1:flights]
maxdelays = Float32[100.0 for t = 1:flights]

proctimes = Float32.(rand(3:3, flights, flights))

for d = 1:flights
   proctimes[d,d] = 0
end

# Cost function
fcost(t, target, early, max_delay=100, coeff=1, deg=4) = t - target < max_delay ? coeff * abs(t - target)^deg : Inf32

struct State
    schedule::Array{Tuple{Float32,Int8}}
    cost::Float32
    rop::Array{Tuple{Float32,Int8}}
end

function solvedp(earlytimes::Array{Float32},targets::Array{Float32}, dependency::Array{UInt8}, proctimes::Array{Float32,2},maxdelays::Array{Float32},fcost::Function, runways=1::UInt8)
    println("in")
    F = length(targets) # number of flights
    S = F + 1   # number of stages
    R = runways # number of runways
    n = 1   # initialising stage counter
    turnovertime = 10    # turnaround time for a plane before they can make another flight
    dependentflights = [dependency[i] for i = 1:F if dependency[i] != 0]
    println("==============================================================================")
    println("Inputted target times -> $targets \n")
    stagetable = Array{Dict{Int64,State}}(1, S)

    stagetable[1] = Dict(1 => State([(-1.0, -1) for i = 1:F], 0.0, [(-1.0, -1) for i = 1:R]))

    function samedependency(s1, s2)
        for d in dependentflights
            if (s1.schedule[d][1] * s2.schedule[d][1]) < 0
                return false
            end
        end
        return true
    end

    function generatestates(state::State, f, r)
        if state.schedule[f][2] == -1
            assigntime = 0
            # Check if there is an dependency
            if dependency[f] != 0
                # Check if the dependency has been satisfied
                if state.schedule[dependency[f]][1] == -1
                    return [(-1, -1)]
                end
                assigntime = state.schedule[dependency[f]][1] + turnovertime
            end
            
            newstates = Array{Tuple{Float32,State}}(0)
            
            prev, precedingflight = state.rop[r]

            precedingflight = precedingflight == -1 ? f : precedingflight

            delaywidth = targets[f] - max(assigntime,prev + proctimes[f,precedingflight],earlytimes[f])
            delaywidth = delaywidth < 0 ? 0 : delaywidth
            
            for k = 0:floor(Int,delaywidth)
                new_schedule, new_rop, new_cost  = copy(state.schedule), copy(state.rop), copy(state.cost)
                new_assigntime = max(assigntime, targets[f] - k, prev + proctimes[f,precedingflight])
                println("$k offset gives assigntime of  $(new_assigntime), $(prev + proctimes[f,precedingflight])")
                addedcost = fcost(new_assigntime, targets[f], earlytimes[f], maxdelays[f])
                if addedcost == Inf32
                    push!(newstates,(new_assigntime,(-1,-1)))
                    continue
                end
                new_schedule[f] = (new_assigntime, r)
                new_cost = new_cost + addedcost
                new_rop[r] = (new_assigntime, f)
                new_state = State(new_schedule, new_cost, new_rop)
                push!(newstates,(new_assigntime,new_state))
            end
            println(newstates)
            return newstates
        end

        return [(-1, -1)]
    end

    function expand!()
        new_idx = 1
        stagetable[n + 1] = Dict{Int64,State}()
        for f = 1:F
            for r = 1:R
                setofstates = Dict{Int64,State}()
                 for i = 1:length(stagetable[n])
                    newstates = generatestates(stagetable[n][i], f, r)
                    for st in newstates
                        t, new_state  = st
                        explored = false
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

    # Main loop
    for n = 1:F
        println("Loop $(n) of $(F) ")
        expand!()
        stagetable[n] = Dict{Int64,State}()

        for v in stagetable[n+1]
            println(v[2])
        end
        
    end

    min_cost_key = reduce((x, y) -> stagetable[end][x].cost <= stagetable[end][y].cost ? x : y, keys(stagetable[end]))

    println("Optimal schedule times -> $(stagetable[end][min_cost_key].schedule)")
    println("Optimal schedule cost -> $(stagetable[end][min_cost_key].cost) \n")

    minsched = [x[1] for x in stagetable[end][min_cost_key].schedule]

    # writedlm("./tmp/schedule.txt", minsched)

end

@time solvedp(earlytimes,targets,dependency,proctimes,maxdelays,fcost,runways)
