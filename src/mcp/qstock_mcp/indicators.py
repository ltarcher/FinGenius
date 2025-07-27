#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
补充一些qstock没有的额外技术指标，如MACD、KDJ、BOLL、RSI、OBV、EXPMA
调用ta库性能较高

'''

import numpy as np
import pandas as pd
import ta
#from common_utils import timeit_decorator

'''
BOLL布林指标:
BOLL指标是一种技术分析指标，用于衡量股票或其他交易资产的价格波动情况。BOLL指标的计算方法如下：

计算中轨线（MB）：MB = n天收盘价的平均值

计算上轨线（UP）：UP = MB + k * n天收盘价的标准差

计算下轨线（DN）：DN = MB - k * n天


def boll_mb(close_prices, n):
    # 计算n天收盘价的平均值
    mb = sum(close_prices[-n:]) / n
    return mb

def boll_std(close_prices, n):
    # 计算n天收盘价的标准差
    mean = sum(close_prices[-n:]) / n
    variance = sum((x - mean) ** 2 for x in close_prices[-n:]) / n
    std = variance ** 0.5
    return std

#计算BOLL当天布林指标(上中下轨)
def boll_day(close_prices, n=20, k=2):
    # 计算中轨线、上轨线和下轨线
    mb = boll_mb(close_prices, n)
    std = boll_std(close_prices, n)
    up = mb + k * std
    dn = mb - k * std
    return up, mb, dn

#计算所有BOLL值得到曲线
def BOLL(close_prices, n=20, k=2):
    boll_df = pd.DataFrame(columns=['boll_upper', 'boll_middle', 'boll_lower'])
    for i in range(n, len(close_prices)):
        boll_df.loc[close_prices.index[i]] = boll_day(close_prices[:i+1], n, k)
    return boll_df
'''

#使用ta库
def BOLL(df, window=20, window_dev=2):
    if df.empty:
        return df
    
    df["boll_upper"] = ta.volatility.bollinger_hband(df.close, window, window_dev)
    df["boll_lower"] = ta.volatility.bollinger_lband(df.close, window, window_dev)
    df["boll_middle"] = ta.volatility.bollinger_mavg(df.close, window, window_dev)

    return df

'''
OBV指标:
OBV指标是一种技术分析指标，用于衡量股票或其他交易资产的买卖压力。OBV指标的计算方法如下：

计算当日的OBV值：如果当日收盘价高于前一日收盘价，则当日OBV值等于前一日OBV值加上当日成交量；如果当日收盘价低于前一日收盘价，则当日OBV值等于前一日OBV值减去当日成交量；如果当日收盘价等于前一日收盘价，则当日OBV值等于前一日OBV值。

计算OBV指标：OBV指标等于一段时间内的OBV值之和。

def calculate_obv(close_prices, volumes):
    # 计算OBV值
    obv = [0] * len(close_prices)
    obv[0] = volumes[0]
    for i in range(1, len(close_prices)):
        if close_prices[i] > close_prices[i-1]:
            obv[i] = obv[i-1] + volumes[i]
        elif close_prices[i] < close_prices[i-1]:
            obv[i] = obv[i-1] - volumes[i]
        else:
            obv[i] = obv[i-1]
    return obv

def OBV(close_prices, volumes):
    obv_df = pd.DataFrame(columns=['OBV'])
    obv = calculate_obv(close_prices, volumes)
    for i in range(0, len(close_prices)):
        obv_df.loc[close_prices.index[i]] = obv[i]
    return obv_df
'''
#使用ta库
def OBV(df):
    if df.empty:
        return df
    
    df['obv'] = ta.volume.on_balance_volume(df.close, df.volume)
    return df

'''
RSI指标：
RSI指标是一种技术分析指标，用于衡量股票或其他交易资产的买卖力量。RSI指标的计算方法如下：

计算相对强弱指数RSI：RSI = 100 - 100 / (1 + RS)
其中，RS = n日内收盘价上涨总幅度 / n日内收盘价下跌总幅度。

计算n日内收盘价上涨总幅度和下跌总幅度。

