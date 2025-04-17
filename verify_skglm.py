# need to install numpy, matplotlib, skglm, scikit-learn

import pickle
import numpy as np
import time
import matplotlib.pyplot as plt

path = 'compare_output.pkl'

with open(path, 'rb') as f:
    data = pickle.load(f)

sklearn_out = data['sklearn'].coef_
skglm_out = data['skglm'].coef_

input1 = data['input1']
input2 = data['input2']

print(input1.shape, input2.shape)

from sklearn.linear_model import Lasso as Lasso_slow
from skglm import Lasso as Lasso_fast

alpha = 1e-8
max_iter = 10000

t1 = time.time() * 1000
clf = Lasso_slow(alpha=alpha, positive=False, max_iter = max_iter, fit_intercept=False)
res=clf.fit(input1, input2)
print('sklearn time', time.time() * 1000 - t1)

t2 = time.time() * 1000
clf2 = Lasso_fast(alpha=alpha, positive=False, max_iter = max_iter, fit_intercept=False) # replicate that in sklearn
res2=clf2.fit(input1, input2)
print('skglm time', time.time() * 1000 - t2)

print("print iteration counts")
print(res.n_iter_, res2.n_iter_)

output1 = res.coef_ # equivalent to sklearn_out
output2 = res2.coef_ # equivalent to skglm_out

from scipy.stats import linregress
slope, intercept, r, p, stderr = linregress(output1, output2)
line = slope * output1 + intercept

plt.figure(figsize=(8, 6))
plt.scatter(output1, output2, label='Data Points')
plt.plot(output1, line, color='red', label='Fit Line')

r_squared = r ** 2

plt.text(0.1, 0.9, f"$r$ = {r:.3f}\n$r^2$ = {r_squared:.3f}\n$y$ = {slope}$x$ + {intercept}", transform = plt.gca().transAxes, fontsize=12)

plt.xlabel('sklearn')
plt.ylabel('skglm')
plt.title('comparison of sklearn and skglm LASSO output')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()