# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
同花顺股票池MCP工具接口
提供同花顺和东方财富网股票池的MCP工具接口
"""

import pandas as pd
from typing import Dict, List, Optional, Union
import logging
import traceback
from mcp_instance import mcp
from qstock.stock.ths_em_pool import (
    ths_pool, limit_pool, stock_zt_pool, stock_dt_pool, 
    stock_strong_pool, ths_break_price, ths_up_down, 
    ths_vol_change, ths_break_ma, ths_price_vol, ths_xzjp
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
async def get_ths_pool(
    ta: Optional[str] = None
) -> List[Dict]:
    """
    获取同花顺股票池数据
    
    参数:
        ta: 技术形态选股类型，可选值:
            - "创月新高", "半年新高", "一年新高", "历史新高"
            - "创月新低", "半年新低", "一年新低", "历史新低"
            - "险资举牌"
            - "连续上涨", "连续下跌"
            - "持续放量", "持续缩量"
            - "量价齐升", "量价齐跌"
            - "强势股"
            - "u10", "u20", "u30", "u60", "u90", "u250", "u500" (向上突破n日均线)
            - "d10", "d20", "d30", "d60", "d90", "d250", "d500" (跌破n日均线)
            
    返回:
        List[Dict]: 包含股票池数据的字典列表
        
    示例:
        data = await get_ths_pool("创月新高")
    """
    try:
        logger.info(f"获取同花顺股票池数据，技术形态: {ta}")
        df = ths_pool(ta=ta)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺股票池数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_limit_pool(
    flag: str = 'u',
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取东方财富网涨停（跌停）板股票池
    
    参数:
        flag: 类型标志，可选值:
              'u'或'up'或'涨停': 涨停板
              'd'或'down'或'跌停': 跌停板
              's'或'strong'或'强势': 强势股
        date: 日期，格式为'YYYYMMDD'，如'20220916'，默认为最新交易日
            
    返回:
        List[Dict]: 包含涨停/跌停/强势股数据的字典列表
        
    示例:
        data = await get_limit_pool('u', '20230101')
    """
    try:
        logger.info(f"获取东方财富网股票池数据，类型: {flag}, 日期: {date}")
        df = limit_pool(flag=flag, date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取东方财富网股票池数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_zt_pool(
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取东方财富网涨停板行情
    
    参数:
        date: 日期，格式为'YYYYMMDD'，如'20220916'，默认为最新交易日
            
    返回:
        List[Dict]: 包含涨停板行情数据的字典列表，包含字段:
                   ['代码', '名称', '涨跌幅', '最新价', '换手率', '成交额(百万)', '流通市值(百万)',
                   '总市值(百万)', '封板资金(百万)', '首次封板时间', '最后封板时间', '炸板次数',
                   '涨停统计', '连板数', '所属行业']
        
    示例:
        data = await get_stock_zt_pool('20230101')
    """
    try:
        logger.info(f"获取东方财富网涨停板行情，日期: {date}")
        df = stock_zt_pool(date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取东方财富网涨停板行情失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_dt_pool(
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取东方财富网跌停股池
    
    参数:
        date: 日期，格式为'YYYYMMDD'，如'20220916'，默认为最新交易日
            
    返回:
        List[Dict]: 包含跌停股池数据的字典列表，包含字段:
                   ['代码', '名称', '涨跌幅', '最新价', '换手率', '最后封板时间',
                   '连续跌停', '开板次数', '所属行业', '成交额(百万)', '封板资金(百万)', '流通市值(百万)',
                   '总市值(百万)']
        
    示例:
        data = await get_stock_dt_pool('20230101')
    """
    try:
        logger.info(f"获取东方财富网跌停股池，日期: {date}")
        df = stock_dt_pool(date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取东方财富网跌停股池失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_strong_pool(
    date: Optional[str] = None
) -> List[Dict]:
    """
    获取东方财富网强势股池
    
    参数:
        date: 日期，格式为'YYYYMMDD'，如'20220916'，默认为最新交易日
            
    返回:
        List[Dict]: 包含强势股池数据的字典列表，包含字段:
                   ['代码', '名称', '涨跌幅', '最新价', '涨停价', '换手率', '涨速', '是否新高', '量比',
                   '涨停统计', '入选理由', '所属行业', '成交额(百万)', '流通市值(百万)', '总市值(百万)']
        
    示例:
        data = await get_stock_strong_pool('20230101')
    """
    try:
        logger.info(f"获取东方财富网强势股池，日期: {date}")
        df = stock_strong_pool(date=date)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取东方财富网强势股池失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_break_price(
    flag: str = "cxg",
    n: int = 1
) -> List[Dict]:
    """
    获取同花顺技术选股-创新高/低个股
    
    参数:
        flag: 类型标志，可选值:
              'cxg': 创新高
              'cxd': 创新低
        n: 周期，可选值:
           1: 历史新高/低
           2: 一年新高/低
           3: 半年新高/低
           4: 创月新高/低
            
    返回:
        List[Dict]: 包含创新高/低个股数据的字典列表，包含字段:
                   ['股票代码', '股票简称', '涨跌幅', '换手率', '最新价',
                   '前期点位', '前期点位日期']
        
    示例:
        data = await get_ths_break_price('cxg', 1)
    """
    try:
        logger.info(f"获取同花顺技术选股-创新高/低个股，类型: {flag}, 周期: {n}")
        df = ths_break_price(flag=flag, n=n)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺技术选股-创新高/低个股失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_up_down(
    flag: str = 'lxsz'
) -> List[Dict]:
    """
    获取同花顺技术选股-连续上涨/下跌
    
    参数:
        flag: 类型标志，可选值:
              'lxsz': 连续上涨
              'lxxd': 连续下跌
            
    返回:
        List[Dict]: 包含连续上涨/下跌数据的字典列表，包含字段:
                   ['股票代码', '股票简称', '收盘价', '最高价',
                   '最低价', '连涨天数', '连续涨跌幅', '累计换手率', '所属行业']
        
    示例:
        data = await get_ths_up_down('lxsz')
    """
    try:
        logger.info(f"获取同花顺技术选股-连续上涨/下跌，类型: {flag}")
        df = ths_up_down(flag=flag)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺技术选股-连续上涨/下跌失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_vol_change(
    flag: str = 'cxfl'
) -> List[Dict]:
    """
    获取同花顺技术选股-持续放量/缩量
    
    参数:
        flag: 类型标志，可选值:
              'cxfl': 持续放量
              'cxsl': 持续缩量
            
    返回:
        List[Dict]: 包含持续放量/缩量数据的字典列表，包含字段:
                   ['股票代码', '股票简称', '涨跌幅', '最新价', '成交量',
                   '基准日成交量', '天数', '阶段涨跌幅', '所属行业']
        
    示例:
        data = await get_ths_vol_change('cxfl')
    """
    try:
        logger.info(f"获取同花顺技术选股-持续放量/缩量，类型: {flag}")
        df = ths_vol_change(flag=flag)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺技术选股-持续放量/缩量失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_break_ma(
    flag: str = 'xstp',
    n: int = 20
) -> List[Dict]:
    """
    获取同花顺技术选股-向上/下突破均线
    
    参数:
        flag: 类型标志，可选值:
              'xstp': 向上突破
              'xxtp': 向下突破
        n: 均线周期，可选值: 5, 10, 20, 30, 60, 90, 250, 500
            
    返回:
        List[Dict]: 包含向上/下突破均线数据的字典列表，包含字段:
                   ['股票代码', '股票简称', '最新价', '成交量(万)',
                   '涨跌幅', '换手率']
        
    示例:
        data = await get_ths_break_ma('xstp', 20)
    """
    try:
        logger.info(f"获取同花顺技术选股-向上/下突破均线，类型: {flag}, 均线周期: {n}")
        df = ths_break_ma(flag=flag, n=n)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺技术选股-向上/下突破均线失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_price_vol(
    flag: str = 'ljqs'
) -> List[Dict]:
    """
    获取同花顺技术选股-量价齐升/齐跌
    
    参数:
        flag: 类型标志，可选值:
              'ljqs': 量价齐升
              'ljqd': 量价齐跌
            
    返回:
        List[Dict]: 包含量价齐升/齐跌数据的字典列表，包含字段:
                   ['股票代码', '股票简称', '最新价',
                   '天数', '阶段涨幅', '累计换手率', '所属行业']
        
    示例:
        data = await get_ths_price_vol('ljqs')
    """
    try:
        logger.info(f"获取同花顺技术选股-量价齐升/齐跌，类型: {flag}")
        df = ths_price_vol(flag=flag)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺技术选股-量价齐升/齐跌失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_ths_xzjp() -> List[Dict]:
    """
    获取同花顺技术选股-险资举牌
    
    返回:
        List[Dict]: 包含险资举牌数据的字典列表，包含字段:
                   ['举牌公告日', '股票代码', '股票简称', '现价', '涨跌幅',
                   '举牌方', '增持数量(万)', '交易均价', '增持数量占总股本比例', '变动后持股总数(万)',
                   '变动后持股比例']
        
    示例:
        data = await get_ths_xzjp()
    """
    try:
        logger.info("获取同花顺技术选股-险资举牌")
        df = ths_xzjp()
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同花顺技术选股-险资举牌失败: {str(e)}")
        traceback.print_exc()
        return []