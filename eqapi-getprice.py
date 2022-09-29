import configparser
import csv
import eqapi
import quotedata
import sys

class MyRqApp(eqapi.RqApplication):
    def __init__(self, conf='config/config.ini', mode='binary'):
        settings=self._readConfig(conf, mode)
        super().__init__(settings)
        self.price_list=[]

    def onConnect(self, msg):
        print(f'onConnect: {msg}')

    def onDisconnect(self, msg):
        print(f'onDisconnect: {msg}')

    def onQuote(self, quotes):
        print(f'onQuote, receive {len(quotes)} quotes')

    def onError(self, msg):
        print(f'onError: {msg}')

    def onLog(self, msg):
        print(f'onLog: {msg}')

    def getLastPrice(self, codes_filename):
        with open(codes_filename, 'r', encoding='utf8') as file:
            for line in file:
                code=line.rstrip('\n')
                temp={}
                if code.startswith('0') or code.startswith('3'):
                    quoteType='szl1'
                    secucode=f'{code}.SZ'
                elif code.startswith('6'):
                    quoteType='shl1'
                    secucode=f'{code}.SH'
                lastSnap=self.getLastSnapshot(quoteType, code)
                temp['SECUCODE']=secucode
                temp['f2']=lastSnap.last/10000
                self.price_list.append(temp)
    
    def get_top5_prices_volumes(self, codes_filename, direction):
        with open(codes_filename, 'r', encoding='utf8') as file:
            for line in file:
                code=line.rstrip('\n')
                temp={}
                if code.startswith('0') or code.startswith('3'):
                    quoteType='szl1'
                    secucode=f'{code}.SZ'
                elif code.startswith('6'):
                    quoteType='shl1'
                    secucode=f'{code}.SH'

                snap=self.getLastSnapshot(quoteType, code)
                buy_volumes_sum=sum(snap.bid_volumes)
                sell_volumes_sum=sum(snap.offer_volumes)
                if direction=='buy' and buy_volumes_sum<3000000:
                    temp['f2']=snap.bid_prices[2]/10000
                    temp['SECUCODE']=secucode
                    self.price_list.append(temp)
                elif direction == 'sell' and sell_volumes_sum<3000000:
                    temp['f2']=snap.offer_prices[2]/10000
                    temp['SECUCODE']=secucode
                    self.price_list.append(temp)
    
    def get_top5_info(self, codes_filename):
        with open(codes_filename, 'r', encoding='utf8') as file:
            for line in file:
                code=line.rstrip('\n')
                temp={}
                if code.startswith('0') or code.startswith('3'):
                    quoteType='szl1'
                    secucode=f'{code}.SZ'
                elif code.startswith('6'):
                    quoteType='shl1'
                    secucode=f'{code}.SH'
                snap=self.getLastSnapshot(quoteType, code)
                if sum(snap.bid_volumes)<3000000:
                    print(snap)

    def writeCSV(self, filename):
        with open(filename,'w',encoding='utf8',newline='') as file:
            csv_writer=csv.DictWriter(file, ['SECUCODE','f2'])
            csv_writer.writeheader()
            csv_writer.writerows(self.price_list)


    def _readConfig(self, conf, mode):
        config = configparser.ConfigParser()
        config.read(conf, encoding='utf8')
        setting0 = eqapi.EqSetting()
        setting0.ip = config['Rq']['ip']
        setting0.port ='12015' if mode=='binary' else config['Rq']['port']
        setting0.user = config['Rq']['user']
        setting0.passwd = config['Rq']['passwd']
        setting1 = eqapi.EqSetting()
        setting1.ip = config['Rq']['ip']
        setting1.port ='12015' if mode=='binary' else config['Rq']['port']
        setting1.user = config['Rq']['user']
        setting1.passwd = config['Rq']['passwd']
        return [setting0, setting1]

if (__name__ == '__main__'):
    argvs=sys.argv
    if len(argvs)==1:
        stockfile='input/stocks.txt'
    elif len(argvs)==2:
        stockfile=argvs[1]
    else:
        print('to many arguments')
        sys.exit(0)

    rqapp = MyRqApp()
    rqapp.start()
    if rqapp.state() == eqapi.EqState.EQ_STATE_CONNECT:
        # get simple price list
        rqapp.getLastPrice(stockfile)
        rqapp.writeCSV('output.csv')

        # # 价格低，成交量低的股票
        # rqapp.get_top5_prices_volumes('stocks.txt', 'buy')
        # rqapp.writeCSV(r'C:\Users\gewei\Documents\wby\StockPrice\orderlist.csv')
    input('enter something')
    rqapp.stop()