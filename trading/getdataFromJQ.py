# encoding: UTF-8
from jqdatasdk import *
auth("15512585336", "")
#from datetime import datetime, date
from time import time, sleep

from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import database_manager
import jqdatasdk as jq

FIELDS = ['open', 'high', 'low', 'close', 'volume']
ex_jq2vn = {
    "XDCE": "DCE",
    "CCFX": "CFFEX",
    "XSGE": "SHFE",
    "XZCE": "CZCE",
    "XINE": "INE"
}


# ----------------------------------------------------------------------
def getAc(name):
    secs = get_all_securities(types=['futures'])
    main_secs = secs[secs.display_name.apply(lambda x: '主力合约' in x)]
    main_secs_code = [get_dominant_future(s[0:-4]) for s in main_secs.name if get_dominant_future(s[0:-4])]
    ac = secs.loc[main_secs_code, :]
    return ac[ac.name == name]


def generateVtBar(row, symbol, exchange):
    """生成K线"""
    bar = BarData(
        symbol=symbol,
        exchange=Exchange(exchange),
        interval=Interval.MINUTE,
        open_price=row["open"],
        high_price=row["high"],
        low_price=row["low"],
        close_price=row["close"],
        volume=row["volume"],
        datetime=row.name.to_pydatetime(),
        gateway_name="DB"
    )
    bar.date = bar.datetime.strftime("%Y%m%d")

    bar.time = bar.datetime.strftime("%H%M%S")
    # 将bar的时间改成提前一分钟
    hour = bar.time[0:2]
    minute = bar.time[2:4]
    sec = bar.time[4:6]
    if minute == "00":
        minute = "59"

        h = int(hour)
        if h == 0:
            h = 24
        hour = str(h - 1).rjust(2, '0')
    else:
        minute = str(int(minute) - 1).rjust(2, '0')
    bar.time = hour + minute + sec
    bar.datetime = bar.datetime.strptime(' '.join([bar.date, bar.time]), '%Y%m%d %H%M%S')
    return bar
def download_minute_bar(name, start_date, end_date, ac):
    """下载某一合约的分钟线数据"""
    print(f"开始下载合约数据{name}")
    symbol_info = ac[ac.name == name]
    symbol = name
    vt_symbol = symbol_info.index[0]
    exchange = ex_jq2vn.get(vt_symbol[-4:])
    print(f"{symbol, exchange}")
    symbol_info = ac[ac.name == name]
    vt_symbol = symbol_info.index[0]
    start = time()
    df = jq.get_price(
        vt_symbol,
        start_date=start_date,
        end_date=end_date,
        frequency="1m",
        fields=FIELDS,
    )
    bars = []
    for ix, row in df.iterrows():
        bar = generateVtBar(row, symbol, exchange)
        bars.append(bar)
    database_manager.save_bar_data(bars)

    end = time()
    cost = (end - start) * 1000

    print(
        "合约%s的分钟K线数据下载完成%s - %s，耗时%s毫秒"
        % (symbol, df.index[0], df.index[-1], cost)
    )
    print(jq.get_query_count())


if __name__ == "__main__":
    symbol = 'rb1910'
    start_date = '2019-01-01'
    end_date = '2019-01-05'
    ac=getAc(symbol)
    download_minute_bar(symbol, start_date, end_date, ac)