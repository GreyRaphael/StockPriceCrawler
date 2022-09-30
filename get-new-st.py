import requests
import time
import csv
import os

HEADERS={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'http://quote.eastmoney.com/',
    'Cookie': r'qgqp_b_id=a04fe66d077d3a18d42e2188587ce168; HAList=ty-1-900937-*ST%u534E%u7535B%2Cty-1-600519-%u8D35%u5DDE%u8305%u53F0%2Cty-1-600008-%u9996%u521B%u73AF%u4FDD%2Cty-0-000001-%u5E73%u5B89%u94F6%u884C%2Cty-1-600570-%u6052%u751F%u7535%u5B50%2Cty-0-301069-%u51EF%u76DB%u65B0%u6750%2Cty-0-000063-%u4E2D%u5174%u901A%u8BAF%2Cty-1-688981-%u4E2D%u82AF%u56FD%u9645%2Cty-1-603927-%u4E2D%u79D1%u8F6F%2Cty-0-300618-%u5BD2%u9510%u94B4%u4E1A; em_hq_fls=js; emshistory=%5B%22%E8%A1%8C%E6%83%85%22%5D',
}

os.environ['NO_PROXY']='push2.eastmoney.com' # bypass Clash Proxy
s=requests.Session()
s.headers.update(HEADERS)

INFO={
    'new':(5,8,1,'f26'), # 新股总共19页,这里为了速度改为5
    'st':(8,4,0,'f2')
}

def get_stocklist(StockTypeInfo):
    TotaPage, tab, asc, sort_field = StockTypeInfo
    stocklist=[]
    timestamp_end=int(time.time()*1000)
    timestamp_start=timestamp_end-10
    for i in range(TotaPage):
        url=f'http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery1124004984617104929223_{timestamp_start}&pn={i+1}&pz=20&po={asc}&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid={sort_field}&fs=m:0+f:{tab},m:1+f:{tab}&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f11,f62,f128,f136,f115,f152&_={timestamp_end}'
        print(url)
        txt=s.get(url).text[43:-2]
        jData=eval(txt)
        for item in jData['data']['diff']:
            if item['f2']=='-': continue
            temp={}
            code = item['f12']
            secucode = f'{code}.SH' if code.startswith('6') else f'{code}.SZ'
            temp['SECUCODE']=secucode
            temp['name']=item['f14']
            temp['launch']=item['f26']
            temp['f2']=item['f2']
            temp['f3']=item['f3']
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
    sz00_list.sort(key=lambda x: x[key], reverse=True)
    sz30_list.sort(key=lambda x: x[key], reverse=True)
    sh60_list.sort(key=lambda x: x[key], reverse=True)
    sh688_list.sort(key=lambda x: x[key], reverse=True)
    return sz00_list+sz30_list+sh60_list+sh688_list

def writeCSV(filename, stock_list):
    colNames=stock_list[0].keys()
    with open(filename,'w',encoding='utf8',newline='') as file:
        csv_writer=csv.DictWriter(file, fieldnames=colNames)
        csv_writer.writeheader()
        csv_writer.writerows(stock_list)

def get_st_stock():
    stock_list=get_stocklist(StockTypeInfo=INFO['st'])
    seperated_list=seperate_stocks(stock_list, key='name', num=10)
    writeCSV('st.csv', seperated_list)

def get_new_stocks():
    stock_list=get_stocklist(StockTypeInfo=INFO['new'])
    seperated_list=seperate_stocks(stock_list,key='launch', num=5)
    writeCSV('new.csv', seperated_list)

if __name__ == "__main__":
    get_new_stocks()
    get_st_stock()
