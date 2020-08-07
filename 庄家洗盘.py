#%% import
import baostock as bs
import pandas as pd
import numpy as np
import tushare as ts
#%% define func
def get_data(code,endtime,type = ''):
    if type == '':
        df = ts.pro_bar(ts_code=code, adj='qfq', start_date='20190101', end_date=endtime).sort_values(
            by="trade_date", ascending=True)
    elif type == 'zs':
        df = ts.pro.index_daily(ts_code=code, start_date='20190101', end_date=endtime).sort_values(
            by="trade_date", ascending=True)
    high = df['high'].tolist()
    low = df['low'].tolist()
    close = df['close'].tolist()
    open = df['open'].tolist()
    date = df['trade_date'].tolist()
    return date,open,high,low,close

def llv(lowList,n):
    low_move = []
    for low in range(len(lowList)-1,n-1,-1):
        low_move.append(min(lowList[low-n+1:low+1]))
    low_move.reverse()
    return np.array(low_move,dtype = 'float_')

def sma(x,n,m):
    result = []
    for i in range(len(x)):
        if i<n:
            result.append(sum(x[:i+1])/(i+1))
        else:
            result.append((m*x[i]+(n-m)*result[i-1])/n)
    return np.array(result,dtype = 'float_')

def ema(c, N):
    result = []
    for i in range(len(c)):
        if i == 0:
            result.append(c[i])
            continue
        result.append((2 * c[i] + (N - 1) * result[i-1]) / (N + 1))
    return np.array(result, dtype='float_')

#%% get data

lg = bs.login()
rs = bs.query_history_k_data_plus("sh.601360",
    "date,code,open,high,low,close,tradestatus,peTTM",
    start_date='2018-01-01', end_date='2020-08-06',
    frequency="d", adjustflag="2")
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)
print(result)
'''
ts.set_token('d9aaf0a62389'
             '6f9803e5724b0a9c37d28f471453c3ecab0c6bd69abc')
pro = ts.pro_api()
date = '20200316'
trade_date,open,high,low,close = get_data('002557.SZ','20200724')
'''
#%% count
date_list = result['date'].tolist()
result['low'] = result['low'].astype(float)
result['open'] = result['open'].astype(float)
result['close'] = result['close'].astype(float)
result['high'] = result['high'].astype(float)
result['low+open+close+high'] = (result['low'] + result['open'] + result['close'] + result['high'])/4
peTTM = result['peTTM'].astype(float).tolist()
low = result['low']
var1B = np.array(result['low+open+close+high'][:-1])#长度-1
'''
avg_price = (np.array(open) + np.array(high) + np.array(low) + np.array(close)) / 4.0
var1B = avg_price[:-1]
'''
low_var1B = np.array(low[1:] - var1B)
max_low_var1B = np.max(np.append([low_var1B],[np.array([0]*len(low_var1B))],axis=0),axis=0)
var2B = sma(np.abs(low_var1B),13,1) / sma(max_low_var1B,10,1)
var2B[np.isinf(var2B)] = 0
var3B = ema(var2B,10)
var4B = llv(np.array(low),33)
low_33 = low[33:].tolist()
var3B_33 = var3B[32:]
var5B_1 = []
for i in range(len(var4B)):
    if low_33[i] <= var4B[i]:
        var5B_1.append(var3B_33[i])
    else:
        var5B_1.append(0)
var5B = ema(var5B_1,3)
print('var1B',var1B[-5:])
print('var2B',var2B[-5:])
print('var3B',var3B[-5:])
print('var4B',var4B[-5:])
print('var5B_1',var5B_1[-5:])
print('var5B',var5B[-5:])
index_comein = var5B[1:] - np.delete(var5B,-1)
index_comein[index_comein < 0] = 0
print('index_comein',index_comein[-20:])
result = pd.DataFrame(index_comein,columns=['score'],index=date_list[34:])
print(result)
print(result.loc[result['score']!=0])


