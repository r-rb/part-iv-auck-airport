using JuMP, Gurobi

## Parameter
prechecks_on = false

## MIP Solver
solver = GurobiSolver()

c = [2, 1, 3, 4, 10, 1, 2, 3, 1, 2, 3, 3, 3]	# Cost of delays for each plane
r = [0, 1, 2, 1, 3, 2, 3, 4, 3, 4, 3, 5, 2]	# Ideal arrival time
s = [1, 2, 1, 2, 2, 3, 2, 1, 2, 2, 3, 3, 2]	# Class for each plane
d_max = [12, 15, 10, 20, 30, 30, 30, 30, 20, 30, 40, 40, 40] # Maximum allowable delay for each plane
p = [ [1 2 4]
	  [1 3 4] 
	  [2 3 5] ] # Processing times for each class, sequence dependent

P = length(c) # Number of planes
C = size(p,1) # Number of classes
D = 3

## Pre-checks
if prechecks_on
	assert(all(r.>=0))
	assert(minimum(r)==0)
	assert(length(r)==P)
	assert(length(s)==P)
	assert(length(d_max)==P)
	assert(maximum(s)==C)
end

N = maximum(r) + maximum(d_max) + maximum(p)
K = N*C*(C+1)/2
row_num = P + D*K
col_num = D*sum(d_max)

A = zeros(Int8, row_num, col_num)
cost = zeros(Float64, col_num)

i = 1
for pl = 1:P
	for de = 1:D
		for d = 1:d_max[pl]
			for cl = 1:C
				for pr = 1:p[s[pl],cl]
					if cl <= s[pl]
						triang = (s[pl]*(s[pl]-1)/2 + cl -1)
					else
						triang = (cl*(cl-1)/2 + s[pl] -1)
					end

					A[Int(P+triang*N+r[pl]+d+pr-1+mod(de-1,D)*K),i] = 1
					A[Int(P+triang*N+r[pl]+d+pr-1+mod(de,D)*K),i] = 1
				end
			end
		
			A[pl,i] = 1
			cost[i] = (d-1)^2*c[pl]
			i = i + 1
		end
	end
end

## Solve
print("Solving...")
m = Model(solver = solver)
@variable(m, x[1:col_num], Bin)
@objective(m, Min, dot(cost,x))
@constraint(m, A*x .<= 1)
@constraint(m, A[1:P,:]*x .== 1)
status = solve(m)
