import requests



url = 'http://www.chinaports.com/shiptracker/newshipquery.do?method=search&isall=1&vession=0&cnqp=413687000&queryParam=413687000'
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
}
r = requests.get(url,headers=headers)
shipid = r.text.split(',')[1].strip()[1:-1]
print(shipid)
urlDetail = 'http://www.chinaports.com/shiptracker/shipinit.do?method=shipInfo&userid={}&source=0'.format(shipid)
r = requests.get(urlDetail,headers=headers)
data = r.text[1:-1].split(',')
imo = data[2]
name = data[18]
length = data[12]
width = data[14]
zaizongdun = data[21]
zongdun = data[20]
chishui = data[16]