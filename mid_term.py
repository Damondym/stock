import baostock as bs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def count_readyup(high,low,price):
    N = 5
    high = np.array(high,dtype = 'float_')
    low = np.array(low,dtype = 'float_')
    price = np.array(price,dtype = 'float_')
    var1 = 4*sma((price[N:]-llv(low,N))/(hhv(high,N)-llv(low,N))*100,5,1) - 3*sma(sma((price[N:]-llv(low,N))/(hhv(high,N)-llv(low,N))*100,5,1),3.2,1)
    var5 = llv(low,27)
    var6 = hhv(high,34)
    var7 = ema( (price[34:]- var5[7:]) / (var6 - var5[7:])*4,4)*25
    return var1,var7

def sma(x,n,m):
    result = []
    for i in range(len(x)):
        if i<n:
            result.append(sum(x[:i+1])/(i+1))
        else:
            result.append((m*x[i]+(n-m)*result[i-1])/n)
    return np.array(result,dtype = 'float_')

def ema(x,n):
    result = []
    for i in range(len(x)):
        if i < n:
            result.append(sum(x[:i + 1]) / (i + 1))
        else:
            result.append( (2*x[i]+(n-1)*result[i-1]) / (n+1))
    return np.array(result, dtype='float_')

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

def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range



lg = bs.login()
rs = bs.query_history_k_data_plus("sh.601006",
    "date,open,high,low,close,volume,amount,pctChg",
    start_date='2015-01-01', end_date='2020-03-04',
    frequency="w", adjustflag="2")
price = []
high = []
low = []
amount = []
while (rs.error_code == '0') & rs.next():
    data = rs.get_row_data()
    if data[5] != '0':
        price.append(float(data[4]))
        high.append(float(data[2]))
        low.append(float(data[3]))
        amount.append(float(data[6]))
print(len(price))
var1, var7 = count_readyup(high,low,price)
price = normalization(price[-90:])
amount = normalization(amount[-90:])
x = range(90)
plt.plot(x, var1[-90:]/100, marker='o', mec='r', mfc='w', label='var1')
plt.plot(x, price, marker='*', ms=10, label='price')
#plt.plot(x, var7[-90:]/100, marker='*', ms=10, label='var7')
plt.plot(x, amount, marker='*', ms=10, label='amount')
plt.grid(axis="x")
plt.legend(loc='upper left')  # 让图例生效
plt.show()