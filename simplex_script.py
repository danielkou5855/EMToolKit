import numpy as np
from scipy.optimize import linprog

called = np.load('sparse_em_solve_called.npz')

zequations = called['zequations']
constraints = called['constraints']
m1s = called['m1s']
m2s = called['m2s']
m3s = called['m3s']
epss = called['epss']
results = called['results']
statuses = called['statuses']

for i in range(len(zequations)):
    # read in inputs
    zequation = zequations[i]
    constraint = constraints[i]
    m1 = m1s[i]
    m2 = m2s[i]
    m3 = m3s[i]
    eps = epss[i]

    # process inputs
    b_ub = np.hstack([constraint[0,0:m1],-constraint[0,m1:m1+m2]])
    A_ub = np.hstack([-constraint[1:,0:m1],constraint[1:,m1:m1+m2]]).T
    b_eq = constraint[0,m1+m2:m1+m2+m3]
    A_eq = constraint[1:,m1+m2:m1+m2+m3].T

    # scipy output using linprog (can be substituted)
    res = linprog(-zequation, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, options={'tol':eps,'autoscale':True}, method='simplex')
    result2 = np.hstack([res['fun'],res['x']])
    status2 = res['status']

    # read out outputs
    result = results[i]
    status = statuses[i]

    