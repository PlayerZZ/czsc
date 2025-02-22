# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2022/7/12 14:22
describe: CZSC 逐K线播放
https://pyecharts.org/#/zh-cn/web_flask
"""
import sys
from datetime import datetime

sys.path.insert(0, '.')
sys.path.insert(0, '..')
from flask import Flask, render_template
from czsc import CZSC, home_path, Freq
from czsc.data import BinanceData


data = BinanceData("BNBUSDT")
app = Flask(__name__, static_folder="templates")
bars = data.get_klines(Freq.F1)
idx = 1000
last_dt = int(bars[-1].dt.timestamp())

def bar_base():
    global idx
    global last_dt
    timenow = int(bars[-1].dt.timestamp())
    if last_dt != timenow:
        last_dt = timenow
        idx += 1
    _bars = bars[-idx:-1]
    # print(idx, _bars[-1].dt)

    c = CZSC(_bars).to_echarts()
    return c


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/barChart")
def get_bar_chart():
    c = bar_base()
    return c.dump_options_with_quotes()


if __name__ == "__main__":
    app.run()


