import sys
sys.setrecursionlimit(10000)

from scipy.io import readsav

filename = 'idl_simplex_inputs_and_outputs.sav'

data = readsav(filename)

breakpoint()