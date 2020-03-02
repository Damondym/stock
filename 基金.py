import requests
import json
import re
from bs4 import BeautifulSoup
import csv

def get_fund_keep():
    url = 'https://api.fund.eastmoney.com/Favor/Get'
    headers = {
        'Cookie': 'qgqp_b_id=41bfe91e7be550f67c1d680056d7af74; pgv_pvi=5144269824; _qddaz=QD.p5v2mr.ew4yli.k1jfnsvu; intellpositionL=1519.19px; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND0=null; EMFUND8=01-22%2000%3A04%3A16@%23%24%u94F6%u6CB3%u521B%u65B0%u6210%u957F%u6DF7%u5408@%23%24519674; EMFUND9=01-22 00:12:19@#$%u8BFA%u5B89%u53CC%u5229%u503A%u5238%u53D1%u8D77@%23%24320021; cowCookie=true; intellpositionT=1055px; st_si=89589852651242; st_asi=delete; p_origin=https%3A%2F%2Fpassport2.eastmoney.com; ct=LCLibMMZWtzjtVmhxJUKtmVONrY_pA_yVmjoLgO_gNs_CSZonQB_KMUjTh9SbC80JMV56eawC00uzoPMi41PCmT-lXrg_dB691x71ZkGQjQmGoCvtaDq1QRjhqN24h4aqJzydWrOh1cvVx0WJ_rC7ekVahSAxj-fbKnmrXRoXp0; ut=FobyicMgeV7bfas_M05TDBeQtx2NIVX8sfhCW1jvs-v_9ybTHHnZz_M7Cm-BuWMwNgCr3eLhEYLII73k_o-YcX7SNmIhCgWgrL5_N5YMqNtdMcWB9iA9007GMvvlSnhwjm45xRAY1ic1HfaV6Ng0AFiWDrwm8POZEj7Jv8UEGEnb3K3oknHlyMNiAAo87n66jLUaFke9f1dWPotwwWe3xAIDt2LJIUUkIudegFxFqPRbEetjQmlxrlocctXY9GU0BUeFWCC6N8bIf3TILokc_YKJoZu0ucuZ; pi=8239385706043144%3bi8239385706043144%3b%e8%82%a1%e5%8f%8b7kQacU%3baT9LubdCJyJngGTB9qvKAb0ad7noTYqTdB%2fAYYPr305BXtdxBzSCCYLFONaVm4Ap3JMqnB0KlUcHm2jOaoLwnaWdOqOgvbOd4N3pOUfjceL67OhESMjCm7lZFbQ3xDknmckXzgCCdbjZf9kmYhWl7t0%2fWjDH5Gzpl9sh7ODcB9nhOoYZy%2bfvbc6gHOKbxTd%2fyfTx%2fc%2bc%3bSTD4fHp5Yp%2bCP6PvmDAZzBDsFCjjwzMd07nGBR4fslWjdmImaRWIAFUh9lhuqanVoo00GaS7XL4wZ3OlngeiAe1lCvoQo%2f%2fI9ZnoDz4NWgUOEU7xpJnnihpfTkQhvI2pGu5EP3FwEiRm6Wfbkquey9%2fZP%2bsrnw%3d%3d; uidal=8239385706043144%e8%82%a1%e5%8f%8b7kQacU; sid=139377040; vtpst=|; st_pvi=82409689587042; st_sp=2019-10-09%2023%3A32%3A14; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=10; st_psi=20200122144053190-119146300572-2046856648',
        'Host': 'api.fund.eastmoney.com',
        'Referer': 'http://favor.fund.eastmoney.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    }
    r = requests.get(url,headers=headers)
    js = json.loads(r.text)
    return js['Data']['KFS']

def get_fund_status(code):
    url = 'http://fund.eastmoney.com/{}.html'.format(code)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    }
    r = requests.get(url,headers=headers)
    r.encoding = 'utf-8'
    text = BeautifulSoup(r.text,'html.parser').get_text()
    near_1_mon = re.findall('近1月：(\S+?)%',text)[0]
    near_3_mon = re.findall('近3月：(\S+?)%',text)[0]
    near_6_mon = re.findall('近6月：(\S+?)%',text)[0]
    near_1_year = re.findall('近1年：(\S+?)%',text)[0]
    near_3_year = re.findall('近3年：(\S+?)%',text)[0]
    if '-' in near_3_year:
        near_3_year = ''
    level = re.findall('class="jjpj(\d?)"',r.text)[0]
    behavior = re.findall('ranking rank_(\d?)',r.text)
    return near_1_mon,near_3_mon,near_6_mon,near_1_year,near_3_year,level,behavior


with open("fund_status.csv", 'w', newline='') as f:
    writer = csv.writer(f)
    keep_list = get_fund_keep()
    writer.writerow(['基金名字','代码','类型','今日收益率','近1月','近3月','近6月','近1年','近3年',
                     '潜在收益','等级','近1月','近1月','近3月','近6月','近1年','近3年'])
    for keep in keep_list:
        code = keep['FCODE']
        type = keep['FTYPE']
        fsrq = keep['FSRQ']
        name = keep['SHORTNAME']
        ratio = keep['gszzl']
        near_1_mon, near_3_mon, near_6_mon, near_1_year, near_3_year, level, behavior = get_fund_status(code)
        if near_3_year == '':
            possible = ''
        else:
            possible = (1 + float(near_3_year)/100) ** 0.3333333333333333333333333333333 * 100 - 100
        writer.writerow([name,code,type,ratio,
                         near_1_mon, near_3_mon, near_6_mon, near_1_year, near_3_year, possible, level,
                         behavior[1],behavior[2],behavior[3],behavior[5],behavior[7]])

