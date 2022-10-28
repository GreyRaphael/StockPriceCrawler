# StockPrice

Get Stock Price from website

## Usage

```bash
# 基本使用
# get from eqapi
python eqapi-getprice.py
```

通过PriceCrawler实现
- `python get-price.py`: 多线程获取 股价
- `python get-opfile.py`: 多线程获取 用于买卖的opfile
- `python get-hold-opfile.py`: 多线程获取 持仓股票对应的opfile
- `python get-share.py`: 多线程获取 股票总股本测试集中度
- `python gen-suigu.py`: 生成测试碎股的股票列表


```bash
# 测试使用
# 获取涨跌停股票列表
python get-ZhangDieTing.py

# 获取新股和ST股票
python get-new-st.py

# 获取可转债+EFT的opfle
python get-kzz-etf.py

# 改变output/*.csv的中的价格
python change-price.py
```