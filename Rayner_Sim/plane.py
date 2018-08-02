class Plane:

    def __init__(self,flight_id,weight_class,eta,delay_cost = 1):
        self.flight_id = flight_id
        self.weight_class = weight_class
        self.delay = 0
        self.appearance_time = None
        self.eta = eta
        self.done = False
        self.delay_cost = delay_cost

    def update(self):
        pass
    
    def move(self):
        pass
    
    def get_ideal_time(self):
        return self.eta + self.delay

class Arrival(Plane):

    def __init__(self,flight_id,weight_class,eta,trail,lng,lat,delay_cost = 1):
        Plane.__init__(self,flight_id,weight_class,eta,delay_cost)
        self.trail = trail
        self.lng = lng
        self.lat = lat
        self.appearance_time = trail[-1]["ts"]
