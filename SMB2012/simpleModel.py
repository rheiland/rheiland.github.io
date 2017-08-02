from math import *
from pylab import *  # requires 3rd party pkg:  http://matplotlib.sourceforge.net/index.html

lowTemp=[19,22,30,41,52,61,65,63,55,43,34,23]
plot(lowTemp,'o')
time = arange(0, 12, 0.1)
F = 22*sin(pi/6 * (time-pi)) + 42
plot(time,F)
input('Enter CR to end: ')
