import pandas as pd
import os

DataframeDict={}
for name in os.listdir('.'):
    if name.endswith('csv'): continue
    filename=f'./{name}'
    key=name.split('.')[0]
    if name.startswith('sh'):
        DataframeDict[key]=pd.read_excel(filename,  dtype={'A股代码':'str'}, parse_dates=[4,], engine='xlrd')
    elif name.startswith('sz'):
        DataframeDict[key]=pd.read_excel(filename, dtype={'A股代码':'str'}, parse_dates=[6,], engine='openpyxl')

print(DataframeDict['sz00'][['A股代码','A股简称', 'A股上市日期']])
print('-'*50)
print(DataframeDict['sh60'][['A股代码', '证券简称', '上市日期']])


print(DataframeDict['sz00'].iloc[0])
print('-'*50)
print(DataframeDict['sh60'].iloc[0])

df_sz00=DataframeDict['sz00']
df_sz30=DataframeDict['sz30']
df_sh60=DataframeDict['sh60']
df_sh68=DataframeDict['sh68']

df_sz00[~df_sz00['A股简称'].str.contains('ST')].to_csv('sz00.csv', columns=['A股代码',], header=None, index=False)
df_sz30[~df_sz30['A股简称'].str.contains('ST')].to_csv('sz30.csv', columns=['A股代码',], header=None, index=False)
df_sh60[~df_sh60['证券简称'].str.contains('ST')].to_csv('sh60.csv', columns=['A股代码',], header=None, index=False)
df_sh68[~df_sh68['证券简称'].str.contains('ST')].to_csv('sh68.csv', columns=['A股代码',], header=None, index=False)

# DataframeDict['sz00'].sort_values(by=['A股上市日期',], ascending=False).to_csv('sz00.csv', columns=['A股代码','A股简称', 'A股上市日期'], header=['Code', 'StockName', 'LaunchDate'], index=False)
# DataframeDict['sz30'].sort_values(by=['A股上市日期',], ascending=False).to_csv('sz30.csv', columns=['A股代码','A股简称', 'A股上市日期'], header=['Code', 'StockName', 'LaunchDate'], index=False)
# DataframeDict['sh60'].sort_values(by=['上市日期',], ascending=False).to_csv('sh60.csv', columns=['A股代码','证券简称', '上市日期'], header=['Code', 'StockName', 'LaunchDate'], index=False)
# DataframeDict['sh68'].sort_values(by=['上市日期',], ascending=False).to_csv('sh68.csv', columns=['A股代码','证券简称', '上市日期'], header=['Code', 'StockName', 'LaunchDate'], index=False)