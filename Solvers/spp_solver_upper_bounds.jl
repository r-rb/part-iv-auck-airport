using JuMP, Gurobi

# Tolerance
tol = 1e-6

# Sub-minute resolution
res = 1

# MIP Solver
solver = GurobiSolver(OutputFlag = 1)

# OR Case?
orcase = true

# Load in data
clate = vec( readdlm("./tests/cost_late.txt") )
cearly = vec( readdlm("./tests/cost_early.txt") )
xbar = vec( readdlm("./tests/target_t.txt") )
rmin = minimum(readdlm("./tests/early_t.txt"))
r = floor.(Int,  res*( vec(readdlm("./tests/early_t.txt"))-rmin ) )
dmax = floor.(Int, res*vec(readdlm("./tests/max_delays.txt"))) + xbar - r
p = round.(Int, res*readdlm("./tests/proc_t.txt"))
l = r + dmax # Latest arrival time

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
row_num = F + K
# Each column corresponds to a single flight, with a given delay.
# So the number of columns to consider for each flight is just the maximum delay.
col_num = F+Int(sum(dmax))
println(" The number of columns are: $col_num")

# Objective function
function fcost(t, target, earliest, max_delay=100, coeff_early=1, coeff_late= 1, deg=1)
    if (t < earliest)
        println("beep")
    end
    if (t > target + max_delay) | (t < earliest)
        # Just a flag to show that the cost function is undefined/infinite
        return -1
    end

    # Piecewise linear objective
    if t <= target
        return coeff_early * (target - t)
    else
        return coeff_late * (t - target)
    end
end

# Find a FCFS for upper bound
order = sortperm(xbar)
t = r[order[1]]
fcfscost = 0
for (idx,f) in enumerate(order)
    addedcost = fcost(t,xbar[order[idx]],r[order[idx]],dmax[order[idx]], cearly[order[idx]], clate[order[idx]])
    fcfscost += addedcost
    if addedcost < 0
        fcfscost = Inf32
        break
    end

    if idx < F
        t = max(t + p[f,order[idx+1]],r[order[idx+1]])
    end
end
println("FCFS Cost: $fcfscost")

# Beasley's upper bound
t = r[order[1]]
bscost = 0
for (idx,f) in enumerate(order)
    addedcost = fcost(t,xbar[order[idx]],r[order[idx]],dmax[order[idx]], cearly[order[idx]], clate[order[idx]])
    bscost += addedcost
    if addedcost < 0
        bscost = Inf32
        break
    end

    if idx < F
        t = max(t + p[f,order[idx+1]],xbar[order[idx+1]])
    end
end
println("Beasley Cost: $bscost")

# Set lower bound
ub = min(fcfscost,bscost)

function solvemip(xbar,p,dep,r,l,ce,cl,F,ub=Inf)
	# Preprocessing
	r = max.(r, xbar-ub./ce)
	l = min.(l, xbar+ub./cl)
	## Model
	m = Model(solver=solver)

	## Variables
	@variable(m, x[1:F]) # Scheduled arrival times
	@variable(m, delta[1:F,1:F], Bin) # Binary matrix; entry (f,g) is equal to 1 if plane f arrives before plane g, and 0 otherwise.
	@variable(m, earliness[1:F] >= 0)
	@variable(m, lateness[1:F] >= 0)


	## Objective
	@objective(m, Min, dot(ce,earliness) + dot(cl,lateness))

	## Constraints
	@constraint(m, r .<= x) # Earliest arrival time
	@constraint(m, x .<= l) # Latest arrival time
	for f = 1:F
		for g = 1:F
			if g != f
				@constraint(m, delta[f,g] + delta[g,f] == 1) # Force an ordering
			end

			if l[f]<r[g]
				@constraint(m, delta[f,g] == 1) # Automatic ordering based on lack of time window overlap
				if l[f]+p[f,g]>r[g]
					@constraint(m, x[f]+p[f,g] <= x[g]) # Minimum separation times
				end
			else
				@constraint(m, x[f] + p[f,g]*delta[f,g] <= x[g] + (l[f]-r[g])*delta[g,f]) # Minimum separation times
				if xbar[f] < xbar[g]
					@constraint(m, delta[f,g] >= 1 - (lateness[f] + earliness[g])/(xbar[g]-xbar[f]) ) # STRENGTHENING: gap closing
				end
				@constraint(m, earliness[f]+lateness[f]+earliness[g]+lateness[g] >= (p[f,g]+xbar[f]-xbar[g])*delta[f,g] + (p[g,f]+xbar[g]-xbar[f])*delta[g,f]) # STRENGTHENING: Minimum deviation
				if l[f] < r[g]+p[g,f]
					@constraint(m, delta[g,f]==0 ) #STRENGTHENING: Order deciding
				end
			end
		end
		if dep[f] > 0
			@constraint(m, delta[dep[f],f] == 1) # Dependencies
		end
	end
	@constraint(m, earliness .>= xbar - x) # Earliness
	@constraint(m, earliness .<= xbar - r)
	@constraint(m, lateness .>= x - xbar) # Lateness
	@constraint(m, lateness .<= l - xbar)
	@constraint(m, x+earliness .== xbar + lateness)

	@constraint(m, 2*sum(delta) == F*(F-1)) # STRENGTHENING: Delta sum

	@constraint(m, dot(ce,earliness) + dot(cl,lateness) <= ub) #Upper bound

	## Solve
	status = solve(m)

	## Return solution
	return getobjectivevalue(m), getvalue(x)
end

# MIP upper bound
fcfsdep = Array{Int}(F)
lastf = 0
for (idx,f) in enumerate(order)
	fcfsdep[f] = lastf
	lastf = f
end
(mipcost,~) = solvemip(xbar,p,fcfsdep,r,l,cearly,clate,F,ub)

if !isnan(mipcost)
	ub = min(ub, mipcost)
	r = Int.(max.(r, ceil.(xbar-ub./cearly)))
	l = Int.(min.(l, ceil.(xbar+ub./clate)))
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
	# Generate a column for each possible delay
	for d = 1:(dmax[f]+1)
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
				row = Int( F + (N*pairnum - 1) + r[f] + d+pr  ) # pairnum is a float because of division by 2, but this should be Int.
				A[row,j] = 1

			end

		end
		
		# Record which flight this column corresponds to
		plane[j] = f
		scht[j] = r[f]+d - 1 # Minus 1 because we index from 1 in Julia, whereas time starts from 0
		A[f,j] = 1 # Set the flight block's unit
		cost[j] = fcost(scht[j]/res + rmin, xbar[f]+rmin, r[f], dmax[f], cearly[f], clate[f])# ????

		# Increment counter
		j = j + 1
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
add_constr!(model,cost, '<', ub)
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
