# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
新闻资讯数据MCP工具接口
提供新闻资讯数据的MCP工具接口
"""

import pandas as pd
from typing import Dict, List, Optional, Union
import logging
import traceback
from mcp_instance import mcp
from qstock.data.news import news_data, news_cls, news_cctv, news_js, stock_news

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
async def get_cls_news() -> List[Dict]:
    """
    获取财联社电报新闻数据
    
    返回:
        List[Dict]: 包含财联社电报新闻数据的字典列表
        
    示例:
        data = await get_cls_news()
    """
    try:
        logger.info("获取财联社电报新闻数据")
        df = news_cls()
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将日期列转换为字符串格式
        if '发布日期' in df.columns:
            df['发布日期'] = df['发布日期'].astype(str)
        
        # 将时间列转换为字符串格式
        if '发布时间' in df.columns:
            df['发布时间'] = df['发布时间'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取财联社电报新闻数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_cctv_news(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """
    获取新闻联播文字稿数据
    
    参数:
        start_date: 开始日期，格式为"YYYYMMDD"，如"20230101"，默认为当前日期
        end_date: 结束日期，格式为"YYYYMMDD"，如"20231231"，默认为当前日期
        
    返回:
        List[Dict]: 包含新闻联播文字稿数据的字典列表
        
    示例:
        data = await get_cctv_news('20230101', '20230110')
    """
    try:
        logger.info(f"获取新闻联播文字稿数据，开始日期: {start_date}, 结束日期: {end_date}")
        df = news_cctv(start=start_date, end=end_date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将日期列转换为字符串格式
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取新闻联播文字稿数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_js_financial_news(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """
    获取金十数据-市场快讯数据
    
    参数:
        start_date: 开始日期，格式为"YYYYMMDD"，如"20230101"，默认为当前日期
        end_date: 结束日期，格式为"YYYYMMDD"，如"20231231"，默认为当前日期
        
    返回:
        List[Dict]: 包含金十数据-市场快讯数据的字典列表
        
    示例:
        data = await get_js_financial_news('20230101', '20230110')
    """
    try:
        logger.info(f"获取金十数据-市场快讯数据，开始日期: {start_date}, 结束日期: {end_date}")
        df = news_js(start=start_date, end=end_date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将datetime列转换为字符串格式
        if 'datetime' in df.columns:
            df['datetime'] = df['datetime'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取金十数据-市场快讯数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_news(
    code: str
) -> List[Dict]:
    """
    获取东方财富-个股新闻数据
    
    参数:
        code: 股票代码，如"000001"、"600000"等
        
    返回:
        List[Dict]: 包含个股新闻数据的字典列表
        
    示例:
        data = await get_stock_news('000001')
    """
    try:
        logger.info(f"获取个股新闻数据，股票代码: {code}")
        df = stock_news(stock=code)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将日期列转换为字符串格式
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取个股新闻数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_news_data(
    news_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    code: Optional[str] = None
) -> List[Dict]:
    """
    获取新闻资讯数据（综合接口）
    
    参数:
        news_type: 新闻类型，可选值:
                  'cctv'或'新闻联播': 获取新闻联播文字稿
                  'js'或'金十数据': 获取金十数据-市场快讯
                  'stock'或'个股新闻'或'个股': 获取个股新闻（需要提供code参数）
                  不提供或为None: 获取财联社电报新闻
        start_date: 开始日期，格式为"YYYYMMDD"，如"20230101"
        end_date: 结束日期，格式为"YYYYMMDD"，如"20231231"
        code: 股票代码，当news_type为'stock'或'个股新闻'或'个股'时需要提供
        
    返回:
        List[Dict]: 包含新闻资讯数据的字典列表
        
    示例:
        data = await get_news_data('cctv', '20230101', '20230110')
        data = await get_news_data('js', '20230101', '20230110')
        data = await get_news_data('stock', code='000001')
        data = await get_news_data()  # 获取财联社电报新闻
    """
    try:
        logger.info(f"获取新闻资讯数据，类型: {news_type}, 开始日期: {start_date}, 结束日期: {end_date}, 股票代码: {code}")
        
        df = news_data(news_type=news_type, start=start_date, end=end_date, code=code)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
        
        # 处理日期和时间列，确保可以序列化为JSON
        date_columns = ['日期', '发布日期', 'date', 'datetime']
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # 处理时间列
        time_columns = ['发布时间', 'time']
        for col in time_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取新闻资讯数据失败: {str(e)}")
        traceback.print_exc()
        return []