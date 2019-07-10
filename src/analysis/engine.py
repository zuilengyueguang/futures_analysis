import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from arch.unitroot import ADF
import statsmodels.api as sm
import re
import datetime


# 数据引擎
class DataEngine:

    # 获取某个合约的前一周的秒级数据
    def getPreWeekSecData(self,symbol):
        e = datetime.datetime.now()
        end_dt = e.strftime('%Y-%m-%d')
        s = e-datetime.timedelta(days=7)
        start_dt = s.strftime('%Y-%m-%d')
        data = get_ticks(symbol, start_dt=start_dt, end_dt=end_dt, fields=['time','current'])
        df1 = DataFrame(data)
        df1.time = pd.to_datetime(df1.time,format='%Y%m%d%H%M%S.%f')
        df1['sec_time'] = df1.time.apply(lambda x: pd.to_datetime(x.strftime(format='%Y%m%d%H%M%S'), format='%Y%m%d%H%M%S'))
        df1.drop(columns='time',inplace=True)
        df1 = df1.groupby('sec_time').agg('max')
        # todo:筛选9点到15点的数据
        return df1

    # 获取所有主力合约信息
    def getAllMainContract(self):
        secs = get_all_securities(types=['futures'])
        main_secs = secs[secs.display_name.apply(lambda x:'主力合约' in x)]
        main_secs_code = [get_dominant_future(s[0:-4]) for s in main_secs.name if get_dominant_future(s[0:-4])]
        return secs.loc[main_secs_code, :]

    # 绘制时间序列数据图，过滤掉中间空白情况
    def plot(self,dataSeries):
        pass


# 计算引擎
class StatisEngine:
    # 判断数据是否为一阶单整序列
    def isIntegration(self, dataSeries):
        return True

    # 判断两个序列是否有协整效应
    def isCointegration(self, priceX, priceY):
        return True

    # 计算协整系数
    def cointegration(self, priceX, priceY):
        return (0, 1)