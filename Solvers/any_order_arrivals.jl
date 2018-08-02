using JuMP, Clp

## LP Solver
solver = ClpSolver()

## Parameters
c = [5., 3.]	# Cost of delays for each plane
t = [1., 2.]	# Ideal arrival time
l = [2., 0.5] # Time spent on the runway
P = length(c) # Number of planes
M = maximum(c) # Big-M

## Model
m = Model(solver = solver)

## Variables
@variable(m, a[1:P]) # Scheduled arrival times
@variable(m, e[1:P]) # Scheduled ending times
@variable(m, S[1:P,1:P]) # The latest arrival time out of two planes
@variable(m, F[1:P,1:P]) # The earliest finishing time out of two planes
@variable(m, G[1:P,1:P] >= 0) # The gap between the finishing and arrival of two planes
@variable(m, d[1:P] >= 0) # Scheduled delays
#@variable(m, L[1:P,1:P]) # Time between the first plane finishing and the second arriving
#@variable(m, L_abs[1:P,1:P] >= 0) # Absolute value of L
#@variable(m, L_pos[1:P,1:P] >= 0) # Positive part of L
#@variable(m, L_neg[1:P,1:P] >= 0) # Negative part of L

## Objective
@objective(m, Min, dot(c,d)) # Minimise the total cost of delays

## Constraints
@constraint(m, S .== F + G) # The start time of the second plane is the finish time of the first, plus the gap between them
@constraint(m, a .== t + d) # The arrival time is the ideal arrival time, plus delay
@constraint(m, e .== a + l) # The ending time is the arrival time plus time spent on runway
#@constraint(m, G .<= L) # G[p,q] is the minimum of L[p,q] and L[q,p]
for p = 1:P
	for q = 1:P
		@constraint(m, S[p,q] >= a[p]) # S[p,q] is the max of A[p] and A[q], constraint I
		@constraint(m, S[p,q] >= a[q]) # S[p,q] is the max of A[p] and A[q], constraint II

		@constraint(m, F[p,q] <= e[p]) # F[p,q] is the min of e[p] and e[q], constraint I
		@constraint(m, F[p,q] <= e[q]) # F[p,q] is the min of e[p] and e[q], constraint II
		
		#@constraint(m, L[p,q] == e[p] - a[q]) # By the definition of L

		@constraint(m, G[p,q] == G[q,p]) # G is symmetric
	end
end
#@constraint(m, L .== L_pos - L_neg)
#@constraint(m, L_abs .== L_pos + L_neg)

## Solve
status = solve(m)

## Print solution
println("Objective value: ", getobjectivevalue(m))
println("Arrival schedule: ", getvalue(a))
println("Runway exit times: ", getvalue(e))
println("F: ", getvalue(F))
println("S: ", getvalue(S))
println("G: ", getvalue(G))
#println("L: ", getvalue(L))
