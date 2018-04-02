using JuMP, Clp

## LP Solver
solver = ClpSolver()

## Variables
P = 2 # Number of planes
c = [5,3]	# Cost of delays for each plane
T = [1, 2]	# Ideal arrival time
l = [2, 0.5] # Time spent on the runway

## Model
m = Model(solver = solver)

## Variables
@variable(m, A[1:P]) # Scheduled arrival times
@variable(m, d[1:P] >= 0) # Scheduled delays

## Objective
@objective(m, Min, dot(c,d)) # Minimise the total cost of delays

## Constraints
for p=1:P-1
	@constraint(m, A[p]+l[p] <= A[p+1]) # Planes must arrive in order
end
@constraint(m, A .== T + d) # The arrival time is the ideal arrival time, plus delay

## Solve
status = solve(m)

## Print solution
println("Objective value: ", getobjectivevalue(m))
println("Arrival schedule: ", getvalue(A))
