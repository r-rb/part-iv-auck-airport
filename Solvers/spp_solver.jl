using JuMP, Gurobi

## Tolerance
tol = 1e-6

## Sub-minute resolution
res = 1

## MIP Solver
solver = GurobiSolver(OutputFlag = 1)

c = vec(readdlm("./tmp/delay_cost.txt"))
r_min = minimum(readdlm("./tmp/arrival_t.txt"))
r = floor.(Int, res*(vec(readdlm("./tmp/arrival_t.txt")) - r_min))
s = round.(Int, vec(readdlm("./tmp/class_num.txt")))
d_max = floor.(Int, res*vec(readdlm("./tmp/max_delay.txt")))
p = round.(Int, res*readdlm("./tmp/sep_t.txt"))

## Pre-checks
P = length(c) # Number of planes
C = size(p,1) # Number of classes

#assert(all(r.>=0))
#assert(minimum(r)==0)
#assert(length(r)==P)
#assert(length(s)==P)
#assert(length(d_max)==P)
#assert(maximum(s)==C)
min_p = minimum(p,2)
max_p = maximum(p,2)
#for cl = 1:C
#	assert(minimum(p[cl,:]+min_p).>=max_p[cl])
#end

N = maximum(r) + maximum(d_max) + maximum(p)
K = N*C*(C+1)/2
row_num = P + K
col_num = sum(d_max)

A = zeros(Bool, row_num, col_num)
cost = zeros(Float64, col_num)
plane = zeros(Int, col_num)
sch_t = zeros(Float64, col_num)
i = 1
for pl = 1:P
	for d = 1:d_max[pl]
		for cl = 1:C
			for pr = 1:p[s[pl],cl]
				if cl <= s[pl]
					triang = (s[pl]*(s[pl]-1)/2 + cl -1)
				else
					triang = (cl*(cl-1)/2 + s[pl] -1)
				end
				A[Int(P+triang*N+r[pl]+d+pr-1),i] = 1
			end
		end
		
		plane[i] = pl
		sch_t[i] = r[pl]+d-1
		A[pl,i] = 1
		cost[i] = (d-1)^2*c[pl]
		i = i + 1
	end
end

# Solve
m = Model(solver = solver)
@variable(m, x[1:col_num], Bin)
@objective(m, Min, dot(cost,x))
@constraint(m, A*x .<= 1)
@constraint(m, A[1:P,:]*x .== 1)
status = solve(m)
X = getvalue(x)

schedule = zeros(Float64, P)
for j=1:size(X,1)
	if X[j]+tol>=1
		schedule[plane[j]] = sch_t[j]/res + r_min
	end
end

writedlm("./tmp/spp_mat.txt", A, ",")
writedlm("./tmp/schedule.txt", schedule, ",")
