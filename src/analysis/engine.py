import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from arch.unitroot import ADF
import statsmodels.api as sm
import re
import datetime


# 数据引擎
class DataEngine():
    # 获取tick数据
    def getTickData(self, symbol, start_dt, end_dt):
        data = get_ticks(symbol, start_dt=start_dt, end_dt=end_dt,
                         fields=['time', 'current', 'volume', 'money', 'position', 'a1_v', 'a1_p', 'b1_v', 'b1_p'])
        df1 = DataFrame(data)
        # 时间标准化，方便后续时间运算
        df1.time = pd.to_datetime(df1.time, format='%Y%m%d%H%M%S.%f')
        df1.index = df1.time
        # 去掉重复索引
        df1.drop_duplicates(subset='time', keep='last', inplace=True)
        # 去掉多余列
        df1.drop(columns='time', inplace=True)
        return df1

    # 取前一周的Tick数据
    def getPreWeekTickData(self, symbol):
        e = datetime.datetime.now()
        end_dt = e.strftime('%Y-%m-%d')
        s = e - datetime.timedelta(days=7)
        start_dt = s.strftime('%Y-%m-%d')
        return self.getTickData(symbol, start_dt=start_dt, end_dt=end_dt)

    # 获取某个合约的前一周的秒级数据

    # 由tick数据转换为秒级数据
    def getPreWeekSecData(self, symbol, freq=1):
        df1 = self.getPreWeekTickData(symbol)
        df1 = df1.current.resample('%dS' % freq).agg(['last', 'first', 'max', 'min']).dropna()
        # 筛选固定交易时间数据，只做日内，并且不做夜盘
        # 这里的数据筛选是特定的针对性数据
        d1 = df1.loc[datetime.time(9, 0, 0):datetime.time(10, 15, 0), :]
        d2 = df1.loc[datetime.time(10, 30, 0):datetime.time(11, 30, 0), :]
        d3 = df1.loc[datetime.time(13, 30, 0):datetime.time(15, 0, 0), :]
        # 连接函数
        return pd.concat([d1, d2, d3])

    # 获取所有主力合约信息
    def getAllMainContract(self):
        secs = get_all_securities(types=['futures'])
        main_secs = secs[secs.display_name.apply(lambda x: '主力合约' in x)]
        main_secs_code = [get_dominant_future(s[0:-4]) for s in main_secs.name if get_dominant_future(s[0:-4])]
        return secs.loc[main_secs_code, :]

    # 绘制时间序列数据图，过滤掉中间空白情况
    def plot(self, dataSeries):
        pass


# 计算引擎
class StatisEngine():
    def integration(self, priceX):
        # 一阶单整计算
        logX = np.log(priceX)
        retX = logX.diff()[1:]
        adfLX = ADF(logX)
        adfRX = ADF(retX)
        return adfLX.pvalue, adfRX.pvalue

    # 判断数据是否为一阶单整序列
    def isIntegration(self, priceX):
        # 对数价格序列是非平稳时间序列
        # 对数差分价格是平稳时间序列
        pLX, pRX = self.integration(priceX)
        # 对数价格置信度大于0.05才认为是非平稳时间序列
        # 差分序列置信度小于0.01才认为是平稳时间序列
        if ((pLX > 0.05) and (pRX < 0.01)):
            # 是一阶单整序列
            return True
        else:
            # 不是一阶单整序列
            return False

    # 判断两个序列是否有协整效应
    def isCointegration(self, priceX, priceY):
        logX = np.log(priceX)
        logY = np.log(priceY)
        results = sm.OLS(logY, sm.add_constant(logX)).fit()
        resid = results.resid
        adfSpread = ADF(resid)
        if adfSpread.pvalue >= 0.05:
            # 不具有协整关系
            return False
        else:
            # 具有协整关系
            return True

    # 计算协整系数
    def cointegration(self, priceX, priceY):
        return 0, 1

    def mergeData(self, priceX, priceY):
        # todo 仅凭价格没办法合并数据，这里需要重新考虑一下
        d1 = DataFrame({'A1909.XDCE': data1['last'], 'C1909.XDCE': data2['last']})
        d1.head(20)


def get_integration(symbol):
    de = DataEngine()
    data1 = de.getPreWeekSecData(symbol)
    if (data1.index.day.unique().size < 5):
        return (symbol, "此合约数据异常")
    priceX = data1['last']
    se = StatisEngine()
    return (symbol, se.integration(priceX))


# 获取所有通过一阶单整检验的有效合约数据
def get_integration_datas():
    de = DataEngine()
    se = StatisEngine()
    ac = de.getAllMainContract()
    validData = {}
    for i in ac.index:
        # 获取经过处理的数据
        data1 = de.getPreWeekSecData(i)
        # 排除没有数据的合约
        if (data1.index.day.unique().size >= 5):
            # 对秒级 频率数据进行一阶单整检验
            result = se.isIntegration(data1['last'])
            if result == True:
                validData[i] = data1['last']
    return DataFrame(validData)


if __name__ == '__main__':
    pass