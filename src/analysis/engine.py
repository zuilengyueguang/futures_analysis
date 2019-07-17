import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from arch.unitroot import ADF
import statsmodels.api as sm
import re
import datetime
from jqdata import jy
from numpy import nan


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

    def getData(self):
        # 可以得到不同时间 不同频率的所有主力合约数据
        pass

    # 获取所有主力合约信息
    def getAllMainContract(self):
        secs = get_all_securities(types=['futures'])
        main_secs = secs[secs.display_name.apply(lambda x: '主力合约' in x)]
        main_secs_code = [get_dominant_future(s[0:-4]) for s in main_secs.name if get_dominant_future(s[0:-4])]
        return secs.loc[main_secs_code, :]

    # 获取所有主力合约上周的tick数据
    # 每日执行一次，方便分析数据时，快速加载数据
    def getPreWeekAllTickData(self):
        e = datetime.datetime.now()
        end_dt = e.strftime('%Y-%m-%d')
        s = e - datetime.timedelta(days=7)
        start_dt = s.strftime('%Y-%m-%d')
        codes = self.getAllMainContract()
        d = {}
        for i in codes.index:
            d[i] = self.getTickData(i, start_dt=start_dt, end_dt=end_dt)
        return pd.Panel(d)

    # 获取某个合约的合约乘数  计数单位 和 最小变动单位
    # 犯了一个基本错误，忘了写self，报了一堆看不懂的错误，郁闷
    def future_basic_info(self, future):
        # 这个后续改成从本地的meta数据中拿metadata数据的方法，暂时先这么使用
        if "9999" in future or "8888" in future:
            match = re.match(r"(?P<underlying_symbol>[A-Z]{1,})", future)
            if not match:
                raise ValueError("未知期货标的：{}".format(future))
            else:
                future = get_dominant_future(match.groupdict()["underlying_symbol"])
        code = future.split(".")[0]
        q = query(jy.Fut_ContractMain).filter(jy.Fut_ContractMain.ContractCode == code)
        result = jy.run_query(query_object=q).to_dict("record")
        if result:
            result = result.pop()
            min_point = re.match("(?P<value>^[0-9]+([.]{1}[0-9]+){0,1})", result["LittlestChangeUnit"]).groupdict(nan)[
                "value"]
            return {"ContractUnit": result["CMValue"],
                    "PriceScale": float(str(min_point)[:-1] + "1") if float(min_point) < 1 else 1,
                    "MinPoint": float(min_point)}
        else:
            cu = nan
            current_code = code[:-4].upper()
            if trade_units.get(current_code):
                cu = trade_units.get(current_code)
            return {"ContractUnit": cu,
                    "PriceScale": nan,
                    "MinPoint": nan}

    # 查询交易单位，输入参数为合约的代码 比如RU1909.XSGE合约，这里输入RU
    def get_trade_units(self, symbol):
        code = symbol.split(".")[0][:-4].upper()
        return trade_units.get(code)

    # 绘制时间序列数据图，过滤掉中间空白情况
    def plot(self, dataSeries):
        pass


# 计算引擎
class StatisEngine():
    def integration(self, priceX):
        # 一阶单整计算
        logX = priceX
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
        if ((pLX > 0.05) and (pRX < 0.05)):
            # 是一阶单整序列
            return True
        else:
            # 不是一阶单整序列
            return False

    # 判断两个序列是否有协整效应
    def isCointegration(self, priceX, priceY):
        logX = priceX
        logY = priceY
        results = sm.OLS(logY, sm.add_constant(logX)).fit()
        resid = results.resid
        adfSpread = ADF(resid)
        if adfSpread.pvalue >= 0.05:
            # 残差序列是非平稳时间序列，不具有协整关系
            return (False, results.params[0], results.params[1])
        else:
            # 残差序列是平稳时间序列，具有协整关系
            return (True, results.params[0], results.params[1])

    # 获取残差序列
    def getSpread(self, priceX, priceY, alpha, beta):
        return priceY - alpha - beta * priceX


