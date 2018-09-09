using JuMP, Gurobi

## MIP Solver
solver = GurobiSolver(OutputFlag=1)

# OR Library Case
xbar = vec(readdlm("./tests/target_t.txt", Float32))
p = readdlm("./tests/proc_t.txt", Float32)

dep = UInt8[0 for t = 1:length(xbar)]
r = vec(readdlm("./tests/early_t.txt", Float32))
dmax = vec(readdlm("./tests/max_delays.txt", Float32))
ce = vec(readdlm("./tests/cost_early.txt", Float32))
cl = vec(readdlm("./tests/cost_late.txt", Float32))

F = length(xbar) # Number of flights
l = r + dmax # Latest arrival time

## Model
m = Model(solver=solver)

## Variables
@variable(m, x[1:F]) # Scheduled arrival times
@variable(m, delta[1:F,1:F], Bin) # Binary matrix; entry (f,g) is equal to 1 if plane f arrives before plane g, and 0 otherwise.
@variable(m, earliness[1:F] >= 0)
@variable(m, lateness[1:F] >= 0)


## Objective
@objective(m, Min, dot(ce,earliness) + dot(cl,lateness))

## Constraints
@constraint(m, r .<= x) # Earliest arrival time
@constraint(m, x .<= l) # Latest arrival time
for f = 1:F
	for g = 1:F
		@constraint(m, x[f] + p[f,g]*delta[f,g] <= x[g] + (l[f]-r[g])*delta[g,f]) # Minimum separation times
		if g != f
			@constraint(m, delta[f,g] + delta[g,f] == 1) # Force an ordering
		end
	end
	if dep[f] > 0
		@constraint(m, delta[dep[f],f] == 1) # Dependencies
	end
end
@constraint(m, earliness .>= xbar - x) # Earliness
@constraint(m, lateness .>= x - xbar) # Lateness

## Solve
status = solve(m)

## Get solution
objective_value = getobjectivevalue(m)
arrivals = getvalue(x)

println(arrivals)
println(xbar)

