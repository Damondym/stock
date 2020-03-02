import requests
import json
import demjson
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

class Stock:
    code = ''
    i = 0
    price = []
    date = []
    ttm = []
    var1 = []
    var7 = []
    status = 0
    if50 = 0
    ifsale = 0
    ifbuy = 1
    def __init__(self,code,date,price,var1,var7,ttm):
        self.code = code
        self.price = price
        self.date = date
        self.ttm = ttm
        self.var1 = var1
        self.var7 = var7

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
        if times == 1:
            score = 0.5 + (ttm - 0.45) * 2 / 7
            num = (self.buyNum[code] * score + 0.5) // 1
            self.sale_log[code] = {'price': price, 'num': num}
        elif times == 2:
            score = 0.3 + (ttm - 0.45) * 2 / 7
            num = (self.buyNum[code] * score + 0.5) // 1
            self.sale_log[code] = {'price': price, 'num': num}
        elif times == 3:
            score = 0.3 + (ttm - 0.45) * 4 / 7
            num = (self.buyNum[code] * score + 0.5) // 1
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
            print(times)
            for buy in self.buy_log:
                self.account -= 100 * self.buy_log[buy]
                if buy not in self.buyNum:
                    self.buyNum[buy] = 1
                else:
                    self.buyNum[buy] += 1
        else:
            score_sum = sum(self.score_log.values())
            account_sum = self.sum / 2.5 * (1 - (ttm_avg-0.45) * 10 / 7)
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

def get_data(code,endtime):
    df = ts.pro_bar(ts_code=code, adj='qfq', start_date='20180101', end_date=endtime).sort_values(
            by="trade_date", ascending=True)
    high = df['high'].tolist()
    low = df['low'].tolist()
    price = df['close'].tolist()
    amount = df['amount'].tolist()
    vol = df['vol'].tolist()
    date = df["trade_date"].tolist()
    if df['trade_date'][0] != endtime:
        url = 'http://d.10jqka.com.cn/v6/line/hs_{}/01/today.js'.format(code[:6])
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Referer': 'http://m.10jqka.com.cn/stockpage/hs_{}/'.format(code[:6])
        }
        r = requests.get(url, headers=headers)
        js = re.findall(':({[\S\s]+})}', r.text)[0]
        js = json.loads(js)
        high.append(js['8'])
        low.append(js['9'])
        price.append(js['11'])
        amount.append(float(js['19']) / 1000)
        vol.append(float(js['13']) / 100)
        date.append(endtime)
    return high, low, price, amount, vol, date

def get_data_csv(name,begin,end):
    df = pd.read_csv("stock_data/" + str(name))
    df = df.sort_values(by="date", ascending=True)
    df = df[(df.date >= begin) & (df.date <= end)]
    high = df['high'].tolist()
    low = df['low'].tolist()
    price = df['price'].tolist()
    amount = df['tradeAmount'].tolist()
    vol = df['vol'].tolist()
    date = df['date'].tolist()
    return high, low, price, amount, vol, date

def get_ttm_csv(name,begin,end):
    df = pd.read_csv("ttm/" + str(name))
    df = df.sort_values(by="date", ascending=True)
    df = df[(df.date >= begin) & (df.date <= end)]
    ttm = df['ttm'].tolist()
    return ttm

def get_ttm(code,begin,end):
    url = 'https://gw.datayes.com/rrp_adventure/web/stockModel/band/{}?apiType=4&category=1&subCategory=1&flag=-1&beginDate={}&endDate={}'.format(code,begin,end)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'cookie': 'gr_user_id=87dc2f4f-119b-4df1-9d4c-1f99f31cd092; UM_distinctid=1702dc92c414e-0e42551d05b787-36664c08-1fa400-1702dc92c4218f; _ga=GA1.2.241021053.1581316124; grwng_uid=f17cb385-6865-476b-b4be-7118e31d72ee; cloud-anonymous-token=5c498c0ab406453abecacae635d1e5ee; cloud-sso-token=77A2C6EFE72354387831C88E1499BA2D; ba895d61f7404b76_gr_last_sent_cs1=6038477%40wmcloud.com; ba895d61f7404b76_gr_session_id=f4834e75-7e4c-4a6b-a7a1-023f1e759379; ba895d61f7404b76_gr_last_sent_sid_with_cs1=f4834e75-7e4c-4a6b-a7a1-023f1e759379; _gid=GA1.2.2031486810.1581411082; ba895d61f7404b76_gr_session_id_f4834e75-7e4c-4a6b-a7a1-023f1e759379=true; JSESSIONID=ED4B42EE7E9FBB4D40B8DE4347914552; _gat=1; ba895d61f7404b76_gr_cs1=6038477%40wmcloud.com',
    }
    times = 1
    while True:
        try:
            r = requests.get(url, headers=headers, timeout = 5)
            break
        except:
            print('retry' + str(code) + ':' + str(times))
            times += 1
            time.sleep(3)
    js = json.loads(r.text)
    ttmList = []
    for data in js['data']['data']:
        ttmList.append(data['value'])
    return ttmList
    '''#亿牛：有错误数据
    url = 'https://eniu.com/chart/pea/' + code  #sz000333
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    js = json.loads(r.text)
    ttmList = js['pe_ttm']
    return ttmList
    '''

