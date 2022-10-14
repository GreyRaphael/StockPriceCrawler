# StockPrice

Get Stock Price from website

## Usage

```bash
# 基本使用
# get from eastmoney.com
python east-getprice.py

# get from eqapi
python eqapi-getprice.py
```

```bash
# 测试使用
# 获取涨跌停股票列表
python get-ZhangDieTing.py

# 获取新股和ST股票
python get-new-st.py

# 多线程获取股票价格
python get-price-thread.py

# 多线程获取总股本，测试集中度
python get-share-thread.py

# 多线程生产opfile.csv
python get-opfile-thread.py

# 改变output/*.csv的中的价格
python change-price.py
```