# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
问财数据MCP工具接口
提供问财数据查询的MCP工具接口
"""

import pandas as pd
from typing import Dict, List, Optional, Union
import logging
import traceback
from mcp_instance import mcp
from qstock.data import wencai  # 导入wencai模块

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
async def query_wencai(
    question: str
) -> List[Dict]:
    """
    通过问财接口查询股票数据
    
    参数:
        question: 输入你要问的条件，不同条件使用"，"或"；"或空格，如'均线多头排列'
        
    返回:
        List[Dict]: 包含查询结果的字典列表
        
    示例:
        data = await query_wencai('均线多头排列')
    """
    try:
        logger.info(f"通过问财接口查询: {question}")
        df = wencai.wencai(question)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列，确保可以序列化为JSON
        for col in df.columns:
            if '日期' in col or '时间' in col:
                if col in df.columns:
                    df[col] = df[col].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"问财查询失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def query_stock_by_condition(
    condition: str
) -> List[Dict]:
    """
    根据条件筛选股票
    
    参数:
        condition: 筛选条件，如'涨跌幅>5%'、'市盈率<30'、'均线多头排列'等
        
    返回:
        List[Dict]: 包含符合条件的股票数据的字典列表
        
    示例:
        data = await query_stock_by_condition('涨跌幅>5%')
    """
    try:
        logger.info(f"根据条件筛选股票: {condition}")
        df = wencai.wencai(condition)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列，确保可以序列化为JSON
        for col in df.columns:
            if '日期' in col or '时间' in col:
                if col in df.columns:
                    df[col] = df[col].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"条件筛选股票失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def query_stock_by_technical_indicator(
    indicator: str
) -> List[Dict]:
    """
    根据技术指标筛选股票
    
    参数:
        indicator: 技术指标条件，如'MACD金叉'、'KDJ超买'、'布林带突破'等
        
    返回:
        List[Dict]: 包含符合技术指标条件的股票数据的字典列表
        
    示例:
        data = await query_stock_by_technical_indicator('MACD金叉')
    """
    try:
        logger.info(f"根据技术指标筛选股票: {indicator}")
        df = wencai.wencai(indicator)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列，确保可以序列化为JSON
        for col in df.columns:
            if '日期' in col or '时间' in col:
                if col in df.columns:
                    df[col] = df[col].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"技术指标筛选股票失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def query_stock_by_fundamental(
    fundamental: str
) -> List[Dict]:
    """
    根据基本面条件筛选股票
    
    参数:
        fundamental: 基本面条件，如'市盈率<30'、'净资产收益率>10%'、'营收增长率>20%'等
        
    返回:
        List[Dict]: 包含符合基本面条件的股票数据的字典列表
        
    示例:
        data = await query_stock_by_fundamental('市盈率<30')
    """
    try:
        logger.info(f"根据基本面条件筛选股票: {fundamental}")
        df = wencai.wencai(fundamental)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列，确保可以序列化为JSON
        for col in df.columns:
            if '日期' in col or '时间' in col:
                if col in df.columns:
                    df[col] = df[col].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"基本面条件筛选股票失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def query_stock_by_industry(
    industry: str
) -> List[Dict]:
    """
    根据行业筛选股票
    
    参数:
        industry: 行业名称，如'银行'、'半导体'、'新能源'等
        
    返回:
        List[Dict]: 包含指定行业的股票数据的字典列表
        
    示例:
        data = await query_stock_by_industry('半导体')
    """
    try:
        logger.info(f"根据行业筛选股票: {industry}")
        query = f"所属行业包含{industry}"
        df = wencai.wencai(query)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列，确保可以序列化为JSON
        for col in df.columns:
            if '日期' in col or '时间' in col:
                if col in df.columns:
                    df[col] = df[col].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"行业筛选股票失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def query_stock_by_concept(
    concept: str
) -> List[Dict]:
    """
    根据概念筛选股票
    
    参数:
        concept: 概念名称，如'人工智能'、'元宇宙'、'碳中和'等
        
    返回:
        List[Dict]: 包含指定概念的股票数据的字典列表
        
    示例:
        data = await query_stock_by_concept('人工智能')
    """
    try:
        logger.info(f"根据概念筛选股票: {concept}")
        query = f"所属概念包含{concept}"
        df = wencai.wencai(query)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列，确保可以序列化为JSON
        for col in df.columns:
            if '日期' in col or '时间' in col:
                if col in df.columns:
                    df[col] = df[col].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"概念筛选股票失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def query_stock_by_market_cap(
    condition: str
) -> List[Dict]:
    """
    根据市值条件筛选股票
    
    参数:
        condition: 市值条件，如'市值>100亿'、'市值<50亿'等
        
    返回:
        List[Dict]: 包含符合市值条件的股票数据的字典列表
        
    示例:
        data = await query_stock_by_market_cap('市值>100亿')
    """
    try:
        logger.info(f"根据市值条件筛选股票: {condition}")
        df = wencai.wencai(condition)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列，确保可以序列化为JSON
        for col in df.columns:
            if '日期' in col or '时间' in col:
                if col in df.columns:
                    df[col] = df[col].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"市值条件筛选股票失败: {str(e)}")
        traceback.print_exc()
        return []