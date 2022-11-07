import concurrent.futures
import requests
import random
import time
import csv
import os

os.environ["NO_PROXY"] = "push2ex.eastmoney.com"  # bypass Clash Proxy


class PriceProvider:
    """get price from eastmoney"""

    def __init__(self, code_list):
        self.s = requests.Session()
        self.code_list = code_list

    def _generate_headers(self):
        num = random.randint(90, 106)
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

    def _get_price(self, code_dict):
        secucode = code_dict["SECUCODE"]
        code, mkt = secucode.split(".")
        market = 0 if mkt == "SZ" else 1

        timestamp_end = int(time.time() * 1000)
        timestamp_start = timestamp_end - 4
        # 10档行情也在push2ex.eastmoney.com, f31~f12
        url = f"http://push2ex.eastmoney.com/getStockFenShi?pagesize=1&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wzfscj&pageindex=0&sort=2&ft=1&cb=jQuery351015686815628587114_{timestamp_start}&code={code}&market={market}&_={timestamp_end}"
        rand_headers = self._generate_headers()
        self.s.headers.update(rand_headers)
        txt = self.s.get(url).text[42:-2]
        jData = eval(txt)

        preclose = jData["data"]["cp"]
        if preclose == 0:
            print(code, "无行情")
        else:
            # lastvolume=jData['data']['data'][0]['v']
            # f3=round(100*(lastprice/preclose-1), 2)
            lastprice = jData["data"]["data"][0]["p"]
            code_dict["f2"] = lastprice / 1000
            return code_dict

    def get_pricelist(self):
        # 数据源: http://quote.eastmoney.com/sz000002.html#fullScreenChart
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            price_generator = executor.map(self._get_price, self.code_list)
            return [item for item in price_generator if item]  # 过滤为None的值

    @staticmethod
    def writeCSV(filename, price_list):
        if len(price_list) == 0:
            print("price list is empty!")
            return
        colNames = price_list[0].keys()
        with open(filename, "w", encoding="utf8", newline="") as file:
            csv_writer = csv.DictWriter(file, fieldnames=colNames)
            csv_writer.writeheader()
            csv_writer.writerows(price_list)

    @staticmethod
    def seperateList(price_list, N=None, writeFlag=True, prefix=''):
        sz00_list = []
        sz30_list = []
        sh60_list = []
        sh688_list = []
        for item in price_list:
            secucode = item["SECUCODE"]
            # price=item['f2']
            if secucode.startswith("0"):
                sz00_list.append(item)
            elif secucode.startswith("3"):
                sz30_list.append(item)
            elif secucode.startswith("60"):
                sh60_list.append(item)
            elif secucode.startswith("688"):
                sh688_list.append(item)

        if writeFlag:
            if sz00_list:
                PriceProvider.writeCSV(f"output/{prefix}sz00.csv", sz00_list[:N])
            if sz30_list:
                PriceProvider.writeCSV(f"output/{prefix}sz30.csv", sz30_list[:N])
            if sh60_list:
                PriceProvider.writeCSV(f"output/{prefix}sh60.csv", sh60_list[:N])
            if sh688_list:
                PriceProvider.writeCSV(f"output/{prefix}sh688.csv", sh688_list[:N])

        return sz00_list[:N] + sz30_list[:N] + sh60_list[:N] + sh688_list[:N]

    def _get_share(self, code_dict):
        secucode = code_dict["SECUCODE"]
        code, mkt = secucode.split(".")
        market = 0 if mkt == "SZ" else 1

        timestamp_end = int(time.time() * 1000)
        timestamp_start = timestamp_end - 4
        url = f"http://push2.eastmoney.com/api/qt/stock/get?invt=2&fltt=1&cb=jQuery351005883306005429367_{timestamp_start}&fields=f58,f84,f85,f116&secid={market}.{code}&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=|0|0|0|web&_={timestamp_end}"
        # print(url)
        rand_headers = self._generate_headers()
        self.s.headers.update(rand_headers)
        txt = self.s.get(url).text[42:-2]
        jData = eval(txt)

        name = jData["data"]["f58"]  # 股票简称
        total_share = int(jData["data"]["f84"])  # 总股本
        total_value = int(jData["data"]["f116"])  # 总市值
        # circulate_share=jData['data']['f85'] # 流通股本

        code_dict["Name"] = name
        code_dict["TotalShare"] = total_share
        code_dict["LimitShare"] = total_share // 1000  # 持仓1‰股本
        code_dict["f2"] = round(total_value / total_share, 2)
        code_dict["cost"] = total_value / 1000
        return code_dict

    def get_sharelist(self):
        # 数据源: http://quote.eastmoney.com/sz000002.html
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            share_generator = executor.map(self._get_share, self.code_list)
            # filter stock
            share_list = []
            for item in share_generator:
                if item:  # 过滤为None的值
                    secucode, limit_share = item["SECUCODE"], item["LimitShare"]
                    if (
                        (secucode.startswith("00") and limit_share <= 1e6)
                        or (secucode.startswith("60") and limit_share <= 1e6)
                        or (secucode.startswith("30") and limit_share <= 3e5)
                        or (secucode.startswith("688") and limit_share <= 1e5)
                    ):
                        share_list.append(item)
            return share_list


if __name__ == "__main__":
    # get price
    example_list = [
        {"SECUCODE": "000001.SZ"},
        {"SECUCODE": "300750.SZ"},
        {"SECUCODE": "600000.SH"},
        {"SECUCODE": "688981.SH"},
    ]
    obj = PriceProvider(example_list)
    price_list = obj.get_pricelist()
    price_list.sort(key=lambda x: x["f2"])
    obj.writeCSV("output/price-all-3s.csv", price_list)
    obj.seperateList(price_list)
