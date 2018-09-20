# Sub-minute resolution
res = 1

# OR Case?
orcase = false

clate = vec( readdlm("./tests/cost_late.txt") )
cearly = vec( readdlm("./tests/cost_early.txt") )
xbar = vec( readdlm("./tests/target_t.txt") )
rmin = minimum(readdlm("./tests/early_t.txt"))
r = floor.(Int,  res*( vec(readdlm("./tests/early_t.txt"))) )
dmax = floor.(Int, res*vec(readdlm("./tests/max_delays.txt"))) + xbar - r
P = round.(Int, res*readdlm("./tests/proc_t.txt"))
l = r + dmax # Latest arrival time
F = length(clate) # Number of flights

# Maximum number of states
Nmax = 50000000

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

Fin = zeros(UInt8,Nmax,F)
p = Array{UInt8}(Nmax)
x = Array{Float64}(Nmax,F)
V = zeros(Float64,Nmax)
compl = zeros(Bool,Nmax)
domcount = 0
bins = [IntSet() for i in 1:F]


# Generate initial state
n=IntSet(1) # Set of indices which contain active states
m = 1
for f=1:F
	Fin[1,f] = 0
end
p[1] = 0
x[1] = 0

# Perform DP search
k=1
while true
	nnew=copy(n)
	for idx in n
		if compl[idx]
			continue
		end

		for f in 1:F
			if Fin[idx,f]==0
				k+=1
				x[k,:] = x[idx,:]
				if p[idx]>0
					x[k,f] = max(r[f],x[idx,p[idx]]+P[p[idx],f])
				else
					x[k,f] = r[f]
				end

				valid = true
				if x[k,f]<=l[f]

					Fin[k,:] = Fin[idx,:]
					Fin[k,f] = 1

					p[k] = f
					V[k] = V[idx] + fcost(x[k,f],r[f],r[f],dmax[f],cearly[f],clate[f])
				else
					valid = false
				end

				#Domination
				for jdx in bins[f]
					if Fin[jdx,:] == Fin[k,:] && V[jdx]<=V[k] && x[jdx,p[jdx]]<=x[k,f]
						domcount +=1
						valid = false
					end
				end

				if valid
					if sum(Fin[k,:])==F
						compl[k] = true
					else
						m+=1
					end

					push!(nnew,k)
					push!(bins[f],k)
				else
					k-=1
				end
			end
		end
		setdiff!(nnew,idx)
		m-=1
		if m%5000==0
			println(m)
		end
		if m==0
			break
		end
	end
	n=copy(nnew)
	if m==0
		break
	end
end

Vbest = Inf
idxbest = 0
for idx in n
	if V[idx]<=Vbest
		Vbest= V[idx]
		idxbest = idx
	end
end
println("Bestkkk schedule:")
println(x[idxbest,:])
println("Best objective: "*string(Vbest))
println("Number of states explored: "*string(k))
println("Number of dominations: "*string(domcount))
println("Done!")
