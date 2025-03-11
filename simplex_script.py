import numpy as np
from scipy.optimize import linprog

import pickle

with open('simplex_inputs_and_outputs.pkl', 'rb') as f:
    called = pickle.load(f)

print(called.keys())

zequations = called['zequations_array']
constraints = called['constraints_array']
m1s = called['m1_array']
m2s = called['m2_array']
m3s = called['m3_array']
epss = called['eps_array']
results = called['r_array']
statuses = called['s_array']

epsfac = 1.0e-10 # another alternative is to use epsfac = 8e-4 (IDL version, which is different from python)

for i in range(len(zequations)):
    for j in range(len(zequations[0])):
        for k in range(len(zequations[0][0])):
            # read in inputs
            zequation = zequations[i][j][k]
            constraint = constraints[i][j][k]
            m1 = m1s[i][j][k]
            m2 = m2s[i][j][k]
            m3 = m3s[i][j][k]
            eps = epss[i][j][k] * epsfac

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
            result = results[i][j][k]
            status = statuses[i][j][k]

            # print(status, status2)