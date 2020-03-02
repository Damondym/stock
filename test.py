import requests

url = 'http://1.optbbs.com/d/csv/d/vixk.csv?v=1582810470557'
r = requests.get(url)
print(r.text)