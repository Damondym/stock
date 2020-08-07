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

class Stock:
    code = ''
    i = 0
    price = []
    date = []
    byebye = []
    host = []
    ttm = []
    tradeStatus = []
    status = 0
    if50 = 0
    ifsale = 0
    ifbuy = 1
    def __init__(self,code,date,price,host,byebye,ttm,tradeStatus):
        self.code = code
        self.price = price
        self.date = date
        self.host = host
        self.byebye = byebye
        self.ttm = np.array(ttm)
        self.tradeStatus = tradeStatus


    def next(self):
        self.i += 1

    def nowDate(self):
        return self.date[self.i]

class Customer:
    account = 0
    buyNum = {}
    sum = 0
    log = []
    status = 0
    buy_log = {}
    sale_log = {}
    price_log = {}
    score_log = {}
    def __init__(self,account = 0):
        self.account = account
        self.sum = account

    def buy(self,code,price,ttm, base = 0):
        score = 2 - ttm - base
        #percent = base - (0.5 - ttm) * 2
        #num = self.sum / price // 100 // percent
        self.score_log[code] = score
        self.buy_log[code] = price
        return

    def sale(self, code, price, ttm, times = 1):
        num = self.buyNum[code] * times
        self.sale_log[code] = {'price': price, 'num': num}
        return

    def if_num(self,code):
        if code not in self.buyNum:
            return False
        elif self.buyNum[code] == 0:
            return False
        else:
            return True

    def get_log(self):
        return self.log

    def get_status(self):
        return self.account,self.buyNum,self.sum

    def get_sum(self, times, ttm_avg):
        #卖
        for sale in self.sale_log:
            self.account += self.sale_log[sale]['num'] * 100 * self.sale_log[sale]['price']
            self.buyNum[sale] -= self.sale_log[sale]['num']
        #买
        if sum(self.buy_log.values()) * 200 > self.account:
            for buy in self.buy_log:
                self.account -= 100 * self.buy_log[buy]
                if buy not in self.buyNum:
                    self.buyNum[buy] = 1
                else:
                    self.buyNum[buy] += 1
        else:
            score_sum = sum(self.score_log.values())
            account_sum = self.sum / 11
            #self.buy_log = sorted(self.buy_log.items(), key=lambda item: item[1]['ttm'])
            for buy in self.buy_log:
                num = (self.score_log[buy] / score_sum * account_sum / self.buy_log[buy] + 50) // 100
                self.account -= num * 100 * self.buy_log[buy]
                if buy not in self.buyNum:
                    self.buyNum[buy] = num
                else:
                    self.buyNum[buy] += num
        #计总
        buySum = 0
        for buy in self.buyNum:
            buySum += self.buyNum[buy] * self.price_log[buy] * 100
        self.sum = self.account + buySum
        buy_num = len(self.buy_log)
        sale_num = len(self.sale_log)
        self.buy_log = {}
        self.sale_log = {}
        self.price_log = {}
        return self.sum,buy_num,sale_num

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

def count_playyou(open,high,low,close,date):
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

def get_data_csv(name,begin,end):
    df = pd.read_csv("stock_data/" + str(name))
    df = df.sort_values(by="date", ascending=True)
    #df = df[(df.date >= begin) & (df.date <= end)]
    open = df['open'].tolist()
    high = df['high'].tolist()
    low = df['low'].tolist()
    price = df['close'].tolist()
    amount = df['amount'].tolist()
    vol = df['volume'].tolist()
    date = df['date'].tolist()
    ttm = df['peTTM'].tolist()
    tradeStatus = df['tradestatus'].tolist()
    return open, high, low, price, amount, vol, date, ttm, tradeStatus

def get_all_data(begin, end):
    lg = bs.login()
    fileList = os.listdir('code')
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
                rs = bs.query_history_k_data_plus(code,
                                                  "date,code,open,high,low,close,amount,volume,tradestatus,peTTM",
                                                  start_date=begin, end_date=end,
                                                  frequency="d", adjustflag="2")
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())
                result = pd.DataFrame(data_list, columns=rs.fields)
                result.to_csv('stock_data/'+ code + '.csv')

def get_stockList(name,begin,end):
    open, high, low, close, amount, vol, date, ttm, tradeStatus = get_data_csv(name, begin, end)
    host = count_playyou(open,high,low,close,date)
    byebye = count_byebye(high,low,close)
    #var1, var7 = count_readyup(high, low, close)
    if len(ttm) < 1278:
        return
    stock = Stock(name, date[-494+34:], close[-494+34:], host[-494+34:], byebye[-494+34:], ttm[-494+34-750:], tradeStatus[-494+34:])
    return stock

