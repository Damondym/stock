# -*- coding:utf-8 -*-
import requests
import json
import re
import csv
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
import os
import tushare as ts

def get_data(code,endtime,type = ''):
    df = ts.pro_bar(ts_code=code, adj='qfq', start_date='20150101', end_date=endtime).sort_values(
            by="trade_date", ascending=True)
    high = df['high'].tolist()
    low = df['low'].tolist()
    price = df['close'].tolist()
    amount = df['amount'].tolist()
    vol = df['vol'].tolist()
    dateList = df['trade_date'].tolist()
    if df['trade_date'][0] != endtime:
        url = 'http://d.10jqka.com.cn/v6/line/hs_{}/01/today.js'.format(code[:6])
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Referer': 'http://m.10jqka.com.cn/stockpage/hs_{}/'.format(code[:6])
        }
        r = requests.get(url, headers=headers)
        try:
            js = re.findall(':({[\S\s]+})}', r.text)[0]
            js = json.loads(js)
            high.append(js['8'])
            low.append(js['9'])
            price.append(js['11'])
            amount.append(float(js['19'])/1000)
            vol.append(float(js['13']) / 100)
            dateList.append(endtime)
        except:
            print(r.text)
    return high, low, price, amount,vol,dateList


def get_bankuai_data(code):
    dataList = []
    url = 'http://d.10jqka.com.cn/v4/line/bk_{}/01/2020.js'.format(code)
    url2 = 'http://d.10jqka.com.cn/v4/line/bk_{}/01/2019.js'.format(code)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Referer': 'http://q.10jqka.com.cn/thshy/detail/code/{}/'.format(code)
            }
    r = requests.get(url,headers=headers)
    r2 = requests.get(url2, headers=headers)
    s = re.findall('"data":"(\S+)"',r.text)[0]
    s2 = re.findall('"data":"(\S+)"', r2.text)[0]
    dataList += s2.split(';')
    dataList += s.split(';')
    return dataList

def get_bankuai_all_data():
    index = '{"公路铁路运输": "881149", "酒店及餐饮": "881161", "物流": "881152","养殖业": "881102", "家用轻工": "881139", "医疗器械服务": "881144", "石油矿业开采": "881106", "其他电子": "881123", "非汽车交运": "881127", "交运设备服务": "881128", "化工新材料": "881111", "建筑装饰": "881116", "中药": "881141", "仪器仪表": "881119", "新材料": "881114", "景点及旅游": "881160", "港口航运": "881148", "证券": "881157", "零售": "881158", "纺织制造": "881135", "采掘服务": "881107", "建筑材料": "881115", "造纸": "881137", "贸易": "881159", "专用设备": "881118", "农业服务": "881104", "服装家纺": "881136", "计算机设备": "881130", "传媒": "881164", "食品加工制造": "881134", "机场航运": "881151", "国防军工": "881166", "视听器材": "881132", "汽车整车": "881125", "计算机应用": "881163", "通信服务": "881162", "银行": "881155", "白色家电": "881131", "保险及其他": "881156", "生物制品": "881142", "化学制品": "881109", "电子制造": "881124", "医药商业": "881143", "房地产开发": "881153", "化工合成材料": "881110", "半导体及元件": "881121", "燃气水务": "881146", "园区开发": "881154", "基础化学": "881108", "钢铁": "881112", "电气设备": "881120", "通信设备": "881129", "农产品加工": "881103", "环保工程": "881147", "包装印刷": "881138", "光学光电子": "881122", "综合": "881165", "有色冶炼加工": "881113", "通用设备": "881117", "公交": "881150", "化学制药": "881140", "汽车零部件": "881126", "饮料制造": "881133","种植业与林业": "881101","电力": "881145","煤炭开采加工": "881105"}'
    index_js = json.loads(index)
    for js in index_js:
        print(js)
        with open('data/'+js+'.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date','open','high','low','close','vol','tradeAmount'])
            dataList = get_bankuai_data(index_js[js])
            for data in dataList:
                data = data.split(',')
                writer.writerow([data[0],data[1],data[2],data[3],data[4],data[5],data[6]])

def get_stock_all_data(date):
    fileList = os.listdir('code')
    for name in fileList:
        print(name)
        with open('code/' + name, "r") as f:
            for code in f.readlines():
                code = code.strip('\n')
                if code[0] == '0' or code[0] == '3':
                    code = code + '.sz'
                elif code[0] == '6':
                    code = code + '.sh'
                else:
                    print(code)
                print(code)
                high, low, price, amount,vol,dateList = get_data(code, date)
                with open('stock_data/' + code + '.csv', 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['high', 'low', 'price', 'vol', 'tradeAmount','date'])
                    for i in range(len(high)):
                        writer.writerow([high[i], low[i], price[i], vol[i], amount[i],dateList[i]])

