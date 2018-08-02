using JuMP, Gurobi

## MIP Solver
solver = GurobiSolver()

c = [2, 1, 3, 4, 10, 1, 2, 3, 1, 2, 3, 3, 3]	# Cost of delays for each plane
r = [0, 1, 2, 1, 3, 2, 3, 4, 3, 4, 3, 5, 2]	# Ideal arrival time
s = [1, 2, 1, 2, 2, 3, 2, 1, 2, 2, 3, 3, 2]	# Class for each plane
d_max = [12, 15, 10, 20, 30, 30, 30, 30, 20, 30, 40, 40, 40] # Maximum allowable delay for each plane
p = [ [1 2 4]
	  [1 3 4] 
	  [2 3 5] ] # Processing times for each class, sequence dependent


## Pre-checks
P = length(c) # Number of planes
C = size(p)[1] # Number of classes

assert(all(r.>=0))
assert(minimum(r)==0)
assert(length(r)==P)
assert(length(s)==P)
assert(length(d_max)==P)
assert(maximum(s)==C)
min_p = minimum(p,2)
max_p = maximum(p,2)
for cl = 1:C
	assert(minimum(p[cl,:]+min_p).>=max_p[cl])
end
exit()

N = maximum(r) + maximum(d_max) + maximum(p)
K = N*C^2
row_num = P + K
col_num = sum(d_max)#+ K

A = zeros(Int8, row_num, col_num)
cost = zeros(Float64, col_num)

i = 1
for pl = 1:P
	for d = 1:d_max[pl]
		for cl = 1:C
			for pr = 1:p[s[pl],cl]
				A[P+(cl-1)*N*C+(s[pl]-1)*N+r[pl]+d+pr-1,i] = 1
				A[P+(s[pl]-1)*N*C+(cl-1)*N+r[pl]+d+pr-1,i] = 1
			end
		end
		A[pl,i] = 1
		cost[i] = (d-1)^2*c[pl]
		i = i + 1
	end
end
#for k = 1:K
#	A[P+k,i+k-1] = 1
#end

# Solve
m = Model(solver = solver)
@variable(m, x[1:col_num], Bin)
@objective(m, Min, dot(cost,x))
@constraint(m, A*x .<= 1)
@constraint(m, A[1:P,:]*x .== 1)
status = solve(m)
print(getvalue(x)[1:sum(d_max)])
