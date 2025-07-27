#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试MCP工具函数的脚本
此脚本将测试所有已实现的MCP工具函数，并显示结果
"""

import asyncio
import json
import sys
import logging
from datetime import datetime
from mcp_app import (
    get_index_realtime_data,
    get_option_target_list,
    get_option_realtime_data,
    get_option_value_data,
    get_option_risk_data,
    get_option_tboard_data,
    get_option_expire_all_data,
    get_option_expire_info_data,
    get_usd_index_data,
    get_ftse_a50_futures_data,
    get_usd_cnh_futures_data,
    get_thirty_year_bond_futures_data,
    get_stock_history_data
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('MCP_Test')

# 格式化输出函数
def format_output(title, data):
    """格式化输出测试结果"""
    print("\n" + "=" * 80)
    print(f"测试: {title}")
    print("=" * 80)
    
    if not data:
        print("无数据返回")
        return
    
    if isinstance(data, list) and len(data) > 0:
        # 显示第一条记录的详细信息
        print(f"返回 {len(data)} 条记录，第一条记录:")
        print(json.dumps(data[0], ensure_ascii=False, indent=2))
        
        # 如果有多条记录，显示所有记录的简要信息
        if len(data) > 1:
            print(f"\n所有记录简要信息:")
            for i, item in enumerate(data):
                if i < 5:  # 只显示前5条
                    if 'name' in item:
                        print(f"{i+1}. {item.get('name', 'N/A')}")
                    elif '名称' in item:
                        print(f"{i+1}. {item.get('名称', 'N/A')}")
                    elif 'code' in item:
                        print(f"{i+1}. {item.get('code', 'N/A')}")
                    elif '代码' in item:
                        print(f"{i+1}. {item.get('代码', 'N/A')}")
                    else:
                        print(f"{i+1}. {str(item)[:50]}...")
            
            if len(data) > 5:
                print(f"... 还有 {len(data) - 5} 条记录")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))

# 测试函数
async def test_all_tools():
    """测试所有MCP工具函数"""
    start_time = datetime.now()
    logger.info(f"开始测试 MCP 工具函数，时间: {start_time}")
    
    # 测试 get_index_realtime_data
    try:
        logger.info("测试 get_index_realtime_data...")
        data = await get_index_realtime_data(codes=['上证指数', '深证成指', '创业板指'])
        format_output("获取中国金融市场多个指数的实时数据", data)
    except Exception as e:
        logger.error(f"测试 get_index_realtime_data 失败: {str(e)}")
    
    # 测试 get_option_target_list
    try:
        logger.info("测试 get_option_target_list...")
        data = await get_option_target_list()
        format_output("获取中国金融市场期权标的列表", data)
    except Exception as e:
        logger.error(f"测试 get_option_target_list 失败: {str(e)}")
    
    # 测试 get_option_realtime_data
    try:
        logger.info("测试 get_option_realtime_data...")
        # 由于期权代码可能会变化，这里不指定具体代码，让函数返回默认数据
        data = await get_option_realtime_data(codes=[])
        format_output("获取中国金融市场期权的实时数据", data)
    except Exception as e:
        logger.error(f"测试 get_option_realtime_data 失败: {str(e)}")
    
    # 测试 get_option_value_data
    try:
        logger.info("测试 get_option_value_data...")
        data = await get_option_value_data(codes=[])
        format_output("获取中国金融市场期权的价值数据", data)
    except Exception as e:
        logger.error(f"测试 get_option_value_data 失败: {str(e)}")
    
    # 测试 get_option_risk_data
    try:
        logger.info("测试 get_option_risk_data...")
        data = await get_option_risk_data(codes=[])
        format_output("获取中国金融市场期权的风险数据", data)
    except Exception as e:
        logger.error(f"测试 get_option_risk_data 失败: {str(e)}")
    
    # 测试 get_option_tboard_data
    try:
        logger.info("测试 get_option_tboard_data...")
        data = await get_option_tboard_data()
        format_output("获取期权T型看板数据", data)
    except Exception as e:
        logger.error(f"测试 get_option_tboard_data 失败: {str(e)}")
    
    # 测试 get_option_expire_all_data
    try:
        logger.info("测试 get_option_expire_all_data...")
        data = await get_option_expire_all_data()
        format_output("获取所有期权市场的到期日信息", data)
    except Exception as e:
        logger.error(f"测试 get_option_expire_all_data 失败: {str(e)}")
    
    # 测试 get_option_expire_info_data
    try:
        logger.info("测试 get_option_expire_info_data...")
        # 使用50ETF期权代码
        data = await get_option_expire_info_data(code="510050", market=1)
        format_output("获取指定期权代码的到期日信息", data)
    except Exception as e:
        logger.error(f"测试 get_option_expire_info_data 失败: {str(e)}")
    
    # 测试 get_usd_index_data
    try:
        logger.info("测试 get_usd_index_data...")
        data = await get_usd_index_data()
        format_output("获取美元指数实时数据", data)
    except Exception as e:
        logger.error(f"测试 get_usd_index_data 失败: {str(e)}")
    
    # 测试 get_ftse_a50_futures_data
    try:
        logger.info("测试 get_ftse_a50_futures_data...")
        data = await get_ftse_a50_futures_data()
        format_output("获取富时A50期货指数实时数据", data)
    except Exception as e:
        logger.error(f"测试 get_ftse_a50_futures_data 失败: {str(e)}")
    
    # 测试 get_usd_cnh_futures_data
    try:
        logger.info("测试 get_usd_cnh_futures_data...")
        data = await get_usd_cnh_futures_data()
        format_output("获取美元兑离岸人民币主连实时数据", data)
    except Exception as e:
        logger.error(f"测试 get_usd_cnh_futures_data 失败: {str(e)}")
    
    # 测试 get_thirty_year_bond_futures_data
    try:
        logger.info("测试 get_thirty_year_bond_futures_data...")
        data = await get_thirty_year_bond_futures_data()
        format_output("获取三十年国债主连实时数据", data)
    except Exception as e:
        logger.error(f"测试 get_thirty_year_bond_futures_data 失败: {str(e)}")
    
    # 测试 get_stock_history_data
    try:
        logger.info("测试 get_stock_history_data...")
        # 测试上证指数历史数据
        data = await get_stock_history_data(code="000001", start_date="2023-01-01", end_date="2023-01-31", freq="d")
        format_output("获取上证指数历史数据（2023年1月日线）", data)
        
        # 测试平安银行历史数据（周线）
        data = await get_stock_history_data(code="000001", start_date="2023-01-01", end_date="2023-06-30", freq="w")
        format_output("获取平安银行历史数据（2023年上半年周线）", data)
        
        # 测试贵州茅台历史数据（月线）
        data = await get_stock_history_data(code="600519", start_date="2022-01-01", end_date="2022-12-31", freq="m")
        format_output("获取贵州茅台历史数据（2022年月线）", data)
    except Exception as e:
        logger.error(f"测试 get_stock_history_data 失败: {str(e)}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"测试完成，耗时: {duration:.2f} 秒")

# 主函数
if __name__ == "__main__":
    print("开始测试 MCP 工具函数...")
    asyncio.run(test_all_tools())
    print("\n测试完成！")