if __name__ == '__main__':
    get_all_data('2011-01-01','2020-01-10')
    ts.set_token('d9aaf0a623896f9803e5724b0a9c37d28f471453c3ecab0c6bd69abc')
    pro = ts.pro_api()
    hs300 = pro.index_daily(ts_code='000300.SH', start_date='20180101', end_date='20200110').sort_values(
        by="trade_date", ascending=True)
    hsDate = hs300['trade_date'].tolist()
    money = 1000000
    dir = 'stock_data'
    fileList = os.listdir(dir)
    stockList = []
    beginList = [20180101] * len(fileList)
    endList = [20200110] * len(fileList)
    args_zip = list(zip(fileList, beginList, endList))
    p = Pool(4)
    stockList = p.starmap(get_stockList, args_zip)
    stockList = list(filter(None, stockList))
    '''
    for name in fileList:
        high, low, price, amount, vol, date = get_data_csv(name, 20180101, 20200110)
        if len(high) != 494:
            print('########'+name)
            continue
        var1, var7 = count_readyup(high, low, price)
        ttm = np.array(get_ttm(name[:6], '20140101', '20200110'))
        if len(ttm) < len(var1) + 750:
            print('!!!!!!!'+name)
            continue
        stock = Stock(name, date, price, var1, ttm[-1 * (len(var1) + 749):])
        stockList.append(stock)
    '''
    a = Customer(money)
    account_log = []
    num_log = []
    sum_log = []
    ttm_log = []
    price_log = []
    buyNum_log = []
    saleNum_log = []
    buy_log = []
    print('begin! numbers is ' + str(len(stockList)))
    for i in range(len(hsDate)-34):
        buy_log.append(0)
        ttm_avg = 0
        price_avg = 0
        for stock in stockList:
            temp = stock.ttm[i: i + 750].copy()
            temp[temp < temp[-1]] = -1
            ttm_percent = np.sum(temp == -1) / len(temp)
            ttm_avg += ttm_percent
            price_avg += stock.price[stock.i]
            a.price_log[stock.code] = stock.price[stock.i]
            if stock.tradeStatus[stock.i] == 0:
                stock.next()
                continue
            bye = stock.byebye[stock.i]
            if stock.ifsale:
                if bye >= 3.5:
                    a.sale(stock.code, stock.price[stock.i], ttm_percent, 0.5)
                    stock.next()
                    continue
                elif bye >= 3.2 and bye < 3.5:
                    stock.next()
                    continue
                elif bye < 3.2:
                    stock.ifsale = 0
                    a.sale(stock.code, stock.price[stock.i], ttm_percent, 1)
                    stock.next()
                    continue
            elif stock.host[stock.i] == 0 and stock.host[stock.i - 1] != 0:
                stock.status = 1
                base = 0
                a.buy(stock.code, stock.price[stock.i], ttm_percent, base)
                buy_log[i] += 1
            elif bye >= 3.2 and a.if_num(stock.code):
                stock.ifsale = 1
                a.sale(stock.code, stock.price[stock.i], ttm_percent, 0.2)
            '''if stock.ifsale:
                stock.ifsale = 0
                a.sale(stock.code, stock.price[stock.i], ttm_percent, 2)
                stock.next()
                continue
            if stock.host[stock.i] == 0 and stock.status == 0:
                stock.status = 1
                base = 0
                a.buy(stock.code, stock.price[stock.i], ttm_percent , base)
            elif var > 90 and a.if_num(stock.code):
                stock.status = 0
                stock.if50 = 0
                stock.ifsale = 1
                stock.ifbuy = 0
                a.sale(stock.code, stock.price[stock.i], ttm_percent, 1)'''
            stock.next()
        s,bn,sn = a.get_sum(i, ttm_avg/len(stockList))
        account_log.append(a.account)
        num_log.append(sum(a.buyNum.values()))
        sum_log.append(a.sum)
        ttm_log.append(ttm_avg/len(stockList))
        price_log.append(price_avg/len(stockList))
        buyNum_log.append(bn)
        saleNum_log.append(sn)

    print(sorted(a.buyNum.items(),key=lambda x:x[1],reverse=True))

    print(a.account)
    print(a.buyNum)
    print(a.sum)
    print(a.get_log())
    x = range(len(account_log))
    '''plt.plot(x, ttm_log, marker='o', mec='r', mfc='w', label='ttm_log')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()'''
    plt.plot(x, account_log, marker='o', mec='r', mfc='w', label='account')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()
    '''plt.plot(x, buyNum_log, marker='*', ms=10, label='buy_num')
    plt.plot(x, saleNum_log, marker='o', mec='r', mfc='w', label='sale_num')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()'''
    '''plt.plot(x, sum_log, marker='*', ms=10, label='sum')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()'''
    '''plt.plot(x, buy_log, marker='*', ms=10, label='buytimes')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()'''


    hs300 = np.array(hs300['close'].tolist()[34:])
    price_log = np.array(price_log)
    price_log = price_log / price_log[0]
    sum_log = np.array(sum_log)
    sum_log = sum_log/money
    hs300 = hs300 / hs300[0]
    plt.plot(x, sum_log, marker='*', ms=10, label='sum')
    plt.plot(x, price_log, marker='o', mec='r', mfc='w', label='price_avg')
    plt.plot(x, hs300, marker='x', mec='g', mfc='w', label='hs300')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()


