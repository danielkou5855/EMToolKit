# import pickle
# import numpy as np

# file1 = '/sanhome/danielkou/public_html/simplex_inputs_and_outputs_tolfac2.5_eps0.0008.pkl'
# file2 = '/sanhome/danielkou/public_html/simplex_inputs_and_outputs_tolfac1.4_eps0.0008.pkl'
# file3 = '/sanhome/danielkou/public_html/simplex_inputs_and_outputs_tolfac2.5_eps1e-10.pkl'
# file4 = '/sanhome/danielkou/public_html/simplex_inputs_and_outputs_tolfac1.4_eps1e-10.pkl'

# file_test = '/sanhome/danielkou/public_html/python_simplex_inputs_and_outputs.pkl'

# with open(file1, 'rb') as file:
#     data1 = pickle.load(file)

# with open(file2, 'rb') as file:
#     data2 = pickle.load(file)

# with open(file3, 'rb') as file:
#     data3 = pickle.load(file)

# with open(file4, 'rb') as file:
#     data4 = pickle.load(file)

# with open(file_test, 'rb') as file:
#     data_test = pickle.load(file)

# rs_array1 = np.array(data1['r_array'])
# rs_array2 = np.array(data2['r_array'])
# rs_array3 = np.array(data3['r_array'])
# rs_array4 = np.array(data4['r_array'])

# rs_array_test = np.array(data_test['r_array'])

from scipy.io import readsav
import numpy as np

sav1 = '/sanhome/danielkou/public_html/simplex_1.4tolfac_1e-10eps_better.sav'
output = '/sanhome/danielkou/public_html/output_2.5tolfac_1e-10eps.genx'

from sunpy.io.special import read_genx

res = read_genx(output)
print(res.keys())

breakpoint()

data1 = readsav(sav1)

rs_array1 = data1['rs_array']

print(data1.keys())

breakpoint()
