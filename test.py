import pandas as pd
import numpy as np


a = np.array([1,-2,3])
b = np.array([0,0,0])
c = np.append([a],[b],axis=0)
print(np.max(c,axis=0))