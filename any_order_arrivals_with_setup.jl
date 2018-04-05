using JuMP, Cbc

## LP Solver
solver = CbcSolver()

## Parameters
c = [1, 1]	# Cost of delays for each plane
t = [1, 2]	# Ideal arrival time
l = [2, 0.5] # Time spent on the runway
set_up = [	[0 5]
			[0 0]	] # Set-up times
d_max = 10 # Maximum allowable delay

## Pre-checks
assert(all(l.>=0))
assert(length(t)==length(c))
assert(length(l)==length(c))

## Computed values
P = length(c) # Number of planes
BigM = Array(Float64,P,P)
for p = 1:P
	for q = 1:P
		BigM[p,q] = 4*d_max + 2*abs(t[p]-t[q]) + l[p]+l[q] # This is chosen based on traignle inequality arguments.
	end
end

## Model
m = Model(solver = solver)

## Variables
@variable(m, a[1:P]) # Scheduled arrival times
@variable(m, e[1:P]) # Scheduled ending times
@variable(m, 0 <= d[1:P] <= d_max) # Scheduled delays
@variable(m, L[1:P,1:P]) # Time between the first plane, p, finishing and the second, q, arriving
@variable(m, W[1:P,1:P] >= 0) # The smallest window of time that contains all intervals of time in which either plane p or plane q is landing.
@variable(m, G[1:P,1:P] >= 0) # The gap between plane p ad q's landings
@variable(m, A[1:P,1:P], Bin) # Binary matrix; entry (p,q) is equal to 1 if plane p arrives after plane q, and 0 otherwise.
@variable(m, S[1:P,1:P] >= 0) # Slack variable for difference between L and L transpose.

## Objective
@objective(m, Min, dot(c,d)) # Minimise the total cost of delays

## Constraints
@constraint(m, a .== t + d) # The arrival time is the ideal arrival time, plus delay
@constraint(m, e .== a + l) # The ending time is the arrival time plus time spent on runway
@constraint(m, W .== L + S) # By the definition of W
for p = 1:P
	for q = 1:P
		@constraint(m, L[p,q] == e[p] - a[q]) # By the definition of L
		
		@constraint(m, S[p,q] <= L[p,q] - L[q,p] + BigM[p,q]*A[p,q]) # S <= abs(L-transpose(L)), positive abs case (see below for an explanation)
		@constraint(m, S[p,q] <= L[q,p] - L[p,q] + BigM[p,q]*(1-A[p,q]) ) # S <= abs(L-transpose(L)), non-positive abs case

		if p != q
			@constraint(m, G[p,q]+l[p]+l[q] == W[p,q]) # The window W is the time the two planes spend each on the runway, plus the gap between these planes.
			@constraint(m, G[p,q] >= set_up[p,q]) # Enforce set-up times
		end
	end
end

# The idea behind this formulation is that if the planes land one after the other you will have a situation like this:

# |----(l[p])----|
#                            |----(l[q])----|
# |-----------------(W[p,q])----------------|
# |-----------------(L[p,q])----------------|
# 				 |-(-L[q,p])-|

# Whereas if the planes are landing at the same time, you have this:
# |----(l[p])----------------|
#               |---------------(l[q])----|
#				<--OVERLAP!-->
# |----------------(W[p,q])---------------|
# |----------------(L[p,q])---------------|
# 				|--(L[q,p])--|

# In the first case, W[p,q] >= l[p] + l[q], while in the second, that inequality is violated. Since G >= 0, this forces no overlap.
# Notice also how W[p,q] = max(L[p,q], L[q,p]).
# The slacks S[p,q] are added to L[p,q] to get L[q,p] if the latter is greater than the first, simply by constraining S <= abs(L-transpose(L)).

## Solve
status = solve(m)

## Print solution
if status == :Optimal
	println("Objective value: ", getobjectivevalue(m))
	println("Arrival schedule: ", getvalue(a))
	println("Runway exit times: ", getvalue(e))
else
	println("Status: ", status)
end
