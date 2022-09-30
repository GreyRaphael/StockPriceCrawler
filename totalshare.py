import requests
import time
import csv
import sys
import os
import concurrent.futures
import random

os.environ['NO_PROXY']='push2.eastmoney.com' # bypass Clash Proxy
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


def get_totalshare(codeinfo):
    market, code = codeinfo
    secucode = f'{code}.SZ' if market==0 else f'{code}.SH'

    timestamp_end=int(time.time()*1000)
    timestamp_start=timestamp_end-2
    url=f'http://push2.eastmoney.com/api/qt/stock/get?ut=fa5fd1943c7b386f172d6893dbfba10b&fltt=2&invt=2&volt=2&fields=f43,f58,f116&secid={market}.{code}&cb=jQuery35105642795117372283_{timestamp_start}&_={timestamp_end}'
    # print(url)
    rand_headers=generate_headers()
    s.headers.update(rand_headers)
    txt = s.get(url).text[41:-2]
    jData=eval(txt)
    
    name=jData['data']['f58']
    close_price=jData['data']['f43']
    total_asset=jData['data']['f116']
    total_share=int(total_asset/close_price)
    limit_share=total_share//1000 # 小于等于改值不触发集中度风控;大于该值触发集中度风控;
    return {'SECUCODE': secucode, 'Name': name,'TotalShare': total_share, 'LimitShare':limit_share}


def get_detaillist(code_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        return executor.map(get_totalshare, code_list)


def writeCSV(filename, detail_list):
    colNames=detail_list[0].keys()
    with open(filename,'w',encoding='utf8',newline='') as file:
        csv_writer=csv.DictWriter(file, fieldnames=colNames)
        csv_writer.writeheader()
        csv_writer.writerows(detail_list)


def seperateList(detail_list, N=None):
    sz00_list=[]
    sz30_list=[]
    sh60_list=[]
    sh688_list=[]
    for item in detail_list:
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

    writeCSV(f'output/details-sz00.csv', sz00_list[:N])
    writeCSV(f'output/details-sz30.csv', sz30_list[:N])
    writeCSV(f'output/details-sh60.csv', sh60_list[:N])
    writeCSV(f'output/details-sh688.csv', sh688_list[:N])


if __name__ == "__main__":
    argvs=sys.argv
    if len(argvs)==1:
        stockfile='input/stocks.txt'
    elif len(argvs)==2:
        stockfile=argvs[1]
    else:
        print('to many arguments')
        sys.exit(0)
    
    print('begin crawler')
    code_list=get_codelist(stockfile)
    detail_generator=get_detaillist(code_list)

    # generate list and sort
    detail_list=list(detail_generator)
    # detail_list.sort(key=lambda x: x['SECUCODE'])
    detail_list.sort(key=lambda x: x['TotalShare'], reverse=True) # 总股本排序

    # write2csv
    writeCSV("output/details.csv",detail_list)
    seperateList(detail_list)
    print('end crawler')
