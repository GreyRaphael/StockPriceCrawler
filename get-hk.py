import requests
import time
import csv
import os

HEADERS = {
    "Host": "push2.eastmoney.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Referer": "http://quote.eastmoney.com/",
    "Cookie": r"qgqp_b_id=a04fe66d077d3a18d42e2188587ce168; HAList=ty-1-513120-%u6E2F%u80A1%u521B%u65B0%u836FETF%2Cty-116-00317-%u4E2D%u8239%u9632%u52A1%2Cty-1-600685-%u4E2D%u8239%u9632%u52A1%2Cty-1-510010-180%u6CBB%u7406ETF%2Cty-1-588100-%u79D1%u521B%u4FE1%u606F%u6280%u672FETF%2Cty-1-562910-%u9AD8%u7AEF%u5236%u9020ETF%2Cty-1-511620-%u8D27%u5E01%u57FA%u91D1ETF%2Cty-1-511060-5%u5E74%u5730%u65B9%u503AETF%2Cty-0-123088-%u5A01%u5510%u8F6C%u503A%2Cty-1-588330-%u53CC%u521B%u9F99%u5934ETF; em_hq_fls=js; emshistory=%5B%22S*ST%22%2C%22%E5%8F%AF%E8%BD%AC%E5%80%BA%22%2C%22%E6%B7%B1100ETF%22%2C%22%E8%A1%8C%E6%83%85%22%5D",
}

os.environ["NO_PROXY"] = "push2.eastmoney.com"  # bypass Clash Proxy
s = requests.Session()
s.headers.update(HEADERS)

def get_stocklist(url, key, direction, volume):
    stocklist = []
    raw_text = s.get(url).text
    pos = raw_text.find("{")
    print("-" * 50, pos)
    txt = raw_text[pos:-2]
    jData = eval(txt)
    for item in jData["data"]["diff"]:
        if item["f2"] == "-":
            continue
        temp = {}
        code = item["f12"]
        secucode = f'{code}.{key}'
        temp["priceType"] = 24
        temp["direction"] = direction
        temp["volume"] = volume
        temp["SECUCODE"] = secucode
        # temp["name"] = item["f14"]
        temp["f2"] = item["f2"]
        stocklist.append(temp)
    return stocklist

def writeCSV(filename, stock_list):
    colNames = stock_list[0].keys()
    with open(filename, "w", encoding="utf8", newline="") as file:
        csv_writer = csv.DictWriter(file, fieldnames=colNames)
        csv_writer.writeheader()
        csv_writer.writerows(stock_list)

def get_hk(num=5):
    timestamp_end = int(time.time() * 1000)
    timestamp_start = timestamp_end - 10
    shhk_url=f'http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery1124011887535527826687_{timestamp_start}&pn=1&pz={num}&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f2&fs=b:MK0144&fields=f2,f12,f14&_={timestamp_end}'
    shhk_list=get_stocklist(shhk_url, 'SHHK', 42, 100)
    print(f"SHHK length={len(shhk_list)}")

    szhk_url=f'http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery11240535765726276071_{timestamp_start}&pn=1&pz={num}&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f2&fs=b:MK0146&fields=f2,f12,f14&_={timestamp_end}'
    szhk_list=get_stocklist(szhk_url, 'SZHK', 42, 100)
    print(f"SZHK length={len(szhk_list)}")
    
    writeCSV('output/hk-opfile.csv', shhk_list+szhk_list)

if __name__ == "__main__":
    get_hk()
