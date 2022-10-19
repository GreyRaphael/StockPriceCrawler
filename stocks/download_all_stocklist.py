
import requests
import pandas as pd


ExchangeDict={
    'sz00':'http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1&selectModule=main',
    'sz30':'http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1&selectModule=nm',
    'sh60':'http://query.sse.com.cn//sseQuery/commonExcelDd.do?sqlId=COMMON_SSE_CP_GPJCTPZ_GPLB_GP_L&type=inParams&CSRC_CODE=&STOCK_CODE=&REG_PROVINCE=&STOCK_TYPE=1&COMPANY_STATUS=2,4,5,7,8',
    'sh68':'http://query.sse.com.cn//sseQuery/commonExcelDd.do?sqlId=COMMON_SSE_CP_GPJCTPZ_GPLB_GP_L&type=inParams&CSRC_CODE=&STOCK_CODE=&REG_PROVINCE=&STOCK_TYPE=8&COMPANY_STATUS=2,4,5,7,8',
}


DataframeDict={}
for key in ExchangeDict:
    if key.startswith('sz'):
        url=ExchangeDict[key]
        HEADERS={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
            "Referer":"http://www.szse.cn/"
            }
        ENGINE='openpyxl' # 因为下载下来是xlsx
    elif key.startswith('sh'):
        url=ExchangeDict[key]
        HEADERS={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
            "Referer":"http://www.sse.com.cn/"
        }
        ENGINE='xlrd' # 因为下载下来是xlsx
    
    excel_binary=requests.get(url, headers=HEADERS).content
    DataframeDict[key]=pd.read_excel(excel_binary, engine=ENGINE)


DataframeDict['sh68'].tail()


# download by pandas
df=pd.read_excel('http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1&selectModule=main',engine='openpyxl')
