#%% import
import requests
import json
import numpy as np
from matplotlib import pyplot
import matplotlib.pyplot as plt
import tushare as ts
from multiprocessing import Pool
import re
import pandas as pd
import os
import time
import csv
import baostock as bs

#%% define
def llv(lowList,n):
    low_move = []
    for low in range(len(lowList)-1,n-1,-1):
        low_move.append(min(lowList[low-n+1:low+1]))
    low_move.reverse()
    return np.array(low_move,dtype = 'float_')

def hhv(highList,n):
    high_move = []
    for low in range(len(highList) - 1, n - 1, -1):
        high_move.append(max(highList[low - n + 1:low+1]))
    high_move.reverse()
    return np.array(high_move,dtype = 'float_')

def ema(x,n):
    result = []
    for i in range(len(x)):
        if i < n:
            result.append(sum(x[:i + 1]) / (i + 1))
        else:
            result.append( (2*x[i]+(n-1)*result[i-1]) / (n+1))
    return np.array(result, dtype='float_')

def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range

#%% get data
lg = bs.login()
rs = bs.query_history_k_data_plus("sh.000300",
    "date,code,open,high,low,close,tradestatus",
    start_date='2018-01-01', end_date='2020-03-30',
    frequency="d", adjustflag="2")
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)
print(result)

date_list = result['date'].tolist()
low = result['low'].astype(float).tolist()
result['open'] = result['open'].astype(float)
close = result['close'].astype(float).tolist()
high = result['high'].astype(float).tolist()

#%% count
var2 = llv(low,10)
var3 = hhv(high,25)
power = ema((np.array(close[25:]) - np.array(var2[15:]))/(np.array(var3) - np.array(var2[15:])) * 4, 4)
power = normalization(power[-120:])
close = normalization(close[-120:])
print(power)
x = range(120)
plt.plot(x, power, marker='o', mec='r', mfc='w', label='power')
plt.plot(x, close, marker='*', ms=10, label='close')
plt.grid(axis="x")
plt.legend(loc='upper left')  # 让图例生效
plt.show()