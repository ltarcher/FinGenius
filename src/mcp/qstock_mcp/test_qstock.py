#!/usr/bin/env python
# -*- encoding=utf8 -*-

import qstock as qs
import stock_rzrq as rzrq
import pandas as pd
from typing import Dict, List, Optional

import sys
from mcp_index import get_economic_calendar
from mcp_macro import get_customs_import_export_data, get_macro_data
import asyncio

gdp = asyncio.run(get_macro_data())
print(gdp)
sys.exit()

cie_list = asyncio.run(get_customs_import_export_data())
print(cie_list)

sys.exit()

ec_list =  asyncio.run(get_economic_calendar('2025-07-26', '2025-08-01'))
print(ec_list)


sys.exit()

# 先获取沪深京三市场的成交数据
realtime_df = qs.realtime_data(market="沪深A", code=["上证指数", "深证成指", "北证50"])
#把时间列转换为日期YYYY-MM-DD格式
realtime_df["日期"] = pd.to_datetime(realtime_df["时间"]).dt.date
print(realtime_df.columns)
print(realtime_df.head())

# 确保日期列是字符串格式
if '日期' in realtime_df.columns:
    realtime_df['日期'] = realtime_df['日期'].astype(str)
print(realtime_df["日期"].unique())
total_turnover = realtime_df["成交额"].sum()
print(total_turnover)



hisdata = qs.get_data(code_list=["上证指数", "深证成指", "北证50"])
hisdata = hisdata.reset_index()
print(hisdata)

# 按照date列进行分组，计算每个日期的成交额总和
grouped_data = hisdata.groupby("date")["turnover"].sum().reset_index()
print(grouped_data)
grouped_data_df = pd.DataFrame(grouped_data)
# 取hisdata中name为"上证指数"的记录
szzs_df = hisdata[hisdata["name"] == "上证指数"]
#按照日期排序
#szzs_df = szzs_df.sort_values(by="date", ascending=True)
szzs_df.reset_index(drop=True, inplace=True)
print(szzs_df)
grouped_data_df["上证指数"] = szzs_df["close"]
print(grouped_data_df)

grouped_data_df["日期"] = pd.to_datetime(grouped_data_df["date"]).dt.date
print(grouped_data_df)


# 获取融资融券历史数据
data = rzrq.get_rzrq_history(page=1, page_size=10, use_chinese_fields=True)
rzrq_df = pd.DataFrame(data.get('result', {}).get('data', []))
if not rzrq_df.empty:
    # 把日期列转换为日期格式
    rzrq_df["日期"] = pd.to_datetime(rzrq_df["交易日期"]).dt.date
print(rzrq_df)

# 把grouped_data_df和rzrq_df按照日期列进行合并
result_df = pd.merge(grouped_data_df, rzrq_df, on="日期", how="left")
print(result_df)

# 按照日期计算融资融券成交比例
rzrq_turnover_ratio = (result_df["总融资买入额"] + result_df["总融券余额"]) / result_df["turnover"] * 100

rzrq_szzs_ratio =  (result_df["总融资买入额"] + result_df["总融券余额"]) / 100000000 / result_df["上证指数"] * 100

print(rzrq_turnover_ratio)

print(rzrq_szzs_ratio)