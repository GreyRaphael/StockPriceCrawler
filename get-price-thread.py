import requests
import time
import csv
import sys
import os
import concurrent.futures
import random

os.environ['NO_PROXY']='push2ex.eastmoney.com' # bypass Clash Proxy
s=requests.Session()


def get_codelist(stock_file):
    code_list=[]
    with open(stock_file,'r',encoding='utf8') as file:
        for line in file:
            code = line.rstrip('\n')
            if code.startswith('0') or code.startswith('3'):
                code_list.append((0, code))
            elif code.startswith('6'):
                code_list.append((1, code))
    return code_list


def generate_headers():
    num=random.randint(90, 105)
    return {
        "Host": "push2ex.eastmoney.com",
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{num}.0) Gecko/20100101 Firefox/{num}.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Referer": "http://quote.eastmoney.com/",
        "Cookie": r"qgqp_b_id=a04fe66d077d3a18d42e2188587ce168; HAList=ty-1-600570-%u6052%u751F%u7535%u5B50%2Cty-0-301069-%u51EF%u76DB%u65B0%u6750%2Cty-0-000063-%u4E2D%u5174%u901A%u8BAF%2Cty-1-688981-%u4E2D%u82AF%u56FD%u9645%2Cty-0-000001-%u5E73%u5B89%u94F6%u884C%2Cty-1-603927-%u4E2D%u79D1%u8F6F%2Cty-0-300618-%u5BD2%u9510%u94B4%u4E1A%2Cty-0-300168-%u4E07%u8FBE%u4FE1%u606F%2Cty-1-601258-%u5E9E%u5927%u96C6%u56E2%2Cty-1-600743-%u534E%u8FDC%u5730%u4EA7; em_hq_fls=js; emshistory=%5B%22%E8%A1%8C%E6%83%85%22%5D",
    }


def get_price(codeinfo):
    market, code = codeinfo
    secucode = f'{code}.SZ' if market==0 else f'{code}.SH'

    timestamp_end=int(time.time()*1000)
    timestamp_start=timestamp_end-1
    # 10档行情也在push2ex.eastmoney.com, f31~f12
    url=f'http://push2ex.eastmoney.com/getStockFenShi?pagesize=1&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wzfscj&pageindex=0&sort=2&ft=1&cb=jQuery351015686815628587114_{timestamp_start}&code={code}&market={market}&_={timestamp_end}'
    # print(url)
    rand_headers=generate_headers()
    s.headers.update(rand_headers)
    txt = s.get(url).text[42:-2]
    jData=eval(txt)
    
    preclose=jData['data']['cp']
    lastprice=jData['data']['data'][0]['p']
    # lastvolume=jData['data']['data'][0]['v']
    f3=round(100*(lastprice/preclose-1), 2)
    return {'SECUCODE': secucode, 'f2': lastprice/1000, 'f3': f3}


def get_pricelist(code_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        return executor.map(get_price, code_list)


def writeCSV(filename, price_list):
    colNames=price_list[0].keys()
    with open(filename,'w',encoding='utf8',newline='') as file:
        csv_writer=csv.DictWriter(file, fieldnames=colNames)
        csv_writer.writeheader()
        csv_writer.writerows(price_list)


def seperateList(price_list, N=None):
    sz00_list=[]
    sz30_list=[]
    sh60_list=[]
    sh688_list=[]
    for item in price_list:
        secucode=item['SECUCODE']
        # price=item['f2']
        if secucode.startswith('0'):
            sz00_list.append(item)
        elif secucode.startswith('3'):
            sz30_list.append(item)
        elif secucode.startswith('60'):
            sh60_list.append(item)
        elif secucode.startswith('688'):
            sh688_list.append(item)

    if sz00_list:
        writeCSV(f'output/sz00.csv', sz00_list[:N])
    if sz30_list:
        writeCSV(f'output/sz30.csv', sz30_list[:N])
    if sh60_list:
        writeCSV(f'output/sh60.csv', sh60_list[:N])
    if sh688_list:
        writeCSV(f'output/sh688.csv', sh688_list[:N])


if __name__ == "__main__":
    argvs=sys.argv
    stockfile='input/stocks.txt'
    seperate_num=None
    if len(argvs)==1:
        pass
    elif len(argvs)==2:
        stockfile=argvs[1]
    elif len(argvs)==3:
        stockfile=argvs[1]
        seperate_num=int(argvs[2])
    else:
        print('to many arguments')
        sys.exit(0)
    
    print('begin crawler')
    code_list=get_codelist(stockfile)
    # 数据源: http://quote.eastmoney.com/sz000002.html#fullScreenChart
    price_generator=get_pricelist(code_list)
    print('end crawler')

    # generate list and sort
    price_list=list(price_generator)
    # price_list.sort(key=lambda x: x['SECUCODE'])
    price_list.sort(key=lambda x: x['f2'])
    # price_list.sort(key=lambda x: x['f3'], reverse=True)

    # write2csv
    print(f'price list length={len(price_list)}')
    writeCSV("output/price_eastmoney_3s.csv",price_list)
    seperateList(price_list, N=seperate_num)
