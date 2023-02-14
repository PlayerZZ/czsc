import time

import pandas as pd
from binance import ThreadedWebsocketManager
# from config import ApiKey,SecretKey
from binance.client import Client
from czsc.objects import RawBar, Freq


def main():
    data = BinanceData('BNBUSDT')
    while True:
        time.sleep(10)
        print("10s")
        klines = data.get_klines(Freq.F1)
        print(klines[-1])


class BinanceData:
    def __init__(self, symbol):
        self.symbol = symbol
        self.client = Client()
        self.twm = ThreadedWebsocketManager()
        self.twm.start()
        # 1分钟K线
        klines_1m = self.client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
        self.twm.start_kline_socket(callback=self.handle_socket_message_1m, symbol=self.symbol)
        self.klines_1m_RawBar = self.format_kline(klines_1m, Freq.F1)
        # 5分钟K线
        klines_5m = self.client.get_historical_klines(symbol, Client.KLINE_INTERVAL_5MINUTE, "1 day ago UTC")
        # self.twm.start_kline_socket(callback=self.handle_socket_message_5m, symbol=self.symbol)
        self.klines_5m_RawBar = self.format_kline(klines_5m, Freq.F5)

    def handle_socket_message_1m(self, msg):
        # 组装成RawBar
        print(msg['k']['v'])
        bar = RawBar(symbol=self.symbol, dt=pd.to_datetime(msg['k']['t'], unit='ms'),
                     id=msg['k']['i'], freq=Freq.F1, open=float(msg['k']['o']),
                     close=float(msg['k']['c']), high=float(msg['k']['h']),
                     low=float(msg['k']['l']), vol=float(msg['k']['v']),)

        # 获取最后一个k线
        last_bar = self.klines_1m_RawBar[-1]
        # 如果最后一个k线的时间小于当前k线的时间，说明是新的一根k线
        if last_bar.dt < bar.dt:
            self.klines_1m_RawBar.append(bar)
        # 如果最后一个k线的时间等于当前k线的时间，说明是最后一根k线的更新
        elif last_bar.dt == bar.dt:
            self.klines_1m_RawBar[-1] = bar
        else:
            print("error happened")

    def format_kline(self, _klines, F1):
        bars = []
        for i, record in enumerate(_klines):
            bar = RawBar(symbol=self.symbol, dt=pd.to_datetime(record[0], unit='ms'),
                         id=i, freq=F1, open=float(record[1]), close=float(record[4]),
                         high=float(record[2]), low=float(record[3]),
                         vol=float(record[5]),  # 成交量，单位：股
                         amount=float(record[7]),  # 成交额，单位：元
                         )
            bars.append(bar)
        return bars

    def get_klines(self, freq):
        if freq == Freq.F1:
            return self.klines_1m_RawBar
        elif freq == Freq.F5:
            return self.klines_5m_RawBar
        else:
            print("error happened")


if __name__ == "__main__":
    main()
