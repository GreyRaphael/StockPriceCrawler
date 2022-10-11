import requests
import time
import csv
import os

HEADERS={
    "Host": "push2ex.eastmoney.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Referer": "http://quote.eastmoney.com/",
    "Cookie": r"qgqp_b_id=a04fe66d077d3a18d42e2188587ce168; HAList=ty-1-900937-*ST%u534E%u7535B%2Cty-1-600519-%u8D35%u5DDE%u8305%u53F0%2Cty-1-600008-%u9996%u521B%u73AF%u4FDD%2Cty-0-000001-%u5E73%u5B89%u94F6%u884C%2Cty-1-600570-%u6052%u751F%u7535%u5B50%2Cty-0-301069-%u51EF%u76DB%u65B0%u6750%2Cty-0-000063-%u4E2D%u5174%u901A%u8BAF%2Cty-1-688981-%u4E2D%u82AF%u56FD%u9645%2Cty-1-603927-%u4E2D%u79D1%u8F6F%2Cty-0-300618-%u5BD2%u9510%u94B4%u4E1A; em_hq_fls=js; emshistory=%5B%22%E8%A1%8C%E6%83%85%22%5D",
}

os.environ['NO_PROXY']='push2ex.eastmoney.com' # bypass Clash Proxy
s=requests.Session()
s.headers.update(HEADERS)

def get_stocklist(info):
    stocklist=[]
    url_date=time.strftime('%Y%m%d')
    timestamp=int(time.time()*1000)
    url=f'http://push2ex.eastmoney.com/getTopic{info}Pool?cb=callbackdata8666913&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=170&sort=c:asc&date={url_date}&_={timestamp}'
    txt=s.get(url).text[20:-2]
    jData=eval(txt)
    for item in jData['data']['pool']:
        temp={}
        code=item['c']
        secucode = f'{code}.SH' if code.startswith('6') else f'{code}.SZ'
        temp['SECUCODE']=secucode
        temp['name']=item['n']
        temp['f2']=item['p']/1000
        temp['f3']=round(item['zdp'], 2)
        stocklist.append(temp)
    return stocklist

def seperate_stocks(stock_list, key, num):
    sz00_list=[]
    sz30_list=[]
    sh60_list=[]
    sh688_list=[]
    COUNTER=[num]*4
    for item in stock_list:
        secucode=item['SECUCODE']
        if secucode.startswith('0') and COUNTER[0]>0:
            COUNTER[0]-=1
            sz00_list.append(item)
        elif secucode.startswith('3') and COUNTER[1]>0:
            COUNTER[1]-=1
            sz30_list.append(item)
        elif secucode.startswith('688') and COUNTER[2]>0:
            COUNTER[2]-=1
            sh688_list.append(item)
        elif secucode.startswith('60') and COUNTER[3]>0:
            COUNTER[3]-=1
            sh60_list.append(item)
    sz00_list.sort(key=lambda x: x[key])
    sz30_list.sort(key=lambda x: x[key])
    sh60_list.sort(key=lambda x: x[key])
    sh688_list.sort(key=lambda x: x[key])
    return sz00_list+sz30_list+sh60_list+sh688_list

def writeCSV(filename, stock_list):
    colNames=stock_list[0].keys()
    with open(filename,'w',encoding='utf8',newline='') as file:
        csv_writer=csv.DictWriter(file, fieldnames=colNames)
        csv_writer.writeheader()
        csv_writer.writerows(stock_list)

def get_ZhangTing():
    stock_list=get_stocklist('ZT')
    seperated_list=seperate_stocks(stock_list, key='f2', num=5)
    print(f'涨停 length={len(seperated_list)}')
    writeCSV('output/zhangT.csv', seperated_list)

def get_DieTing():
    stock_list=get_stocklist('DT')
    seperated_list=seperate_stocks(stock_list, key='f2', num=5)
    print(f'跌停 length={len(seperated_list)}')
    writeCSV('output/dieT.csv', seperated_list)

if __name__ == "__main__":
    # 数据源: http://quote.eastmoney.com/ztb/
    print('begin crawler')
    get_ZhangTing()
    get_DieTing()
    print('end crawler')