import numpy as np
from scipy.optimize import linprog

import pickle, time
import pdb

##############################################################

# you'll need these imports
from scipy.sparse import csc_matrix
import highspy

def solveLP(c, Aineq, bineq):
    """Solve a linear program of the form
        argmin c^T x s.t. x >= 0, Aineq@x <= bineq
    skipping a lot of scipy cruft"""
    # make a sparse matrix of the inequality matrix
    # in the BPDEM case, this is shared, so if you want
    # another speed-up, you can probably pull this part out
    Aineq = csc_matrix(Aineq)

    # Create the highs environment. Hoisting this outside the function 
    # (i.e., so it's created once) doesn't speed things up much
    highs = highspy._Highs()
    # turn off loggging info
    highs.setOptionValue("log_to_console", False)
    highs_options = highspy.HighsOptions()
    setattr(highs_options, 'log_to_console', False)

    # Create a lp object. This object can't be reused, as far as I can 
    # tell. The nomenclature here is a bit funny
    lp = highspy.HighsLp()
    # set up the sizes
    numcol, numrow = c.size, bineq.size
    lp.num_col_ = numcol
    lp.num_row_ = numrow
    lp.a_matrix_.num_col_ = numcol
    lp.a_matrix_.num_row_ = numrow

    # setup the format
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise

    # objective goes here
    lp.col_cost_ = c
    
    # bounds on the variables; col is [0,inf]
    lp.col_lower_ = np.zeros_like(c)
    lp.col_upper_ = np.ones_like(c) * np.inf
    
    # We have Aineq @ x <= bineq but no other constraints 
    # There are no lower bounds on Aineq @ x (since we've
    # put them in by having two rows
    lp.row_lower_ = - np.ones_like(c) * np.inf 
    lp.row_upper_ = bineq

    # put the inequality matrix in
    lp.a_matrix_.start_ = Aineq.indptr
    lp.a_matrix_.index_ = Aineq.indices
    lp.a_matrix_.value_ = Aineq.data

    # pass the options and run
    highs.passOptions(highs_options)
    highs.passModel(lp)
    run_status = highs.run()

    status = highs.getModelStatus()
    res = {'x': None, 'fun': None, 'status': None}

    # if we succeed, update the returns
    if status == highspy.HighsModelStatus.kOptimal:
        res['x'] = np.array(highs.getSolution().col_value)
        res['fun'] = np.sum(res['x'])
        res['status'] = 0

    return res


##############################################################

with open('python_2.5tolfac_1e-10eps.pkl', 'rb') as f:
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

scale = 10**26
tic = time.time()

for i in range(len(zequations)):
    print(i, len(zequations))
    microtic = time.time()
    num = len(zequations[0])*len(zequations[0][0])
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
            A_ub = np.hstack([constraint[1:,0:m1],-constraint[1:,m1:m1+m2]]).T 
            b_eq = constraint[0,m1+m2:m1+m2+m3]
            A_eq = constraint[1:,m1+m2:m1+m2+m3].T 

            if b_eq.size != 0:
                print("equality constraints")
                pdb.set_trace()

            # scipy output using linprog (can be substituted)
            # res = linprog(-zequation, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, options={'tol':eps,'autoscale':True}, method='simplex')
            res2 = solveLP(-zequation, A_ub, b_ub)

            # result2 = np.hstack([res['fun'],res['x']])
            # status2 = res['status']

            result22 = np.hstack([res2['fun'],res2['x']])
            status22 = res2['status']

            # read out outputs
            result = results[i][j][k]
            status = statuses[i][j][k]

            if np.max(np.array(result)) != 0:
                print(result22)
                print(result)

                breakpoint()

            # diff = result2 - result22
            # if status2 == status22:
            #     print(np.nanmax(diff), np.nanmin(diff), np.average(diff))
            # else:
            #     breakpoint()
            #     print("statuses differ")

            # print(status, status2)
    microtoc = time.time()
    print("One subiteration (%d items) in %.3f seconds" % (num, microtoc-microtic))

toc = time.time()
print("Total: %.2f seconds" % (toc-tic))
