from vnpy.trader.database.initialize import init
from vnpy.trader.object import TickData
from vnpy.trader.constant import Exchange
import csv
import codecs
from datetime import datetime


class LoadCsvData:
    def save(self, ticks):
        setting = {
            "driver": "mysql",
            "database": "vnpy",
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "123456",
            "authentication_source": "admin"
        }
        dm = init(setting)
        dm.save_tick_data(ticks)

    def covertf(self, value):
        try:
            return float(value)
        except :
            return 0.0

    def load(self, csv_path):
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
                    gateway_name="DB"
                )
                ticks.append(tick)
        return ticks


if __name__ == '__main__':
    ls = LoadCsvData()
    #data = ls.load(csv_path="D://workspace//data//rb1910_20181016_20190723_1S.csv")
    #ls.save(ticks=data)