# 一阶单整检验筛选
def filter_integration_datas(ac):
    de = DataEngine()
    se = StatisEngine()
    print("1. 获取主力合约基本面数据")
    validData = {}
    print("2. 开始一阶单整检验")
    for i in ac.index:
        # 获取经过处理的数据
        print("%s 合约-------------1. 错误合约检验" % str(i))
        if i not in error_stocks:
            print("%s 合约-------------2. 获取秒级数据" % str(i))
            data1 = de.getPreWeekSecData(i)
            # 排除没有数据的合约
            print("%s 合约-------------3. 数据量检验,数据量要在10000以上" % str(i))
            if (data1.shape[0] >= 10000):
                # 对秒级 频率数据进行一阶单整检验
                print("%s 合约-------------4. 合约一阶单整检验" % str(i))
                result = se.isIntegration(data1['last'])
                if result == True:
                    print("%s 合约-------------5. 合约一阶单整检验成功" % str(i))
                    # 用收盘价数据乘以最小交易单位作为要分析的数据
                    last_data = data1['last']
                    cu = de.get_trade_units(str(i))
                    print("%s 合约-------------6. cu:%s" % (str(i), str(cu)))
                    validData[i] = (last_data * cu)
    data = DataFrame(validData)
    return data.dropna(how='all')


# 协整效应筛选
def filter_cointegration(ac, data):
    l = data.columns.size
    se = StatisEngine()
    pairs = []
    for i in range(l):
        for j in range(i + 1, l):
            s1 = data.columns[i]
            s2 = data.columns[j]
            # 前项和后项填充都用上，防止出现空值
            t1 = data.loc[:, [s1, s2]].dropna(how='all').bfill().ffill()
            d1 = t1[s1]
            d2 = t1[s2]
            print("套利对：(%s,%s)开始协整检验" % (s1, s2))
            (result, alpha, beta) = se.isCointegration(d1, d2)
            if result:
                print("套利对为：(%s,%s),alpha:%s,beta:%s"
                      % (ac.loc[s1, :].display_name, ac.loc[s2, :].display_name, str(alpha), str(beta)))
                pairs.append((s1, s2, alpha, beta))
    return pairs


e = datetime.datetime.now()
end_date = e.strftime('%Y-%m-%d')
s = e - datetime.timedelta(days=7)
start_date = s.strftime('%Y-%m-%d')


def Main(sec='1s', start_date=start_date, end_date=end_date):
    # todo 改造为 可以传送频率 时间段 和 具体
    # 获取主力合约基本面数据
    de = DataEngine()
    ac = de.getAllMainContract()
    # 一阶单整筛选
    data = filter_integration_datas(ac)
    # 协整检验
    pairs = filter_cointegration(ac, data)
    # 对所有套利对生成策略图
    # todo 添加导出报表的功能，一天分析一次，然后做各种比较
    create_report(ac, pairs, data)
    print("协整检验完成")
    return ac, pairs, data


# 目前有问题的合约和无法交易的合约
error_stocks = ['JR2005.XZCE', 'IC1907.CCFX', 'IF1907.CCFX', 'IH1907.CCFX', 'T1909.CCFX', 'TF1909.CCFX', 'TS1909.CCFX']
# 合约代码和交易单位数据，暂时存放在这里
trade_units = {'AP': 10, 'CF': 5, 'CJ': 5, 'CY': 5, 'FG': 20, 'JR': 20, 'LR': 20, 'MA': 10, 'OI': 10, 'PM': 50,
               'RI': 20, 'RM': 10,
               'RS': 10, 'SF': 5, 'SM': 5, 'SR': 10, 'TA': 5, 'WH': 20, 'ZC': 100, 'A': 10, 'AG': 15, 'AL': 5,
               'AU': 1000,
               'B': 10, 'BB': 500, 'BU': 10, 'C': 10, 'CS': 10, 'CU': 5, 'EG': 10, 'FB': 500, 'FU': 10, 'HC': 10,
               'I': 100, 'IC': 200, 'IF': 300, 'IH': 300, 'J': 100, 'JD': 10, 'JM': 60, 'L': 5, 'M': 10, 'NI': 1,
               'P': 10, 'PB': 5, 'PP': 5, 'RB': 10, 'RU': 10, 'SC': 1000, 'SN': 1, 'SP': 10, 'T': 10000, 'TF': 10000,
               'TS': 20000, 'V': 5, 'WR': 10, 'Y': 10, 'ZN': 5}

if __name__ == '__main__':
    # Main()
    print("hello")