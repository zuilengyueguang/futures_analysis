import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.tsa.stattools as st
import datetime
from matplotlib.ticker import FuncFormatter


def plotData(data, title='', signal=False):
    def format_date(x, pos=None):
        if x < 0 or x > len(date_tickers) - 1:
            return ''
        return date_tickers[int(x)]

    plt.figure(figsize=(16, 5.2))
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示乱码的问题
    date_tickers = data.index.tolist()
    newData = data.copy()
    newData.index = range(newData.size)
    ax = plt.subplot()
    ax.xaxis.set_major_formatter(FuncFormatter(format_date))
    newData.plot(ax=ax, title=title)
    if signal:
        mu = np.mean(data)
        std = np.std(data)
        plt.axhline(y=mu, color='black')
        plt.axhline(y=mu + 0.2 * std, color='blue')
        plt.axhline(y=mu - 0.2 * std, color='blue')
        plt.axhline(y=mu + 1.5 * std, color='green')
        plt.axhline(y=mu - 1.5 * std, color='green')
        plt.axhline(y=mu + 2.5 * std, color='red')
        plt.axhline(y=mu - 2.5 * std, color='red')


# 数据引擎
class DataEngine():
    # 获取tick数据
    def getTickData(self, symbol, start_date, end_date):
        data = get_ticks(symbol, start_dt=start_date, end_dt=end_date,
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

    def getData(self, symbol, start_date, end_date, sec='1S'):
        if sec.endswith('S'):
            tickData = self.getTickData(symbol, start_date=start_date, end_date=end_date)
            changeData = tickData.loc[:, ['current', 'volume', 'money']].resample(sec).agg(
                {'current': ['last', 'first', 'max', 'min'], 'volume': 'last', 'money': 'last'})
            data = changeData.current
            data = data.rename(columns={'first': 'open', 'last': 'close', 'max': 'high', 'min': 'low'})
            data['volume'] = changeData.volume['last'].diff().fillna(0)
            data['money'] = changeData.money['last'].diff().fillna(0)
            d1 = data.loc[datetime.time(9, 0, 0):datetime.time(10, 15, 0), :]
            d2 = data.loc[datetime.time(10, 30, 0):datetime.time(11, 30, 0), :]
            d3 = data.loc[datetime.time(13, 30, 0):datetime.time(15, 0, 0), :]
            data = pd.concat([d1, d2, d3])
            return data
        elif sec.endswith('m'):
            data = get_price('RM1909.XZCE', start_date=start_date, end_date=end_date, frequency=sec,
                             fields=['open', 'close', 'high', 'low', 'volume', 'money'])
            d1 = data.loc[datetime.time(9, 0, 0):datetime.time(10, 15, 0), :]
            d2 = data.loc[datetime.time(10, 30, 0):datetime.time(11, 30, 0), :]
            d3 = data.loc[datetime.time(13, 30, 0):datetime.time(15, 0, 0), :]
            data = pd.concat([d1, d2, d3])
            return data
        elif sec.endswith('d'):
            data = get_price('RM1909.XZCE', start_date=start_date, end_date=end_date, frequency=sec,
                             fields=['open', 'close', 'high', 'low', 'volume', 'money'])
            return data
        else:
            raise Exception("不支持的频率类型，请使用频率 1m分钟 1S秒 1d天")

    # 获取所有主力合约信息
    def getAllMainContract(self):
        secs = get_all_securities(types=['futures'])
        main_secs = secs[secs.display_name.apply(lambda x: '主力合约' in x)]
        main_secs_code = [get_dominant_future(s[0:-4]) for s in main_secs.name if get_dominant_future(s[0:-4])]
        ac = secs.loc[main_secs_code, :]
        ac['code'] = ac.index
        ac.code = ac.code.apply(lambda s: str(s[0:-9]).upper())
        ac = ac[ac.code.apply(lambda s: s not in suit_futures)]  # 过滤掉期货特定品种
        ac = ac[ac.code.apply(lambda s: s not in error_futures)]  # 过滤掉有问题合约
        return ac

    # 查询交易单位，输入参数为合约的代码 比如RU1909.XSGE合约，这里输入RU
    def get_trade_units(self, symbol):
        code = symbol.split(".")[0][:-4].upper()
        return trade_units.get(code)


# 计算引擎
class StatisEngine():
    def integration(self, priceX):
        # 一阶单整计算  一节单整检验还是用对数价格
        logX = np.log(priceX)
        retX = logX.diff()[1:]
        adfLX = st.adfuller(logX)
        adfRX = st.adfuller(retX)
        return adfLX[1], adfRX[1]

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
        # 协整检验用真实数据
        logX = priceX
        logY = priceY
        results = sm.OLS(logY, sm.add_constant(logX)).fit()
        resid = results.resid
        adfSpread = st.adfuller(resid)
        if adfSpread[1] >= 0.05:
            # 残差序列是非平稳时间序列，不具有协整关系
            return (False, results.params[0], results.params[1])
        else:
            # 残差序列是平稳时间序列，具有协整关系
            return (True, results.params[0], results.params[1])

    # 获取残差序列
    def getSpread(self, priceX, priceY, alpha, beta):
        return priceY - alpha - beta * priceX


# 2. 一阶单整检验筛选
def filter_integration_datas(ac, sec, ana_start, ana_end, trade_start, trade_end):
    de = DataEngine()
    se = StatisEngine()
    validData = {}
    for i in ac.index:
        # 获取经过处理的数据
        print("%s 合约-------------进行一阶单整筛选" % str(i))
        # print("%s 合约-------------1. 获取数据，数据进行筛选" % str(i))
        tmp_data = de.getData(i, start_date=ana_start, end_date=trade_end, sec=sec)
        # 排除没有数据的合约
        # print("%s 合约-------------2. 最后一日成交量量要在10000手以上" % str(i))
        # 获取最后一日的成交量
        if tmp_data.shape[0]>10000:
            volume = tmp_data[str(tmp_data.index[-1].date())].volume.sum()
            if volume >= 10000:
                # print("%s 合约-------------3. 获取分析期数据，并去重" % str(i))
                close_ana_data = tmp_data.loc[ana_start:ana_end, :]['close'].dropna()
                # print("%s 合约-------------4. 合约一阶单整检验" % str(i))
                result = se.isIntegration(close_ana_data)
                if result:
                    # print("%s 合约-------------5. 合约一阶单整检验成功" % str(i))
                    # 用收盘价数据乘以最小交易单位作为要分析的数据
                    cu = de.get_trade_units(str(i))
                    close_data = tmp_data['close'].dropna()
                    validData[i] = (close_data * cu)
    data = DataFrame(validData).dropna(how='all')
    ana_date = data.loc[ana_start:ana_end, :]
    trade_date = data.loc[trade_start:trade_end, :]
    return ana_date, trade_date


# 协整效应筛选
def filter_cointegration(ac, ana_data, trade_data):
    l = ana_data.columns.size
    se = StatisEngine()
    pairs_list = []
    pairs_ana_data = {}
    pairs_trade_data = {}
    for i in range(l):
        for j in range(i + 1, l):
            s1 = ana_data.columns[i]
            s2 = ana_data.columns[j]
            # 前项和后项填充都用上，防止出现空值
            t1 = ana_data.loc[:, [s1, s2]].dropna(how='all').bfill().ffill()
            d1 = t1[s1]
            d2 = t1[s2]
            print("套利对：(%s,%s)进行协整检验" % (s1, s2))
            (result, alpha, beta) = se.isCointegration(d1, d2)
            if result:
                alpha = round(alpha + 0.1, 0)  # alpha值进行取整
                beta = round(beta + 0.001, 2)  # beta值保留两位小数
                s1_name = ac.loc[s1, :].display_name
                s2_name = ac.loc[s2, :].display_name
                pairs_list.append((s1, s2, s1_name, s2_name, alpha, beta))
                pairs_ana_data[s1 + '_' + s2] = t1
                pairs_trade_data[s1 + '_' + s2] = trade_data.loc[:, [s1, s2]].dropna(how='all').bfill().ffill()
    pairs = DataFrame(pairs_list, columns=['s1', 's2', 's1_name', 's2_name', 'alpha', 'beta'])
    pairs.index = pairs.s1 + '_' + pairs.s2
    return pairs, pairs_ana_data, pairs_trade_data


def create_report(pairs, pairs_ana_data, pairs_trade_data):
    print(pairs)
    for i in pairs.index:
        pair = pairs.loc[i, :]
        ana_data = pairs_ana_data[i]
        trade_data = pairs_trade_data[i]
        ana_resid = ana_data[pair.s2] - pair.alpha - pair.beta * ana_data[pair.s1]
        trade_resid = trade_data[pair.s2] - pair.alpha - pair.beta * trade_data[pair.s1]
        plotData(ana_resid, title=('%s和%s分析期数据的价差图' % (pair.s1_name, pair.s2_name)), signal=True)
        plotData(trade_resid, title=('%s和%s交易期数据的价差图' % (pair.s1_name, pair.s2_name)), signal=True)


def Main(sec, ana_start, ana_end, trade_start, trade_end):
    print("1. 获取合约信息")
    de = DataEngine()
    ac = de.getAllMainContract()
    print("2. 进行一阶单整筛选")
    (ana_date, trade_data) = filter_integration_datas(ac, sec=sec, ana_start=ana_start,
                                                      ana_end=ana_end, trade_start=trade_start, trade_end=trade_end)
    print("3. 进行协整检验")
    (pairs, pairs_ana_data, pairs_trade_data) = filter_cointegration(ac, ana_date, trade_data)
    # 对所有套利对生成策略图
    print("4. 打印最后的协整分析结果")
    create_report(pairs, pairs_ana_data, pairs_trade_data)
    print("协整检验完成")
    return ac, pairs, pairs_ana_data, pairs_trade_data


# 适当性品种，这些品种目前无法交易,需要额外申请
suit_futures = ['IC', 'IF', 'IH', 'T', 'TF', 'TS', 'I', 'SC', 'TA']
# 目前有问题的合约，粳稻期货目前无人参与交易，一条数据都没有
# 普麦也无数据
error_futures = ['JR','PM']
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