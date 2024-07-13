class Car:
    def __init__(self, make, model):
        self.make = make
        self.model = model

    def start_car(self):
        return "Wrooom"
    
bmw = Car("BMW", "M5")
cit = Car("Citroen", "Creative Technologie")