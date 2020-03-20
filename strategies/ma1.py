from vnpy.app.cta_strategy import CtaTemplate
from vnpy.trader.object import TickData, BarData
from vnpy.trader.utility import BarGenerator, ArrayManager

'''
双均线交易系统
'''


class Ma1(CtaTemplate):
    author = "李鹏"
    fast_window = 10
    slow_window = 20
    fixed_size = 1
    fast_ma1 = 0.0
    fast_ma2 = 0.0
    slow_ma1 = 0.0
    slow_ma2 = 0.0

    parameters = ["fast_window", "slow_window", "fixed_size"]
    variables = ["fast_ma1", "fast_ma2", "slow_ma1", "slow_ma2"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super(Ma1, self).__init__(cta_engine, strategy_name, vt_symbol, setting)
        # K 线生成器，用来生成分钟K线 小时K线 日K线 或者周K线 主要是根据tick线生成K线
        self.bg = BarGenerator(self.on_bar)
        # K线序列管理器
        self.am = ArrayManager()

    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(20)

    def on_start(self):
        self.write_log("策略启动")

    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        # 默认的分钟K线更新，除了tick级别和分钟K线级别是这两个，其他上层级别可自己定义
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return
        fast_ma = am.sma(self.fast_window, array=True)
        # 获取最新的快速均线值，因为每根K线都是在形成后才调用的这个函数，所以不用刻意的向前跳
        self.fast_ma1 = fast_ma[-1]
        self.fast_ma2 = fast_ma[-2]
        slow_ma = am.sma(self.slow_window, array=True)
        self.slow_ma1 = slow_ma[-1]
        self.slow_ma2 = slow_ma[-2]
        # 上穿和下穿的标志
        cross_over = self.fast_ma1 > self.slow_ma1 and self.fast_ma2 < self.slow_ma2
        cross_below = self.fast_ma1 < self.slow_ma1 and self.fast_ma2 > self.slow_ma2
        if cross_over:
            if self.pos == 0:
                # 当前空仓就多头开仓
                self.buy(bar.close_price, self.fixed_size)  # 多头开仓，买开
            elif self.pos < 0:
                # 当前空头持仓，就平掉空仓，再多头开仓
                self.cover(bar.close_price, self.fixed_size)  # 空头平仓，买平
                self.buy(bar.close_price, self.fixed_size)  # 买开
        if cross_below:
            if self.pos == 0:
                self.short(bar.close_price, self.fixed_size)
            elif self.pos > 0:
                self.sell(bar.close_price, self.fixed_size)
                self.short(bar.close_price, self.fixed_size)
