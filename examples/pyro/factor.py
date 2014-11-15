
import sys
from math import sqrt
import pyutilib.pyro

if sys.version_info >= (3,0):
    xrange = range


def factorize(n):
    def isPrime(n):
        return not [x for x in xrange(2,int(sqrt(n))+1) if n%x == 0]
    primes = []
    candidates = xrange(2,n+1)
    candidate = 2
    while not primes and candidate in candidates:
        if n%candidate == 0 and isPrime(candidate):
            primes = primes + [candidate] + factorize(n/candidate)
        candidate += 1
    return primes


class FactorWorker(pyutilib.pyro.TaskWorker):

    def process(self,data):
        print "factorizing",data,"-->",
        sys.stdout.flush()
        res = factorize(int(data))
        print res
        return res
