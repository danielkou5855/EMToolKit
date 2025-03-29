from scipy.io import readsav

file1 = '/sanhome/danielkou/public_html/simplex_2.5tolfac_8e-4eps_better.sav'
file2 = '/sanhome/danielkou/public_html/simplex_1.4tolfac_8e-4eps_better.sav'

data1 = readsav(file1)
data2 = readsav(file2)

rs_array1 = data1['rs_array']
rs_array2 = data2['rs_array']

diff = rs_array1 - rs_array2
ratio = rs_array1 / rs_array2

import numpy as np

# print(np.nanmax(rs_array1), np.nanmin(rs_array1), np.nanmax(rs_array2), np.nanmin(rs_array2))

file3 = '/sanhome/danielkou/public_html/simplex_inputs_and_outputs_tolfac2.5_eps0.0008.pkl'

import pickle

with open(file3, 'rb') as file:
    data3 = pickle.load(file)

rs_array3 = data3['r_array']

breakpoint()

import matplotlib.pyplot as plt

for i in range(81):
    if np.nanmax(rs_array1) < 1e-16 and np.nanmin(rs_array1) > -1e-16:
        print('zeros')
        continue

    plt.subplot(1, 3, 1)
    plt.imshow(rs_array1[i])
    plt.colorbar()

    plt.subplot(1, 3, 2)
    plt.imshow(rs_array2[i])
    plt.colorbar()

    plt.subplot(1, 3, 3)
    plt.imshow(ratio[i])
    plt.colorbar()
    
    plt.show()

breakpoint()