def RSI(close_prices, n=14):
    delta = close_prices.diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    up = up.rolling(window=n).sum()
    down = -down.rolling(window=n).sum()
    rs = up / down
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi_df = pd.DataFrame({'RSI': rsi.values, }, index=close_prices.index)
    return rsi_df
'''
#使用ta库计算
def RSI(df, n=12):
    if df.empty:
        return df
    
    df['rsi'] = ta.momentum.rsi(df.close, window=n)
    df['rsi_ma'] = df['rsi'].rolling(window=n).mean()
    df['rsi_gc'] = (df['rsi'] > df['rsi_ma']) & (df['rsi'].shift(1) < df['rsi_ma'].shift(1))
    df['rsi_dc'] = (df['rsi'] < df['rsi_ma']) & (df['rsi'].shift(1) > df['rsi_ma'].shift(1))
    return df

"""
EXPMA指标:
EXPMA指标是一种技术分析指标，用于衡量股票或其他交易资产的趋势。EXPMA指标的计算方法如下：

计算移动平均线EMA：EMA = (2 * 当日收盘价 + (n-1) * 前一日EMA) / (n+1)
其中，n表示计算EMA值所需的天数。

计算EXPMA指标：EXPMA = EMA * (2 / (m+1)) + 前一日EXPMA * (1 - 2 / (m+1))
其中，m表示计算EXPMA值所需的天数。
"""
"""
def calculate_ema(close_prices, n=12):
    # 计算移动平均线EMA
    ema = [0] * len(close_prices)
    ema[0] = close_prices[0]
    for i in range(1, len(close_prices)):
        ema[i] = (2 * close_prices[i] + (n-1) * ema[i-1]) / (n+1)
    return ema

def calculate_expma(close_prices, n=12, m=9):
    # 计算EMA值
    ema = calculate_ema(close_prices, n)
    # 计算EXPMA指标
    expma = [0] * len(close_prices)
    expma[0] = ema[0]
    for i in range(1, len(close_prices)):
        expma[i] = ema[i] * (2 / (m+1)) + expma[i-1] * (1 - 2 / (m+1))
    return expma
"""
#使用ta库计算
def EXPMA(df, n=5):
    if df.empty:
        return df
    
    df['expma'] = ta.trend.ema_indicator(df.close, window=n)
    df['expma_ma'] = df['expma'].rolling(window=n).mean()
    df['expma_gc'] = (df['expma'] > df['expma_ma']) & (df['expma'].shift(1) < df['expma_ma'].shift(1))
    df['expma_dc'] = (df['expma'] < df['expma_ma']) & (df['expma'].shift(1) > df['expma_ma'].shift(1))
    return df

'''
MACD指标是一种技术分析指标，用于衡量股票或其他资产价格趋势的强度和方向。
它由两条移动平均线和一条信号线组成，通过计算两条移动平均线之间的差异来确定价格趋势的强度和方向。
当MACD线从下向上穿过信号线时，这被视为一个买入信号；当MACD线从上向下穿过信号线时，这被视为一个卖出信号。
MACD指标的计算方法如下：

计算短期移动平均线（EMA12）和长期移动平均线（EMA26）：
EMA12 = 前一日EMA12 x 11/13 + 今日收盘价 x 2/13
EMA26 = 前一日EMA26 x 25/27 + 今日收盘价 x 2/27

其中，EMA12表示12日指数移动平均线，EMA26表示26日指数移动平均线。

计算MACD线：
MACD = EMA12 - EMA26

计算信号线（9日EMA）：
Signal = 前一日Signal x 8/10 + 今日MACD x 2/10

计算柱状图（DIF）：
DIF = MACD - Signal

