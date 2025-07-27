# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
交易数据MCP工具接口
提供股票、债券、基金等交易数据的MCP工具接口
"""

import pandas as pd
from typing import Dict, List, Optional, Union
import logging
import traceback
from datetime import datetime
from mcp_instance import mcp
from qstock.data import trade  # 导入trade模块

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
async def get_market_codes(market: str = '沪深A') -> List[str]:
    """
    获取某市场所有股票/债券/基金代码
    
    参数:
        market: 市场名称，可选值:
               '沪深京A': 沪深京A股市场
               '沪深A': 沪深A股市场(默认)
               '沪A': 沪市A股市场
               '深A': 深市A股市场
               '北A': 北证A股市场
               '可转债': 沪深可转债市场
               '期货': 期货市场
               '期权': 期权市场
               '债券': 债券市场
               '创业板': 创业板市场
               '美股': 美股市场
               '港股': 港股市场
               '中概股': 中国概念股市场
               '新股': 沪深新股市场
               '科创板': 科创板市场
               '沪股通': 沪股通市场
               '深股通': 深股通市场
               '行业板块': 行业板块市场
               '概念板块': 概念板块市场
               '沪深指数': 沪深系列指数市场
               '上证指数': 上证系列指数市场
               '深证指数': 深证系列指数市场
               'ETF': ETF基金市场
               'LOF': LOF基金市场
    
    返回:
        List[str]: 包含指定市场所有交易标的代码的列表
        
    示例:
        codes = await get_market_codes('沪深A')
    """
    try:
        logger.info(f"获取{market}市场所有交易标的代码")
        codes = trade.get_code(market=market)
        
        if not codes:
            logger.warning(f"获取{market}市场所有交易标的代码为空")
            return []
            
        logger.info(f"获取{market}市场所有交易标的代码成功，共{len(codes)}个代码")
        return codes
    except Exception as e:
        logger.error(f"获取{market}市场所有交易标的代码失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_market_names(market: str = '沪深A') -> List[str]:
    """
    获取某市场所有股票/债券/基金名称
    
    参数:
        market: 市场名称，可选值同get_market_codes函数
    
    返回:
        List[str]: 包含指定市场所有交易标的名称的列表
        
    示例:
        names = await get_market_names('沪深A')
    """
    try:
        logger.info(f"获取{market}市场所有交易标的名称")
        names = trade.get_name(market=market)
        
        if not names:
            logger.warning(f"获取{market}市场所有交易标的名称为空")
            return []
            
        logger.info(f"获取{market}市场所有交易标的名称成功，共{len(names)}个名称")
        return names
    except Exception as e:
        logger.error(f"获取{market}市场所有交易标的名称失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_market_name_code_dict(market: str = '沪深A') -> Dict[str, str]:
    """
    获取某市场所有股票/债券/基金名称代码字典
    
    参数:
        market: 市场名称，可选值同get_market_codes函数
    
    返回:
        Dict[str, str]: 包含指定市场所有交易标的名称和代码的字典，键为名称，值为代码
        
    示例:
        name_code_dict = await get_market_name_code_dict('沪深A')
    """
    try:
        logger.info(f"获取{market}市场所有交易标的名称代码字典")
        name_code_dict = trade.get_name_code(market=market)
        
        if not name_code_dict:
            logger.warning(f"获取{market}市场所有交易标的名称代码字典为空")
            return {}
            
        logger.info(f"获取{market}市场所有交易标的名称代码字典成功，共{len(name_code_dict)}个键值对")
        return name_code_dict
    except Exception as e:
        logger.error(f"获取{market}市场所有交易标的名称代码字典失败: {str(e)}")
        traceback.print_exc()
        return {}

@mcp.tool()
async def get_market_realtime_data(market: str = '沪深A') -> List[Dict]:
    """
    获取某指定市场所有标的最新行情指标
    
    参数:
        market: 市场名称，可选值同get_market_codes函数
    
    返回:
        List[Dict]: 包含指定市场所有交易标的最新行情指标的字典列表
        Dict包含字段: ['代码', '名称', '涨幅', '最新', '最高', '最低', '今开', '换手率', '量比', 
                    '市盈率', '成交量', '成交额', '昨收', '总市值', '流通市值', '时间']
        
    示例:
        data = await get_market_realtime_data('沪深A')
    """
    try:
        logger.info(f"获取{market}市场所有标的最新行情指标")
        df = trade.market_realtime(market=market)
        
        if df.empty:
            logger.warning(f"获取{market}市场所有标的最新行情指标为空")
            return []
            
        logger.info(f"获取{market}市场所有标的最新行情指标成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取{market}市场所有标的最新行情指标失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_realtime_data(code_list: Union[str, List[str]]) -> List[Dict]:
    """
    获取单个或多个证券的最新行情指标
    
    参数:
        code_list: 证券代码或名称，可以是单个字符串或字符串列表
                  如"000001"或["000001", "600000", "平安银行"]
    
    返回:
        List[Dict]: 包含指定证券最新行情指标的字典列表
        Dict包含字段: ['代码', '名称', '涨幅', '最新', '最高', '最低', '今开', '换手率', '量比', 
                    '市盈率', '成交量', '成交额', '昨收', '总市值', '流通市值', '市场', '时间']
        
    示例:
        data = await get_stock_realtime_data('000001')
        data = await get_stock_realtime_data(['000001', '600000', '平安银行'])
    """
    try:
        if isinstance(code_list, str):
            code_list = [code_list]
            
        logger.info(f"获取{code_list}的最新行情指标")
        df = trade.stock_realtime(code_list=code_list)
        
        if df.empty:
            logger.warning(f"获取{code_list}的最新行情指标为空")
            return []
            
        logger.info(f"获取{code_list}的最新行情指标成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取{code_list}的最新行情指标失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_intraday_data(code: str) -> List[Dict]:
    """
    获取单只证券最新交易日日内数据
    
    参数:
        code: 证券代码或名称，如"000001"或"平安银行"
    
    返回:
        List[Dict]: 包含指定证券最新交易日日内数据的字典列表
        Dict包含字段: ['名称', '代码', '时间', '昨收', '成交价', '成交量', '单数']
        
    示例:
        data = await get_intraday_data('000001')
    """
    try:
        logger.info(f"获取{code}最新交易日日内数据")
        df = trade.intraday_data(code=code)
        
        if df.empty:
            logger.warning(f"获取{code}最新交易日日内数据为空")
            return []
            
        logger.info(f"获取{code}最新交易日日内数据成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取{code}最新交易日日内数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_snapshot(code: str) -> Dict:
    """
    获取个股当天实时交易快照数据
    
    参数:
        code: 股票代码，如"000001"
    
    返回:
        Dict: 包含个股当天实时交易快照数据的字典
        Dict包含字段: ['代码', '名称', '时间', '涨跌额', '涨跌幅', '最新价', '昨收', '今开', '开盘', '最高', '最低', 
                    '均价', '涨停价', '跌停价', '换手率', '成交量', '成交额', '卖1价'至'卖5价', '买1价'至'买5价', 
                    '卖1数量'至'卖5数量', '买1数量'至'买5数量']
        
    示例:
        data = await get_stock_snapshot('000001')
    """
    try:
        logger.info(f"获取{code}当天实时交易快照数据")
        df = trade.stock_snapshot(code=code)
        
        if df.empty:
            logger.warning(f"获取{code}当天实时交易快照数据为空")
            return {}
            
        logger.info(f"获取{code}当天实时交易快照数据成功")
        return df.to_dict(orient='records')[0]
    except Exception as e:
        logger.error(f"获取{code}当天实时交易快照数据失败: {str(e)}")
        traceback.print_exc()
        return {}

@mcp.tool()
async def get_realtime_change(flag: Optional[Union[int, str]] = None) -> List[Dict]:
    """
    获取实时交易盘口异动数据
    
    参数:
        flag: 盘口异动类型，可选值:
             整数1-22或以下字符串:
             '火箭发射', '快速反弹', '加速下跌', '高台跳水', '大笔买入', '大笔卖出', 
             '封涨停板', '封跌停板', '打开跌停板', '打开涨停板', '有大买盘', '有大卖盘', 
             '竞价上涨', '竞价下跌', '高开5日线', '低开5日线', '向上缺口', '向下缺口', 
             '60日新高', '60日新低', '60日大幅上涨', '60日大幅下跌'
             默认为None，表示输出全部类型的异动情况
    
    返回:
        List[Dict]: 包含实时交易盘口异动数据的字典列表
        Dict包含字段: ['时间', '代码', '名称', '板块', '相关信息']
        
    示例:
        data = await get_realtime_change('火箭发射')
        data = await get_realtime_change(1)  # 1表示'火箭发射'
    """
    try:
        logger.info(f"获取实时交易盘口异动数据，类型: {flag}")
        df = trade.realtime_change(flag=flag)
        
        if df.empty:
            logger.warning("获取实时交易盘口异动数据为空")
            return []
            
        # 将时间列转换为字符串格式
        if '时间' in df.columns:
            df['时间'] = df['时间'].astype(str)
            
        logger.info(f"获取实时交易盘口异动数据成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取实时交易盘口异动数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_billboard(
    start: Optional[str] = None, 
    end: Optional[str] = None
) -> List[Dict]:
    """
    获取龙虎榜详情数据
    
    参数:
        start: 起始日期，格式为'YYYY-MM-DD'，如'2021-08-21'，默认为None表示最新
        end: 结束日期，格式为'YYYY-MM-DD'，如'2021-08-21'，默认为None表示最新
    
    返回:
        List[Dict]: 包含龙虎榜详情数据的字典列表
        Dict包含字段: ['股票代码', '股票名称', '上榜日期', '收盘价', '涨跌幅', '换手率',
                    '龙虎榜净买额', '流通市值', '上榜原因', '解读']
        
    示例:
        data = await get_stock_billboard()  # 获取最新龙虎榜数据
        data = await get_stock_billboard('2021-08-01', '2021-08-21')  # 获取指定日期范围的龙虎榜数据
    """
    try:
        logger.info(f"获取龙虎榜详情数据，起始日期: {start}, 结束日期: {end}")
        df = trade.stock_billboard(start=start, end=end)
        
        if df.empty:
            logger.warning("获取龙虎榜详情数据为空")
            return []
            
        logger.info(f"获取龙虎榜详情数据成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取龙虎榜详情数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_stock_sector(code: str) -> List[Dict]:
    """
    获取股票所属板块
    
    参数:
        code: 股票代码或名称，如"000001"或"平安银行"
    
    返回:
        List[Dict]: 包含股票所属板块信息的字典列表
        Dict包含字段: ['代码', '简称', '涨幅']
        
    示例:
        data = await get_stock_sector('000001')
    """
    try:
        logger.info(f"获取{code}所属板块")
        df = trade.stock_sector(code=code)
        
        if df.empty:
            logger.warning(f"获取{code}所属板块为空")
            return []
            
        logger.info(f"获取{code}所属板块成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取{code}所属板块失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_index_member(code: str) -> List[Dict]:
    """
    获取指数成分股信息
    
    参数:
        code: 指数代码或名称，如"000300"或"沪深300"
    
    返回:
        List[Dict]: 包含指数成分股信息的字典列表
        Dict包含字段: ['指数代码', '指数名称', '股票代码', '股票名称', '股票权重']
        
    示例:
        data = await get_index_member('000300')
        data = await get_index_member('沪深300')
    """
    try:
        logger.info(f"获取{code}指数成分股信息")
        df = trade.index_member(code=code)
        
        if df is None or df.empty:
            logger.warning(f"获取{code}指数成分股信息为空")
            return []
            
        logger.info(f"获取{code}指数成分股信息成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取{code}指数成分股信息失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_company_indicator(date: Optional[str] = None) -> List[Dict]:
    """
    获取沪深市场股票某一季度的财务指标
    
    参数:
        date: 报告发布日期，默认最新，如'2022-09-30'
              一季度：'2021-03-31'；二季度：'2021-06-30'
              三季度：'2021-09-30'；四季度：'2021-12-31'
    
    返回:
        List[Dict]: 包含沪深市场股票某一季度财务指标的字典列表
        Dict包含字段: ['代码', '简称', '公告日期', '营收', '营收同比', '营收环比', '净利润', 
                    '净利润同比', '净利润环比', '每股收益', '每股净资产', '净资产收益率', 
                    '销售毛利率', '每股经营现金流']
        
    示例:
        data = await get_company_indicator()  # 获取最新季度财务指标
        data = await get_company_indicator('2022-09-30')  # 获取指定季度财务指标
    """
    try:
        logger.info(f"获取沪深市场股票季度财务指标，日期: {date}")
        df = trade.company_indicator(date=date)
        
        if df.empty:
            logger.warning("获取沪深市场股票季度财务指标为空")
            return []
            
        # 确保日期列是字符串格式
        if '公告日期' in df.columns:
            df['公告日期'] = df['公告日期'].astype(str)
            
        logger.info(f"获取沪深市场股票季度财务指标成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取沪深市场股票季度财务指标失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_latest_trade_date() -> str:
    """
    获取最新交易日期
    
    参数:
        无
    
    返回:
        str: 最新交易日期，格式为'YYYY-MM-DD'
        
    示例:
        date = await get_latest_trade_date()
    """
    try:
        logger.info("获取最新交易日期")
        date = trade.latest_trade_date()
        
        if not date:
            logger.warning("获取最新交易日期为空")
            return ""
            
        logger.info(f"获取最新交易日期成功: {date}")
        return date
    except Exception as e:
        logger.error(f"获取最新交易日期失败: {str(e)}")
        traceback.print_exc()
        return ""

@mcp.tool()
async def get_stock_info(code: str) -> Dict:
    """
    获取单只个股最新的基本财务指标
    
    参数:
        code: 股票代码或名称，如"000001"或"平安银行"
    
    返回:
        Dict: 包含个股基本财务指标的字典
        Dict包含字段: ['代码', '名称', '市盈率(动)', '市净率', '所处行业', '总市值', '流通市值', 
                    'ROE', '净利率', '净利润', '毛利率']
        
    示例:
        data = await get_stock_info('000001')
    """
    try:
        logger.info(f"获取{code}的基本财务指标")
        series = trade.stock_info(code=code)
        
        if series.empty:
            logger.warning(f"获取{code}的基本财务指标为空")
            return {}
            
        logger.info(f"获取{code}的基本财务指标成功")
        return series.to_dict()
    except Exception as e:
        logger.error(f"获取{code}的基本财务指标失败: {str(e)}")
        traceback.print_exc()
        return {}

@mcp.tool()
async def get_stock_basics(code_list: Union[str, List[str]]) -> List[Dict]:
    """
    获取单只或多只股票最新的基本财务指标
    
    参数:
        code_list: 股票代码或名称，可以是单个字符串或字符串列表
                  如"000001"或["000001", "600000", "平安银行"]
    
    返回:
        List[Dict]: 包含股票基本财务指标的字典列表
        Dict包含字段: ['代码', '名称', '净利润', '总市值', '流通市值', '所处行业', '市盈率', 
                    '市净率', 'ROE', '毛利率', '净利率']
        
    示例:
        data = await get_stock_basics('000001')
        data = await get_stock_basics(['000001', '600000', '平安银行'])
    """
    try:
        if isinstance(code_list, str):
            code_list = [code_list]
            
        logger.info(f"获取{code_list}的基本财务指标")
        df = trade.stock_basics(code_list=code_list)
        
        if df.empty:
            logger.warning(f"获取{code_list}的基本财务指标为空")
            return []
            
        logger.info(f"获取{code_list}的基本财务指标成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取{code_list}的基本财务指标失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_fund_data(code_list: Union[str, List[str]]) -> List[Dict]:
    """
    获取单只或多只基金的历史净值数据
    
    参数:
        code_list: 基金代码，可以是单个字符串或字符串列表
                  如"000001"或["000001", "000002"]
    
    返回:
        List[Dict]: 包含基金历史净值数据的字典列表
        Dict包含字段: ['code', 'name', '单位净值', '累计净值', '涨跌幅']
        
    示例:
        data = await get_fund_data('000001')
        data = await get_fund_data(['000001', '000002'])
    """
    try:
        if isinstance(code_list, str):
            code_list = [code_list]
            
        logger.info(f"获取{code_list}的基金历史净值数据")
        df = trade.fund_data(code_list=code_list)
        
        if df.empty:
            logger.warning(f"获取{code_list}的基金历史净值数据为空")
            return []
            
        # 重置索引，将日期列添加到数据中
        df = df.reset_index()
        
        # 确保日期列是字符串格式
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
            
        logger.info(f"获取{code_list}的基金历史净值数据成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取{code_list}的基金历史净值数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_fund_position(code: str, n: int = 1) -> List[Dict]:
    """
    获取基金持仓信息
    
    参数:
        code: 基金代码，如"000001"
        n: 获取最近n期数据，默认为1表示最近一期数据
    
    返回:
        List[Dict]: 包含基金持仓信息的字典列表
        Dict包含字段: ['基金代码', '股票代码', '股票简称', '持仓占比', '较上期变化', '公开日期']
        
    示例:
        data = await get_fund_position('000001')  # 获取最近一期持仓
        data = await get_fund_position('000001', 2)  # 获取最近两期持仓
    """
    try:
        logger.info(f"获取{code}的基金持仓信息，最近{n}期")
        df = trade.fund_position(code=code, n=n)
        
        if df.empty:
            logger.warning(f"获取{code}的基金持仓信息为空")
            return []
            
        # 确保日期列是字符串格式
        if '公开日期' in df.columns:
            df['公开日期'] = df['公开日期'].astype(str)
            
        logger.info(f"获取{code}的基金持仓信息成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取{code}的基金持仓信息失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_fund_info(code_list: Optional[Union[str, List[str]]] = None, ft: str = 'gp') -> List[Dict]:
    """
    获取基金基本信息
    
    参数:
        code_list: 基金代码，可以是单个字符串或字符串列表
                  如"000001"或["000001", "000002"]
                  默认为None，表示获取指定类型的所有基金
        ft: 基金类型，当code_list为None时有效，可选值:
            'zq': 债券类型基金
            'gp': 股票类型基金(默认)
            'etf': ETF基金
            'hh': 混合型基金
            'zs': 指数型基金
            'fof': FOF基金
            'qdii': QDII型基金
    
    返回:
        List[Dict]: 包含基金基本信息的字典列表
        Dict包含字段: ['基金代码', '基金简称', '成立日期', '涨跌幅', '最新净值', '基金公司', 
                    '净值更新日期', '简介']
        
    示例:
        data = await get_fund_info('000001')  # 获取单只基金信息
        data = await get_fund_info(ft='etf')  # 获取所有ETF基金信息
    """
    try:
        logger.info(f"获取基金基本信息，基金代码: {code_list}, 基金类型: {ft}")
        df = trade.fund_info(code_list=code_list, ft=ft)
        
        if df.empty:
            logger.warning("获取基金基本信息为空")
            return []
            
        # 确保日期列是字符串格式
        if '成立日期' in df.columns:
            df['成立日期'] = df['成立日期'].astype(str)
        if '净值更新日期' in df.columns:
            df['净值更新日期'] = df['净值更新日期'].astype(str)
            
        logger.info(f"获取基金基本信息成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取基金基本信息失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_bond_info(code_list: Optional[Union[str, List[str]]] = None) -> List[Dict]:
    """
    获取单只或多只债券基本信息
    
    参数:
        code_list: 债券代码，可以是单个字符串或字符串列表
                  如"123456"或["123456", "123457"]
                  默认为None，表示获取所有债券信息
    
    返回:
        List[Dict]: 包含债券基本信息的字典列表
        Dict包含字段: ['债券代码', '债券名称', '正股代码', '正股名称', '债券评级', '申购日期', 
                    '发行规模(亿)', '网上发行中签率(%)', '上市日期', '到期日期', '期限(年)', 
                    '利率说明']
        
    示例:
        data = await get_bond_info('123456')  # 获取单只债券信息
        data = await get_bond_info()  # 获取所有债券信息
    """
    try:
        logger.info(f"获取债券基本信息，债券代码: {code_list}")
        df = trade.bond_info(code_list=code_list)
        
        if df.empty:
            logger.warning("获取债券基本信息为空")
            return []
            
        # 确保日期列是字符串格式
        date_cols = ['申购日期', '上市日期', '到期日期']
        for col in date_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
                
        logger.info(f"获取债券基本信息成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取债券基本信息失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_future_info() -> List[Dict]:
    """
    获取期货基本信息
    
    参数:
        无
    
    返回:
        List[Dict]: 包含期货基本信息的字典列表
        Dict包含字段: ['代码', '名称', '涨幅', '最新', 'ID', '市场', '时间']
        
    示例:
        data = await get_future_info()
    """
    try:
        logger.info("获取期货基本信息")
        df = trade.future_info()
        
        if df.empty:
            logger.warning("获取期货基本信息为空")
            return []
            
        # 确保时间列是字符串格式
        if '时间' in df.columns:
            df['时间'] = df['时间'].astype(str)
            
        logger.info(f"获取期货基本信息成功，共{df.shape[0]}条记录")
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取期货基本信息失败: {str(e)}")
        traceback.print_exc()
        return []

