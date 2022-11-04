import requests
import time
import csv
import os
from PriceCrawler import PriceProvider

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Referer": "http://quote.eastmoney.com/",
    "Cookie": r"qgqp_b_id=a04fe66d077d3a18d42e2188587ce168; HAList=ty-1-900937-*ST%u534E%u7535B%2Cty-1-600519-%u8D35%u5DDE%u8305%u53F0%2Cty-1-600008-%u9996%u521B%u73AF%u4FDD%2Cty-0-000001-%u5E73%u5B89%u94F6%u884C%2Cty-1-600570-%u6052%u751F%u7535%u5B50%2Cty-0-301069-%u51EF%u76DB%u65B0%u6750%2Cty-0-000063-%u4E2D%u5174%u901A%u8BAF%2Cty-1-688981-%u4E2D%u82AF%u56FD%u9645%2Cty-1-603927-%u4E2D%u79D1%u8F6F%2Cty-0-300618-%u5BD2%u9510%u94B4%u4E1A; em_hq_fls=js; emshistory=%5B%22%E8%A1%8C%E6%83%85%22%5D",
}

os.environ["NO_PROXY"] = "push2.eastmoney.com"  # bypass Clash Proxy
s = requests.Session()
s.headers.update(HEADERS)


def get_stock_numbers(ini_url):
    txt = s.get(ini_url).text[42:-2]
    jData = eval(txt)
    return jData["data"]["total"]


def get_stocklist(url):
    stocklist = []
    txt = s.get(url).text[42:-2]
    jData = eval(txt)
    for item in jData["data"]["diff"]:
        if item["f2"] == "-":
            continue
        temp = {}
        code = item["f12"]
        secucode = f"{code}.SH" if code.startswith("6") else f"{code}.SZ"
        temp["SECUCODE"] = secucode
        temp["name"] = item["f14"]
        temp["launch"] = item["f26"]
        temp["f2"] = item["f2"]
        # temp['f3']=item['f3']
        stocklist.append(temp)
    return stocklist


def seperate_stocks(stock_list, key, num):
    sz00_list = []
    sz30_list = []
    sh60_list = []
    sh688_list = []
    COUNTER = [num] * 4
    for item in stock_list:
        secucode = item["SECUCODE"]
        if secucode.startswith("0") and COUNTER[0] > 0:
            COUNTER[0] -= 1
            sz00_list.append(item)
        elif secucode.startswith("3") and COUNTER[1] > 0:
            COUNTER[1] -= 1
            sz30_list.append(item)
        elif secucode.startswith("688") and COUNTER[2] > 0:
            COUNTER[2] -= 1
            sh688_list.append(item)
        elif secucode.startswith("60") and COUNTER[3] > 0:
            COUNTER[3] -= 1
            sh60_list.append(item)
    sz00_list.sort(key=lambda x: x[key], reverse=True)
    sz30_list.sort(key=lambda x: x[key], reverse=True)
    sh60_list.sort(key=lambda x: x[key], reverse=True)
    sh688_list.sort(key=lambda x: x[key], reverse=True)
    return sz00_list + sz30_list + sh60_list + sh688_list


def writeCSV(filename, stock_list):
    colNames = stock_list[0].keys()
    with open(filename, "w", encoding="utf8", newline="") as file:
        csv_writer = csv.DictWriter(file, fieldnames=colNames)
        csv_writer.writeheader()
        csv_writer.writerows(stock_list)


def get_new():
    timestamp_end = int(time.time() * 1000)
    timestamp_start = timestamp_end - 10

    ini_url = f"http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407274305058214278_{timestamp_start}&pn=1&pz=1&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f26&fs=m:0+f:8,m:1+f:8&fields=f2,f3,f12,f14,f26&_={timestamp_end}"
    total_numbers = get_stock_numbers(ini_url)

    url = f"http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407274305058214278_{timestamp_start+20}&pn=1&pz={total_numbers}&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f26&fs=m:0+f:8,m:1+f:8&fields=f2,f3,f12,f14,f26&_={timestamp_end+20}"
    stock_list = get_stocklist(url)
    seperated_list = seperate_stocks(stock_list, key="launch", num=5)
    print(f"new stocks length={len(seperated_list)}")
    writeCSV("output/new.csv", seperated_list)


def get_st():
    timestamp_end = int(time.time() * 1000)
    timestamp_start = timestamp_end - 10

    ini_url = f"http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407274305058214278_{timestamp_start}&pn=1&pz=1&po=0&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f12&fs=m:0+f:4,m:1+f:4&fields=f2,f3,f12,f14,f26&_={timestamp_end}"
    total_numbers = get_stock_numbers(ini_url)

    url = f"http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407274305058214278_{timestamp_start}&pn=1&pz={total_numbers}&po=0&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f12&fs=m:0+f:4,m:1+f:4&fields=f2,f3,f12,f14,f26&_={timestamp_end}"
    stock_list = get_stocklist(url)
    seperated_list = seperate_stocks(stock_list, key="name", num=10)
    print(f"ST length={len(seperated_list)}")
    writeCSV("output/st.csv", seperated_list)


def get_black():
    code_list = [{"SECUCODE": "601066.SH"}]
    obj = PriceProvider(code_list)
    pirce_list = obj.get_pricelist()
    print(f"black list length={len(pirce_list)}")
    obj.writeCSV("output/blacklist.csv", pirce_list)


if __name__ == "__main__":
    # 数据源: http://quote.eastmoney.com/center/gridlist.html
    get_new()
    get_st()
    get_black()
