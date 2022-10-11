import concurrent.futures
import random
import time
import csv
import sys
import os
import requests

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
        "Host": "push2.eastmoney.com",
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{num}.0) Gecko/20100101 Firefox/{num}.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Referer": "http://quote.eastmoney.com/",
        "Cookie": r"qgqp_b_id=a04fe66d077d3a18d42e2188587ce168; HAList=ty-0-000002-%u4E07%20%20%u79D1%uFF21%2Cty-0-000001-%u5E73%u5B89%u94F6%u884C%2Cty-1-000001-%u4E0A%u8BC1%u6307%u6570%2Cty-1-601515-%u4E1C%u98CE%u80A1%u4EFD%2Cty-0-300059-%u4E1C%u65B9%u8D22%u5BCC%2Cty-0-300684-%u4E2D%u77F3%u79D1%u6280%2Cty-1-900937-*ST%u534E%u7535B%2Cty-1-600519-%u8D35%u5DDE%u8305%u53F0%2Cty-1-600008-%u9996%u521B%u73AF%u4FDD%2Cty-1-600570-%u6052%u751F%u7535%u5B50; em_hq_fls=js; emshistory=%5B%22%E8%A1%8C%E6%83%85%22%5D",    
    }

def get_share(codeinfo):
    market, code = codeinfo
    secucode = f'{code}.SZ' if market==0 else f'{code}.SH'

    timestamp_end=int(time.time()*1000)
    timestamp_start=timestamp_end-2
    url=f'http://push2.eastmoney.com/api/qt/stock/get?invt=2&fltt=1&cb=jQuery351005883306005429367_{timestamp_start}&fields=f58,f84,f85&secid={market}.{code}&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=|0|0|0|web&_={timestamp_end}'
    # print(url)
    rand_headers=generate_headers()
    s.headers.update(rand_headers)
    txt=s.get(url).text[42:-2]
    jData=eval(txt)
    name=jData['data']['f58'] # 股票简称
    total_share=int(jData['data']['f84']) # 总股本
    # circulate_share=jData['data']['f85'] # 流通股本
    limit_share=total_share//1000 # 持仓股本限制
    return {'SECUCODE': secucode, 'Name': name,'TotalShare': total_share, 'LimitShare':limit_share}


def get_sharelist(code_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        return executor.map(get_share, code_list)
    
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

    if sz00_list:
        writeCSV(f'output/details-sz00.csv', sz00_list[:N])
    if sz30_list:
        writeCSV(f'output/details-sz30.csv', sz30_list[:N])
    if sh60_list:
        writeCSV(f'output/details-sh60.csv', sh60_list[:N])
    if sh688_list:
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
    # 数据源: http://quote.eastmoney.com/sz000002.html
    share_generator=get_sharelist(code_list)
    print('end crawler')

    # generate list and sort
    share_list=list(share_generator)
    print(f"share_list length={len(share_list)}")
    # share_list.sort(key=lambda x: x['SECUCODE'])
    share_list.sort(key=lambda x: x['TotalShare'], reverse=True) # 总股本排序

    # write2csv
    writeCSV("output/details.csv",share_list)
    seperateList(share_list)