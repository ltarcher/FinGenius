# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
期货品种数据MCP工具接口
提供期货品种数据的MCP工具接口
"""

import pandas as pd
from typing import Dict, List, Optional, Union
import logging
import traceback
from mcp_instance import mcp
from qh_list import FuturesList
from qh_lhb import FuturesLHB
from qh_ccjg import FuturesCCJG
from qh_jcgc import FuturesJCGC


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建期货品种数据实例
futures_list = FuturesList()

@mcp.tool()
async def get_futures_market_codes() -> Dict[str, str]:
    """
    获取所有期货交易市场代码
    
    返回:
        Dict[str, str]: 市场名称和代码的映射字典
        
    示例:
        market_codes = await get_market_codes()
    """
    try:
        logger.info("调用获取期货交易市场代码接口")
        return futures_list.get_market_codes()
    except Exception as e:
        logger.error(f"获取交易市场代码失败: {e}")
        traceback.print_exc()
        return {"错误": str(e)}


@mcp.tool()
async def get_future_org_list(
    page_size: int = 200,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取期货公司列表数据
    
    参数:
        page_size: 每页数据量，默认为200
        use_chinese_fields: 是否使用中文字段名，默认为True
            
    返回:
        List[Dict]: 包含期货公司数据的字典列表
        
    示例:
        data = await get_future_org_list()
    """
    try:
        logger.info("调用获取期货公司列表数据接口")
        df = futures_list.get_future_org_list(
            page_size=page_size,
            use_chinese_fields=use_chinese_fields
        )
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取期货公司列表数据失败: {e}")
        traceback.print_exc()
        return []


