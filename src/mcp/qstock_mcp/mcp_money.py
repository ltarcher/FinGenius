# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
资金流向数据MCP工具接口
提供个股资金流向、北向资金流向和同花顺资金流向数据的MCP工具接口
"""

import pandas as pd
from typing import Dict, List, Optional, Union
import logging
import traceback
from mcp_instance import mcp
from qstock.data import money  # 直接导入money模块

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
async def get_intraday_money(
    code: str
) -> List[Dict]:
    """
    获取单只股票最新交易日的日内分钟级单子流入流出数据
    
    参数:
        code: 股票代码，如"000001"、"600000"等
        
    返回:
        List[Dict]: 包含股票日内资金流向数据的字典列表
        
    示例:
        data = await get_intraday_money('000001')
    """
    try:
        logger.info(f"获取股票日内资金流向数据，股票代码: {code}")
        df = money.intraday_money(code=code)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将时间列转换为字符串格式
        if '时间' in df.columns:
            df['时间'] = df['时间'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取股票日内资金流向数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_hist_money(
    code: str
) -> List[Dict]:
    """
    获取单支股票、债券的历史单子流入流出数据
    
    参数:
        code: 股票代码，如"000001"、"600000"等
        
    返回:
        List[Dict]: 包含股票历史资金流向数据的字典列表
        
    示例:
        data = await get_hist_money('000001')
    """
    try:
        logger.info(f"获取股票历史资金流向数据，股票代码: {code}")
        df = money.hist_money(code=code)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将日期列转换为字符串格式
        if '日期' in df.columns:
            df['日期'] = df['日期'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取股票历史资金流向数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_money(
    code: str,
    ndays: Union[int, List[int]] = [3, 5, 10, 20]
) -> List[Dict]:
    """
    获取个股n日资金流
    
    参数:
        code: 股票代码或名称，如"000001"、"600000"等
        ndays: 时间周期，可以是单个整数或整数列表，如3、5、10、20等，默认为[3, 5, 10, 20]
        
    返回:
        List[Dict]: 包含个股n日资金流数据的字典列表
        
    示例:
        data = await get_stock_money('000001', [3, 5, 10])
    """
    try:
        logger.info(f"获取个股n日资金流数据，股票代码: {code}, 时间周期: {ndays}")
        df = money.stock_money(code=code, ndays=ndays)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 重置索引，将日期列转换为字符串
        df = df.reset_index()
        if 'index' in df.columns:
            df['index'] = df['index'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取个股n日资金流数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_north_money(
    flag: Optional[str] = None,
    n: Union[int, str] = 1
) -> Union[List[Dict], Dict]:
    """
    获取北向资金流向数据
    
    参数:
        flag: 数据类型，可选值:
             None: 返回北上资金总体每日净流入数据
             '行业': 北向资金增持行业板块排行
             '概念': 北向资金增持概念板块排行
             '地域': 北向资金增持地域板块排行
             '个股': 北向资金增持个股情况
             '沪股通': 沪股通资金流向
             '深股通': 深股通资金流向
        n: 代表n日排名，可选值:
           1, 3, 5, 10, 'M', 'Q', 'Y'
           即 {'1':"今日", '3':"3日",'5':"5日", '10':"10日",'M':"月", 'Q':"季", 'Y':"年"}
        
    返回:
        List[Dict]或Dict: 包含北向资金流向数据的字典列表或字典
        
    示例:
        data = await get_north_money('行业', 5)
    """
    try:
        logger.info(f"获取北向资金流向数据，类型: {flag}, 周期: {n}")
        result = money.north_money(flag=flag, n=n)
        
        if isinstance(result, pd.DataFrame):
            if result.empty:
                logger.warning("返回数据为空")
                return []
                
            # 处理日期列
            date_cols = ['日期', 'date']
            for col in date_cols:
                if col in result.columns:
                    result[col] = result[col].astype(str)
                    
            return result.to_dict(orient='records')
        elif isinstance(result, pd.Series):
            # 如果返回的是Series，转换为字典
            result = result.to_dict()
            return result
        else:
            return result
    except Exception as e:
        logger.error(f"获取北向资金流向数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_north_money_flow(
    flag: str = "北上"
) -> List[Dict]:
    """
    获取东方财富网沪深港通持股-北向资金净流入
    
    参数:
        flag: 资金流向类型，可选值:
             "沪股通": 沪股通资金流向
             "深股通": 深股通资金流向
             "北上": 北上资金总体流向（默认）
        
    返回:
        List[Dict]: 包含北向资金净流入数据的字典列表
        
    示例:
        data = await get_north_money_flow('沪股通')
    """
    try:
        logger.info(f"获取北向资金净流入数据，类型: {flag}")
        df = money.north_money_flow(flag=flag)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将日期列转换为字符串格式
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取北向资金净流入数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_north_money_stock(
    n: Union[int, str] = 1
) -> List[Dict]:
    """
    获取东方财富北向资金增减持个股情况
    
    参数:
        n: 代表n日排名，可选值:
           1, 3, 5, 10, 'M', 'Q', 'Y'
           即 {'1':"今日", '3':"3日",'5':"5日", '10':"10日",'M':"月", 'Q':"季", 'Y':"年"}
        
    返回:
        List[Dict]: 包含北向资金增减持个股情况数据的字典列表
        
    示例:
        data = await get_north_money_stock(5)
    """
    try:
        logger.info(f"获取北向资金增减持个股情况数据，周期: {n}")
        df = money.north_money_stock(n=n)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将日期列转换为字符串格式
        if '日期' in df.columns:
            df['日期'] = df['日期'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取北向资金增减持个股情况数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_north_money_sector(
    flag: str = "行业",
    n: Union[int, str] = 1
) -> List[Dict]:
    """
    获取东方财富网北向资金增持板块排行
    
    参数:
        flag: 板块类型，可选值:
             "行业": 行业板块（默认）
             "概念": 概念板块
             "地域": 地域板块
        n: 代表n日排名，可选值:
           1, 3, 5, 10, 'M', 'Q', 'Y'
           即 {'1':"今日", '3':"3日",'5':"5日", '10':"10日",'M':"月", 'Q':"季", 'Y':"年"}
        
    返回:
        List[Dict]: 包含北向资金增持板块排行数据的字典列表
        
    示例:
        data = await get_north_money_sector('概念', 5)
    """
    try:
        logger.info(f"获取北向资金增持板块排行数据，板块类型: {flag}, 周期: {n}")
        df = money.north_money_sector(flag=flag, n=n)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将日期列转换为字符串格式
        if '日期' in df.columns:
            df['日期'] = df['日期'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取北向资金增持板块排行数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_money(
    flag: Optional[str] = None,
    n: Optional[int] = None
) -> List[Dict]:
    """
    获取同花顺个股、行业、概念资金流数据
    
    参数:
        flag: 数据类型，可选值:
             None: 默认获取个股资金流数据
             '个股': 获取个股资金流数据
             '概念'或'概念板块': 获取概念板块资金流数据
             '行业'或'行业板块': 获取行业板块资金流数据
        n: 时间周期，可选值:
           None, 3, 5, 10, 20
           分别表示"即时", "3日排行", "5日排行", "10日排行", "20日排行"
        
    返回:
        List[Dict]: 包含同花顺资金流数据的字典列表
        
    示例:
        data = await get_ths_money('概念', 5)
    """
    try:
        logger.info(f"获取同花顺资金流数据，类型: {flag}, 周期: {n}")
        df = money.ths_money(flag=flag, n=n)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺资金流数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_stock_money(
    n: Optional[int] = None
) -> List[Dict]:
    """
    获取同花顺个股资金流向
    
    参数:
        n: 时间周期，可选值:
           None, 3, 5, 10, 20
           分别表示"即时", "3日排行", "5日排行", "10日排行", "20日排行"
        
    返回:
        List[Dict]: 包含同花顺个股资金流向数据的字典列表
        
    示例:
        data = await get_ths_stock_money(5)
    """
    try:
        logger.info(f"获取同花顺个股资金流向数据，周期: {n}")
        df = money.ths_stock_money(n=n)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺个股资金流向数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_concept_money(
    n: Optional[int] = None
) -> List[Dict]:
    """
    获取同花顺概念板块资金流
    
    参数:
        n: 时间周期，可选值:
           None, 3, 5, 10, 20
           分别表示"即时", "3日排行", "5日排行", "10日排行", "20日排行"
        
    返回:
        List[Dict]: 包含同花顺概念板块资金流数据的字典列表
        
    示例:
        data = await get_ths_concept_money(5)
    """
    try:
        logger.info(f"获取同花顺概念板块资金流数据，周期: {n}")
        df = money.ths_concept_money(n=n)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺概念板块资金流数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_industry_money(
    n: Optional[int] = None
) -> List[Dict]:
    """
    获取同花顺行业资金流
    
    参数:
        n: 时间周期，可选值:
           None, 3, 5, 10, 20
           分别表示"即时", "3日排行", "5日排行", "10日排行", "20日排行"
        
    返回:
        List[Dict]: 包含同花顺行业资金流数据的字典列表
        
    示例:
        data = await get_ths_industry_money(5)
    """
    try:
        logger.info(f"获取同花顺行业资金流数据，周期: {n}")
        df = money.ths_industry_money(n=n)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺行业资金流数据失败: {str(e)}")
        traceback.print_exc()
        return []