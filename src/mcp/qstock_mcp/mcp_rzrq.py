# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
融资融券数据MCP工具接口
提供融资融券数据的MCP工具接口
"""

import logging
from typing import Dict, List, Optional
import traceback
from mcp_instance import mcp
from stock_rzrq import (
    get_rzrq_industry_rank,
    get_rzrq_industry_detail,
    get_rzrq_history,
    get_rzrq_market_summary,
    get_rzrq_concept_rank,
    get_rzrq_account_data
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
async def get_rzrq_industry_rank_mcp(
    page: int = 1,
    page_size: int = 5,
    sort_column: str = "FIN_NETBUY_AMT",
    sort_type: int = -1,
    board_type_code: str = "006",
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取东方财富网融资融券行业板块排行数据(MCP工具版本)
    
    参数:
        page: 页码，默认为1
        page_size: 每页数量，默认为5
        sort_column: 排序列，默认为"FIN_NETBUY_AMT"(融资净买入额)
        sort_type: 排序类型，1为升序，-1为降序，默认为-1
        board_type_code: 板块类型代码，默认为"006"(财富通行业)
        use_chinese_fields: 是否使用中文字段名，默认为True
    
    返回:
        List[Dict]: 包含融资融券行业板块排行数据的字典列表
    """
    try:
        logger.info(f"获取融资融券行业板块排行数据，页码：{page}，每页数量：{page_size}")
        data = get_rzrq_industry_rank(
            page=page,
            page_size=page_size,
            sort_column=sort_column,
            sort_type=sort_type,
            board_type_code=board_type_code,
            use_chinese_fields=use_chinese_fields
        )
        return data.get('result', {}).get('data', []) if data else []
    except Exception as e:
        logger.error(f"获取融资融券行业板块排行数据时发生错误：{str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_rzrq_industry_detail_mcp(
    board_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取特定行业板块的融资融券明细数据(MCP工具版本)
    
    参数:
        board_code: 板块代码
        start_date: 开始日期，格式为'YYYY-MM-DD'，默认为None
        end_date: 结束日期，格式为'YYYY-MM-DD'，默认为None
        page: 页码，默认为1
        page_size: 每页数量，默认为20
        use_chinese_fields: 是否使用中文字段名，默认为True
    
    返回:
        List[Dict]: 包含特定行业板块融资融券明细数据的字典列表
    """
    try:
        logger.info(f"获取板块{board_code}的融资融券明细数据")
        data = get_rzrq_industry_detail(
            board_code=board_code,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            use_chinese_fields=use_chinese_fields
        )
        return data.get('result', {}).get('data', []) if data else []
    except Exception as e:
        logger.error(f"获取行业板块融资融券明细数据时发生错误：{str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_rzrq_history_mcp(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取融资融券交易历史明细数据(沪深北三市场)(MCP工具版本)
    
    参数:
        start_date: 开始日期，格式为'YYYY-MM-DD'，默认为None
        end_date: 结束日期，格式为'YYYY-MM-DD'，默认为None
        page: 页码，默认为1
        page_size: 每页数量，默认为10
        use_chinese_fields: 是否使用中文字段名，默认为True
    
    返回:
        List[Dict]: 包含融资融券交易历史明细数据的字典列表
    """
    try:
        logger.info(f"获取融资融券交易历史明细数据，页码：{page}，每页数量：{page_size}")
        data = get_rzrq_history(
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            use_chinese_fields=use_chinese_fields
        )
        return data.get('result', {}).get('data', []) if data else []
    except Exception as e:
        logger.error(f"获取融资融券交易历史明细数据时发生错误：{str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_rzrq_market_summary_mcp(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取市场融资融券交易总量数据(含上证指数和融资融券汇总数据)(MCP工具版本)
    
    参数:
        start_date: 开始日期，格式为'YYYY-MM-DD'，默认为None
        end_date: 结束日期，格式为'YYYY-MM-DD'，默认为None
        page: 页码，默认为1
        page_size: 每页数量，默认为10
        use_chinese_fields: 是否使用中文字段名，默认为True
    
    返回:
        List[Dict]: 包含市场融资融券交易总量数据的字典列表
    """
    try:
        logger.info(f"获取市场融资融券交易总量数据，页码：{page}，每页数量：{page_size}")
        data = get_rzrq_market_summary(
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            use_chinese_fields=use_chinese_fields
        )
        return data.get('result', {}).get('data', []) if data else []
    except Exception as e:
        logger.error(f"获取市场融资融券交易总量数据时发生错误：{str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_rzrq_concept_rank_mcp(
    page: int = 1,
    page_size: int = 50,
    sort_column: str = "FIN_NETBUY_AMT",
    sort_type: int = -1,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取东方财富网融资融券概念板块排行数据(MCP工具版本)
    
    参数:
        page: 页码，默认为1
        page_size: 每页数量，默认为50
        sort_column: 排序列，默认为"FIN_NETBUY_AMT"(融资净买入额)
        sort_type: 排序类型，1为升序，-1为降序，默认为-1
        use_chinese_fields: 是否使用中文字段名，默认为True
    
    返回:
        List[Dict]: 包含融资融券概念板块排行数据的字典列表
    """
    try:
        logger.info(f"获取融资融券概念板块排行数据，页码：{page}，每页数量：{page_size}")
        data = get_rzrq_concept_rank(
            page=page,
            page_size=page_size,
            sort_column=sort_column,
            sort_type=sort_type,
            use_chinese_fields=use_chinese_fields
        )
        return data.get('result', {}).get('data', []) if data else []
    except Exception as e:
        logger.error(f"获取融资融券概念板块排行数据时发生错误：{str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_rzrq_account_data_mcp(
    page: int = 1,
    page_size: int = 50,
    sort_column: str = "STATISTICS_DATE",
    sort_type: int = -1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    use_chinese_fields: bool = True
) -> List[Dict]:
    """
    获取两融账户信息数据(MCP工具版本)
    
    参数:
        page: 页码，默认为1
        page_size: 每页数量，默认为50
        sort_column: 排序列，默认为"STATISTICS_DATE"(统计日期)
        sort_type: 排序类型，1为升序，-1为降序，默认为-1
        start_date: 开始日期，格式为'YYYY-MM-DD'，默认为None
        end_date: 结束日期，格式为'YYYY-MM-DD'，默认为None
        use_chinese_fields: 是否使用中文字段名，默认为True
    
    返回:
        List[Dict]: 包含两融账户信息数据的字典列表
    """
    try:
        logger.info(f"获取两融账户信息数据，页码：{page}，每页数量：{page_size}")
        data = get_rzrq_account_data(
            page=page,
            page_size=page_size,
            sort_column=sort_column,
            sort_type=sort_type,
            start_date=start_date,
            end_date=end_date,
            use_chinese_fields=use_chinese_fields
        )
        return data.get('result', {}).get('data', []) if data else []
    except Exception as e:
        logger.error(f"获取两融账户信息数据时发生错误：{str(e)}")
        traceback.print_exc()
        return []