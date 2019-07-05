import tushare as tu
import datetime
date='2017-01-01'
# symbolL=[]
# #中金所和郑商所
L=tu.get_cffex_daily(date)['symbol'].tolist()
print(L)
# #上期所和大商所
# L=tu.get_shfe_daily(date)['symbol'].tolist()
# print(L)


def get_codes():
    '''获取现在还存在的合约代码信息'''
    l=[]
    tu.get_cffex_daily()

print(datetime.datetime.now())