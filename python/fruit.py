volume0 = 13.0

class Fruit:
    def __init__(self):
        self.sweet = True
    
    def color(self):
        return 'red'

    def volume(self):
        return volume0*2

class Banana(Fruit):
    def color(self):
        return 'yellow'

    def shape(self):
        return 'shape is not round'

    def volume(self):
        return volume0*3

class Tomato(Fruit):
    def __init__(self):
        self.sweet = False

print '----- Fruit -----'
fruit = Fruit()
print 'Sweet? ',fruit.sweet
print fruit.color()
print fruit.volume()

print '----- Banana -----'
fruit = Banana()
print 'Sweet? ',fruit.sweet
print fruit.color()
print fruit.shape()
print fruit.volume()

print '----- Tomato -----'
fruit = Tomato()
print 'Sweet? ',fruit.sweet
print fruit.color()
print fruit.shape()