def get_all_ttm(begin, end):
    dir = 'stock_data'
    fileList = os.listdir(dir)
    for name in fileList:
        print(name)
        with open('ttm/' + name, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'ttm'])
            url = 'https://gw.datayes.com/rrp_adventure/web/stockModel/band/{}?apiType=4&category=1&subCategory=1&flag=-1&beginDate={}&endDate={}'.format(name[:6], begin, end)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                'cookie': 'gr_user_id=87dc2f4f-119b-4df1-9d4c-1f99f31cd092; UM_distinctid=1702dc92c414e-0e42551d05b787-36664c08-1fa400-1702dc92c4218f; _ga=GA1.2.241021053.1581316124; grwng_uid=f17cb385-6865-476b-b4be-7118e31d72ee; cloud-anonymous-token=5c498c0ab406453abecacae635d1e5ee; cloud-sso-token=77A2C6EFE72354387831C88E1499BA2D; ba895d61f7404b76_gr_last_sent_cs1=6038477%40wmcloud.com; ba895d61f7404b76_gr_session_id=f4834e75-7e4c-4a6b-a7a1-023f1e759379; ba895d61f7404b76_gr_last_sent_sid_with_cs1=f4834e75-7e4c-4a6b-a7a1-023f1e759379; _gid=GA1.2.2031486810.1581411082; ba895d61f7404b76_gr_session_id_f4834e75-7e4c-4a6b-a7a1-023f1e759379=true; JSESSIONID=ED4B42EE7E9FBB4D40B8DE4347914552; _gat=1; ba895d61f7404b76_gr_cs1=6038477%40wmcloud.com',
            }
            times = 1
            while True:
                try:
                    r = requests.get(url, headers=headers, timeout=5)
                    break
                except:
                    print('retry' + str(name[:6]) + ':' + str(times))
                    times += 1
                    time.sleep(3)
            js = json.loads(r.text)
            ttmList = []
            for data in js['data']['data']:
                date = data['tradeDate'][:4] + data['tradeDate'][5:7] + data['tradeDate'][8:]
                writer.writerow([int(date), data['value']])

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

def get_stockList(name,begin,end,check):
    high, low, price, amount, vol, date = get_data_csv(name, begin, end)
    var1, var7 = count_readyup(high, low, price)
    var7 = [50] * 29 + var7.tolist()
    ttm = np.array(get_ttm_csv(name, 20110101, 20200110))
    #ttm = np.array(get_ttm(name[:6], '20140101', '20200110'))
    if len(ttm) < check + 750:
        print('!!!!!!!' + name)
        return
    stock = Stock(name, date[5:], price, var1, var7, ttm[-1 * (check + 749):])
    return stock

