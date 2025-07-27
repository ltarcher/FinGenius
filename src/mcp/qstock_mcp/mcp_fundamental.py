# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
基本面数据MCP工具接口
提供股票基本面数据的MCP工具接口
"""

import pandas as pd
from typing import Dict, List, Optional, Union
import logging
import traceback
from mcp_instance import mcp
from qstock.data import fundamental  # 直接导入fundamental模块

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
async def get_stock_holder(
    holder: Optional[str] = None,
    date: Optional[str] = None,
    code: Optional[str] = None,
    n: int = 2
) -> List[Dict]:
    """
    获取股东变动情况数据
    
    参数:
        holder: 股东类型：
               '实控人'或'1'：返回实控人持股变动情况
               '股东'或'2'：返回股东增减持情况
               None：返回全市场个股股东增减持情况或某指定个股前十大股票变化情况
        date: 日期，格式如'20220331'
        code: 股票代码或简称
        n: 获取最近n个季度的数据，默认为2
        
    返回:
        List[Dict]: 包含股东变动情况的字典列表
        
    示例:
        data = await get_stock_holder(code='000001')
        data = await get_stock_holder(holder='实控人')
    """
    try:
        logger.info(f"获取股东变动情况，类型: {holder}, 日期: {date}, 代码: {code}")
        df = fundamental.stock_holder(holder=holder, date=date, code=code, n=n)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列，确保可以序列化为JSON
        date_cols = ['日期', '变动日期', '截止日', '公告日', '开始日']
        for col in date_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取股东变动情况数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_holder_top10(
    code: str,
    n: int = 2
) -> List[Dict]:
    """
    获取沪深市场指定股票前十大股东信息
    
    参数:
        code: 股票代码或简称
        n: 最新n个季度前10大流通股东公开信息，默认为2
        
    返回:
        List[Dict]: 包含前十大股东信息的字典列表
        
    示例:
        data = await get_stock_holder_top10('000001')
    """
    try:
        logger.info(f"获取股票 {code} 的前十大股东信息")
        df = fundamental.stock_holder_top10(code=code, n=n)
        
        if df.empty:
            logger.warning(f"获取的股票 {code} 前十大股东信息为空")
            return []
            
        # 处理日期列
        if '日期' in df.columns:
            df['日期'] = df['日期'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取股票 {code} 的前十大股东信息失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_holder_num(
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取沪深A股市场公开的股东数目变化情况
    
    参数:
        date: 报告期日期，格式如'20220331'或'2022-03-31'，默认为最新报告期
        
    返回:
        List[Dict]: 包含股东数目变化情况的字典列表
        
    示例:
        data = await get_stock_holder_num('20220331')
    """
    try:
        logger.info(f"获取股东数目变化情况，日期: {date}")
        df = fundamental.stock_holder_num(date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取股东数目变化情况失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_holder_con() -> List[Dict]:
    """
    获取实际控制人持股变动数据
    
    返回:
        List[Dict]: 包含实际控制人持股变动数据的字典列表
        
    示例:
        data = await get_stock_holder_con()
    """
    try:
        logger.info("获取实际控制人持股变动数据")
        df = fundamental.stock_holder_con()
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列
        if '变动日期' in df.columns:
            df['变动日期'] = df['变动日期'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取实际控制人持股变动数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_holder_change() -> List[Dict]:
    """
    获取大股东增减持变动明细
    
    返回:
        List[Dict]: 包含大股东增减持变动明细的字典列表
        
    示例:
        data = await get_stock_holder_change()
    """
    try:
        logger.info("获取大股东增减持变动明细")
        df = fundamental.stock_holder_change()
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列
        date_cols = ['开始日', '截止日', '公告日']
        for col in date_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取大股东增减持变动明细失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_institute_hold(
    quarter: str = "20221"
) -> List[Dict]:
    """
    获取机构持股一览表
    
    参数:
        quarter: 季度，如'20221'表示2022年一季度，'20193'表示2019年三季度
        
    返回:
        List[Dict]: 包含机构持股数据的字典列表
        
    示例:
        data = await get_institute_hold('20221')
    """
    try:
        logger.info(f"获取机构持股一览表，季度: {quarter}")
        df = fundamental.institute_hold(quarter=quarter)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取机构持股一览表失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_main_business(
    code: str
) -> List[Dict]:
    """
    获取公司主营业务构成
    
    参数:
        code: 股票代码或简称
        
    返回:
        List[Dict]: 包含公司主营业务构成的字典列表
        
    示例:
        data = await get_main_business('000001')
    """
    try:
        logger.info(f"获取公司 {code} 的主营业务构成")
        df = fundamental.main_business(code=code)
        
        if df.empty:
            logger.warning(f"获取的公司 {code} 主营业务构成为空")
            return []
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取公司 {code} 的主营业务构成失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_financial_statement(
    flag: str = '业绩报表',
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取财务报表和业绩指标
    
    参数:
        flag: 报表类型，可选值:
             '业绩报表'或'yjbb'：返回年报季报财务指标
             '业绩快报'或'yjkb'：返回市场最新业绩快报
             '业绩预告'或'yjyg'：返回市场最新业绩预告
             '资产负债表'或'zcfz'：返回最新资产负债指标
             '利润表'或'lrb'：返回最新利润表指标
             '现金流量表'或'xjll'：返回最新现金流量表指标
        date: 报表日期，如'20220630'，默认当前最新季报
        
    返回:
        List[Dict]: 包含财务报表数据的字典列表
        
    示例:
        data = await get_financial_statement('利润表', '20220331')
    """
    try:
        logger.info(f"获取财务报表，类型: {flag}, 日期: {date}")
        df = fundamental.financial_statement(flag=flag, date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列
        date_cols = ['公告日', '日期']
        for col in date_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取财务报表失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_balance_sheet(
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取资产负债表数据
    
    参数:
        date: 报表日期，如'20220630'，默认当前最新季报
        
    返回:
        List[Dict]: 包含资产负债表数据的字典列表
        
    示例:
        data = await get_balance_sheet('20220331')
    """
    try:
        logger.info(f"获取资产负债表，日期: {date}")
        df = fundamental.balance_sheet(date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列
        if '公告日' in df.columns:
            df['公告日'] = df['公告日'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取资产负债表失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_income_statement(
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取利润表数据
    
    参数:
        date: 报表日期，如'20220630'，默认当前最新季报
        
    返回:
        List[Dict]: 包含利润表数据的字典列表
        
    示例:
        data = await get_income_statement('20220331')
    """
    try:
        logger.info(f"获取利润表，日期: {date}")
        df = fundamental.income_statement(date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列
        if '公告日' in df.columns:
            df['公告日'] = df['公告日'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取利润表失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_cashflow_statement(
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取现金流量表数据
    
    参数:
        date: 报表日期，如'20220630'，默认当前最新季报
        
    返回:
        List[Dict]: 包含现金流量表数据的字典列表
        
    示例:
        data = await get_cashflow_statement('20220331')
    """
    try:
        logger.info(f"获取现金流量表，日期: {date}")
        df = fundamental.cashflow_statement(date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列
        if '公告日' in df.columns:
            df['公告日'] = df['公告日'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取现金流量表失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_yjkb(
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取业绩快报数据
    
    参数:
        date: 报表日期，如'20220630'，默认当前最新季报
        
    返回:
        List[Dict]: 包含业绩快报数据的字典列表
        
    示例:
        data = await get_stock_yjkb('20220331')
    """
    try:
        logger.info(f"获取业绩快报，日期: {date}")
        df = fundamental.stock_yjkb(date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列
        if '公告日' in df.columns:
            df['公告日'] = df['公告日'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取业绩快报失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_yjyg(
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取业绩预告数据
    
    参数:
        date: 报表日期，如'20220630'，默认当前最新季报
        
    返回:
        List[Dict]: 包含业绩预告数据的字典列表
        
    示例:
        data = await get_stock_yjyg('20220331')
    """
    try:
        logger.info(f"获取业绩预告，日期: {date}")
        df = fundamental.stock_yjyg(date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列
        if '公告日' in df.columns:
            df['公告日'] = df['公告日'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取业绩预告失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_yjbb(
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取业绩报表数据
    
    参数:
        date: 报表日期，如'20220630'，默认当前最新季报
        
    返回:
        List[Dict]: 包含业绩报表数据的字典列表
        
    示例:
        data = await get_stock_yjbb('20220331')
    """
    try:
        logger.info(f"获取业绩报表，日期: {date}")
        df = fundamental.stock_yjbb(date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 处理日期列
        if '最新公告日' in df.columns:
            df['最新公告日'] = df['最新公告日'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取业绩报表失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_indicator(
    code: str
) -> List[Dict]:
    """
    获取个股历史报告期所有财务分析指标
    
    参数:
        code: 股票代码或简称
        
    返回:
        List[Dict]: 包含个股财务分析指标的字典列表
        
    示例:
        data = await get_stock_indicator('000001')
    """
    try:
        logger.info(f"获取股票 {code} 的财务分析指标")
        df = fundamental.stock_indicator(code=code)
        
        if df.empty:
            logger.warning(f"获取的股票 {code} 财务分析指标为空")
            return []
            
        # 处理日期列
        if '日期' in df.columns:
            df['日期'] = df['日期'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取股票 {code} 的财务分析指标失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_eps_forecast() -> List[Dict]:
    """
    获取上市公司机构研报评级和每股收益预测
    
    返回:
        List[Dict]: 包含机构研报评级和每股收益预测的字典列表
        
    示例:
        data = await get_eps_forecast()
    """
    try:
        logger.info("获取机构研报评级和每股收益预测")
        df = fundamental.eps_forecast()
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取机构研报评级和每股收益预测失败: {str(e)}")
        traceback.print_exc()
        return []