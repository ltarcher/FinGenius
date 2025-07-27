#!/usr/bin/env python
# -*- encoding=utf8 -*-

import qstock as qs
import stock_rzrq as rzrq
import pandas as pd
import logging
import traceback
from mcp_instance import mcp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from pyquery import PyQuery as pq

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool()
async def get_index_realtime_data(codes: list|str, market: str = "沪深A") -> list:
    """ 获取中国金融市场指定指数或股票、期权、期货的实时数据
    参数：
    - codes: 指数或股票、期权、期货代码/名称，类型可以是字符串或列表；如果是字符串，多个代码用逗号分隔，为空时默认获取指定的市场指数
    - market: 市场类型，可选：["沪深A", "港股", "美股", "期货", "外汇", "债券"]，默认为沪深A
    返回：
    - List[Dict]: 包含指数或股票代码、名称、最新价、涨跌幅等，
    Dict包含字段:
    ['代码', '名称', '涨幅', '最新', '最高', '最低', '今开', '换手率', '量比', '市盈率', '成交量', '成交额', '昨收', '总市值', '流通市值', '市场', '时间']
    """
    if isinstance(codes, str):
        if not codes:
            index_codes = ['上证指数', '深证成指', '创业板指', '沪深300', '中证500', '上证50', '中证1000', '科创50', "恒生指数", "恒生科技指数"]  # 默认上证指数
        else:
            index_codes = codes.split(',')
    elif isinstance(codes, list):
        index_codes = codes
    else:
        logger.error("参数 'codes' 必须是字符串或列表")
        return []
    
    # 对market参数进行处理
    if market not in ["沪深A", "港股", "美股", "期货", "外汇", "债券"]:
        logger.info(f"当前输入的市场: {market}")
        logger.warning(f"参数 'market' 必须是以下值之一: 沪深A, 港股, 美股, 期货, 外汇, 债券")
        market = "沪深A"  # 默认市场为沪深A
    
    # 使用qstock获取指数实时数据
    try:
        df = qs.realtime_data(market=market, code=index_codes)
        logger.info(f"获取指数实时数据: {df}")
        if df.empty:
            logger.warning("获取的指数数据为空")
            return []
        logger.info(f"指数数据获取成功: {df.shape[0]} 条记录")
        logger.info(f"指数数据列名: {df.columns.tolist()}")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取指数实时数据失败: {str(e)}")
        traceback.print_exc()
    return []

# 获取实时沪深京三市场的总成交数据
@mcp.tool()
async def get_board_trade_realtime_data() -> Dict:
    """ 获取沪深京三市场的成交数据
    返回：
    - Dict: 包含日期和成交额的字典，格式为 {'日期': 日期, '总成交额': 总成交额'}
    """
    try:
        realtime_df = qs.realtime_data(market="沪深A", code=["上证指数", "深证成指", "北证50"])
        # 把时间列转换为日期YYYY-MM-DD格式
        realtime_df["日期"] = pd.to_datetime(realtime_df["时间"]).dt.date
        # 确保日期列是字符串格式
        if '日期' in realtime_df.columns:
            realtime_df['日期'] = realtime_df['日期'].astype(str)
        total_turnover = realtime_df["成交额"].sum()
        return {"日期": realtime_df["日期"].iloc[0], "总成交额": total_turnover}
    except Exception as e:
        logger.error(f"获取成交数据失败: {str(e)}")
        traceback.print_exc()
        return {}

# 获取沪深京三市场的历史总成交数据
@mcp.tool()
async def get_turnover_history_data(start_date: Optional[str] = None, end_date: Optional[str] = None, page: int = 1, page_size: int = 10, use_chinese_fields: bool = True) -> List[Dict]:
    """ 获取沪深京三市场的历史总成交数据
    参数：
    - start_date: 开始日期，格式为'YYYY-MM-DD'，默认为None
    - end_date: 结束日期，格式为'YYYY-MM-DD'，默认为None
    - use_chinese_fields: 是否使用中文字段名，默认为True
    返回：
    - List[Dict]: 包含成交数据的字典列表
    Dict包含字段: ['日期', '成交额'] 或 ['date', 'turnover']（取决于use_chinese_fields参数）
    """
    try:
        hisdata = qs.get_data(code_list=["上证指数", "深证成指", "北证50"], start = start_date.replace('-', ''), end = end_date.replace('-', ''))
        hisdata = hisdata.reset_index()

        # 按照date列进行分组，计算每个日期的成交额总和
        grouped_data = hisdata.groupby("date")["turnover"].sum().reset_index()
        if use_chinese_fields:
            grouped_data = grouped_data.rename(columns={"date": "日期", "turnover": "总成交额"})

        return grouped_data.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取成交数据失败: {str(e)}")
        traceback.print_exc()
        return {}
    