其中，MACD线表示短期EMA和长期EMA之间的差异，信号线表示MACD线的9日EMA，柱状图表示MACD线和信号线之间的差异。
'''
# 计算MACD
def calculate_macd(close, short=12, long=26, signal=9):
    ema12 = pd.DataFrame.ewm(close, span=short).mean()
    ema26 = pd.DataFrame.ewm(close, span=long).mean()
    # dif组成的线叫MACD线
    dif = ema12 - ema26
    # dea组成的线叫signal线
    dea = pd.DataFrame.ewm(dif, span=signal).mean()
    # dif与dea的差得到柱状
    hist = 2 * (dif - dea)
    dif = np.round(dif, 3)
    dea = np.round(dea, 3)
    hist = np.round(hist, 3)
    return dif, dea, hist

def MACD(df, short=12, long=26, signal=9):
    if df.empty:
        return df
    
    df["diff"], df["dea"], df["macd"] = calculate_macd(df.close, short=short, long=long, signal=signal)
    df['macd_gc'] = (df['diff'] > df['dea']) & (df['diff'].shift(1) < df['dea'].shift(1))
    df['macd_dc'] = (df['diff'] < df['dea']) & (df['diff'].shift(1) > df['dea'].shift(1))
    return df

'''
KDJ指标：
KDJ指标是一种技术分析指标，用于衡量股票或其他交易资产的超买超卖程度。KDJ指标的计算方法如下：

计算未成熟随机值RSV：RSV = (收盘价 - 最低价) / (最高价 - 最低价) * 100

计算K值：K = 2/3 * 前一日K值 + 1/3 * 当日RSV

计算D值：D = 2/3 * 前一日D值 + 1/3 * 当日K值

计算J值：J = 3 * 当日K值 - 2 * 当日D值

