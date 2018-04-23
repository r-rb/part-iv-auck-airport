using JuMP,Gurobi

function solve_model(seperation,planes,costs,d_max,solver = GurobiSolver(Presolve=1))

    ## Inputs:
        # c -> cost array which prices the delay for any plane
        # p -> dictionary of planes with the class of the plane and ideal arrival time
        # s -> dictionary of seperation times for all pairwise class combinations (time on runway built into it)
        # t->  array of targeted times based on horizon
        # d_max -> max delay
    ## Output:
        # m-> model to be solved

    P = length(costs)
    t = [planes[x]["arr_time"] for x = 1:P]

    M = 500
    c = costs

    m = Model(solver = solver)

    @variables m begin
        A[1:P] >= 0 # time assigned to plane p
        δ[1:P,1:P],Bin # δ_{p,q} is  1 if q immediately follows p else 0
        f[1:P],Bin # 1st on runway
        l[1:P],Bin # last on runway
    end

    # minimise the deviation * cost
    @objective(m,Min,sum((A[i] -t[i])*c[i] for i=1:P))

    # only one first and last plane on the runway
    @constraint(m,sum(f[i] for i = 1:P)==1)
    @constraint(m,sum(l[i] for i = 1:P)==1)

    # adding in constraints
    for p = 1:P
        
        # make sure the plane is assigned to land within its landing window
        @constraint(m, A[p] <= t[p] + d_max[p])
        @constraint(m, t[p] <= A[p] )

        # constraining the binary matrix
        @constraint(m,sum(δ[i,p] for i = 1:P) + f[p] == 1)
        @constraint(m,sum(δ[p,i] for i = 1:P) + l[p] == 1)
        for q = 1:P

            if p !=q

                # make sure planes dont land on eachother using big M constraint
                @constraint(m, A[p] + seperation[planes[p]["class"]][planes[q]["class"]] <= A[q] + M * (1 - δ[p,q]))
                
                # keep the relative ordering of planes of same class constant
                if t[p]<=t[q] && planes[p]["class"] == planes[q]["class"]
                    @constraint(m,A[p]<=A[q]) 
                end
            end

            # By definition of δ, a plane cant land immediately after itself
            if p ==q
                @constraint(m,δ[p,p] == 0)
            end
        end
    end



    ## Solve
    print("Solving model...\n")
    status = solve(m)


    ## Print solution
    print("Solving finished.\n")
    if status == :Optimal
        ## Get solution
        objective_value = getobjectivevalue(m)
        arrivals = getvalue(A)
        deltas = getvalue(δ)
        first = getvalue(f)
        last = getvalue(l)
        println("Objective value: ", objective_value)
        println("Arrival schedule: ", arrivals)
        println("Deltas: ", deltas)
        println("First: ", first)
        println("Last: ", last)
    else
        println("Status: ", status)
    end
end


classes = ["H","L","M"]
# how many planes
P = 10

# plane info dictionaries
p = Dict(i => Dict("class" => classes[rand(1:end)], "arr_time" => 2*(P+1-i)) for i=1:P)

# seperation times ( runway times can be added in for simplicity)
s = Dict("H" => Dict("H" => 2.0,
                    "L" => 3.0, 
                    "M" => 2.5),
        "L" => Dict("H" => 2.0,
                    "L" => 3.0, 
                    "M" => 2.5),            
        "M" => Dict("H" => 2.0,
                    "L" => 3.0, 
                    "M" => 2.5
                    ))
# cost array
c = ones(P)

# max delay
d_max  = 10*P * ones(c)

solve_model(s,p,c,d_max)