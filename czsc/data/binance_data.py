import time

import pandas as pd
from binance import ThreadedWebsocketManager
# from config import ApiKey,SecretKey
from binance.client import Client
from czsc.objects import RawBar, Freq




def main():

    # symbol = 'BNBUSDT'
    # client = Client()
    # #kline里面的值依次为：
    # # Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore
    # klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    # print(klines)
    # twm = ThreadedWebsocketManager()
    # # start is required to initialise its internal loop
    # twm.start()
    #
    # def handle_socket_message(msg):
    #     print("进来了")
    #     print(msg)
    #
    # twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)
    #
    # # twm.join()
    # while True:
    #     time.sleep(1)
    #     print("1s")
    data = BinanceData('BNBUSDT')
    while True:
        time.sleep(10)
        print("10s")
        klines = data.get_klines(Freq.F1)
        print(klines[-1])






class BinanceData:
    def __init__(self,symbol):
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


    def handle_socket_message_1m(self,msg):
        #组装成RawBar
        bar = RawBar(symbol=self.symbol, dt=pd.to_datetime(msg['k']['t'],unit='ms'),
                     id=msg['k']['i'], freq=Freq.F1, open=msg['k']['o'], close=msg['k']['c'],
                     high=msg['k']['h'], low=msg['k']['l'],
                     vol=msg['k']['v'],  # 成交量，单位：股
                     amount=msg['k']['q'],  # 成交额，单位：元
                     )
        #获取最后一个k线
        last_bar = self.klines_1m_RawBar[-1]
        #如果最后一个k线的时间小于当前k线的时间，说明是新的一根k线
        if last_bar.dt < bar.dt:
            self.klines_1m_RawBar.append(bar)
        #如果最后一个k线的时间等于当前k线的时间，说明是最后一根k线的更新
        elif last_bar.dt == bar.dt:
            self.klines_1m_RawBar[-1] = bar
        else:
            print("error happened")


    def format_kline(self, _klines, F1):
        bars = []
        for i, record in enumerate(_klines):
            bar = RawBar(symbol=self.symbol, dt=pd.to_datetime(record[0], unit='ms'),
                         id=i, freq=F1, open=record[1], close=record[4],
                         high=record[2], low=record[3],
                         vol=record[5],  # 成交量，单位：股
                         amount=record[7],  # 成交额，单位：元
                         )
            bars.append(bar)
        return bars
    def get_klines(self,freq):
        if freq == Freq.F1:
            return self.klines_1m_RawBar
        elif freq == Freq.F5:
            return self.klines_5m_RawBar
        else:
            print("error happened")
   

if __name__ == "__main__":
   main()