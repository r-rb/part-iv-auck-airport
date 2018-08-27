using JuMP, Gurobi

## MIP Solver
solver = GurobiSolver(OutputFlag=0)

## Parameters

# t = vec(readdlm("./tmp/arrival_t.txt"))
# c = vec(readdlm("./tmp/delay_cost.txt"))
# set_up = readdlm("./tmp/proc_t.txt")
# d_max = vec(readdlm("./tmp/max_delay.txt"))

t = [1,2,3,4]
c = [1,1,1,1]
set_up = [3 3 3 3;3 3 3 3;3 3 3 3;3 3 3 3]
d_max = [100 100 100 100]

## Pre-checks
P = length(c) # Number of planes
l = zeros(P)

#assert(all(l.>=0))
#assert(length(t)==P)
#assert(length(l)==P)
#assert(length(d_max)==P)
#assert(size(set_up)==(P,P))

## Computed value
BigM = Array{Float64}(P, P)
for p = 1:P
    	for q = 1:P
        		BigM[p,q] = 2 * d_max[p] + 2 * d_max[q] + 2 * abs(t[p] - t[q]) + l[p] + l[q] # This is chosen based on a traignle inequality argument, below.
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




###########################################################################################################




## Model
m = Model(solver=solver)

## Variables
@variable(m, a[1:P]) # Scheduled arrival times
@variable(m, e[1:P]) # Scheduled ending times
@variable(m, d[1:P] >= 0) # Scheduled delays
@variable(m, L[1:P,1:P]) # Time between the first plane, p, finishing and the second, q, arriving
@variable(m, W[1:P,1:P] >= 0) # The smallest window of time that contains all intervals of time in which either plane p or plane q is landing.
@variable(m, G[1:P,1:P] >= 0) # The gap between plane p ad q's landings
@variable(m, A[1:P,1:P], Bin) # Binary matrix; entry (p,q) is equal to 1 if plane p arrives before plane q, and 0 otherwise.

## Objective
@objective(m, Min, dot(c, d)) # Minimise the total cost of delays

## Constraints
@constraint(m, a .== t + d) # The arrival time is the ideal arrival time, plus delay
@constraint(m, e .== a + l) # The ending time is the arrival time plus time spent on runway
@constraint(m, d .<= d_max) # Maximum delay
for p = 1:P
    	for q = 1:P
        		@constraint(m, L[p,q] == e[p] - a[q]) # By the definition of L
		
        		@constraint(m, W[p,q] >= L[p,q]) # W[p,q] == maximum(L[p,q], L[q,p]), constraint I
        		@constraint(m, W[p,q] >= L[q,p]) # W[p,q] == maximum(L[p,q], L[q,p]), constraint II
        		@constraint(m, W[p,q] <= L[p,q] + BigM[p,q] * A[p,q]) # W[p,q] == maximum(L[p,q], L[q,p]), constraint III
        		@constraint(m, W[p,q] <= L[q,p] + BigM[p,q] * (1 - A[p,q])) # W[p,q] == maximum(L[p,q], L[q,p]), constraint IV

        		if p != q
            			@constraint(m, G[p,q] + l[p] + l[q] == W[p,q]) # The window W is the time the two planes spend each on the runway, plus the gap between these planes.
            			@constraint(m, G[p,q] >= set_up[p,q] .* A[p,q]) # Enforce set-up times
            			@constraint(m, A[p,q] + A[q,p] == 1) # Plane p comes before plane q, or q before p, but not both.
        		end
    	end
end
# Now for some constraints that should help make the problem easier to solve, but aren't necessary in enforcing the logic of the problem.
# The first is to get an upper bound on each delay.
# In the very worst case scenario, plane p is scheduled to arrive first, but arrives last, after all the other planes have arrived one after the other, incurring times of sum(l)-l[p]+(P-1)*maximum(set_up) in total. Therefore
for p = 1:P
    	@constraint(m, d[p] <= sum(l) - l[p] + (P - 1) * maximum(set_up))
end
# Given a sequence of planes pqrs..., plane p comes before all of them and so will have (P-1) ones in its row of the A matrix.
# Plane q has one fewer, (P-2), and plane r has (P-3). This continues up until the final plane numbered P, which has all zeros.
# The total number of ones in the A matrix is therefore
# \sum_{p=1}^{P} (P-p) = \sum_{p=1}^{P} P - \sum_{p=1}^{P} p
#					   = P^2 - P(P+1)/2
#					   = P(P-1)/2
@constraint(m, sum(A) == P * (P - 1) / 2)
# "Coming before" is a transitive property. What this means is that if p comes before q, and q comes before r, then p comes before r.
# This fact can put some more constraints on the A matrix.
for p = 1:P
    	for q = 1:P
        		for r = 1:P
            			@constraint(m, A[p,q] + A[q,r] <= 1 + A[p,r])
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




###########################################################################################################




## Solve
status = solve(m)

## Get solution
objective_value = getobjectivevalue(m)
arrivals = getvalue(a)
exits = getvalue(e)
ideals = t

# Save file
writedlm("./tmp/schedule.txt", arrivals, "\n")

