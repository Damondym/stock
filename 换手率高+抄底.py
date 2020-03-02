import requests
import json
import demjson
import numpy as np
from matplotlib import pyplot
import matplotlib.pyplot as plt
import tushare as ts
from multiprocessing import Pool
import re

def get_pe_price(id):
    url = 'https://eniu.com/chart/pea/{}'.format(id)
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
    r = requests.get(url,headers=headers)
    js = json.loads(r.text)
    pe = js['pe_ttm']
    date = js['date']
    price = js['price']
    return date, pe, price

def get_turnover(turnover):
    page = 1
    turnover_list = []
    while page:
        url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={}&num=100&sort=turnoverratio&asc=0&node=hs_a&symbol=&_s_r_a=page'.format(page)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        r = requests.get(url, headers=headers)
        share_list = r.text[1:-1].replace('},{','}},{{').split('},{')
        for share in share_list:
            js = demjson.decode(share)
            if js['turnoverratio'] < turnover:
                page = -1
                break
            else:
                turnover_list.append(js)
        page += 1
    return turnover_list

def get_sz50():
    sz50 = []
    url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple?page=1&num=50&sort=symbol&asc=1&node=zhishu_000016&_s_r_a=init'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    share_list = r.text[1:-1].replace('},{', '}},{{').split('},{')
    for share in share_list:
        js = demjson.decode(share)
        sz50.append(js)
    return sz50

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

def get_data(code,endtime,type = ''):
    if type == '':
        df = ts.pro_bar(ts_code=code, adj='qfq', start_date='20190101', end_date=endtime).sort_values(
            by="trade_date", ascending=True)
    elif type == 'zs':
        df = pro.index_daily(ts_code=code, start_date='20190101', end_date=endtime).sort_values(
            by="trade_date", ascending=True)
    high = df['high'].tolist()
    low = df['low'].tolist()
    price = df['close'].tolist()
    amount = df['amount'].tolist()
    vol = df['vol'].tolist()
    date = df['trade_date'].tolist()
    if df['trade_date'][0] != endtime:
        if type == '':
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
            amount.append(float(js['19'])/1000)
            vol.append(float(js['13'])/100)
        elif type == 'zs':
            url = 'http://d.10jqka.com.cn/v4/line/zs_1B0016/01/today.js'
            headers = {
                'Referer': 'http://q.10jqka.com.cn/zs/detail/code/1B0016/',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Mobile Safari/537.36',
            }
            r = requests.get(url, headers=headers)
            js = re.findall(':({[\S\s]+})}', r.text)[0]
            js = json.loads(js)
            high.append(js['8'])
            low.append(js['9'])
            price.append(js['11'])
            amount.append(float(js['19'])/1000)
            vol.append(float(js['13'])/100)
            date.append(endtime)
    return high, low, price, amount, vol , date
    '''
    if type == '':
        code = "cn_"+code
    elif type == 'zs':
        code = type+'_'+code
    high = []
    low = []
    price = []
    url = 'http://q.stock.sohu.com/hisHq?code={}&start=20190301&end={}&stat=1&order=D&period=d&callback=historySearchHandler&rt=jsonp'.format(code,endtime)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    js = json.loads(r.text[22:-3])
    try:
        hq = js['hq']
    except:
        print(code)
        print(js)
        return
    for day in hq:
        high.append(day[6])
        low.append(day[5])
        price.append(day[2])
    high.reverse()
    low.reverse()
    price.reverse()
    return high,low,price
    '''
def process(share,date):
    code = share['code'] + '.' + share['symbol'][:2]
    try:
        high, low, price = get_data(code, date)
        high.append(share['high'])
        low.append(share['low'])
        price.append(share['trade'])
        var1, var7 = count_readyup(high, low, price)
        if len(var1) < 150:
            return
        if var1[len(var1) - 1] < 10 and var7[len(var7) - 1] < 11:  # and var7[len(var7) - 1] < 11:
            print('########' + code)
        elif var1[len(var1) - 1] < 10:
            print('****' + code)
        # elif var7[len(var7) - 1] < 11:
        #    print('!!!!'+code)
    except:
        print(code)

def choose_stock(turnover,date):
    turnoverList = get_turnover(turnover)
    dateList = [date]*len(turnoverList)
    args_zip = list(zip(turnoverList,dateList))
    p = Pool(4)
    p.starmap(process, args_zip)
    p.close()
    p.join()

def count_var(code,type=''):
    high, low, price,amount = get_data(code, '20191230',type)
    var1, var7 = count_readyup(high, low, price)
    return var1,var7

def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range

def buy_sale_stock(priceList,var1):
    status = 0
    buyPrice = 0
    earn = 0
    ifSale = 0
    for i,var in enumerate(var1):
        if ifSale:
            status = 0
            ifSale = 0
            print(df.iloc[[i + 5]]["trade_date"].values[0])
            print('sale' + str(priceList[i]))
            print((priceList[i] - buyPrice) / buyPrice)
            earn += (priceList[i] - buyPrice) / buyPrice
        if var < 10 and status == 0:
            status = 1
            buyPrice = priceList[i]
            print(df.iloc[[i + 5]]["trade_date"].values[0])
            print('buy' + str(priceList[i]))
        elif var > 90 and status == 1:
            status = 0
            ifSale = 0
            print(df.iloc[[i + 5]]["trade_date"].values[0])
            print('sale' + str(priceList[i]))
            print((priceList[i] - buyPrice) / buyPrice)
            earn += (priceList[i] - buyPrice) / buyPrice
    print(earn)

def process_count(stock,date):
    code = stock['code'] + '.' + stock['symbol'][:2]
    high, low, price, amount, vol,date_list = get_data(code, date)
    var1, var7 = count_readyup(high, low, price)
    var1_1 = var1[-91:-1]
    var7_1 = var7[-91:-1]
    var1 = var1[-90:]
    var7 = var7[-90:]
    var1 = (var1 - var1_1) / 2 + var1
    var7 = (var7 - var7_1) / 2 + var7
    return var1,var7

def get_dirction(date):
    a, b, sz, amount, vol, date_list = get_data('000016.SH', date, 'zs')
    sz = np.array(sz, dtype='float_')[-90:]
    amount = np.array(amount, dtype='float_')[-90:]
    print((amount[-1]-amount[-2])/amount[-2])
    vol = np.array(vol, dtype='float_')[-90:]
    per = amount / vol
    dateList = [date]*90
    data = get_sz50()
    args_zip = list(zip(data, dateList))
    p = Pool(4)
    varList = p.starmap(process_count, args_zip)
    var1_sum = np.array([0] * 90)
    var7_sum = np.array([0] * 90)
    for var in varList:
        var1_sum = var1_sum + var[0]
        var7_sum = var7_sum + var[1]
        '''
    for stock in data:
        
        code = stock['code'] + '.' + stock['symbol'][:2]
        high, low, price = get_data(code, '20200110')
        var1, var7 = count_readyup(high, low, price)
        var1_1 = var1[-91:-1]
        var7_1 = var7[-91:-1]
        var1 = var1[-90:]
        var7 = var7[-90:]
        var1 = (var1 - var1_1) / 2 + var1
        var7 = (var7 - var7_1) / 2 + var7
        var1_sum = var1_sum + var1
        var7_sum = var7_sum + var7
    '''
    var1_sum = var1_sum / 50
    var7_sum = var7_sum / 50
    var1_sum = var1_sum / 100  # normalization(var1_sum)
    var7_sum = var7_sum / 100  # normalization(var7_sum)
    sz = normalization(sz)
    amount = normalization(amount)
    per = normalization(per)
    #per = per / 2
    x = range(90)
    plt.plot(x, var1_sum, marker='o', mec='r', mfc='w', label='var1')
    #plt.plot(x, var7_sum, marker='*', ms=10, label='var7')
    plt.plot(x, sz, marker='*', ms=10, label='sz')
    plt.plot(x, amount, marker='*', ms=10, label='amount')
    plt.plot(x, per, marker='*', ms=10, label='per')
    plt.grid(axis="x")
    plt.legend(loc='upper left')  # 让图例生效
    plt.show()

if __name__ == '__main__':
    ts.set_token('d9aaf0a623896f9803e5724b0a9c37d28f471453c3ecab0c6bd69abc')
    pro = ts.pro_api()
    date = '20200228'

    #choose_stock(15,'20200110')
    get_dirction(date)
    '''
    a, b, sz, amount, vol,date = get_data('000016.SH', date, 'zs')
    sz = sz
    amount = amount[:-6]
    date = date[:-6]
    num1 = 0
    num2 = 0
    result = [0,0,0,0,0]
    result2 = [0, 0, 0, 0, 0]
    for i in range(len(amount)-1):
        if (amount[i+1] - amount[i])/ amount[i] < -0.08:
            print(date[i+1])
            num1 += 1
            for k in range(len(result)):
                result[k] += (sz[i+1+k] - sz[i])/sz[i]
        else:
            num2 += 1
            for k in range(len(result2)):
                result2[k] += (sz[i + 1 + k] - sz[i]) / sz[i]
    result = [i/num1 for i in result]
    result2 = [i / num2 for i in result2]
    print(result)
    print(result2)
    print('[-0.0015055366198569564, -0.0015862842305952051, 0.0008959632991999697, 0.004421402458890069, 0.004861482303152965]')
    print('[0.0026434386023270516, 0.003972436336717862, 0.0037543415203713827, 0.002967048782785959, 0.004157233524311797]')
    print('[-0.0014494059536010544, -0.0015355994446962118, 0.0011129078873739976, 0.004785606806727731, 0.004979400847849]')
    print('[0.0023719225154711487, 0.0036212815599211278, 0.0034755409006577667, 0.0028646719064779275, 0.004137734435745481]')
    '''

    #high, low, price, amount,vol = get_data('601100.SH', '20200206')
    #var1, var7 = count_readyup(high, low, price)
    #print(var7)

