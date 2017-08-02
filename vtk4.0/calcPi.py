# -----------------------------------------------
# calcPi.py -- Patrick Miller Mon Dec 20 
#
# MPIPython program for calculating pi
#
# Adapted from Fortran Program for calculating pi
# Figure 3.2 on page 23 of
#
# "Using MPI: portable parallel parallel programming
# with the message-passing interface", William Gropp/
# Ewing Lusk/Anthony Skellum, MIT Press, 1994
# ISBN 0-262-57104-8
#
# Modified Mon Jan 22 15:57:39 PST 2001
# byt Martin Casado to support PyTestUtils
# -----------------------------------------------

import mpi

def f(a):
    "The function to integrate"
    return 4.0/(1.0 + a*a)

def integrate(rectangles, function):
    # equivalent to mpi.WORLD.bcast(n,0) or rather a
    # C call to MPI_Bcast(PYTHON_COMM_WORLD,n,0,&status)
    n = mpi.bcast(rectangles)

    h = 1.0/n
    sum = 0.0
    for i in range(mpi.rank+1,n+1,mpi.procs):
        x = h * (i-0.5)
        sum = sum + function(x)

    myAnswer = h * sum
    answer = mpi.reduce(myAnswer,mpi.SUM)
    return answer


if __name__ == '__main__':
    import math
    if mpi.rank == 0:
        try:
            import string,sys
            n = string.atoi(sys.argv[1])
        except:
            n = 2000
    else:
        n = 0

    pi = integrate(n,f)
    if mpi.rank == 0:
        diff = abs(math.pi-pi)
        print 'My answer is',pi,'Error is',diff
        if diff > 1e-6: 
          print '------ Error is greater than 1e-6'
        else:
          print '------ Error is acceptable'