# 获取融资融券占比市场成交额的历史数据
@mcp.tool()
async def get_rzrq_turnover_ratio(start_date = None, end_date = None, page: int = 1, page_size: int = 10, use_chinese_fields: bool = True) -> List[Dict]:
    """ 获取融资融券占总成交比例数据(含总融资余额与上证指数偏离率)
    参数：
    - start_date: 开始日期，格式为'YYYY-MM-DD'，默认为None
    - end_date: 结束日期，格式为'YYYY-MM-DD'，默认为None
    - page: 页码，默认为1
    - page_size: 每页数量，默认为10
    - use_chinese_fields: 是否使用中文字段名，默认为True
    返回：
    - List[Dict]: 包含日期和融资融券占成交比例的字典列表，格式为 [{'日期': 日期, '融资融券占总成交比例': 比例, '总融资余额与上证指数偏离率': 偏离比例}]
    """
    try:
        hisdata = qs.get_data(code_list=["上证指数", "深证成指", "北证50"], start= start_date.replace('-', ''), end = end_date.replace('-', ''))
        hisdata = hisdata.reset_index()

        szzs_df = hisdata[hisdata["name"] == "上证指数"]
        szzs_df.reset_index(inplace=True, drop=True)

        # 按照date列进行分组，计算每个日期的成交额总和
        grouped_data = hisdata.groupby("date")["turnover"].sum().reset_index()
        grouped_data_df = pd.DataFrame(grouped_data)
        #统一日期列
        grouped_data_df["日期"] = pd.to_datetime(grouped_data_df["date"]).dt.date

        # 获取融资融券历史数据
        data = rzrq.get_rzrq_history(start_date=start_date, end_date=end_date, page=page, page_size=page_size, use_chinese_fields=True)
        rzrq_df = pd.DataFrame(data.get('result', {}).get('data', []))
        if not rzrq_df.empty:
            # 把日期列转换为日期格式
            rzrq_df["日期"] = pd.to_datetime(rzrq_df["交易日期"]).dt.date

        # 把grouped_data_df和rzrq_df按照日期列进行合并
        result_df = pd.merge(grouped_data_df, rzrq_df, on="日期", how="left")
        result_df["上证指数"] = szzs_df["close"]

        # 按照日期计算融资融券成交比例
        rzrq_turnover_ratio = (result_df["总融资买入额"] + result_df["总融券余额"]) / result_df["turnover"] * 100

        # 融资融券额额与上证指数偏离率
        rzrq_szzs_ratio =  (result_df["总融资买入额"] + result_df["总融券余额"]) / 100000000 / result_df["上证指数"] * 100

        rzrq_turnover_df = pd.DataFrame(rzrq_turnover_ratio, columns=["融资融券成交比例"])
        rzrq_turnover_df["总融资余额与上证指数偏离率"] = rzrq_szzs_ratio
        rzrq_turnover_df.index = result_df["日期"]
        rzrq_turnover_df.reset_index(inplace=True)
        return rzrq_turnover_df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取融资融券成交比例数据失败: {str(e)}")
        traceback.print_exc()
        return {}

@mcp.tool()
async def get_usd_index_data() -> list:
    """ 获取美元指数实时数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含美元指数的实时数据，
    Dict包含字段:  ['代码', '名称', '涨幅', '最新', '最高', '最低', '今开', '换手率', '量比', '市盈率', '成交量', '成交额', '昨收', '总市值', '流通市值', '市场', '时间']
    """
    
    # 使用qstock获取美元指数实时数据
    try:
        # 使用美股市场获取美元指数数据
        df = qs.realtime_data(market="美股", code="美元指数")
        if not df.empty:
            logger.info(f"美元指数数据获取成功: {df.shape[0]} 条记录")
            logger.info(f"美元指数数据列名: {df.columns.tolist()}")
            return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取美元指数实时数据失败: {str(e)}")
        traceback.print_exc()
    return []