def get_data_csv(name):
    df = pd.read_csv("data/" + str(name))
    df = df.sort_values(by="date", ascending=True)
    high = df['high'].tolist()
    low = df['low'].tolist()
    price = df['close'].tolist()
    amount = df['tradeAmount'].tolist()
    vol = df['vol'].tolist()
    return high, low, price, amount, vol

def get_stock_csv(name):
    df = pd.read_csv("stock_data/" + str(name))
    high = df['high'].tolist()
    low = df['low'].tolist()
    price = df['price'].tolist()
    amount = df['tradeAmount'].tolist()
    vol = df['vol'].tolist()
    return high, low, price, amount, vol

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
        return code,'','','','','','','','',''


def get_bankuai_ttm(industry):
    if industry == '':
        return '','','','',''
    url = 'https://eniu.com/industry/{}/market/sh'.format(industry)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    ttm = re.findall('平均市盈率：(\S+)</a>', r.text)[0]
    pb = re.findall('平均市净率：(\S+)</a>', r.text)[0]
    near3 = re.findall('近三年平均ROE：(\S+%)', r.text)[0]
    near5 = re.findall('近五年平均ROE：(\S+%)', r.text)[0]
    near = re.findall('历史平均ROE：(\S+%)', r.text)[0]
    return ttm,pb,near3,near5,near

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

def get_bankuai_low_plt(ratio):
    dir = 'data'
    fileList = os.listdir(dir)
    for name in fileList:
        print(name)
        high, low, price, amount,vol = get_data_csv(name)
        var1, var7 = count_readyup(high, low, price)
        amount = normalization(amount[-50:])
        price = normalization(price[-50:])
        var1_0 = var1[-50:] / 100
        var1_1 = var1[-51:-1] / 100
        var1 = (var1_0 - var1_1) / 2 + var1_0
        var7 = var7[-50:] / 100
        x = range(50)
        if var1[49] < ratio:
            font = {'family': 'SimHei'}
            plt.rc('font', **font)
            plt.plot(x, var1, marker='o', mec='r', mfc='w', label='var1')
            plt.plot(x, var7, marker='*', ms=10, label='var7')
            plt.plot(x, price, marker='*', ms=10, label='price')
            plt.plot(x, amount, marker='*', ms=10, label='amount')
            plt.title(name)
            plt.legend()  # 让图例生效
            plt.show()

def get_bankuai_status(name):
    high, low, price, amount = get_data_csv(name+'.csv')
    var1, var7 = count_readyup(high, low, price)
    amount = normalization(amount[-50:])
    price = normalization(price[-50:])
    var1_0 = var1[-50:] / 100
    var1_1 = var1[-51:-1] / 100
    var1 = (var1_0 - var1_1) / 2 + var1_0
    var7 = var7[-50:] / 100
    x = range(50)
    font = {'family': 'SimHei'}
    plt.rc('font', **font)
    plt.plot(x, var1, marker='o', mec='r', mfc='w', label='var1')
    plt.plot(x, var7, marker='*', ms=10, label='var7')
    plt.plot(x, price, marker='*', ms=10, label='price')
    plt.plot(x, amount, marker='*', ms=10, label='amount')
    plt.title(name)
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()

def get_status(date):
    fileList = os.listdir('code')
    for name in fileList:
        print(name)
        with open('code/' + name, "r") as f:
            for code in f.readlines():
                code = code.strip('\n')
                if code[0] == '0' or code[0] == '3':
                    code = code + '.sz'
                elif code[0] == '6':
                    code = code + '.sh'
                else:
                    print(code)
                print(code)
                high, low, price, amount = get_data(code, date, )
                var1, var7 = count_readyup(high, low, price)
                if var1[len(var1) - 1] < 15:
                    print('######' + code)

