#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''市场融资融券交易总量数据获取示例'''

from stock_rzrq import get_rzrq_market_summary
import json
from datetime import datetime, timedelta

def print_json(data):
    """格式化打印JSON数据"""
    print(json.dumps(data, ensure_ascii=False, indent=2))

def format_number(num):
    """格式化数字为带千分位的字符串"""
    if isinstance(num, (int, float)):
        return f"{num:,}"
    return str(num)

def format_percent(num):
    """格式化百分比数字"""
    if isinstance(num, (int, float)):
        return f"{num:.2f}%"
    return str(num)

def main():
    # 示例1：获取最近市场融资融券交易总量数据（使用中文字段）
    print("示例1：获取最近市场融资融券交易总量数据（使用中文字段）")
    summary_data = get_rzrq_market_summary(page=1, page_size=5, use_chinese_fields=True)
    if summary_data:
        # 打印总页数和数据条数
        print(f"总页数: {summary_data['result']['pages']}")
        print(f"总数据条数: {summary_data['result']['count']}")
        
        # 打印前5条数据的关键信息
        print("\n市场融资融券交易总量数据:")
        for item in summary_data['result']['data']:
            print(f"日期: {item['交易日期']}")
            print(f"  上证指数: {item['上证指数收盘点位']} (涨跌幅: {format_percent(item['上证指数涨跌幅'])})")
            print(f"  融资余额: {format_number(item['融资余额'])} 元 (占比: {format_percent(item['融资余额占比'])})")
            print(f"  融资买入额: {format_number(item['融资买入额'])} 元")
            print(f"  融资偿还额: {format_number(item['融资偿还额'])} 元")
            print(f"  融资净买入: {format_number(item['融资净买入'])} 元")
            print(f"  融券余额: {format_number(item['融券余额'])} 元")
            print(f"  融券余量: {format_number(item['融券余量'])} 股")
            print(f"  融资融券余额: {format_number(item['融资融券余额'])} 元")
            print("-" * 50)
    
    print("\n" + "-" * 80 + "\n")
    
    # 示例2：获取指定日期范围的市场融资融券交易总量数据
    # 计算一个月前的日期
    today = datetime.now()
    one_month_ago = today - timedelta(days=30)
    start_date = one_month_ago.strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    
    print(f"示例2：获取指定日期范围的市场融资融券交易总量数据（{start_date}至{end_date}）")
    summary_data_range = get_rzrq_market_summary(
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=3,
        use_chinese_fields=True
    )
    if summary_data_range:
        print(f"总页数: {summary_data_range['result']['pages']}")
        print(f"总数据条数: {summary_data_range['result']['count']}")
        
        # 打印前3条数据的关键信息
        print("\n指定日期范围的市场融资融券交易总量数据:")
        for item in summary_data_range['result']['data']:
            print(f"日期: {item['交易日期']}")
            print(f"  上证指数: {item['上证指数收盘点位']} (涨跌幅: {format_percent(item['上证指数涨跌幅'])})")
            print(f"  融资余额: {format_number(item['融资余额'])} 元")
            print(f"  融资买入额: {format_number(item['融资买入额'])} 元")
            print(f"  融资买入额3日: {format_number(item['融资买入额3日'])} 元")
            print(f"  融资买入额5日: {format_number(item['融资买入额5日'])} 元")
            print(f"  融资净买入: {format_number(item['融资净买入'])} 元")
            print(f"  融资净买入3日: {format_number(item['融资净买入3日'])} 元")
            print(f"  融资净买入5日: {format_number(item['融资净买入5日'])} 元")
            print("-" * 50)
    
    print("\n" + "-" * 80 + "\n")
    
    # 示例3：获取市场融资融券交易总量数据（使用原始英文字段）
    print("示例3：获取市场融资融券交易总量数据（使用原始英文字段）")
    summary_data_en = get_rzrq_market_summary(page=1, page_size=2, use_chinese_fields=False)
    if summary_data_en:
        print("\n使用英文字段的市场融资融券交易总量数据:")
        print_json(summary_data_en['result']['data'])

if __name__ == "__main__":
    main()