@mcp.tool()
async def get_futures_list(
    is_main_code: bool = True,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取期货品种列表数据
    
    参数:
        is_main_code: 是否只获取主力合约，默认为True
        use_chinese_fields: 是否使用中文字段名，默认为True
            
    返回:
        List[Dict]: 包含期货品种数据的字典列表
        
    示例:
        data = await get_futures_list()
    """
    try:
        logger.info("调用获取期货品种列表数据接口")
        df = futures_list.get_futures_list(
            is_main_code=is_main_code,
            use_chinese_fields=use_chinese_fields
        )
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取期货品种列表数据失败: {e}")
        traceback.print_exc()
        return []
    
@mcp.tool()
async def get_exchange_codes() -> Dict[str, str]:
    """
    获取交易所编码映射(用于获取交易所名称和编码的映射或查询交易所可交易品种列表)
    
    返回:
        Dict[str, str]: 交易所名称和编码的映射字典
        
    示例:
        exchange_codes = await get_exchange_codes()
    """
    try:
        logger.info("获取交易所编码映射")
        return FuturesList.EXCHANGE_MSGID.copy()
    except Exception as e:
        logger.error(f"获取交易所编码失败: {e}")
        traceback.print_exc()
        return {"错误": str(e)}

@mcp.tool()
async def get_exchange_products(
    exchange_name: str,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取交易所可交易品种列表
    
    参数:
        exchange_name: 交易所名称(如上期所、中金所等)
        use_chinese_fields: 是否使用中文字段名，默认为True
        
    返回:
        List[Dict]: 包含交易所品种数据的字典列表
        
    示例:
        data = await get_exchange_products("中金所")
    """
    try:
        logger.info(f"获取交易所品种数据，交易所: {exchange_name}")
        
        # 获取交易所编码
        msgid = FuturesList.EXCHANGE_MSGID.get(exchange_name)
        if not msgid:
            raise ValueError(f"不支持的交易所名称: {exchange_name}")
            
        # 获取品种数据
        df = futures_list.get_exchange_products(
            msgid=msgid,
            use_chinese_fields=use_chinese_fields
        )
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        traceback.print_exc()
        return []
    except Exception as e:
        logger.error(f"获取交易所品种数据失败: {str(e)}")
        traceback.print_exc()
        return []
    
# ==================== 龙虎榜数据工具 =============# 

# ==== 修改后代码 ====

@mcp.tool()
async def get_qh_lhb_data(
    security_code: str,
    trade_date: str,
    cookies: Optional[Dict[str, str]] = None,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取期货龙虎榜数据
    
    参数:
        security_code: 合约代码(如IF2509)
        trade_date: 交易日期(YYYY-MM-DD)
        cookies: 请求cookies字典
        use_chinese_fields: 是否使用中文字段名，默认为True
        
    返回:
        List[Dict]: 包含龙虎榜数据的字典列表
        
    示例:
        data = await get_qh_lhb_data("IF2509", "2025-07-18")
    """
    try:
        lhb = FuturesLHB(cookies=cookies)
        df = lhb.get_data(
            security_code=security_code,
            trade_date=trade_date,
            use_chinese_fields=use_chinese_fields
        )
        
        logger.info(f"获取期货龙虎榜数据成功，合约: {security_code}, 日期: {trade_date}")
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取期货龙虎榜数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_qh_lhb_rank(
    security_code: str,
    trade_date: str,
    rank_field: str,
    cookies: Optional[Dict[str, str]] = None,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取特定排名的期货龙虎榜数据
    
    参数:
        security_code: 合约代码(如IF2509)
        trade_date: 交易日期(YYYY-MM-DD)
        rank_field: 排名字段(如VOLUMERANK, LPRANK等)
        cookies: 请求cookies字典
        use_chinese_fields: 是否使用中文字段名，默认为True
        
    返回:
        List[Dict]: 包含特定排名龙虎榜数据的字典列表
        
    示例:
        data = await get_qh_lhb_rank("IF2509", "2025-07-18", "VOLUMERANK")
    """
    try:
        lhb = FuturesLHB(cookies=cookies)
        df = lhb.get_data(
            security_code=security_code,
            trade_date=trade_date,
            sort_field=rank_field,
            use_chinese_fields=use_chinese_fields
        )
        
        logger.info(f"获取期货{rank_field}排名数据成功，合约: {security_code}, 日期: {trade_date}")
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取期货排名数据失败: {str(e)}")
        traceback.print_exc()
        return []

# ==================== 持仓结构数据工具 =============#


# ==== 修改后代码 ====

@mcp.tool()
async def get_qh_ccjg_data(
    org_code: str,
    trade_date: str,
    market_name: str,
    cookies: Optional[Dict[str, str]] = None,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取期货公司持仓结构数据
    
    参数:
        org_code: 机构代码
        trade_date: 交易日期(YYYY-MM-DD)
        market_name: 市场名称(如上期所、中金所等)
        cookies: 请求cookies字典
        use_chinese_fields: 是否使用中文字段名，默认为True
        
    返回:
        List[Dict]: 包含持仓结构数据的字典列表
        
    示例:
        data = await get_qh_ccjg_data("10102950", "2025-07-18", "中金所")
    """
    try:
        ccjg = FuturesCCJG(cookies=cookies)
        df = ccjg.get_data(
            org_code=org_code,
            trade_date=trade_date,
            market_name=market_name,
            use_chinese_fields=use_chinese_fields
        )
        
        logger.info(f"获取期货公司持仓结构数据成功，机构: {org_code}, 日期: {trade_date}, 市场: {market_name}")
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取期货公司持仓结构数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_qh_ccjg_multi_market(
    org_code: str,
    trade_date: str,
    markets: List[str],
    cookies: Optional[Dict[str, str]] = None,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取期货公司在多个市场的持仓数据
    
    参数:
        org_code: 机构代码
        trade_date: 交易日期(YYYY-MM-DD)
        markets: 市场名称列表(如上期所、中金所等)
        cookies: 请求cookies字典
        use_chinese_fields: 是否使用中文字段名，默认为True
        
    返回:
        List[Dict]: 包含多市场持仓数据的字典列表
        
    示例:
        data = await get_qh_ccjg_multi_market("10102950", "2025-07-18", ["中金所", "上期所"])
    """
    try:
        ccjg = FuturesCCJG(cookies=cookies)
        df = ccjg.get_org_positions(
            org_code=org_code,
            trade_date=trade_date,
            markets=markets,
            use_chinese_fields=use_chinese_fields
        )
        
        logger.info(f"获取多市场持仓数据成功，机构: {org_code}, 日期: {trade_date}, 市场: {markets}")
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取多市场持仓数据失败: {str(e)}")
        traceback.print_exc()
        return []

# ==================== 建仓过程数据工具 =============#


# ==== 修改后代码 ====

@mcp.tool()
async def get_qh_jcgc_data(
    security_code: str,
    org_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    cookies: Optional[Dict[str, str]] = None,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取期货建仓过程数据
    
    参数:
        security_code: 合约代码(如IF2507)
        org_code: 机构代码
        start_date: 开始日期(YYYY-MM-DD)，可选
        end_date: 结束日期(YYYY-MM-DD)，可选
        cookies: 请求cookies字典
        use_chinese_fields: 是否使用中文字段名，默认为True
        
    返回:
        List[Dict]: 包含建仓过程数据的字典列表
        
    示例:
        data = await get_qh_jcgc_data("IF2507", "10102950", "2025-06-01", "2025-07-18")
    """
    try:
        jcgc = FuturesJCGC(cookies=cookies)
        df = jcgc.get_data(
            security_code=security_code,
            org_code=org_code,
            start_date=start_date,
            end_date=end_date,
            use_chinese_fields=use_chinese_fields
        )
        
        logger.info(f"获取建仓过程数据成功，合约: {security_code}, 机构: {org_code}")
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取建仓过程数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_qh_jcgc_history(
    security_code: str,
    org_code: str,
    days: int = 30,
    end_date: Optional[str] = None,
    cookies: Optional[Dict[str, str]] = None,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取指定天数的持仓历史数据
    
    参数:
        security_code: 合约代码(如IF2507)
        org_code: 机构代码
        days: 获取的天数，默认30天
        end_date: 结束日期(YYYY-MM-DD)，可选
        cookies: 请求cookies字典
        use_chinese_fields: 是否使用中文字段名，默认为True
        
    返回:
        List[Dict]: 包含持仓历史数据的字典列表
        
    示例:
        data = await get_qh_jcgc_history("IF2507", "10102950", days=15)
    """
    try:
        jcgc = FuturesJCGC(cookies=cookies)
        df = jcgc.get_position_history(
            security_code=security_code,
            org_code=org_code,
            days=days,
            end_date=end_date,
            use_chinese_fields=use_chinese_fields
        )
        
        logger.info(f"获取持仓历史数据成功，合约: {security_code}, 机构: {org_code}, 天数: {days}")
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取持仓历史数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_qh_jcgc_summary(
    security_code: str,
    org_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    cookies: Optional[Dict[str, str]] = None
) -> Dict[str, Dict[str, float]]:
    """
    获取持仓数据摘要
    
    参数:
        security_code: 合约代码(如IF2507)
        org_code: 机构代码
        start_date: 开始日期(YYYY-MM-DD)，可选
        end_date: 结束日期(YYYY-MM-DD)，可选
        cookies: 请求cookies字典
        
    返回:
        Dict: 包含持仓数据摘要的字典
        
    示例:
        summary = await get_qh_jcgc_summary("IF2507", "10102950", "2025-06-01", "2025-07-18")
    """
    try:
        jcgc = FuturesJCGC(cookies=cookies)
        df = jcgc.get_data(
            security_code=security_code,
            org_code=org_code,
            start_date=start_date,
            end_date=end_date,
            use_chinese_fields=True  # 摘要使用中文字段名
        )
        
        logger.info(f"获取持仓数据摘要成功，合约: {security_code}, 机构: {org_code}")
        
        if df.empty:
            logger.warning("返回数据为空")
            return {}
            
        return jcgc.get_position_summary(df)
    except Exception as e:
        logger.error(f"获取持仓数据摘要失败: {str(e)}")
        traceback.print_exc()
        return {}