# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
行业板块数据MCP工具接口
提供同花顺行业板块和概念板块数据的MCP工具接口
"""

import pandas as pd
from typing import Dict, List, Optional, Union
import logging
import traceback
from mcp_instance import mcp
from qstock.data import industry  # 直接导入industry模块

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
async def get_ths_index_name(
    flag: str = '概念'
) -> List[str]:
    """
    获取同花顺概念或行业板块名称
    
    参数:
        flag: 板块类型，可选值:
             '概念'或'概念板块': 获取概念板块名称
             '行业'或'行业板块': 获取行业板块名称
            
    返回:
        List[str]: 包含板块名称的列表
        
    示例:
        data = await get_ths_index_name('概念')
    """
    try:
        logger.info(f"获取同花顺{flag}板块名称")
        names = industry.ths_index_name(flag=flag)
        
        if not names:
            logger.warning("返回数据为空")
            return []
            
        return names
    except Exception as e:
        logger.error(f"获取同花顺{flag}板块名称失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_index_member(
    code: str
) -> List[Dict]:
    """
    获取同花顺概念或行业板块成份股
    
    参数:
        code: 板块代码或名称，如"机器人"、"半导体及元件"、"881101"等
        
    返回:
        List[Dict]: 包含成份股数据的字典列表
        
    示例:
        data = await get_ths_index_member('机器人')
    """
    try:
        logger.info(f"获取同花顺板块成份股，板块: {code}")
        df = industry.ths_index_member(code=code)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺板块成份股失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_index_price(
    flag: str = '概念'
) -> List[Dict]:
    """
    获取同花顺指数数据
    
    参数:
        flag: 板块类型，可选值:
             '概念'或'概念板块': 获取概念板块指数数据
             '行业'或'行业板块': 获取行业板块指数数据
            
    返回:
        List[Dict]: 包含指数数据的字典列表
        
    示例:
        data = await get_ths_index_price('概念')
    """
    try:
        logger.info(f"获取同花顺{flag}指数数据")
        df = industry.ths_index_price(flag=flag)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 重置索引，将日期列转换为字符串
        df = df.reset_index()
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺{flag}指数数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_index_data(
    code: str
) -> List[Dict]:
    """
    获取同花顺概念或行业板块指数行情数据
    
    参数:
        code: 板块代码或名称，如"机器人"、"半导体及元件"、"881101"等
        
    返回:
        List[Dict]: 包含指数行情数据的字典列表
        
    示例:
        data = await get_ths_index_data('机器人')
    """
    try:
        logger.info(f"获取同花顺板块指数行情数据，板块: {code}")
        df = industry.ths_index_data(code=code)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 重置索引，将日期列转换为字符串
        df = df.reset_index()
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺板块指数行情数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_industry_member(
    code: str = "机器人"
) -> List[Dict]:
    """
    获取同花顺行业板块的成份股
    
    参数:
        code: 行业板块代码或名称，如"机器人"、"半导体及元件"、"881101"等
        
    返回:
        List[Dict]: 包含行业板块成份股数据的字典列表
        
    示例:
        data = await get_ths_industry_member('机器人')
    """
    try:
        logger.info(f"获取同花顺行业板块成份股，行业: {code}")
        df = industry.ths_industry_member(code=code)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺行业板块成份股失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_industry_data(
    code: str = "半导体及元件",
    start: str = "20200101",
    end: Optional[str] = None
) -> List[Dict]:
    """
    获取同花顺行业板块指数数据
    
    参数:
        code: 行业板块代码或名称，如"半导体及元件"、"881101"等
        start: 开始日期，格式为"YYYYMMDD"，如"20200101"
        end: 结束日期，格式为"YYYYMMDD"，如"20231231"，默认为None（取到最新数据）
        
    返回:
        List[Dict]: 包含行业板块指数数据的字典列表
        
    示例:
        data = await get_ths_industry_data('半导体及元件', '20200101', '20231231')
    """
    try:
        logger.info(f"获取同花顺行业板块指数数据，行业: {code}, 开始日期: {start}, 结束日期: {end}")
        df = industry.ths_industry_data(code=code, start=start, end=end)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 重置索引，将日期列转换为字符串
        df = df.reset_index()
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺行业板块指数数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_concept_name() -> List[str]:
    """
    获取同花顺概念板块-概念名称
    
    返回:
        List[str]: 包含概念板块名称的列表
        
    示例:
        data = await get_ths_concept_name()
    """
    try:
        logger.info("获取同花顺概念板块名称")
        names = industry.ths_concept_name()
        
        if not names:
            logger.warning("返回数据为空")
            return []
            
        return names
    except Exception as e:
        logger.error(f"获取同花顺概念板块名称失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_concept_code() -> Dict[str, str]:
    """
    获取同花顺概念板块-概念代码
    
    返回:
        Dict[str, str]: 包含概念板块名称和代码的字典，键为名称，值为代码
        
    示例:
        data = await get_ths_concept_code()
    """
    try:
        logger.info("获取同花顺概念板块代码")
        code_dict = industry.ths_concept_code()
        
        if not code_dict:
            logger.warning("返回数据为空")
            return {}
            
        return code_dict
    except Exception as e:
        logger.error(f"获取同花顺概念板块代码失败: {str(e)}")
        traceback.print_exc()
        return {}

@mcp.tool()
async def get_ths_concept_member(
    code: str = "阿里巴巴概念"
) -> List[Dict]:
    """
    获取同花顺概念板块成份股
    
    参数:
        code: 概念板块代码或名称，如"阿里巴巴概念"等
        
    返回:
        List[Dict]: 包含概念板块成份股数据的字典列表
        
    示例:
        data = await get_ths_concept_member('阿里巴巴概念')
    """
    try:
        logger.info(f"获取同花顺概念板块成份股，概念: {code}")
        df = industry.ths_concept_member(code=code)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺概念板块成份股失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_concept_data(
    code: str = '白酒概念',
    start: str = "2020"
) -> List[Dict]:
    """
    获取同花顺概念板块指数数据
    
    参数:
        code: 概念板块代码或名称，如"白酒概念"等
        start: 开始年份，如"2020"
        
    返回:
        List[Dict]: 包含概念板块指数数据的字典列表
        
    示例:
        data = await get_ths_concept_data('白酒概念', '2020')
    """
    try:
        logger.info(f"获取同花顺概念板块指数数据，概念: {code}, 开始年份: {start}")
        df = industry.ths_concept_data(code=code, start=start)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 重置索引，将日期列转换为字符串
        df = df.reset_index()
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺概念板块指数数据失败: {str(e)}")
        traceback.print_exc()
        return []