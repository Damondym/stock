import baostock as bs
import pandas as pd
import numpy as np
import os
import requests
from bs4 import BeautifulSoup
import re
import time

def hhv(highList,n):
    high_move = []
    for low in range(len(highList) - 1, n - 1, -1):
        high_move.append(max(highList[low - n + 1:low+1]))
    high_move.reverse()
    return np.array(high_move,dtype = 'float_')

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

def count_playyou(open,high,low,close):
    avg_price = (np.array(open) + np.array(high) + np.array(low) + np.array(close)) / 4.0
    var1B = avg_price[:-1]
    low_var1B = np.array(low[1:] - var1B)
    max_low_var1B = np.max(np.append([low_var1B],[np.array([0]*len(low_var1B))],axis=0),axis=0)
    var2B = sma(np.abs(low_var1B),13,1) / sma(max_low_var1B,10,1)
    var2B[np.isinf(var2B)] = 0
    var3B = ema(var2B,10)
    var4B = llv(np.array(low),33)
    low_33 = low[33:]
    var3B_33 = var3B[32:]
    var5B_1 = []
    for i in range(len(var4B)):
        if low_33[i] <= var4B[i]:
            var5B_1.append(var3B_33[i])
        else:
            var5B_1.append(0)
    var5B = ema(var5B_1,3)
    index_comein = var5B[1:] - np.delete(var5B,-1)
    index_comein[index_comein < 0] = 0
    return index_comein

def count_byebye(high,low,close):
    var2 = llv(low, 10)
    var3 = hhv(high, 25)
    power = ema((np.array(close[25:]) - np.array(var2[15:])) / (np.array(var3) - np.array(var2[15:])) * 4, 4)
    return power

def get_stock_ttm(code):
    url = 'https://eniu.com/gu/{}/pe_ttm'.format(code)#sz000001
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    try:
        soup = BeautifulSoup(r.text, 'html.parser')
        pannel = soup.find('div', {'class': 'panel panel-success'})
        stock_name = pannel.find('h3', {'class': 'panel-title'}).find('a', {'target': '_self'}).get_text()
        ttm = pannel.find('a', {'title': '市盈率'}).get_text()
        pb = pannel.find('a', {'title': '市净率'}).get_text()
        value = pannel.find('a', {'title': '市 值'}).get_text()
        roe = pannel.find('a', {'title': 'ROE'}).get_text()
        near3 = re.findall('近3年：(\S+%)', r.text)[0]
        near5 = re.findall('近5年：(\S+%)', r.text)[0]
        near10 = re.findall('近10年：(\S+%)', r.text)[0]
        near = re.findall('所有时间：(\S+%)', r.text)[0]
        industry = re.findall('href="/industry/(\S+)/market/', r.text)[0]
        return stock_name, ttm, pb, value, roe, near3, near5, near10, near, industry
    except:
        print('!!!!!!!!!'+code)
        print(r.text)
        return code,'','','','','','','','',''

begin = '2017-01-01'
end = '2020-08-06'
lg = bs.login()
fileList = os.listdir('code')
pd_stock = pd.DataFrame(columns=['name','pctChg',"playyou","byebye","peTTM","TTMPercent"])
attention_list = []
signal_list = []
for name in fileList:
    print(name)
    with open('code/' + name, "r") as f:
        for code in f.readlines():
            code = code.strip('\n')
            if code[0] == '0' or code[0] == '3':
                code = 'sz.' + code
            elif code[0] == '6':
                code = 'sh.' + code
            else:
                print(code)
            print(code)
            while True:
                try:
                    rs = bs.query_history_k_data_plus(code,
                                                      "date,code,pctChg,open,high,low,close,amount,volume,tradestatus,peTTM",
                                                      start_date=begin, end_date=end,
                                                      frequency="d", adjustflag="2")
                    data_list = []
                    while (rs.error_code == '0') & rs.next():
                        data_list.append(rs.get_row_data())
                    result = pd.DataFrame(data_list, columns=rs.fields)
                    result = result[result['tradestatus']=='1']
                    break
                except:
                    print(code,'error')
                    time.sleep(20)
            pctChg = result['pctChg'].astype(float).tolist()
            low = result['low'].astype(float).tolist()
            openPrice = result['open'].astype(float).tolist()
            close = result['close'].astype(float).tolist()
            high = result['high'].astype(float).tolist()
            stock_name, ttm, pb, value, roe, near3, near5, near10, near, industry = get_stock_ttm(code[:2]+code[3:])
            playyou = count_playyou(openPrice,high,low,close)
            byebye = count_byebye(high,low,close)
            if playyou[-1] != 0:
                attention_list.append(code)
            elif playyou[-1] == 0 and playyou[-2] != 0:
                signal_list.append(code)
            pd_stock.loc[code] = {'name':stock_name, 'pctChg':pctChg[-1],"playyou":playyou[-1],"byebye":byebye[-1],"peTTM":ttm,"TTMPercent":near3}
print(pd_stock[pd_stock.index.isin(attention_list)])
print(pd_stock[pd_stock.index.isin(signal_list)])
bs.logout()


