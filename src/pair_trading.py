import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from arch.unitroot import ADF
import statsmodels.api as sm
import re

class PairTrading:

    def SSD(self, priceX, priceY):
        '''
        # 计算标准化价格偏差之平方和
        priceX: Series
        priceY: Series
        '''
        if priceX is None or priceY is None:
            print("缺少价格序列。")
        returnX = (priceX - priceX.shift(1)) / priceX.shift(1)[1:]  # 单期收益率
        returnY = (priceY - priceY.shift(1)) / priceY.shift(1)[1:]
        standardX = (returnX + 1).cumprod()  # 标准化价格
        standardY = (returnY + 1).cumprod()
        data = np.sum((standardX - standardY) ** 2)
        return data

    def SSDSpread(self, priceX, priceY):
        '''
        计算标准化价格偏差序列
        '''
        if priceX is None or priceY is None:
            print("缺少价格序列")
        returnX = (priceX - priceX.shift(1)) / priceX.shift(1)[1:]  # 单期收益率
        returnY = (priceY - priceY.shift(1)) / priceY.shift(1)[1:]
        standardX = (returnX + 1).cumprod()  # 标准化价格
        standardY = (returnY + 1).cumprod()
        spread = (standardX - standardY)
        return spread

    def cointegration(self, priceX, priceY):
        '''
        协整关系判断
        '''
        if priceX is None or priceY is None:
            print("缺少价格序列")
        logX = np.log(priceX)
        logY = np.log(priceY)
        results = sm.OLS(logY, sm.add_constant(logX)).fit()
        resid = results.resid
        adfSpread = ADF(resid)
        if adfSpread.pvalue >= 0.05:
            print("""交易价格不具有协整关系。
            p-value of ADF test:%f,
            Coefficients of regression:
            Intercept: %f
            beta: %f
            """ % (adfSpread.pvalue, results.params[0], results.params[1]))
            return None
        else:
            print("""交易价格具有协整关系。
            p-value of ADF test:%f,
            Coefficients of regression:
            Intercept: %f
            beta: %f
            """ % (adfSpread.pvalue, results.params[0], results.params[1]))
            return (results.params[0], results.params[1])

    def cointegrationSpread(self, priceX, priceY, formperiod, tradeperiod):
        '''
        返回交易期的残差序列
        :param priceX: 必须是时间序列数据，这样可以根据索引截取形成期和交易期的数据
        :param priceY:
        :param formperiod:
        :param tradeperiod:
        :return:
        '''
        if priceX is None or priceY is None:
            print("缺少价格序列")
        if not (re.fullmatch("\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}",formperiod) or
                re.fullmatch("\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}",tradeperiod)):
            print("形成期格式错误")
        formX = priceX[formperiod.split(":")[0]:formperiod.split(":")[1]]
        formY = priceY[formperiod.split(":")[0]:formperiod.split(":")[1]]
        coefficients = self.cointegration(formX,formY) # 计算系数
        if coefficients is None:
            print("未形成协整关系，无法配对")
        else:
            spread = (np.log(priceY[tradeperiod.split(":")[0]:tradeperiod.split(":")[1]])
                   -coefficients[0]-coefficients[1]*np.log(priceX[tradeperiod.split(":")[0]:tradeperiod.split(":")[1]]))
            return spread

    def calBound(self,priceX,priceY,method,formperiod,width=1.5):
        if not re.fullmatch("\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}", formperiod):
            print("形成期格式错误")
        if method=='SSD':
            spread = self.SSDSpread(priceX[formperiod.split(":")[0]:formperiod.split(":")[1]],
                                    priceY[formperiod.split(":")[0]:formperiod.split(":")[1]])
            mu = np.mean(spread)
            sd = np.std(spread)
            upperBound = mu+width*sd
            lowerBound = mu-width*sd
            return (upperBound,lowerBound)
        elif method=='cointegration':
            spread = self.cointegrationSpread(priceX,priceY,formperiod,formperiod)
            mu = np.mean(spread)
            sd = np.std(spread)
            upperBound = mu + width * sd
            lowerBound = mu - width * sd
            return (upperBound, lowerBound)
        else:
            print("不存在该方法，请选择 SSD，或 cointegration")