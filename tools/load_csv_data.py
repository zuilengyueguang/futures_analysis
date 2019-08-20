from vnpy.trader.database.initialize import init
from vnpy.trader.object import TickData,BarData
from vnpy.trader.constant import Exchange,Interval
import csv
import codecs
from datetime import datetime

class LoadCsvData:
    def __init__(self):
        setting = {
            "driver": "mongodb",
            "database": "vnpy",
            "host": "localhost",
            "port": 27017,
            "user": "root",
            "password": "123456",
            "authentication_source": "vnpy"
        }
        self.dm = init(setting)

    def save_ticks(self, ticks):
        self.dm.save_tick_data(ticks)

    def save_bars(self, bars):
        self.dm.save_bar_data(bars)

    def covertf(self, value):
        try:
            return float(value)
        except :
            return 0.0

    def load_ticks(self, csv_path: str):
        ticks = []
        with codecs.open(csv_path, "r", "utf-8") as f:
            reader = csv.DictReader(f)
            for item in reader:
                dt = datetime.strptime(item['datetime'], '%Y-%m-%d %H:%M:%S')
                tick = TickData(
                    symbol=item['symbol'],
                    exchange=Exchange(item['exchange']),
                    datetime=dt,
                    name=item['name'],
                    volume=self.covertf(item['volume']),
                    open_interest=self.covertf(item['open_interest']),
                    last_price=self.covertf(item['last_price']),
                    last_volume=self.covertf(item['last_volume']),
                    limit_up=self.covertf(item['limit_up']),
                    limit_down=self.covertf(item['limit_down']),
                    open_price=self.covertf(item['open_price']),
                    high_price=self.covertf(item['high_price']),
                    low_price=self.covertf(item['low_price']),
                    pre_close=self.covertf(item['pre_close']),
                    bid_price_1=self.covertf(item['bid_price_1']),
                    ask_price_1=self.covertf(item['ask_price_1']),
                    bid_volume_1=self.covertf(item['bid_volume_1']),
                    ask_volume_1=self.covertf(item['ask_volume_1']),
                    gateway_name="JQ"
                )
                ticks.append(tick)
        return ticks

    def load_bars(self, csv_path: str):
        bars = []
        with codecs.open(csv_path, "r", "utf-8") as f:
            reader = csv.DictReader(f)
            for item in reader:
                dt = datetime.strptime(item['datetime'], '%Y-%m-%d %H:%M:%S')
                bar = BarData(
                    symbol=item['symbol'],
                    exchange=Exchange(item['exchange']),
                    datetime=dt,
                    interval=Interval.MINUTE,
                    volume=self.covertf(item['volume']),
                    open_interest=0.0,
                    open_price=self.covertf(item['open']),
                    high_price=self.covertf(item['high']),
                    low_price=self.covertf(item['low']),
                    close_price=self.covertf(item['close']),
                    gateway_name="JQ"
                )
                bars.append(bar)
        return bars

    def one(self, symbol: str, exchange: str):
        ex = Exchange(exchange)
        self.dm.get_newest_tick_data(symbol, ex)


if __name__ == '__main__':
    ls = LoadCsvData()
    data = ls.load_bars("D://workspace//data//SR909_20180315_20190726_1M.csv")
    ls.save_bars(data)



