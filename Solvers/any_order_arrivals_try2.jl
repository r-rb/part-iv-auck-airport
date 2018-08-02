using JuMP, Clp

## LP Solver
solver = ClpSolver()

## Parameters
c = [5, 3]	# Cost of delays for each plane
t = [1, 2]	# Ideal arrival time
l = [2, 0.5] # Time spent on the runway
P = length(c) # Number of planes

## Model
m = Model(solver = solver)

## Variables
@variable(m, a[1:P]) # Scheduled arrival times
@variable(m, e[1:P]) # Scheduled ending times
@variable(m, d[1:P] >= 0) # Scheduled delays
@variable(m, W[1:P,1:P] >= 0) # The length of time in which either planes p or q are on the runway
@variable(m, L[1:P,1:P]) # Time between the first plane, p, finishing and the second, q, arriving
@variable(m, L_abs[1:P,1:P] >= 0) # Absolute value of L
@variable(m, L_pos[1:P,1:P] >= 0) # Positive part of L
@variable(m, L_neg[1:P,1:P] >= 0) # Negative part of L

## Objective
@objective(m, Min, dot(c,d)) # Minimise the total cost of delays

## Constraints
@constraint(m, a .== t + d) # The arrival time is the ideal arrival time, plus delay
@constraint(m, e .== a + l) # The ending time is the arrival time plus time spent on runway
for p = 1:P
	for q = 1:P
		@constraint(m, L[p,q] == e[p] - a[q]) # By the definition of L

		@constraint(m, W[p,q] <= L_abs[p,q]) # By the definition of W, constraint I
		@constraint(m, W[p,q] <= L_abs[q,p]) # By the defintion of W, constraint II
		@constraint(m, W[p,q] == W[q,p]) # W must be symmetric

		if p != q
			@constraint(m, W[p,q] >= l[p] + l[q]) # The planes' landing times must not overlap.
		end
	end
end
@constraint(m, L .== L_pos - L_neg)	# Split L into signed parts
@constraint(m, L_abs .== L_pos + L_neg)	# Absolute value is the sum of the signed parts


## Solve
status = solve(m)

## Print solution
println("Objective value: ", getobjectivevalue(m))
println("Arrival schedule: ", getvalue(a))
println("Runway exit times: ", getvalue(e))
println("L_abs: ", getvalue(L_abs))
println("L_pos: ", getvalue(L_pos))
println("L_neg: ", getvalue(L_neg))
println("L: ", getvalue(L))
println("W: ", getvalue(W))
