import tushare as ts

# df = ts.get_stock_basics()
# date = df.ix['601333']['timeToMarket'] #上市日期YYYYMMDD
# print(date)

df1 = ts.get_k_data('601333', start='2017-4-25', end='2017-4-25', ktype='15')
# print(df1)

df = ts.get_today_all()
print(df)
