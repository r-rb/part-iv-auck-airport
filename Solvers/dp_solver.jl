# targets = readdlm("../Sim/tmp/arrival_t.txt", Float32)
# maxdelay = readdlm("../Sim/tmp/max_delay.txt", Float32)
# classes = readdlm("../Sim/tmp/class_num.txt", UInt8)

# Targets for the flights
targets = Float32[1,2,5,8]

# Index of flights that to be processed before 
# the corresponding flight as the same plane is being used.
dependency = UInt8[0,0,0,2]

# Processing times ()
proctimes = convert(Array{Float32,2}, [2 3 2 4; 2 3 4 5; 4 4 2 1; 3 7 2 0])

# Number of runways
runways = convert(UInt8, 1)

fcost(coeff, deg, t, target, max_delay=100) = t - target < max_delay ? coeff * (t - target)^deg : Inf32

struct State
    schedule::Array{Tuple{Float32,Int8}}
    cost::Float32
    rop::Array{Tuple{Float32,Int8}}
end


function solvedp(targets::Array{Float32}, dependency::Array{UInt8}, proctimes::Array{Float32,2}, fcost::Function, runways=1::UInt8)

    F = length(targets)
    S = F + 1
    R = runways

    stagetable = Array{Dict{Int64,State}}(1, S)

    init = Dict(1 => State([(-1.0, -1) for i = 1:F], 0.0, [(-1.0, -1) for i = 1:R]))

    #println(init)

    
    function expand!(n)
        for f = 1:F
            for r = 1:R
            
            end
        end
    end


    for n = 1:F
        expand!(n)
    end


end


solvedp(targets, dependency, proctimes, fcost, runways)

