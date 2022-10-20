import requests
import time
import csv
import os

HEADERS={
'Host': 'push2.eastmoney.com',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
'Accept': '*/*',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate',
'Connection': 'keep-alive',
'Referer': 'http://quote.eastmoney.com/',
'Cookie': r'qgqp_b_id=a04fe66d077d3a18d42e2188587ce168; HAList=ty-0-001300-%u4E09%u67CF%u7855%2Cty-1-510300-%u6CAA%u6DF1300ETF%2Cty-1-113021-%u4E2D%u4FE1%u8F6C%u503A%2Cty-1-110038-%u6D4E%u5DDD%u8F6C%u503A%2Cty-1-601066-%u4E2D%u4FE1%u5EFA%u6295%2Cty-0-128145-%u65E5%u4E30%u8F6C%u503A%2Cty-1-518880-%u9EC4%u91D1ETF%2Cty-0-159985-%u8C46%u7C95ETF%2Cty-1-600282-%u5357%u94A2%u80A1%u4EFD%2Cty-1-600068-%u845B%u6D32%u575D; em_hq_fls=js; emshistory=%5B%22S*ST%22%2C%22%E5%8F%AF%E8%BD%AC%E5%80%BA%22%2C%22%E6%B7%B1100ETF%22%2C%22%E8%A1%8C%E6%83%85%22%5D',
}

os.environ['NO_PROXY']='push2.eastmoney.com' # bypass Clash Proxy
s=requests.Session()
s.headers.update(HEADERS)

def get_total_numbers(ini_url, start=42):
    txt=s.get(ini_url).text[start:-2]
    jData=eval(txt)
    return jData['data']['total']


def get_stocklist(url, start=42):
    stocklist=[]
    txt=s.get(url).text[start:-2]
    jData=eval(txt)
    for item in jData['data']['diff']:
        if item['f2']=='-': continue
        temp={}
        code = item['f12']
        secucode = f'{code}.SH' if code.startswith('11') else f'{code}.SZ'
        temp['SECUCODE']=secucode
        temp['name']=item['f14']
        temp['f2']=item['f2']
        stocklist.append(temp)
    return stocklist

def writeCSV(filename, stock_list):
    colNames=stock_list[0].keys()
    with open(filename,'w',encoding='utf8',newline='') as file:
        csv_writer=csv.DictWriter(file, fieldnames=colNames)
        csv_writer.writeheader()
        csv_writer.writerows(stock_list)

def get_sh_kzz(num=5):
    timestamp_end=int(time.time()*1000)
    timestamp_start=timestamp_end-10
    
    ini_url=f'http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112405834242064147962_{timestamp_start}&pn=1&pz=1&po=0&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f2&fs=m:1+b:MK0354&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152&_={timestamp_end}'
    total_numbers=get_total_numbers(ini_url, 42)

    url=f'http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112405834242064147962_{timestamp_start+20}&pn=1&pz={total_numbers//4}&po=0&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f2&fs=m:1+b:MK0354&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152&_={timestamp_end+20}'
    stock_list =  get_stocklist(url, 42)
    print(f'new stocks length={len(stock_list)}')
    writeCSV('output/sh_kzz.csv', stock_list[:5])


def get_sz_kzz(num=5):
    timestamp_end=int(time.time()*1000)
    timestamp_start=timestamp_end-10
    
    ini_url=f'http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery1124011940983944937822_{timestamp_start}&pn=1&pz=1&po=0&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f2&fs=m:0 b:MK0354&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152&_={timestamp_end}'
    total_numbers=get_total_numbers(ini_url, 43)
    print(total_numbers)

    url=f'http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery1124011940983944937822_{timestamp_start}&pn=1&pz=100&po=0&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f2&fs=m:0 b:MK0354&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152&_={timestamp_end}'
    print(url)
    stock_list =  get_stocklist(url, 43)
    print(f'new stocks length={len(stock_list)}')
    writeCSV('output/sz_kzz.csv', stock_list[:5])

if __name__ == "__main__":
    # 数据源:
    # http://quote.eastmoney.com/center/gridlist.html#bond_convertible_sh
    # http://quote.eastmoney.com/center/gridlist.html#bond_convertible_sz
    get_sh_kzz()
    get_sz_kzz()