# %%
import requests
import time
import csv
import os

# %%
HEADERS={
"Host": "push2ex.eastmoney.com",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
"Accept": "*/*",
"Accept-Language": "en-US,en;q=0.5",
"Accept-Encoding": "gzip, deflate",
"Connection": "keep-alive",
"Referer": "http://quote.eastmoney.com/",
"Cookie": r"qgqp_b_id=a04fe66d077d3a18d42e2188587ce168; HAList=ty-1-600570-%u6052%u751F%u7535%u5B50%2Cty-0-301069-%u51EF%u76DB%u65B0%u6750%2Cty-0-000063-%u4E2D%u5174%u901A%u8BAF%2Cty-1-688981-%u4E2D%u82AF%u56FD%u9645%2Cty-0-000001-%u5E73%u5B89%u94F6%u884C%2Cty-1-603927-%u4E2D%u79D1%u8F6F%2Cty-0-300618-%u5BD2%u9510%u94B4%u4E1A%2Cty-0-300168-%u4E07%u8FBE%u4FE1%u606F%2Cty-1-601258-%u5E9E%u5927%u96C6%u56E2%2Cty-1-600743-%u534E%u8FDC%u5730%u4EA7; em_hq_fls=js; emshistory=%5B%22%E8%A1%8C%E6%83%85%22%5D",
}

s=requests.Session()
s.headers.update(HEADERS)
os.environ['NO_PROXY']='push2ex.eastmoney.com'

# %%
def get_price(market, code):
    timestamp_end=int(time.time()*1000)
    timestamp_start=timestamp_end-1
    url=f'http://push2ex.eastmoney.com/getStockFenShi?pagesize=1&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wzfscj&pageindex=0&sort=2&ft=1&cb=jQuery351015686815628587114_{timestamp_start}&code={code}&market={market}&_={timestamp_end}'
    # print(url)
    response=eval(s.get(url).text[42:-2])
    preclose=response['data']['cp']
    lastprice=response['data']['data'][0]['p']
    # lastvolume=response['data']['data'][0]['v']
    f3=round(100*(lastprice/preclose-1), 2)
    return lastprice, f3


# %%
def get_stockfile(stock_file):
    price_list=[]
    with open(stock_file,'r',encoding='utf8') as file:
        for line in file:
            temp={}
            code=line.rstrip('\n')
            if code.startswith('0') or code.startswith('3'):
                market=0
                secucode=f'{code}.SZ'
            elif code.startswith('6'):
                market=1
                secucode=f'{code}.SH'
            f2, f3 = get_price(market, code)
            temp['SECUCODE']=secucode
            temp['f2']=f2/1000
            # temp['f3']=f3
            price_list.append(temp)
    return price_list

# %%
def writeCSV(filename, price_list):
    with open(filename,'w',encoding='utf8',newline='') as file:
        # csv_writer=csv.DictWriter(file, ['SECUCODE','f2','f3'])
        csv_writer=csv.DictWriter(file, ['SECUCODE','f2'])
        csv_writer.writeheader()
        csv_writer.writerows(price_list)

# %%
if __name__ == "__main__":
    price_list=get_stockfile('stocks.txt')
    writeCSV("eastmoney_price_3s.csv",price_list)
