from vnpy.app.algo_trading import AlgoTemplate
from vnpy.trader.engine import BaseEngine

'''
算法交易代码，完成后，拷贝到algos下面，可以在页面操作运行
'''

class ArbitrageSimple(AlgoTemplate):
    # 存放策略名称，方便页面展示
    display_name = '简单的套利策略'
    # 存放对应的参数变量, 方便页面展示，对应的中文在display.py里面
    # 不写对应名字，则使用英文
    default_setting = {
        "active_vt_symbol": "",
        "passive_vt_symbol": ""
    }

    def __init__(self,
        algo_engine: BaseEngine,
        algo_name: str,
        setting: dict):
        super().__init__(algo_engine, algo_name, setting)