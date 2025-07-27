# -*- coding:utf-8 -*-
# !/usr/bin/env python

import time
import traceback
import logging
from indicators import BOLL, OBV, MACD, KDJ, RSI, EXPMA, VolumeAnalyze, SupportAnalyze, DemarkTDSequential

# 配置日志
logger = logging.getLogger("mcp_instance")

def timeit_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录函数开始执行的时间
        result = func(*args, **kwargs)  # 执行被装饰的函数
        end_time = time.time()  # 记录函数执行结束的时间
        elapsed_time = end_time - start_time  # 计算执行时间
        print(f"函数 {func.__name__} 执行时间为 {elapsed_time:.4f} 秒。")
        return result
    return wrapper

def get_stock_indicators(df, indicators=[BOLL, OBV, MACD, KDJ, RSI, EXPMA, VolumeAnalyze, SupportAnalyze, DemarkTDSequential]):
    for func in indicators:
        try:
            func(df)
        except Exception as e:
            logger.error("{0}指标获取异常:{1}".format(str(func.__name__), e))
            traceback.print_exc()
    return df