@mcp.tool()
async def get_ftse_a50_futures_data() -> list:
    """ 获取富时A50期货指数实时数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含富时A50期货指数的实时数据，
    Dict包含字段: ['代码', '名称', '涨幅', '最新', '最高', '最低', '今开', '成交量', '成交额', '昨收', '持仓量', '市场', '时间']
    """
    # 使用qstock获取富时A50期货指数实时数据
    try:
        df = qs.realtime_data(market="期货", code="富时A50期指主连")
        if not df.empty:    
            logger.info(f"富时A50期货指数数据获取成功: {df.shape[0]} 条记录")
            logger.info(f"富时A50期货指数数据列名: {df.columns.tolist()}")
            return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取富时A50期货指数实时数据失败: {str(e)}")
        traceback.print_exc()
    return []

@mcp.tool()
async def get_usd_cnh_futures_data() -> list:
    """ 获取美元兑离岸人民币主连实时数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含美元兑离岸人民币主连的实时数据，
    Dict包含字段: ['代码', '名称', '涨幅', '最新', '最高', '最低', '今开', '成交量', '成交额', '昨收', '持仓量', '市场', '时间']
    """
    # 使用qstock获取美元兑离岸人民币主连实时数据
    try:
        df = qs.realtime_data(market="期货", code="美元兑离岸人民币")
        if not df.empty:             
            logger.info(f"美元兑离岸人民币主连数据获取成功: {df.shape[0]} 条记录")
            logger.info(f"美元兑离岸人民币主连数据列名: {df.columns.tolist()}")
            return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取美元兑离岸人民币主连实时数据失败: {str(e)}")
        traceback.print_exc()
    return []

@mcp.tool()
async def get_thirty_year_bond_futures_data() -> list:
    """ 获取三十年国债主连实时数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含三十年国债主连的实时数据，
    Dict包含字段: ['代码', '名称', '涨幅', '最新', '最高', '最低', '今开', '成交量', '成交额', '昨收', '持仓量', '市场', '时间']
    """
    # 使用qstock获取三十年国债主连实时数据
    try:
        df = qs.realtime_data(market="期货", code="三十年国债主连")
        if not df.empty:         
            logger.info(f"三十年国债主连数据获取成功: {df.shape[0]} 条记录")
            logger.info(f"三十年国债主连数据列名: {df.columns.tolist()}")
            return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取三十年国债主连实时数据失败: {str(e)}")
        traceback.print_exc()
    return []

@mcp.tool()
async def get_economic_calendar(start_date: str = None, end_date: str = None, country: str = None) -> List[Dict]:
    """ 获取未来7天的全球经济报告日历
    参数：
    - start_date: 开始日期，格式为'YYYY-MM-DD'，默认为None（表示当前日期）
    - end_date: 结束日期，格式为'YYYY-MM-DD'，默认为None（表示当前日期+7天）
    - country: 国家代码，默认为None（表示所有国家）
    返回：
    - List[Dict]: 包含经济日历数据的字典列表，
    Dict包含字段: ['序号', '公布日', '时间', '国家/地区', '事件', '报告期', '公布值', '预测值', '前值', '重要性', '趋势']
    """
    try:
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        url = f"https://forex.eastmoney.com/fc.html?Date={start_date},{end_date}&country={country if country else ''}"
        response = requests.get(url)
        response.raise_for_status()
        
        doc = pq(response.text)
        events = []
        
        for row in doc('.dataList tr').items():
            if row.attr('class') == 'title':
                continue
            
            seq = row('td:nth-child(1)').text()
            date = row('td:nth-child(2)').text()
            time = row('td:nth-child(3)').text()
            country_name = row('td:nth-child(4)').text()
            event = row('td:nth-child(5)').text()
            report_period = row('td:nth-child(6)').text()
            actual = row('td:nth-child(7)').text()
            forecast = row('td:nth-child(8)').text()
            previous = row('td:nth-child(9)').text()
            importance = row('td:nth-child(10)').text()
            trend = row('td:nth-child(11)').text()

            if not seq:
                # 无数据忽略
                continue
            
            events.append({
                '序号': seq,
                '公布日': date,
                '时间': time,
                '国家/地区': country_name,
                '事件': event,
                '报告期': report_period,
                '公布值': actual,
                '预测值': forecast,
                '前值': previous,
                '重要性': importance,
                '趋势': trend
            })
        
        return events
    except Exception as e:
        logger.error(f"获取经济日历数据失败: {str(e)}")
        traceback.print_exc()
        return []