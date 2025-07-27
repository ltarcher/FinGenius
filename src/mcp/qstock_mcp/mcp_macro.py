# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
宏观经济数据MCP工具接口
提供宏观经济数据的MCP工具接口
"""

import pandas as pd
from typing import Dict, List, Optional, Union
import logging
import traceback
import requests
import json
from mcp_instance import mcp
from qstock.data import macro  # 直接导入macro模块

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
async def get_interbank_rate(
    market: str = 'sh',
    fc: Optional[str] = None
) -> List[Dict]:
    """
    获取同业拆借利率数据
    
    参数:
        market: 同业拆借市场简称，各个市场英文缩写为：
               'sh': 上海银行同业拆借市场
               'ch': 中国银行同业拆借市场
               'l': 伦敦银行同业拆借市场
               'eu': 欧洲银行同业拆借市场
               'hk': 香港银行同业拆借市场
               's': 新加坡银行同业拆借市场
        fc: 货币代码，如USD、CNY、EUR等
            香港市场，fc可选：'港元'，'美元','人民币'
            新加坡市场，fc可选：'星元','美元'
            伦敦市场，fc可选：'英镑','美元','欧元','日元'
            
    返回:
        List[Dict]: 包含同业拆借利率数据的字典列表
        
    示例:
        data = await get_interbank_rate('sh', 'CNY')
    """
    try:
        logger.info(f"获取同业拆借利率数据，市场: {market}, 货币: {fc}")
        df = macro.ib_rate(market=market, fc=fc)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将日期列转换为字符串格式
        df['报告日'] = df['报告日'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取同业拆借利率数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_specific_interbank_rate(
    market: str,
    fc: str,
    indicator: str
) -> List[Dict]:
    """
    获取特定市场、货币和期限的同业拆借利率数据
    
    参数:
        market: 同业拆借市场简称或名称
        fc: 货币代码或名称
        indicator: 期限指标，如'隔夜'、'1周'、'1月'、'3月'、'1年'等
        
    返回:
        List[Dict]: 包含特定同业拆借利率数据的字典列表
        
    示例:
        data = await get_specific_interbank_rate('上海银行同业拆借市场', '人民币', '1月')
    """
    try:
        logger.info(f"获取特定同业拆借利率数据，市场: {market}, 货币: {fc}, 期限: {indicator}")
        df = macro.interbank_rate(market=market, fc=fc, indicator=indicator)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将日期列转换为字符串格式
        df['报告日'] = df['报告日'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取特定同业拆借利率数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_macro_data(
    indicator: str = 'gdp'
) -> List[Dict]:
    """
    获取宏观经济常见指标数据
    
    参数:
        indicator: 指标类型，可选值:
                  'lpr': 贷款基准利率
                  'ms': 货币供应量
                  'cpi': 消费者物价指数
                  'ppi': 工业品出厂价格指数
                  'pmi': 采购经理人指数
                  'gdp': 国内生产总值(默认)
        
    返回:
        List[Dict]: 包含宏观经济指标数据的字典列表
        
    示例:
        data = await get_macro_data('cpi')
    """
    try:
        logger.info(f"获取宏观经济指标数据: {indicator}")
        df = macro.macro_data(flag=indicator)
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
        
        # 处理日期/季度/月份列，确保可以序列化为JSON
        date_col = '季度' if '季度' in df.columns else '月份' if '月份' in df.columns else '日期'
        if date_col in df.columns:
            df[date_col] = df[date_col].astype(str)
            
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取宏观经济指标数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_loan_prime_rate() -> List[Dict]:
    """
    获取中国贷款报价利率(LPR)数据
    
    返回:
        List[Dict]: 包含LPR数据的字典列表
        
    示例:
        data = await get_loan_prime_rate()
    """
    try:
        logger.info("获取中国贷款报价利率(LPR)数据")
        df = macro.lpr()
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将日期列转换为字符串格式
        df['日期'] = df['日期'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取中国贷款报价利率数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_money_supply() -> List[Dict]:
    """
    获取中国货币供应量数据
    
    返回:
        List[Dict]: 包含货币供应量数据的字典列表
        
    示例:
        data = await get_money_supply()
    """
    try:
        logger.info("获取中国货币供应量数据")
        df = macro.ms()
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将月份列转换为字符串格式
        df['月份'] = df['月份'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取中国货币供应量数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_consumer_price_index() -> List[Dict]:
    """
    获取中国消费者物价指数(CPI)数据
    
    返回:
        List[Dict]: 包含CPI数据的字典列表
        
    示例:
        data = await get_consumer_price_index()
    """
    try:
        logger.info("获取中国消费者物价指数(CPI)数据")
        df = macro.cpi()
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将月份列转换为字符串格式
        df['月份'] = df['月份'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取中国消费者物价指数数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_gdp() -> List[Dict]:
    """
    获取中国国内生产总值(GDP)数据
    
    返回:
        List[Dict]: 包含GDP数据的字典列表
        
    示例:
        data = await get_gdp()
    """
    try:
        logger.info("获取中国国内生产总值(GDP)数据")
        df = macro.gdp()
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将季度列转换为字符串格式
        df['季度'] = df['季度'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取中国国内生产总值数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_producer_price_index() -> List[Dict]:
    """
    获取中国工业品出厂价格指数(PPI)数据
    
    返回:
        List[Dict]: 包含PPI数据的字典列表
        
    示例:
        data = await get_producer_price_index()
    """
    try:
        logger.info("获取中国工业品出厂价格指数(PPI)数据")
        df = macro.ppi()
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将月份列转换为字符串格式
        df['月份'] = df['月份'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取中国工业品出厂价格指数数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_purchasing_managers_index() -> List[Dict]:
    """
    获取中国采购经理人指数(PMI)数据
    
    返回:
        List[Dict]: 包含PMI数据的字典列表
        
    示例:
        data = await get_purchasing_managers_index()
    """
    try:
        logger.info("获取中国采购经理人指数(PMI)数据")
        df = macro.pmi()
        
        if df.empty:
            logger.warning("返回数据为空")
            return []
            
        # 将月份列转换为字符串格式
        df['月份'] = df['月份'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取中国采购经理人指数数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_customs_import_export_data(
    page_number: int = 1,
    page_size: int = 20
) -> List[Dict]:
    """
    获取中国海关进出口数据
    
    参数:
        page_number: 页码，默认为1
        page_size: 每页数据量，默认为20
    
    返回:
        List[Dict]: 包含海关进出口数据的字典列表
        
    示例:
        data = await get_customs_import_export_data(page_number=1, page_size=10)
    """
    try:
        logger.info(f"获取中国海关进出口数据，页码: {page_number}, 每页数据量: {page_size}")
        url = f"https://datacenter-web.eastmoney.com/api/data/v1/get?callback=datatable2553667&columns=REPORT_DATE%2CTIME%2CEXIT_BASE%2CIMPORT_BASE%2CEXIT_BASE_SAME%2CIMPORT_BASE_SAME%2CEXIT_BASE_SEQUENTIAL%2CIMPORT_BASE_SEQUENTIAL%2CEXIT_ACCUMULATE%2CIMPORT_ACCUMULATE%2CEXIT_ACCUMULATE_SAME%2CIMPORT_ACCUMULATE_SAME&pageNumber={page_number}&pageSize={page_size}&sortColumns=REPORT_DATE&sortTypes=-1&source=WEB&client=WEB&reportName=RPT_ECONOMY_CUSTOMS&_=1753524202774"
        response = requests.get(url)
        response.raise_for_status()
        
        # 解析JSONP格式的响应数据
        jsonp_data = response.text
        json_data = jsonp_data[jsonp_data.find('(')+1:jsonp_data.rfind(')')]
        data = json.loads(json_data)
        
        if not data.get('result', {}).get('data'):
            logger.warning("返回数据为空")
            return []
        
        # 转换数据格式
        result = []
        for item in data['result']['data']:
            result.append({
                '报告日期': item['REPORT_DATE'],
                '时间': item['TIME'],
                '出口额': item['EXIT_BASE'],
                '进口额': item['IMPORT_BASE'],
                '出口同比': item['EXIT_BASE_SAME'],
                '进口同比': item['IMPORT_BASE_SAME'],
                '出口环比': item['EXIT_BASE_SEQUENTIAL'],
                '进口环比': item['IMPORT_BASE_SEQUENTIAL'],
                '累计出口额': item['EXIT_ACCUMULATE'],
                '累计进口额': item['IMPORT_ACCUMULATE'],
                '累计出口同比': item['EXIT_ACCUMULATE_SAME'],
                '累计进口同比': item['IMPORT_ACCUMULATE_SAME']
            })
        
        return result
    except Exception as e:
        logger.error(f"获取中国海关进出口数据失败: {str(e)}")
        traceback.print_exc()
        return []