def get_stock_status_csv():
    dir = 'stock_data'
    fileList = os.listdir(dir)
    industry_list = {}
    with open("stock_status.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['股票','今日增幅','var1[0]', 'var1[1]', 'var1[2]', '是否最低标志', 'var7[0]', 'var7[1]', 'var7[2]',
                         'ttm', 'near3', 'near5', 'near10', 'near', 'ttm_ind',
                         'pb', 'pb_ind','value',
                         'roe', 'roe_near3_ind', 'roe_near5_ind','roe_near_ind'])
        for name in fileList:
            print(name)
            high, low, price, amount, vol = get_stock_csv(name)
            var1, var7 = count_readyup(high, low, price)
            ifBegin = 'False'
            for i in var7[-25:]:
                if i < 10:
                    ifBegin = 'True'
                    break
            var1 = var1[-3:]
            var7 = var7[-3:]
            ratio = (price[-1] - price[-2])/price[-2] * 100
            #其他指标
            stock_name,ttm,pb,value,roe,near3,near5,near10,near,industry = get_stock_ttm(name[-6:-4]+name[:6])
            if industry not in industry_list:
                ind_ttm, ind_pb, ind_near3, ind_near5, ind_near = get_bankuai_ttm(industry)
                industry_list[industry] = {}
                industry_list[industry]['ttm'] = ind_ttm
                industry_list[industry]['pb'] = ind_pb
                industry_list[industry]['roe_near3'] = ind_near3
                industry_list[industry]['roe_near5'] = ind_near5
                industry_list[industry]['roe_near'] = ind_near
            writer.writerow([stock_name, ratio, var1[0], var1[1], var1[2], ifBegin, var7[0], var7[1], var7[2],
                            ttm, near3, near5, near10, near, industry_list[industry]['ttm'],
                            pb, industry_list[industry]['pb'], value,
                            roe, industry_list[industry]['roe_near3'], industry_list[industry]['roe_near5'], industry_list[industry]['roe_near']])

def get_bankuai_status_csv():
    dir = 'data'
    fileList = os.listdir(dir)
    with open("bankuai_status.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name','var1[0]','var1[1]','var1[2]','var7[0]','var7[1]','var7[2]',
                         'amount[0]','amount[1]','amount[2]','per[0]','per[1]','per[2]','avg_per'])
        for name in fileList:
            print(name)
            high, low, price, amount,vol = get_data_csv(name)
            var1, var7 = count_readyup(high, low, price)
            var1 = var1[-3:]
            var7 = var7[-3:]
            amount = np.array(amount,dtype = 'float_')
            vol = np.array(vol,dtype = 'float_')
            per = amount/vol
            avg_per = sum(per)/len(per)
            amount = amount[-3:]
            vol = vol[-3:]
            per = per[-3:]
            writer.writerow([name,var1[0],var1[1],var1[2],var7[0],var7[1],var7[2],
                             amount[0],amount[1],amount[2],per[0],per[1],per[2],avg_per])

def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range

def get_stock_plot(num):
    dir = 'stock_data'
    fileList = os.listdir(dir)
    var1_sum = np.array([0] * num)
    var7_sum = np.array([0] * num)
    price_sum = np.array([0] * num)
    amount_sum = np.array([0] * num)
    fileNum = 0
    for name in fileList:
        print(name)
        high, low, price, amount, vol = get_stock_csv(name)
        var1, var7 = count_readyup(high, low, price)
        if len(var7) < num + 1:
            continue
        fileNum += 1
        var1_1 = var1[-1 * (num+1):-1]
        var7_1 = var7[-1 * (num+1):-1]
        var1 = var1[-1*num:]
        var7 = var7[-1*num:]
        var1 = (var1 - var1_1) / 2 + var1
        var7 = (var7 - var7_1) / 2 + var7
        var1_sum = var1_sum + var1[-1*num:]
        var7_sum = var7_sum + var7[-1*num:]
        price_sum = price_sum + price[-1*num:]
        amount_sum = amount_sum + amount[-1*num:]
    var1_sum = var1_sum / fileNum / 100
    var7_sum = var7_sum / fileNum / 100
    price_sum = normalization(price_sum)
    amount_sum = normalization(amount_sum)
    x = range(num)
    plt.plot(x, var1_sum, marker='o', mec='r', mfc='w', label='var1')
    plt.plot(x, var7_sum, marker='*', ms=10, label='var7')
    plt.plot(x, price_sum, marker='*', ms=10, label='price')
    plt.plot(x, amount_sum, marker='*', ms=10, label='amount')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()
    return

def get_stock_var7(date):
    df = pd.read_csv('top.csv',names=['code','name'])
    for code in df['code'].tolist():
        try:
            high, low, price, amount, vol, dateList = get_data(code, date)
        except:
            print('error' + code)
            continue
        var1, var7 = count_readyup(high, low, price)
        if var7[-1] < 15:
            if var1[-1] < 10:
                print('##########' + code)
                print(var7[-1])
            else:
                print('!!!!!!!' + code)
                print(var7[-1])


ts.set_token('d9aaf0a623896f9803e5724b0a9c37d28f471453c3ecab0c6bd69abc')
pro = ts.pro_api()
date = '20200310'
#分析板块并获取趋势图
#get_bankuai_all_data()
#get_bankuai_low_plt(0.2)
#分析板块并获取csv
#get_bankuai_all_data()
#get_bankuai_status_csv()
#m获取某一板块的趋势
#get_bankuai_status('半导体及元件')
#获取自选股的趋势
get_stock_all_data(date)
get_stock_status_csv()
#get_stock_plot(120)
#从行业龙头里寻找低点股
#get_stock_var7(date)
#get_status('20200115')

