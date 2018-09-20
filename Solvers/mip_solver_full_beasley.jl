using JuMP, Gurobi

## MIP Solver
solver = GurobiSolver(OutputFlag=0)

# OR Library Case
# xbar = vec(readdlm("./tests/target_t.txt", Float32))
# p = readdlm("./tests/proc_t.txt", Float32)

# dep = UInt8[0 for t = 1:length(xbar)]
# r = vec(readdlm("./tests/early_t.txt", Float32))
# dmax = vec(readdlm("./tests/max_delays.txt", Float32)) + xbar - r
# ce = vec(readdlm("./tests/cost_early.txt", Float32))
# cl = vec(readdlm("./tests/cost_late.txt", Float32))

xbar = vec(readdlm("./tmp/arrival_t.txt", Float32))
p = readdlm("./tmp/proc_t.txt", Float32)
dep = Int.(vec(readdlm("./tmp/depends.txt", Float64)))
r = vec(readdlm("./tmp/arrival_t.txt", Float32))
dmax = vec(readdlm("./tmp/max_delay.txt", Float32)) + xbar - r
ce = vec(readdlm("./tmp/delay_cost.txt", Float32))
cl = vec(readdlm("./tmp/delay_cost.txt", Float32))

F = length(xbar) # Number of flights
l = r + dmax # Latest arrival time

turnover = 5

println(dmax)

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
    addedcost = fcost(t,xbar[order[idx]],r[order[idx]],dmax[order[idx]], ce[order[idx]], cl[order[idx]])
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
    addedcost = fcost(t,xbar[order[idx]],r[order[idx]],dmax[order[idx]], ce[order[idx]], cl[order[idx]])
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
			@constraint(m, x[dep[f]] + turnover <= x[f])
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
(mipcost,~) = solvemip(xbar,p,fcfsdep,r,l,ce,cl,F,ub)

if !isnan(mipcost)
	ub = min(ub, mipcost)
end

(obj,arrivals) = solvemip(xbar,p,dep,r,l,ce,cl,F,ub)
println(arrivals)
println(xbar)


writedlm("./tmp/schedule.txt", arrivals, "\n")
