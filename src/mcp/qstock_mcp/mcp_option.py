# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
期权相关数据MCP工具接口

"""

import pandas as pd
from typing import Dict, List, Optional, Union
import logging
import traceback
from mcp_instance import mcp
import replace_qstock_func

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
async def get_option_target_list()-> list:
    '''获取中国金融市场期权标的列表
    参数：
    - 无
    返回：
    - List[Dict]: 包含期权标的代码(code)、名称(name)、市场(market)等，
    Dict包含字段: ['market', 'code', 'name']
    '''
    try:
        # 使用replace_qstock_func中的option_market_code获取期权标的数据
        return replace_qstock_func.option_market_code
    except Exception as e:
        logger.error(f"获取期权标的数据失败: {str(e)}")
        traceback.print_exc()

@mcp.tool()
async def get_option_realtime_data(codes: list|str, market: str = "期权") -> list:
    """ 获取中国金融市场多个期权的实时数据
    参数：
    - codes: 期权代码/名称，多个代码用逗号分隔，为空时默认获取指定的市场期权
    - market: 市场类型，默认为期权
    返回：
    - List[Dict]: 包含期权代码、名称、最新价、涨跌幅等，
    Dict包含字段: ['代码', '名称', '涨幅', '最新价', '成交量', '成交额', '今开', '昨结', '持仓量', '行权价', '剩余日', '日增']
    """
    if isinstance(codes, str):
        if not codes:
            option_codes = []  # 空字符串情况下，使用空列表
        else:
            option_codes = codes.split(',')  # 将逗号分隔的字符串转换为列表
    elif isinstance(codes, list):
        option_codes = codes
    else:
        logger.error("参数 'codes' 必须是字符串或列表")
        return []
    
    # 使用replace_qstock_func中的bso_option_realtime函数获取期权实时数据
    try:
        # 调用bso_option_realtime函数，传入option_detail_dict作为字段定义
        df = replace_qstock_func.bso_option_realtime(market=market, trade_detail_dict=replace_qstock_func.option_detail_dict, fltt='1')
        
        logger.info(f"获取期权实时数据: {df}")
        if df.empty:
            logger.warning("获取的期权数据为空")
            return []
            
        # 如果指定了期权代码，则过滤数据
        if option_codes:
            df = df[df['代码'].isin(option_codes)]
            if df.empty:
                logger.warning(f"未找到指定的期权代码: {option_codes}")
                return []
                
        logger.info(f"期权数据获取成功: {df.shape[0]} 条记录")
        logger.info(f"期权数据列名: {df.columns.tolist()}")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取期权实时数据失败: {str(e)}")
        traceback.print_exc()
    return []

@mcp.tool()
async def get_option_value_data(codes: list|str, market: str = "期权") -> list:
    """ 获取中国金融市场多个期权的价值数据
    参数：
    - codes: 期权代码/名称，多个代码用逗号分隔，为空时默认获取指定的市场期权
    - market: 市场类型，默认为期权
    返回：
    - List[Dict]: 包含期权代码、名称、隐含波动率、时间价值、内在价值、理论价格等，
    Dict包含字段: ['代码', '名称', '涨幅', '最新价', '隐含波动率', '时间价值', '内在价值', '理论价格', '到期日', 
                '标的代码', '标的名称', '标的最新价', '标的涨幅', '标的近1年波动率']
    """
    if isinstance(codes, str):
        if not codes:
            option_codes = []  # 空字符串情况下，使用空列表
        else:
            option_codes = codes.split(',')  # 将逗号分隔的字符串转换为列表
    elif isinstance(codes, list):
        option_codes = codes
    else:
        logger.error("参数 'codes' 必须是字符串或列表")
        return []
    
    # 使用replace_qstock_func中的bso_option_realtime函数获取期权价值数据
    try:
        # 调用bso_option_realtime函数，传入option_value_detail_dict作为字段定义
        df = replace_qstock_func.bso_option_realtime(market=market, trade_detail_dict=replace_qstock_func.option_value_detail_dict, fltt='1')
        
        logger.info(f"获取期权价值数据: {df}")
        if df.empty:
            logger.warning("获取的期权价值数据为空")
            return []
            
        # 如果指定了期权代码，则过滤数据
        if option_codes:
            df = df[df['代码'].isin(option_codes)]
            if df.empty:
                logger.warning(f"未找到指定的期权代码: {option_codes}")
                return []
                
        logger.info(f"期权价值数据获取成功: {df.shape[0]} 条记录")
        logger.info(f"期权价值数据列名: {df.columns.tolist()}")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取期权价值数据失败: {str(e)}")
        traceback.print_exc()
    return []

@mcp.tool()
async def get_option_risk_data(codes: list|str, market: str = "期权风险") -> list:
    """ 获取中国金融市场多个期权的风险数据
    参数：
    - codes: 期权代码/名称，多个代码用逗号分隔，为空时默认获取指定的市场期权
    - market: 市场类型，默认为期权风险
    返回：
    - List[Dict]: 包含期权代码、名称、Delta、Gamma、Vega、Theta、Rho等希腊字母指标，
    Dict包含字段: ['代码', '名称', '涨幅', '最新价', '杠杆比率', '实际杠杆比率', 'Delta', 'Gamma', 'Vega', 'Rho', 'Theta', '到期日']
    """
    if isinstance(codes, str):
        if not codes:
            option_codes = []  # 空字符串情况下，使用空列表
        else:
            option_codes = codes.split(',')  # 将逗号分隔的字符串转换为列表
    elif isinstance(codes, list):
        option_codes = codes
    else:
        logger.error("参数 'codes' 必须是字符串或列表")
        return []
    
    # 使用replace_qstock_func中的bso_option_realtime函数获取期权风险数据
    try:
        # 调用bso_option_realtime函数，传入option_risk_detail_dict作为字段定义
        df = replace_qstock_func.bso_option_realtime(market=market, trade_detail_dict=replace_qstock_func.option_risk_detail_dict, fltt='1')
        
        logger.info(f"获取期权风险数据: {df}")
        if df.empty:
            logger.warning("获取的期权风险数据为空")
            return []
            
        # 如果指定了期权代码，则过滤数据
        if option_codes:
            df = df[df['代码'].isin(option_codes)]
            if df.empty:
                logger.warning(f"未找到指定的期权代码: {option_codes}")
                return []
                
        logger.info(f"期权风险数据获取成功: {df.shape[0]} 条记录")
        logger.info(f"期权风险数据列名: {df.columns.tolist()}")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取期权风险数据失败: {str(e)}")
        traceback.print_exc()
    return []

@mcp.tool()
async def get_option_tboard_data(expire_month: str = None) -> list:
    """ 获取期权T型看板数据
    参数：
    - expire_month: 到期月份，格式为YYYYMM，如202312。为空时获取所有月份的T型看板数据
    返回：
    - List[Dict]: 包含期权T型看板数据，
    Dict包含字段: ['购代码', '购名称', '购最新价', '购涨跌额', '标的最新价', '购涨跌幅', '购持仓量', '购成交量', 
                '购隐含波动率', '购折溢价率', '行权价', '沽名称', '沽代码', '沽最新价', '沽涨跌额', '沽涨跌幅', 
                '沽持仓量', '沽成交量', '沽隐含波动率', '沽折溢价率', '时间', '到期日']
    """
    # 使用replace_qstock_func中的函数获取期权T型看板数据
    try:
        if expire_month:
            # 获取指定月份的T型看板数据
            df = replace_qstock_func.bso_option_tboard_month(expire_month)
        else:
            # 获取所有月份的T型看板数据
            df = replace_qstock_func.bso_option_tboard_all()
        
        logger.info(f"获取期权T型看板数据: {df}")
        if df.empty:
            logger.warning("获取的期权T型看板数据为空")
            return []
                
        logger.info(f"期权T型看板数据获取成功: {df.shape[0]} 条记录")
        logger.info(f"期权T型看板数据列名: {df.columns.tolist()}")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取期权T型看板数据失败: {str(e)}")
        traceback.print_exc()
    return []

@mcp.tool()
async def get_option_expire_all_data() -> list:
    """ 获取所有期权标的的到期日信息
    参数：
    - 无
    返回：
    - List[Dict]: 包含所有期权标的的到期日信息，
    Dict包含字段: ['到期日', '剩余日', '市场', '代码']
    """
    # 使用replace_qstock_func中的bso_option_expire_all函数获取所有期权市场的到期日信息
    try:
        df = replace_qstock_func.bso_option_expire_all()
        
        logger.info(f"获取所有期权标的的到期日信息: {df}")
        if df.empty:
            logger.warning("获取的期权标的到期日信息为空")
            return []
                
        logger.info(f"期权标的到期日信息获取成功: {df.shape[0]} 条记录")
        logger.info(f"期权标的到期日信息列名: {df.columns.tolist()}")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取所有期权标的的到期日信息失败: {str(e)}")
        traceback.print_exc()
    return []

@mcp.tool()
async def get_option_expire_info_data(code: str, market: int = 0) -> list:
    """ 获取指定期权标的代码的到期日信息
    参数：
    - code: 期权标的代码，如510050（50ETF）
    - market: 市场类型，0表示深交所，1表示上交所，默认为0
    返回：
    - List[Dict]: 包含指定期权代码的到期日信息，
    Dict包含字段: ['到期日', '剩余日', '市场', '代码']
    """
    # 参数验证
    if not code:
        logger.error("参数 'code' 不能为空")
        return []
    
    if market not in [0, 1]:
        logger.warning(f"参数 'market' 必须是0或1，当前值为: {market}，将使用默认值0")
        market = 0
    
    # 使用replace_qstock_func中的bso_option_expire_info函数获取指定期权代码的到期日信息
    try:
        df = replace_qstock_func.bso_option_expire_info(code, market)
        
        logger.info(f"获取期权标的代码 {code} 的到期日信息: {df}")
        if df.empty:
            logger.warning(f"获取的期权标的代码 {code} 的到期日信息为空")
            return []
                
        logger.info(f"期权标的代码 {code} 的到期日信息获取成功: {df.shape[0]} 条记录")
        logger.info(f"期权标的到期日信息列名: {df.columns.tolist()}")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取期权标的代码 {code} 的到期日信息失败: {str(e)}")
        traceback.print_exc()
    return []