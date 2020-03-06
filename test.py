import requests
import csv

with open("e.csv", 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['MMSI','IMO','船名','船长','船宽','载重吨','总吨','吃水'])
    with open('t1.csv', newline='', encoding='UTF-8') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            mmsi = row[0]
            print('mmsi: ' + mmsi)
            url = 'http://www.chinaports.com/shiptracker/newshipquery.do?method=search&isall=1&vession=0&cnqp={}&queryParam={}'.format(mmsi,mmsi)
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            }
            r = requests.get(url,headers=headers)
            try:
                shipid = r.text.split(',')[1].strip()[1:-1]
            except:
                print('shipid not exsit:  ' + str(mmsi))
                writer.writerow([mmsi, '', '', '','','','',''])
	continue
            print('shipid: ' + shipid)
            urlDetail = 'http://www.chinaports.com/shiptracker/shipinit.do?method=shipInfo&userid={}&source=0'.format(shipid)
            r = requests.get(urlDetail,headers=headers)
            data = r.text[1:-1].split(',')
            try:
                imo = data[2]
                name = data[18]
                length = data[12]
                width = data[14]
                zaizongdun = data[21]
                zongdun = data[20]
                chishui = data[16]
                writer.writerow([mmsi,imo,name,length,width,zaizongdun,zongdun,chishui])
            except:
	writer.writerow([mmsi, '', '', '','','','',''])
                print('###error: '+shipid)
                print(r.text)