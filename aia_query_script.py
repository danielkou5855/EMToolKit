import drms

client = drms.Client()  

keys, segments = client.query('aia.lev1_euv_12s[2022-03-30T12:04:00Z/11s]', key='WAVELNTH, T_OBS, EXPTIME', seg='image')

print(keys, segments)