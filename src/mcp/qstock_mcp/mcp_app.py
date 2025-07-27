#!/usr/bin/env python
# -*- encoding=utf8 -*-

import sys
import logging
import traceback
import argparse
import qstock as qs
import replace_qstock_func
from mcp_instance import mcp
import mcp_index as index
import mcp_qh as qh
import mcp_option_qvix as qvix
import mcp_macro as macro
import mcp_rzrq as rzrq
import mcp_news as news
import mcp_industry as industry
import mcp_money as money
import mcp_fundamental as fundamental
import mcp_wencai as wencai
import mcp_stock_pool as stock_pool
import mcp_trade as trade
import mcp_option as option
from common_utils import get_stock_indicators

logger = logging.getLogger('mcp-stock')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Add an addition tool

@mcp.tool()
async def get_stock_history_data(code: list|str, freq: str = "d", fqt: int=1, start_date: str = '19000101', end_date: str = None, indicator: bool = False) -> list:
    """ 获取指定股票代码的历史数据
    参数：
    - code: 股票代码或名称，可以是字符串也可以是列表，如"000001"、"600000"等
    - freq: 数据频率，时间频率，默认是日(d)，
      - 1 : 分钟；
      - 5 : 5 分钟；
      - 15 : 15 分钟；
      - 30 : 30 分钟；
      - 60 : 60 分钟；
      - 101或'D'或'd'：日；
      - 102或‘w’或'W'：周; 
      - 103或'm'或'M': 月
    - start_date: 开始日期，格式为"YYYY-MM-DD"，如"2023-01-01"，默认为'19000101'（取尽可能早的数据）
    - end_date: 结束日期，格式为"YYYY-MM-DD"，如"2023-12-31"，默认为None（取到最新数据）
    - fqt: 前复权方式，默认为1（前复权），0为不复权，2为后复权
    - indicator: 是否计算技术指标，默认为False，不计算
    返回：
    - List[Dict]: 包含股票历史数据，
    Dict包含字段: ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
    - 如果indicator为True，则还会包含技术指标数据，如BOLL、MACD等返回字段包含：
    Dict包含字段: ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
    额外的技术指标字段：
    BOLL: 布林指标，包含boll_upper, boll_middle, boll_lower
    OBV: 能量潮指标，包含obv
    RSI: 相对强弱指标，包含rsi, rsi_ma, rsi_gc, rsi_dc
    EXPMA: 指数平滑移动平均线，包含expma, expma_ma, expma_gc, expma_dc
    MACD: 平滑异同移动平均线，包含diff, dea, macd, macd_gc, macd_dc
    KDJ: 随机指标，包含kdj_k, kdj_d, kdj_j, kdj_gc, kdj_dc
    VolumeAnalyze: 量能分析，包含va5, va10, va_gc, va_dc
    SupportAnalyze: 支撑位分析，包含sp30_max, sp30_min, sp30, sp45_max, sp45_min, sp45, sp60_max, sp60_min, sp60, sp75_max, sp75_min, sp75, sp90_max, sp90_min, sp90, sp120_max, sp120_min, sp120
    技术字段中的gc表示金叉，dc表示死叉
    """
    # 参数验证
    if not code:
        logger.error("参数 'code' 不能为空")
        return []
    
    # 验证频率参数
    valid_freqs = [1, 5, 15, 30, 60, 'd', 'D', 'w', 'W', 'm', 'M', 101, 102, 103]
    if freq not in valid_freqs:
        logger.warning(f"参数 'freq' 必须是以下值之一: {', '.join(valid_freqs)}，当前值为: {freq}，将使用默认值'daily'")
        freq = "d"
    
    # 使用qstock获取股票历史数据
    try:
        # 调用qstock.get_data函数获取历史数据
        df = qs.get_data(code, start=start_date, end=end_date, freq=freq, fqt=fqt)
        
        logger.info(f"获取股票 {code} 的历史数据: {df}")
        if df.empty:
            logger.warning(f"获取的股票 {code} 历史数据为空")
            return []
        
        # 如果需要计算技术指标，则调用get_stock_indicators函数计算技术指标
        if indicator:
            df = get_stock_indicators(df)

        # 重置索引
        df = df.reset_index()
                
        logger.info(f"股票 {code} 历史数据获取成功: {df.shape[0]} 条记录")
        logger.info(f"股票历史数据列名: {df.columns.tolist()}")
        
        # 确保日期列是字符串格式
        if '日期' in df.columns:
            df['日期'] = df['日期'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取股票 {code} 的历史数据失败: {str(e)}")
        traceback.print_exc()
    return []

@mcp.tool()
async def get_china_latest_trade_day() -> dict:
    """ 获取A股最后一个交易日
    参数：
    - 无
    返回：
    - Dict: 包含最后一个交易日信息，
    Dict包含字段: ['trade_date', 'is_open']，其中trade_date为交易日期（格式为YYYY-MM-DD），is_open表示当天是否为交易日（1为是，0为否）
    """
    # 使用qstock获取A股最后一个交易日
    try:
        # 调用qstock.latest_trade_day函数获取最后一个交易日
        latest_day = qs.latest_trade_date()
        
        logger.info(f"获取A股最后一个交易日: {latest_day}")
        
        # 构建返回结果
        result = {
            "trade_date": str(latest_day),
            "is_open": 1  # 默认为交易日
        }
        
        # 检查今天是否为交易日
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        if latest_day != today:
            result["is_open"] = 0  # 如果最后交易日不是今天，则今天不是交易日
        
        return result
    except Exception as e:
        logger.error(f"获取A股最后一个交易日失败: {str(e)}")
        traceback.print_exc()
        return {"trade_date": "", "is_open": 0, "error": str(e)}

@mcp.tool()
async def get_stock_intraday_money(code: str) -> list:
    """ 获取股票即时资金流入流出情况
    参数：
    - code: 股票代码或名称，如"000001"、"600000"等
    返回：
    - List[Dict]: 包含股票即时资金流入流出数据，
    Dict包含字段: ['名称', '代码', '时间', '主力净流入', '小单净流入', '中单净流入', '大单净流入', '超大单净流入']
    """
    # 参数验证
    if not code:
        logger.error("参数 'code' 不能为空")
        return []
    
    # 使用qstock获取股票即时资金流入流出数据
    try:
        # 调用qstock.intraday_money函数获取即时资金流入流出数据
        df = qs.intraday_money(code)
        
        logger.info(f"获取股票 {code} 的即时资金流入流出数据")
        if df.empty:
            logger.warning(f"获取的股票 {code} 即时资金流入流出数据为空")
            return []
                
        logger.info(f"股票 {code} 即时资金流入流出数据获取成功: {df.shape[0]} 条记录")
        logger.info(f"股票即时资金流入流出数据列名: {df.columns.tolist()}")
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取股票 {code} 的即时资金流入流出数据失败: {str(e)}")
        traceback.print_exc()
    return []

@mcp.tool()
async def get_stock_hist_money(code: str, start_date: str = None, end_date: str = None) -> list:
    """ 获取股票历史资金流入流出情况
    参数：
    - code: 股票代码或名称，如"000001"、"600000"等
    - start_date: 开始日期，格式为"YYYY-MM-DD"，如"2023-01-01"，默认为None（取最近10个交易日）
    - end_date: 结束日期，格式为"YYYY-MM-DD"，如"2023-12-31"，默认为None（取到最新数据）
    返回：
    - List[Dict]: 包含股票历史资金流入流出数据，
    Dict包含字段: ['名称', '代码', '日期', '主力净流入', '小单净流入', '中单净流入', '大单净流入', '超大单净流入',
       '主力净流入占比', '小单流入净占比', '中单流入净占比', '大单流入净占比', '超大单流入净占比', '收盘价', '涨跌幅']
    """
    # 参数验证
    if not code:
        logger.error("参数 'code' 不能为空")
        return []
    
    # 使用qstock获取股票历史资金流入流出数据
    try:
        # 调用qstock.hist_money函数获取历史资金流入流出数据
        df = qs.hist_money(code)
        
        logger.info(f"获取股票 {code} 的历史资金流入流出数据")
        if df.empty:
            logger.warning(f"获取的股票 {code} 历史资金流入流出数据为空")
            return []
                
        logger.info(f"股票 {code} 历史资金流入流出数据获取成功: {df.shape[0]} 条记录")
        logger.info(f"股票历史资金流入流出数据列名: {df.columns.tolist()}")
        
        # 确保日期列是字符串格式
        if '日期' in df.columns:
            df['日期'] = df['日期'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取股票 {code} 的历史资金流入流出数据失败: {str(e)}")
        traceback.print_exc()
    return []
    
# Start the server
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the MCP server")
    parser.add_argument('-t', '--transport', type=str, default='stdio', help='Transport type for the MCP server (default: stdio)')
    parser.add_argument('-p', '--port', type=int, default=8000, help='Port number for the MCP server (default: 8000)')
    parser.add_argument('-H', '--host', type=str, default='127.0.0.1', help='Host to listen on when using sse or http transport (default: 127.0.0.1)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    transport = args.transport
    port = args.port
    host = args.host

    logger.info("Starting MCP server as a %s server...", transport)
    
    # 根据传输方式决定是否需要设置host和port
    if transport in ['sse', 'streamable-http']:
        logger.info(f"Server will listen on {host}:{port}")
        # 在FastMCP实例上设置host和port属性
        mcp.settings.host = host
        mcp.settings.port = port
    
    # 运行MCP服务器，不在run方法中传递host和port参数
    if transport == "sse":
        mcp.run(transport=transport, mount_path="/")
    elif transport == "streamable-http":
        mcp.run(transport=transport, mount_path="/mcp")
    else:
        mcp.run(transport=transport)
    
    logger.info("MCP server started successfully.")
    logger.info("Press Ctrl+C to stop the server.")