struct State
    schedule::Array{Tuple{Float32,Int8}}
    cost::Float32
    rop::Array{Tuple{Float32,Int8}}
end

function add_to_array_any(n)
    arr = Array{State}(n)
    for i in 1:n
        new_state = State([(-1.0, -1) for i = 1:1], 0.0, [(-1.0, -1) for i = 1:1])
        arr[i] = new_state
    end
end

function add_to_array(n)
    arr = Array{State}(0)
    for i in 1:n
        new_state = State([(-1.0, -1) for i = 1:1], 0.0, [(-1.0, -1) for i = 1:1])
        push!(arr,new_state)
    end
end

function add_to_dict(n)
    statedict = Dict{Int64,State}()
    for i in 1:n
        new_state = State([(-1.0, -1) for i = 1:1], 0.0, [(-1.0, -1) for i = 1:1])
        statedict[i] = new_state
    end
end

n = 10000000

@time add_to_array(n)

@time add_to_array_any(n)

@time add_to_dict(n)