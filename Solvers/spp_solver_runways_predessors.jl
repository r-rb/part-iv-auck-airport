using JuMP, Gurobi

# Tolerance
tol = 1e-6

# Sub-minute resolution
res = 1

# MIP Solver
solver = GurobiSolver(OutputFlag = 0)

# OR Case?
orcase = true

# How many runways do you want to consider
R = 3

# Load in data
clate = vec( readdlm("./tests/cost_late.txt") )
cearly = vec( readdlm("./tests/cost_early.txt") )
xbar = vec( readdlm("./tests/target_t.txt") )
rmin = minimum(readdlm("./tests/early_t.txt"))
r = floor.(Int,  res*( vec(readdlm("./tests/early_t.txt"))-rmin ) )
dmax = floor.(Int, res*vec(readdlm("./tests/max_delays.txt"))) + xbar - r
p = round.(Int, res*readdlm("./tests/proc_t.txt"))

# pred

if !orcase
	c = round.(Int, vec(readdlm("./tmp/class_num.txt")))
else
	c = Int[i for i in 1:length(clate)]
end

F = length(clate) # Number of flights
C = length(c) # Number of classes

# Minimum and maximum separation time between each plane and any subsequent plane.
# "For any plane, what is the min/max separation time between a given plane and any subsequent plane.?"
minp = minimum(p,2)
maxp = maximum(p,2)

# The number of discrete time units to consider
N = maximum(r) + maximum(dmax) + maximum(p)

# The number of time-related rows in an SPP column
# The triangular term involving S comes from the number of unique pairs between classes
K = N * C*(C+1)/2
# The total number of rows. The combined rows from the time-related blocks and the flight-related blocks
row_num = F + (R * K)
# Each column corresponds to a single flight, with a given delay.
# So the number of columns to consider for each flight is just the maximum delay.
col_num = Int(sum(dmax)*R)
println(" The number of columns are: $col_num")

# Objective function
function fcost(t, target, earliest, max_delay=100, coeff_early=1, coeff_late= 1, deg=1)
    if (t > target + max_delay) | (t < earliest)
        # Just a flag to show that the cost function is undefined/infinite
        return 99999
    end

    # Piecewise linear objective
    if t <= target
        return coeff_early * (target - t)
    else
        return coeff_late * (t - target)
    end
end

# Initialise arrays
A = zeros(Bool, row_num, col_num)
cost = zeros(Float64, col_num)
plane = zeros(Int, col_num)
scht = zeros(Float64, col_num)

println("The length of the plane vector is  $(length(cost))")

# Column index (how many columns we have generated so far)
j = 1
println("Generating SPP array...")
# Generate each flight's columns
for f = 1:F
	for rw = 1:R
		# Generate a column for each possible delay
		for d = 1:dmax[f]
			# Fill each class block.
			# We consider every class-pair between this flight f's class and every class, s
			# This should be considered to be the class
			for cl = 1:C
				# We need to fill in ones to enforce separation times.
				# We will step through time units up to the separation time.
				for pr = 1:p[c[f],cl]

					# We are considering the pair (s[f],cl) to be equivalent to (cl,s[f]).
					# WLOG, we will set the first "coordinate" to be the smaller one.
					# See the below comment.
					if cl <= c[f]
						# pairnum represents the index of a given class pair.
						# For example, given the pairs
						# (1,1),(1,2),(1,3),(2,2),(2,3),(3,3)
						# Then providing 2 and 3 (as c[f] and cl) would return pairnum = 5
						# In other words, we are enumerating these pairs.
						pairnum = (c[f]*(c[f]-1)/2 + cl -1)
					else
						# NB this is identical to the above line, up to c[f] interchange with cl
						pairnum = (cl*(cl-1)/2 + c[f] -1) 
					end
					# Skip block of flights: F
					# Find the pairnum'th block (each block is size N, the number of time units): pairnum*N - 1
					# (Minus one because we want to be just before the block starts.)
					# Now move to the arrival time: r[f]
					# Incur delays and processing time: d+pr
					row = Int( F + rw*(N*pairnum - 1 + r[f] + d + pr)  ) # pairnum is a float because of division by 2, but this should be Int.
					A[row,j] = 1

				end

			end
			
			# Record which flight this column corresponds to
			plane[j] = f
			scht[j] = r[f] + d - 1 # Minus 1 because we index from 1 in Julia, whereas time starts from 0
			A[f,j] = 1 # Set the flight block's unit
			cost[j] = fcost(scht[j]/res + rmin, xbar[f]+rmin, r[f], dmax[f], cearly[f], clate[f])# ????

			# Increment counter
			j = j + 1

		end

	end

end


println("Building model...")

env = Gurobi.Env()
setparam!(env,"Presolve",1)
model = Gurobi.Model(env,"spp",:minimize)
add_bvars!(model,cost)
for rw in 1:F
	add_constr!(model,A[rw,:],'=', 1.0)
end
for rw in F+1:row_num
	rw = convert(Int,rw)
	add_constr!(model, A[rw,:], '<', 1.0)
end
update_model!(model)

println("Building model...")
optimize(model)
objv  = get_objval(model)
println("The objective is $(objv)")

# Solve
# 

# m = Model(solver = solver)
# @variable(m, x[1:col_num], Bin)
# @objective(m, Min, dot(cost,x))
# @constraint(m, A*x .<= 1)
# @constraint(m, A[1:F,:]*x .== 1)
# println("Solving...")
# status = solve(m)
# X = getvalue(x)

# println("Cost is $(dot(cost,X))")

# # Generate the schedule
# schedule = zeros(Float64, F)
# # Check each column,
# for j=1:size(X,1)
# 	# If the column is selected,
# 	if X[j]+tol>=1
# 		# Record that this plane is scheduled
# 		schedule[plane[j]] = scht[j]/res + rmin
# 	end
# end

#writedlm("./tmp/spp_mat.txt", A, ",")
#writedlm("./tmp/schedule.txt", schedule, ",")
