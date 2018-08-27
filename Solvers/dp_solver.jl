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

targets = vec(readdlm("./tmp/arrival_t.txt",Float32))
proctimes = readdlm("./tmp/sep_t.txt",Float32)
classes = convert(Array{UInt8,1},vec(readdlm("./tmp/class_num.txt",Float32)))
dependency = UInt8[0,0,0,0,0]
#depedency = convert(Array{UInt8,1},vec(readdlm("./tmp/depends.txt",Float32)))


#targets = Float32[t for t = 1:flights]
#dependency = UInt8[0 for t = 1:flights]
#proctimes = Float32.(rand(3:3, flights, flights))

#for d = 1:flights
#    proctimes[d,d] = 0
#end

# Number of runways
runways = convert(UInt8, 1)

# Cost function
fcost(t, target, coeff=1, deg=1, max_delay=1000) = t - target < max_delay ? coeff * (t - target)^deg : Inf32

struct State
    schedule::Array{Tuple{Float32,Int8}}
    cost::Float32
    rop::Array{Tuple{Float32,Int8}}
end

function solvedp(targets::Array{Float32}, dependency::Array{UInt8}, proctimes::Array{Float32,2}, fcost::Function, runways=1::UInt8)

    F = length(targets) # number of flights
    S = F + 1   # number of stages
    R = runways # number of runways
    n = 1   # initialising stage counter
    turnovertime = 3    # turnaround time for a plane before they can make another flight

    dependentflights = [dependency[i] for i = 1:F if dependency[i] != 0]

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

    function generatestate(state::State, f, r)
        if state.schedule[f][2] == -1
            assigntime = 0
            # Check if there is an dependency
            # if dependency[f] != 0
            #     # Check if the dependency has been satisfied
            #     if state.schedule[dependency[f]][1] == -1
            #         return (-1, -1)
            #     end
            #     assigntime = state.schedule[dependency[f]][1] + turnovertime
            # end

            # copy over information from the old state
            new_schedule, new_rop, new_cost  = copy(state.schedule), copy(state.rop), copy(state.cost)

            prev, precedingflight = state.rop[r]

            precedingflight = precedingflight == -1 ? f : precedingflight
            assigntime = max(assigntime, targets[f], prev + proctimes[f,precedingflight])
            addedcost = fcost(assigntime, targets[f])

            if addedcost == Inf32
                return (-1, -1)
            end

            new_schedule[f] = (assigntime, r)
            new_cost = new_cost + addedcost
            new_rop[r] = (assigntime, f)

            new_state = State(new_schedule, new_cost, new_rop)

            return (assigntime, new_state)
        end

        return (-1, -1)
    end

    function expand!()
        new_idx = 1
        stagetable[n + 1] = Dict{Int64,State}()
        for f = 1:F
            for r = 1:R
                setofstates = Dict{Int64,State}()
                for i = 1:length(stagetable[n])
                    t, new_state = generatestate(stagetable[n][i], f, r)
                    explored = false
                    if t != -1
                        for (idx, state) in setofstates
                            if t == state.rop[r][1]
                                #&& samedependency(new_state, state)
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
                merge!(stagetable[n + 1], setofstates)
            end
        end
    end

    statesexpanded = 1
    # Main loop
    for n = 1:F
        expand!()
        stagetable[n] = Dict{Int64,State}()
        println(length(stagetable[n]))
        statesexpanded += length(stagetable[n + 1])
    end

    println(statesexpanded)
    println(length(stagetable[end]))

    min_cost_key = reduce((x, y) -> stagetable[end][x].cost <= stagetable[end][y].cost ? x : y, keys(stagetable[end]))

    println(stagetable[end][min_cost_key])


end

@time solvedp(targets, dependency, proctimes, fcost, runways)