if __name__ == '__main__':
    ts.set_token('d9aaf0a623896f9803e5724b0a9c37d28f471453c3ecab0c6bd69abc')
    pro = ts.pro_api()
    #get_all_ttm('20110101','20200110')
    hs300 = pro.index_daily(ts_code='000300.SH', start_date='20150101', end_date='20200110').sort_values(
        by="trade_date", ascending=True)
    hsDate = hs300['trade_date'].tolist()
    money = 1000000
    dir = 'stock_data'
    fileList = os.listdir(dir)
    stockList = []
    beginList = [20150101] * len(fileList)
    endList = [20200110] * len(fileList)
    checkList = [len(hsDate)] * len(fileList)
    args_zip = list(zip(fileList, beginList, endList,checkList))
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
    print('begin! numbers is ' + str(len(stockList)))
    for i in range(len(hsDate)-5):
        ttm_avg = 0
        price_avg = 0
        for stock in stockList:
            temp = stock.ttm[i: i + 750].copy()
            temp[temp < temp[-1]] = -1
            ttm_percent = np.sum(temp == -1) / len(temp)
            ttm_avg += ttm_percent
            price_avg += stock.price[stock.i + 5]
            a.price_log[stock.code] = stock.price[stock.i + 5]
            if int(stock.nowDate()) != int(hsDate[i+5]):
                continue
            var = stock.var1[stock.i]
            if stock.ifsale:
                stock.ifsale = 0
                a.sale(stock.code, stock.price[stock.i + 5], ttm_percent, 2)
                stock.next()
                continue
            if var < 6.3 and stock.status == 0:
                stock.status = 1
                base = 0
                if stock.var7[stock.i] < 15:
                    base = -0.5
                a.buy(stock.code, stock.price[stock.i + 5], ttm_percent , base)
            elif var > 90 and a.if_num(stock.code):
                stock.status = 0
                stock.if50 = 0
                stock.ifsale = 1
                stock.ifbuy = 0
                a.sale(stock.code, stock.price[stock.i + 5], ttm_percent, 1)
            elif var > 50 and stock.status == 1 and stock.if50 == 0:
                stock.if50 = 1
            elif var < 50 and stock.status == 1 and stock.if50 == 1:
                stock.if50 = 2
                a.sale(stock.code, stock.price[stock.i + 5], ttm_percent, 3)
            elif var < 25 and stock.status == 0 and stock.ifbuy == 0:
                stock.ifbuy = 1
                base = 0.5
                if stock.var7[stock.i] < 15 or stock.var7[stock.i-1] < 15:
                    base = 0
                a.buy(stock.code, stock.price[stock.i + 5], ttm_percent, base)
            elif var < 6.3 and stock.status == 1 and stock.if50 == 2:
                stock.if50 = 0
                stock.ifbuy = 1
                base = 0.5
                if stock.var7[stock.i] < 15 or stock.var7[stock.i-1] < 15:
                    base = 0
                a.buy(stock.code, stock.price[stock.i + 5], ttm_percent, base)
            stock.next()
            '''
            elif stock.var7[i] < 10 and var < 30:
                if stock.var7[i-1] < 10:
                    continue
                a.buy(stock.code, stock.price[i + 5], ttm_percent, 0)
            '''
        s,bn,sn = a.get_sum(i, ttm_avg/len(stockList))
        account_log.append(a.account)
        num_log.append(sum(a.buyNum.values()))
        sum_log.append(a.sum)
        ttm_log.append(ttm_avg/len(stockList))
        price_log.append(price_avg/len(stockList))
        buyNum_log.append(bn)
        saleNum_log.append(sn)
    '''
    for i,var in enumerate(stock.var1):
        temp = stock.ttm[i: i + 750].copy()
        temp[temp < temp[-1]] = -1
        ttm_log.append(np.sum(temp == -1) / len(temp))
        if stock.ifsale:
            stock.ifsale = 0
            a.get_sum(stock.price[i + 5])
            account_log.append(a.account)
            num_log.append(a.buyNum)
            sum_log.append(a.sum)
            continue
        if var < 6.3 and stock.status == 0:
            stock.status = 1
            temp = stock.ttm[i: i + 750].copy()
            temp[temp < temp[-1]] = -1
            ttm_percent = 0.5 - (np.sum(temp == -1) / len(temp))
            a.buy(stock.date[i+5],stock.price[i+5],2-ttm_percent*2)
        elif var > 90 and a.if_num():
            stock.status = 0
            stock.if50 = 0
            stock.ifsale = 1
            stock.ifbuy = 0
            a.sale(stock.date[i+5], stock.price[i+5], 2)
            a.sale(stock.date[i+6], stock.price[i+6], 2)
        elif var > 50 and stock.status ==1 and stock.if50 == 0:
            stock.if50 = 1
        elif var < 50 and stock.status ==1 and stock.if50 == 1:
            stock.if50 = 2
            a.sale(stock.date[i+5],stock.price[i+5],3)
        elif var<20 and stock.status == 0 and stock.ifbuy == 0:
            stock.ifbuy = 1
            temp = stock.ttm[i: i + 750].copy()
            temp[temp < temp[-1]] = -1
            ttm_percent = 0.5 - (np.sum(temp == -1) / len(temp))
            a.buy(stock.date[i + 5], stock.price[i+5],3-ttm_percent*2)
        elif var < 6.3 and stock.status == 1 and stock.if50 == 2:
            stock.if50 = 0
            stock.ifbuy = 1
            temp = stock.ttm[i: i + 750].copy()
            temp[temp < temp[-1]] = -1
            ttm_percent = 0.5 - (np.sum(temp == -1) / len(temp))
            a.buy(stock.date[i + 5], stock.price[i + 5], 3 - ttm_percent * 2)
        a.get_sum(stock.price[i+5])
        account_log.append(a.account)
        num_log.append(a.buyNum)
        sum_log.append(a.sum)
    '''

    print(a.account)
    print(a.buyNum)
    print(a.sum)
    print(a.get_log())
    x = range(len(account_log))
    plt.plot(x, ttm_log, marker='o', mec='r', mfc='w', label='ttm_log')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()
    plt.plot(x, account_log, marker='o', mec='r', mfc='w', label='account')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()
    plt.plot(x, buyNum_log, marker='*', ms=10, label='buy_num')
    plt.plot(x, saleNum_log, marker='o', mec='r', mfc='w', label='sale_num')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()
    plt.plot(x, sum_log, marker='*', ms=10, label='sum')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()


    hs300 = np.array(hs300['close'].tolist()[5:])
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