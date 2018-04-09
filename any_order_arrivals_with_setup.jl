using JuMP, Cbc

## MIP Solver
solver = CbcSolver()

## Parameters
c = [2, 1, 2, 4]	# Cost of delays for each plane
t = [1, 2, 2, 3]	# Ideal arrival time
l = [2, 0.5, 1, 2] # Time spent on the runway
set_up = [	[0 5 2 3]
			[1 0 2 3]
			[2 0 3 4]
			[2 0 4 4]	] # Set-up times: entry (p,q) is the minimum time required between the finish of plane p and the arrival of plane q
d_max = [20, 20, 20, 20] # Maximum allowable delay for each plane

## Pre-checks
P = length(c) # Number of planes
assert(all(l.>=0))
assert(length(t)==P)
assert(length(l)==P)
assert(length(d_max)==P)
assert(size(set_up)==(P,P))

## Computed value
BigM = Array(Float64,P,P)
for p = 1:P
	for q = 1:P
		BigM[p,q] = 2*d_max[p] + 2*d_max[q] + 2*abs(t[p]-t[q]) + l[p]+l[q] # This is chosen based on a traignle inequality argument, below.
		# We would like BigM[p,q] >= W[p,q].

		# W == maximum(L[p,q],L[q,p])
		#   <= abs(L[p,q]) + abs(L[q,p])
		#	== abs(e[p]-a[q]) + abs(e[q]-a[p])
		#	== abs(l[p]+a[p]-a[q]) + abs(l[q]+a[q]-a[p])
		#	<= abs(l[p])+abs(a[p]-a[q]) + abs(l[q])+ abs(a[q]-a[p])		By the triangle inequality
		#	== l[p]+l[q] + 2*abs(a[p]-a[q])								Since l >= 0
		#	== l[p]+l[q] + 2*abs(t[p]+d[p]-t[q]-d[q])
		#	<= l[p]+l[q] + 2*( abs(t[p]-t[q])+abs(d[p])+abs(d[q]) )		By the triangle inequality
		#	== 2*abs(d[p])+2*abs(d[q]) + 2*abs(t[p]-t[q]) + l[p]+l[q]
		#	<= 2*d_max[p]+2*d_max[q] + 2*abs(t[p]-t[q]) + l[p]+l[q]
		#	== BigM[p.q]
	end
end

## Model
m = Model(solver = solver)

## Variables
@variable(m, a[1:P]) # Scheduled arrival times
@variable(m, e[1:P]) # Scheduled ending times
@variable(m, d[1:P] >= 0) # Scheduled delays
@variable(m, L[1:P,1:P]) # Time between the first plane, p, finishing and the second, q, arriving
@variable(m, W[1:P,1:P] >= 0) # The smallest window of time that contains all intervals of time in which either plane p or plane q is landing.
@variable(m, G[1:P,1:P] >= 0) # The gap between plane p ad q's landings
@variable(m, A[1:P,1:P], Bin) # Binary matrix; entry (p,q) is equal to 1 if plane p arrives before plane q, and 0 otherwise.

## Objective
@objective(m, Min, dot(c,d)) # Minimise the total cost of delays

## Constraints
@constraint(m, a .== t + d) # The arrival time is the ideal arrival time, plus delay
@constraint(m, e .== a + l) # The ending time is the arrival time plus time spent on runway
@constraint(m, d .<= d_max) # Maximum delay
for p = 1:P
	for q = 1:P
		@constraint(m, L[p,q] == e[p] - a[q]) # By the definition of L
		
		@constraint(m, W[p,q] >= L[p,q]) # W[p,q] == maximum(L[p,q], L[q,p]), constraint I
		@constraint(m, W[p,q] >= L[q,p]) # W[p,q] == maximum(L[p,q], L[q,p]), constraint II
		@constraint(m, W[p,q] <= L[p,q] + BigM[p,q]*A[p,q]) # W[p,q] == maximum(L[p,q], L[q,p]), constraint III
		@constraint(m, W[p,q] <= L[q,p] + BigM[p,q]*(1-A[p,q])) # W[p,q] == maximum(L[p,q], L[q,p]), constraint IV

		if p != q
			@constraint(m, G[p,q]+l[p]+l[q] == W[p,q]) # The window W is the time the two planes spend each on the runway, plus the gap between these planes.
			@constraint(m, G[p,q] >= set_up[p,q].*A[p,q]) # Enforce set-up times
			@constraint(m, A[p,q] + A[q,p] == 1) # Plane p comes before plane q, or q before p, but not both. This constraint is not strictly necessary, but it may decrease the feasible region.
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
# Notice also how W[p,q] = maximum(L[p,q], L[q,p]). At least one of the two arguments must be positive, so W must be too.

## Solve
status = solve(m)

## Get solution
objective_value = getobjectivevalue(m)
arrivals = getvalue(a)
exits = getvalue(e)
ideals = t

## Print solution
if status == :Optimal
	println("Objective value: ", objective_value)
	println("Arrival schedule: ", arrivals)
	println("Runway exit times: ", exits)
else
	println("Status: ", status)
end

## Post-processing
event_times = sort(union(ideals,arrivals,exits))
T = length(event_times)

is_ideally_arrived = Array(Bool, P, T)
is_arrived = Array(Bool, P, T)
is_finished = Array(Bool, P, T)
for p=1:P
	is_ideally_arrived[p,:] = (event_times .>= ideals[p])
	is_arrived[p,:] = (event_times .>= arrivals[p])
	is_finished[p,:] = (event_times .>= exits[p])
end
is_delayed = is_ideally_arrived & !is_arrived
is_landing = is_arrived & !is_finished

## Display schedule
print("\n")
event_line = "|"
for ev = 1:T
	added = "--$(round(event_times[ev],1))"
	event_line *= added * "-"^(7-length(added))
end
event_line *= "--|\n"
print(event_line)

for p = 1:P
	plane_line = "|"
	plane_land = false
	for ev = 1:T
		if is_landing[p,ev]
			if plane_land
				plane_line *= "======="
			else
				plane_land = true
				plane_line *= "---<==="
			end
		else
			if plane_land
				plane_land = false
				plane_line *= "===>---"
			else
				plane_line *= "-------"
			end
		end
	end
	plane_line *= "--|\n"
	print(plane_line)
end