'''

def calculate_rsv(close_prices, low_prices, high_prices, n=9):
    # 计算未成熟随机值RSV
    rsv = [0] * len(close_prices)
    for i in range(n-1, len(close_prices)):
        c = close_prices[i]
        l = min(low_prices[i-n+1:i+1])
        h = max(high_prices[i-n+1:i+1])
        rsv[i] = (c - l) / (h - l) * 100
    return rsv

def KDJ(df, n=9):
    if df.empty:
        return df
    
    rsv = calculate_rsv(df.close, df.low, df.high, n)
    # 计算所有日期的kdj值
    # 初始化KDJ指标的初始值
    #k_values = [50] * len(df.close)
    #d_values = [50] * len(df.close)
    #j_values = [0] * len(df.close)
    k_values = np.full_like(df.close, 50)
    d_values = np.full_like(df.close, 50)
    j_values = np.zeros_like(df.close)
    
    for i in range(n-1, len(df.close)):
        k_values[i] = 2/3 * k_values[i-1] + 1/3 * rsv[i]
        d_values[i] = 2/3 * d_values[i-1] + 1/3 * k_values[i]
        j_values[i] = 3 * k_values[i] - 2 * d_values[i]

    df["kdj_k"] = k_values
    df["kdj_d"] = d_values
    df["kdj_j"] = j_values
    #KDJ金叉判断
    df['kdj_gc'] = (df['kdj_k'] > df['kdj_d']) & (df['kdj_k'].shift(1) < df['kdj_d'].shift(1))
    #KDJ死叉判断
    df['kdj_dc'] = (df['kdj_k'] < df['kdj_d']) & (df['kdj_k'].shift(1) > df['kdj_d'].shift(1))

    return df

#量能分析
def VolumeAnalyze(df):
    if df.empty:
        return df
    
    df["va5"] = df["volume"].rolling(window=5).mean()
    df["va10"] = df["volume"].rolling(window=10).mean()
    #量能金叉判断
    df["va_gc"] = (df["va5"] > df["va10"]) & (df["va5"].shift(1) < df["va10"].shift(1))
    #量能死叉判断
    df["va_dc"] = (df["va5"] < df["va10"]) & (df["va5"].shift(1) > df["va10"].shift(1))
    return df

#大涨后回调支撑位，看一段时间内高低点对比，支撑位=(高点-低点)/3 + 低点，参考K线支撑
def SupportAnalyze(df):
    if df.empty:
        return df
    
    df["sp30_max"] = df["close"].rolling(window=30, min_periods=1).max()
    df["sp30_min"] = df["close"].rolling(window=30, min_periods=1).min()
    df["sp30"] = (df["sp30_max"] - df["sp30_min"]) / 3 + df["sp30_min"]
    df["sp45_max"] = df["close"].rolling(window=45, min_periods=1).max()
    df["sp45_min"] = df["close"].rolling(window=45, min_periods=1).min()
    df["sp45"] = (df["sp45_max"] - df["sp45_min"]) / 3 + df["sp45_min"]
    df["sp60_max"] = df["close"].rolling(window=60, min_periods=1).max()
    df["sp60_min"] = df["close"].rolling(window=60, min_periods=1).min()
    df["sp60"] = (df["sp60_max"] - df["sp60_min"]) / 3 + df["sp60_min"]
    df["sp75_max"] = df["close"].rolling(window=75, min_periods=1).max()
    df["sp75_min"] = df["close"].rolling(window=75, min_periods=1).min()
    df["sp75"] = (df["sp75_max"] - df["sp75_min"]) / 3 + df["sp75_min"]
    df["sp90_max"] = df["close"].rolling(window=90, min_periods=1).max()
    df["sp90_min"] = df["close"].rolling(window=90, min_periods=1).min()
    df["sp90"] = (df["sp90_max"] - df["sp90_min"]) / 3 + df["sp90_min"]
    df["sp120_max"] = df["close"].rolling(window=120, min_periods=1).max()
    df["sp120_min"] = df["close"].rolling(window=120, min_periods=1).min()
    df["sp120"] = (df["sp120_max"] - df["sp120_min"]) / 3 + df["sp120_min"]
    return df

#获取指定周期内特定值（最高、最低）所在的整数索引
def ValueIndexOfPeriod(df, period):
    last_value = df[period].iloc[-1]
    last_index = df[period][::-1].ne(last_value).idxmax()
    integer_index = df.index.get_loc(last_index) + 1
    return integer_index

#判断是否符合回调支撑图形（缠论）
def CheckValidSupport(df, period):
    #必须是低位在前面，高位在中间
    low_index = ValueIndexOfPeriod(df, period + "_min")
    high_index = ValueIndexOfPeriod(df, period + "_max")
    return low_index < high_index

#神奇九转（Demark TD Sequential）
def DemarkTDSequential(df):
    if df.empty:
        return df
    # 计算TD Sequential的条件
    df['direction'] = df['close'].diff().apply(lambda x: 'up' if x > 0 else 'down')
    df['td_count'] = (df['direction'] != df['direction'].shift()).cumsum()
    df['td_direction'] = df['direction'].apply(lambda x: 1 if x == 'up' else -1)
    df['td_count'] = df.groupby('td_count')['td_direction'].cumsum().abs()
    df['td_setup'] = (df['td_count'] == 9)
    df['td_setup_completed'] = (df['td_count'] >= 13)

    # 计算TD Phase的条件
    df['td_phase'] = 0
    df.loc[df['td_setup_completed'].shift(1) & (df['close'] < df['close'].shift(1)), 'td_phase'] = 1
    df.loc[df['td_phase'].shift(1) == 1 & (df['close'] > df['close'].shift(1)), 'td_phase'] = 2
    df.loc[df['td_phase'].shift(1) == 2 & (df['close'] < df['close'].shift(1)), 'td_phase'] = 3

    # 生成买卖信号
    df['td_signal'] = '保持'
    df.loc[(df['td_phase'].shift(1) == 3) & (df['td_phase'] == 0), 'td_signal'] = '买入'
    df.loc[(df['td_phase'].shift(1) == 2) & (df['td_phase'] == 3), 'td_signal'] = '卖出'

    # 返回买卖信号
    return df

#头肩顶
#timeit_decorator
def head_and_shoulders(data, window=30):
  """
  该函数在给定的数据窗口中检测头肩顶模式。
  
  参数:
      data (pd.DataFrame): 包含股票价格数据的DataFrame。
      window (int): 模式检测的回溯窗口大小。
  
  返回值:
      pattern: 一个布尔值列表，表示窗口中每一天是否存在模式（True表示存在，False表示不存在）。
      pnl: 模式检测到的每一天的交易利润或损失列表。
  """
  pattern = []  # 存储模式检测结果的列表
  pnl = []  # 存储交易盈亏的列表
  dates = []  # 存储日期的列表
  for i in range(window, len(data) - window):
    data_window = data.iloc[i-window:i + window]  # 获取当前窗口的数据
    pattern_window = data.iloc[i-window:i]  # 获取模式窗口的数据
    # 提取相关数据点
    head_idx = np.argmax(pattern_window["high"].iloc[:window])  # 找到头部位置的索引
    head = np.max(pattern_window["high"].iloc[:window])  # 找到头部的最高点
  
    if head_idx > 8:
      left_shoulder = np.max(pattern_window["high"].iloc[:head_idx-3])  # 找到左肩的最高点
      left_shoulder_idx = np.argmax(pattern_window["high"].iloc[:head_idx-3])  # 找到左肩位置的索引
    else:
      pattern += [False]  # 如果头部位置不在中间，当前窗口不构成模式
      continue
    if head_idx < (window-8):
      right_shoulder_idx = np.argmax(pattern_window["high"].iloc[head_idx+3:])  # 找到右肩的最高点索引
      right_shoulder = np.max(pattern_window["high"].iloc[head_idx+3:])  # 找到右肩的最高点
    else:
      pattern += [False]  # 如果头部位置太靠近窗口边缘，当前窗口不构成模式
      continue
  
    # 计算颈线位置
    neckline = np.min(pattern_window["low"].iloc[left_shoulder_idx:right_shoulder_idx])
    next_20_days = data_window["close"].iloc[window:]  # 获取窗口后20天的收盘价
  
    entry_price = data_window['close'].iloc[window]  # 计算入场价格
    # 检查头肩顶模式的条件
    if head > left_shoulder and head > right_shoulder and neckline > entry_price:
      # 计算潜在的盈亏（假设在颈线突破时买入）
  
      min_next_20d = next_20_days.min()  # 计算接下来20天的最小值
      # 计算出场价格
      exit_price = min_next_20d if (min_next_20d < entry_price) else next_20_days.iloc[-1]
  
      # 我们对模式进行空头交易
      profit_loss = (exit_price - entry_price) / entry_price * -100
  
      # 打印模式确认和潜在盈亏
      print(f"在{data.index[i]}检测到头肩顶模式。潜在盈亏：{profit_loss:.2f}%")
      pattern.append(True)  # 模式存在
      pnl.append(profit_loss)  # 记录盈亏
    else:
      pattern.append(False)  # 模式不存在
  return pattern, pnl  # 返回模式检测结果和盈亏列表

#头肩底
#@timeit_decorator
def head_and_shoulders_bottom(data, window=30):
  """
  该函数在给定的数据窗口中检测头肩底模式。
  
  参数:
      data (pd.DataFrame): 包含股票价格数据的DataFrame。
      window (int): 模式检测的回溯窗口大小。
      
  返回值:
      pattern: 一个布尔值列表，表示窗口中每一天是否存在模式（True表示存在，False表示不存在）。
      pnl: 模式检测到的每一天的交易利润或损失列表。
  """
  pattern = []  # 存储模式检测结果的列表
  pnl = []  # 存储交易盈亏的列表
  dates = []  # 存储日期的列表
  for i in range(window, len(data) - window):
    data_window = data.iloc[i-window:i + window]  # 获取当前窗口的数据
    pattern_window = data.iloc[i-window:i]  # 获取模式窗口的数据
    # 提取相关数据点
    head_idx = np.argmin(pattern_window["low"].iloc[:window])  # 找到头部位置的索引
    head = np.min(pattern_window["low"].iloc[:window])  # 找到头部的最低点
  
    if head_idx > 8:
      left_shoulder = np.min(pattern_window["low"].iloc[:head_idx-3])  # 找到左肩的最低点
      left_shoulder_idx = np.argmin(pattern_window["low"].iloc[:head_idx-3])  # 找到左肩位置的索引
    else:
      pattern += [False]  # 如果头部位置不在中间，当前窗口不构成模式
      continue
    if head_idx < (window-8):
      right_shoulder_idx = np.argmin(pattern_window["low"].iloc[head_idx+3:])  # 找到右肩的最低点索引
      right_shoulder = np.min(pattern_window["low"].iloc[head_idx+3:])  # 找到右肩的最低点
    else:
      pattern += [False]  # 如果头部位置太靠近窗口边缘，当前窗口不构成模式
      continue
    
    # 计算颈线位置
    neckline = np.max(pattern_window["high"].iloc[left_shoulder_idx:right_shoulder_idx])
    next_20_days = data_window["open"].iloc[window:]  # 获取窗口后20天的开盘价
  
    entry_price = data_window['open'].iloc[window]  # 计算入场价格
    # 检查头肩底模式的条件
    if head < left_shoulder and head < right_shoulder and neckline < entry_price:
      # 计算潜在的盈亏（假设在颈线突破时买入）
      
      max_next_20d = next_20_days.max()  # 计算接下来20天的最大值
      # 计算出场价格
      exit_price = max_next_20d if (max_next_20d > entry_price) else next_20_days.iloc[-1]
      
      # 我们对模式进行多头交易
      profit_loss = (exit_price - entry_price) / entry_price * 100
      
      # 打印模式确认和潜在盈亏
      print(f"在{data.index[i]}检测到头肩底模式。潜在盈亏：{profit_loss:.2f}%")
      pattern.append(True)  # 模式存在
      pnl.append(profit_loss)  # 记录盈亏
    else:
      pattern.append(False)  # 模式不存在
  return pattern, pnl  # 返回模式检测结果和盈亏列表

#头肩顶（卖出）
#@timeit_decorator
def detect_head_and_shoulders(data, window=30):
    """
    检测给定DataFrame中的收盘价数据是否出现头肩顶形态，并给出卖出价格。
    
    参数:
        data (pd.DataFrame): 包含股票价格的DataFrame，其中包含一个名为'close'的列。
        window (int): 用于分析的时间窗口大小，默认为30。
    
    返回值:
        bool: 是否出现头肩顶形态。
        float: 如果出现头肩顶形态，给出卖出价格；否则返回None。
    """
    # 获取收盘价数据
    close_prices = data['close']
    
    # 找到局部最大值作为头部
    head_high = np.max(close_prices[-window:-window+1])
    head_index = -window + np.argmax(close_prices[-window:-window+1])
    
    # 找到左右肩的局部最大值
    left_shoulder_high = np.max(close_prices[:window])
    right_shoulder_high = np.max(close_prices[-window+1:])
    
    # 找到颈线，即两个局部最小值中的较低者
    neckline = min(close_prices[head_index-1], close_prices[head_index+1])
    
    # 判断是否满足头肩顶形态的条件
    if (head_high > left_shoulder_high and
        head_high > right_shoulder_high and
        neckline < head_high):
        # 计算卖出价格，假设在颈线下方一定比例处卖出
        sell_price = neckline * 0.95  # 卖出价格为颈线下95%
        return True, sell_price
    else:
        return False, None
    
#头肩底（买入）
#@timeit_decorator
def detect_head_and_shoulders_bottom(data, window=30):
    """
    检测给定DataFrame中的收盘价数据是否出现头肩底形态，并给出买入价格。
    
    参数:
        data (pd.DataFrame): 包含股票价格的DataFrame，其中包含一个名为'close'的列。
        window (int): 用于分析的时间窗口大小，默认为30。
    
    返回值:
        bool: 是否出现头肩底形态。
        float: 如果出现头肩底形态，给出买入价格；否则返回None。
    """
    # 获取收盘价数据
    close_prices = data['close']
    
    # 找到局部最小值作为头部
    head_low = np.min(close_prices[-window:-window+1])
    head_index = -window + np.argmin(close_prices[-window:-window+1])
    
    # 找到左右肩的局部最小值
    left_shoulder_low = np.min(close_prices[:window])
    right_shoulder_low = np.min(close_prices[-window+1:])
    
    # 找到颈线，即两个局部最大值中的较高者
    neckline = max(close_prices[head_index-1], close_prices[head_index+1])
    
    # 判断是否满足头肩底形态的条件
    if (head_low < left_shoulder_low and
        head_low < right_shoulder_low and
        neckline > head_low):
        # 价格必须突破颈线才考虑买入
        if close_prices[-1] > neckline:
            # 计算买入价格，通常在颈线突破后的小幅回调处买入
            buy_price = neckline * 1.01  # 买入价格为颈线上101%
            return True, buy_price
        else:
            return True, None  # 价格还没有突破颈线，不构成买入条件
    else:
        return False, None