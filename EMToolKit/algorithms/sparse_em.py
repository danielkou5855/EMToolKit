import numpy as np

def sparse_em_init(trlogt_list, tresp_list, bases_sigmas=None, 
                   differential=False, bases_powers=[], normalize=False, use_lgtaxis=None):

    if(bases_sigmas is None): bases_sigmas=np.array([0.0,0.1,0.2,0.6])
    if(use_lgtaxis is None): lgtaxis = trlogt_list[0]
    else: lgtaxis=use_lgtaxis
    nchannels = len(tresp_list)
    ntemp = lgtaxis.size
    dlgt = lgtaxis[1]-lgtaxis[0]
    
    nsigmas = len(bases_sigmas)
    npowers = len(bases_powers)
    
    nbases = (nsigmas+npowers)*ntemp
    basis_funcs = np.zeros([nbases,ntemp])
    Dict = np.zeros([nchannels,nbases])
    
    tresps = np.zeros([nchannels,ntemp])
    for i in range(0,nchannels): tresps[i,:] = np.interp(lgtaxis,trlogt_list[i],tresp_list[i])    
    
    for s in range(0,nsigmas):
        if(bases_sigmas[s] == 0):
            for m in range(0,ntemp): basis_funcs[ntemp*s+m,m] = 1
        else:
            extended_lgtaxis = (np.arange(50)-25)*dlgt+6.0
            line = np.exp(-((extended_lgtaxis-6.0)/bases_sigmas[s])**2.0)
            cut = line < 0.04
            line[cut] = 0.0
            norm = np.sum(line)
            for m in range(0,ntemp):
                line = np.exp(-((lgtaxis-lgtaxis[m])/bases_sigmas[s])**2.0)
                cut = line < 0.04
                line[cut] = 0.0
                if(normalize): line = line/norm
                basis_funcs[ntemp*s+m,0:ntemp] = line
            
    for s in range(0,npowers):
        for m in range(0,ntemp):
            if(bases_powers[s] < 0):
                basis_funcs[ntemp*(s+nsigmas)+m, m:ntemp] = exp((lgtaxis[m:ntemp]-lgtaxis[m])/bases_powers[s])
            if(bases_powers[s] > 0):
                basis_funcs[ntemp*(s+nsigmas)+m, 0:m+1] = exp((lgtaxis[0:m+1]-lgtaxis[m])/bases_powers[s])
    
    if(differential):
        for i in range(0,nchannels):
            for j in range(0,nbases):
                Dict[i,j] = np.trapz(tresps[i,:]*basis_funcs[j,:],lgtaxis)
    else: Dict = np.matmul(tresps,basis_funcs.T)
    
    return Dict, lgtaxis, basis_funcs, bases_sigmas

zequations = []
constraints = []
m1s = []
m2s = []
m3s = []
epss = []

results = []
statuses = []

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

def simplex(zequation, constraint, m1, m2, m3, eps=None):
    from scipy.optimize import linprog

    b_ub = np.hstack([constraint[0,0:m1],-constraint[0,m1:m1+m2]])
    A_ub = np.hstack([-constraint[1:,0:m1],constraint[1:,m1:m1+m2]]).T
    b_eq = constraint[0,m1+m2:m1+m2+m3]
    A_eq = constraint[1:,m1+m2:m1+m2+m3].T

    result2 = linprog(-zequation, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, options={'tol':eps,'autoscale':True}, method='simplex')
    result = solveLP(-zequation, A_ub, b_ub)

    with open('res.txt', 'a') as f:
        f.write(str(result2))

    with open('res2.txt', 'a') as f:
        f.write(str(result))

    return np.hstack([result['fun'],result['x']]), result['status']


def sparse_em_solve(image, errors, exptimes, Dict, zfac=[],
            eps=1.0e-3, tolfac=2.5, relax=True, symmbuff=1.0, adaptive_tolfac=True, epsfac=1e-10):#8e-4):
    dim = image.shape
    nocounts = np.where(np.sum(image,axis=2) < 10*eps)

    zmax = np.zeros([dim[0],dim[1]])
    status = np.zeros([dim[0],dim[1]])
    tolmap = np.zeros([dim[0],dim[1]])
    [nchannels,ntemp] = Dict.shape
    if(len(zfac) == ntemp):
        zequation = -zfac
    else:
        zequation = np.zeros(ntemp) - 1.0

    tolfac2 = tolfac
    if(adaptive_tolfac and np.isscalar(tolfac)): tolfac = tolfac*np.array([1.0,1.5,2.25])
    if(np.isscalar(tolfac)): tolfac = [tolfac]
    ntol = len(tolfac)

    if(relax):
        m1=nchannels
        m2=nchannels
        m3=0
        m=m1+m2+m3
    constraint = np.zeros([m,ntemp+1])
    constraint[0:m1,1:ntemp+1] = -Dict
    constraint[m1:m1+m2,1:ntemp+1] = -Dict
    coeffs = np.zeros([image.shape[0],image.shape[1],ntemp])
    tols = np.zeros([image.shape[0],image.shape[1]])

    zequations_array = [[[0] * ntol] * dim[1]] * dim[0]
    constraints_array = [[[0] * ntol] * dim[1]] * dim[0]
    m1_array = [[[0] * ntol] * dim[1]] * dim[0]
    m2_array = [[[0] * ntol] * dim[1]] * dim[0]
    m3_array = [[[0] * ntol] * dim[1]] * dim[0]
    eps_array = [[[0] * ntol] * dim[1]] * dim[0]
    r_array = [[[0] * ntol] * dim[1]] * dim[0]
    s_array = [[[0] * ntol] * dim[1]] * dim[0]

    for i in range(0,dim[0]):
        for j in range(0,dim[1]):
            y = np.clip(image[i,j,:],0,None)/exptimes
            for k in range(0,ntol):
                if(relax):
                    tol=tolfac[k]*errors[i,j,:]/exptimes
                    constraint[0:m1,0] = y+tol
                    constraint[m1:m1+m2,0] = np.clip((y-symmbuff*tol), 0.0, None)
                    [r, s] = simplex(zequation, constraint.T, m1, m2, m3, eps=eps*np.max(y)*epsfac)

                    zequations_array[i][j][k] = zequation
                    constraints_array[i][j][k] = constraint.T
                    m1_array[i][j][k] = m1
                    m2_array[i][j][k] = m2
                    m3_array[i][j][k] = m3
                    eps_array[i][j][k] = eps*np.max(y)
                    r_array[i][j][k] = r
                    s_array[i][j][k] = s
                else:
                    constraint = np.hstack([y,-Dict])
                    [r, s] = simplex(zequation, constraint.T, 0, 0, nchannels)
                if(s==0): break
            if r[0] == None or (np.min(r[1:ntemp+1]) < 0.0):
                coeffs[i,j,0:ntemp] = 0.0
                s = 10
            else:
                coeffs[i,j,0:ntemp] = r[1:ntemp+1]
            zmax[i,j] = r[0]
            status[i,j] = s
            tols[i,j] = k
    if(len(nocounts[0]) > 0):
        status[nocounts] = 11.0

    data = {
        'zequations_array': zequations_array,
        'constraints_array': constraints_array, 
        'm1_array': m1_array,
        'm2_array': m2_array,
        'm3_array': m3_array,
        'eps_array': eps_array,
        'r_array': r_array,
        's_array': s_array
    }

    import pickle
    with open(f'simplex_inputs_and_outputs_tolfac{tolfac2}_eps{epsfac}.pkl', 'wb') as f:
        pickle.dump(data, f)

    return coeffs, zmax, status