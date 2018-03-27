m = Model()

c=1
P=3

T = [1,2,3]
l = [0.5,0.5,0.5]

# Number of planes is P
@variable(m, A[1:P]) # Arrival time
@variable(m, d[1:P]) # Delay

@constraint(m, A[p]+l[p] <= A[p+1] for p=1:(P-1)) # Arrive in order
@constraint(m, A[p] == T[p] + d[p] for p=1:P) # Allow delay
@constraint(m, d[p] >= 0 for p=1:P) # No early arrivals

@objective(m, Min, sum(c*d[p] for p=1:P))