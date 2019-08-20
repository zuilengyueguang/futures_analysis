from datetime import datetime

from vnpy.trader.ui import create_qapp, QtCore
from vnpy.trader.database.initialize import init
from vnpy.trader.constant import Exchange, Interval
from vnpy.chart import ChartWidget, VolumeItem, CandleItem

if __name__ == "__main__":
    app = create_qapp()

    setting = {
        "driver": "mongodb",
        "database": "vnpy",
        "host": "localhost",
        "port": 27017,
        "user": "root",
        "password": "123456",
        "authentication_source": "vnpy"
    }
    database_manager = init(setting)

    bars = database_manager.load_bar_data(
        "m1909",
        Exchange.DCE,
        interval=Interval.MINUTE,
        start=datetime(2019, 7, 1),
        end=datetime(2019, 7, 29)
    )

    widget = ChartWidget()
    widget.add_plot("candle", hide_x_axis=True)
    widget.add_plot("volume", maximum_height=200)
    widget.add_item(CandleItem, "candle", "candle")
    widget.add_item(VolumeItem, "volume", "volume")
    widget.add_cursor()

    n = 1000
    history = bars[:n]
    new_data = bars[n:]

    widget.update_history(history)

    def update_bar():
        bar = new_data.pop(0)
        widget.update_bar(bar)

    timer = QtCore.QTimer()
    timer.timeout.connect(update_bar)
    #timer.start(100)

    widget.show()
    app.exec_()
