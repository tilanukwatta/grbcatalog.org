import numpy as np

def mean(x):
    values = np.array(x, float)
    return values.mean()

"""
def median(x):
    values = np.array(x, float)
    return values.median()
"""

def std(x):
    values = np.array(x, float)
    return values.std()

def corr(x, y):
    values = np.array([x, y], float)
    corr = np.corrcoef(values)
    #import ipdb; ipdb.set_trace() # debugging code
    return corr[0][1]
