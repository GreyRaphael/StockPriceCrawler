from fileinput import filename
import requests
import time
import csv
import os

HEADERS={
    "Host": "datacenter-web.eastmoney.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://data.eastmoney.com/",
    "Cookie": r"qgqp_b_id=a04fe66d077d3a18d42e2188587ce168; HAList=ty-1-600282-%u5357%u94A2%u80A1%u4EFD%2Cty-1-600068-%u845B%u6D32%u575D%2Cty-1-688208-%u9053%u901A%u79D1%u6280%2Cty-1-688009-%u4E2D%u56FD%u901A%u53F7%2Cty-1-600008-%u9996%u521B%u73AF%u4FDD%2Cty-1-600000-%u6D66%u53D1%u94F6%u884C%2Cty-1-601333-%u5E7F%u6DF1%u94C1%u8DEF%2Cty-1-600061-%u56FD%u6295%u8D44%u672C%2Cty-0-000001-%u5E73%u5B89%u94F6%u884C%2Cty-1-688779-%u957F%u8FDC%u9502%u79D1; em_hq_fls=js; emshistory=%5B%22%E8%A1%8C%E6%83%85%22%5D; JSESSIONID=916B95FAF1C31BDE30BF2B74BA1229E2",
    "Sec-Fetch-Dest": "script",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-site",
}

os.environ['NO_PROXY']='datacenter-web.eastmoney.com' # bypass Clash Proxy
s=requests.Session()
s.headers.update(HEADERS)

info={
    'hs300':{'pages':300, 'column':1},
    'sz50':{'pages':50, 'column':2},
    'zz500':{'pages':500, 'column':3},
    'kc50':{'pages':50, 'column':4},
}

def get_stocklist_dict():
    stocklist_dict={}
    true=True
    for k in info:
        pages=info[k]['pages']
        column=info[k]['column']
        timestamp=int(time.time()*1000)
        url=f'https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery1123012439262961766051_{timestamp}&sortColumns=SECURITY_CODE&sortTypes=1&pageSize={pages}&pageNumber=1&reportName=RPT_INDEX_TS_COMPONENT&columns=SECURITY_CODE&source=WEB&client=WEB&filter=(TYPE="{column}")'
        txt=s.get(url).text[43:-2]
        jData=eval(txt)
        stocklist_dict[k]=[item['SECURITY_CODE'] for item in jData['result']['data']]
    return stocklist_dict

def writeList(filename, stock_list):
    with open(filename, 'w', encoding='utf8') as file:
        for code in stock_list:
            line=f'{code}\n'
            file.write(line)


if __name__ == "__main__":
    stocklist_dict=get_stocklist_dict()
    for k in stocklist_dict:
        filename=f'input/{k}.txt'
        stocklist=stocklist_dict[k]
        print(f'write {filename}...')
        writeList(filename, stocklist)