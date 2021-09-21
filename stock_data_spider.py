# 导入tushare
import tushare as ts

stock_id = '000001.sz'

# 初始化pro接口
pro = ts.pro_api('5d113abec9e036a51e8b0dcf07fbd3a381e69a8626d265e5423f006d')

# 拉取数据
df = pro.daily(**{
    "ts_code": stock_id,
    "trade_date": "",
    "start_date": 20150101,
    "end_date": 20201231,
    "offset": "",
    "limit": ""
}, fields=[
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "vol"
])
df.to_csv('{}.csv'.format(stock_id))

