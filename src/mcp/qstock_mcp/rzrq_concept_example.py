#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''融资融券概念板块排行数据获取示例'''

from stock_rzrq import get_rzrq_concept_rank
import json

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
    # 示例1：获取融资融券概念板块排行数据（按融资净买入额降序，使用中文字段）
    print("示例1：获取融资融券概念板块排行数据（按融资净买入额降序，使用中文字段）")
    concept_data = get_rzrq_concept_rank(page=1, page_size=10, sort_column="FIN_NETBUY_AMT", sort_type=-1, use_chinese_fields=True)
    if concept_data:
        # 打印总页数和数据条数
        print(f"总页数: {concept_data['result']['pages']}")
        print(f"总数据条数: {concept_data['result']['count']}")
        
        # 打印前10条数据的关键信息
        print("\n融资融券概念板块排行数据（按融资净买入额降序）:")
        for item in concept_data['result']['data']:
            print(f"概念板块: {item['板块名称']} (代码: {item['板块代码']})")
            print(f"  融资余额: {format_number(item['融资余额'])} 元")
            print(f"  融资余额占比: {format_percent(item['融资余额占比'])}")
            print(f"  融资买入额: {format_number(item['融资买入额'])} 元")
            print(f"  融资偿还额: {format_number(item['融资偿还额'])} 元")
            print(f"  融资净买入额: {format_number(item['融资净买入额'])} 元")
            print(f"  融券余额: {format_number(item['融券余额'])} 元")
            print(f"  融券余量: {format_number(item['融券余量'])} 股")
            print(f"  融资融券余额: {format_number(item['融资融券余额'])} 元")
            print("-" * 50)
    
    print("\n" + "-" * 80 + "\n")
    
    # 示例2：获取融资融券概念板块排行数据（按融资余额占比降序）
    print("示例2：获取融资融券概念板块排行数据（按融资余额占比降序）")
    concept_data_ratio = get_rzrq_concept_rank(
        page=1,
        page_size=10,
        sort_column="FIN_BALANCE_RATIO",
        sort_type=-1,
        use_chinese_fields=True
    )
    if concept_data_ratio:
        print(f"总页数: {concept_data_ratio['result']['pages']}")
        print(f"总数据条数: {concept_data_ratio['result']['count']}")
        
        # 打印前10条数据的关键信息
        print("\n融资融券概念板块排行数据（按融资余额占比降序）:")
        for item in concept_data_ratio['result']['data']:
            print(f"概念板块: {item['板块名称']} (代码: {item['板块代码']})")
            print(f"  融资余额: {format_number(item['融资余额'])} 元")
            print(f"  融资余额占比: {format_percent(item['融资余额占比'])}")
            print(f"  流通市值: {format_number(item['流通市值'])} 元")
            print(f"  融资融券余额: {format_number(item['融资融券余额'])} 元")
            print(f"  融资融券余额差值: {format_number(item['融资余额差值'])} 元")
            print("-" * 50)
    
    print("\n" + "-" * 80 + "\n")
    
    # 示例3：获取融资融券概念板块排行数据（使用原始英文字段）
    print("示例3：获取融资融券概念板块排行数据（使用原始英文字段）")
    concept_data_en = get_rzrq_concept_rank(page=1, page_size=5, use_chinese_fields=False)
    if concept_data_en:
        print("\n使用英文字段的融资融券概念板块排行数据:")
        print_json(concept_data_en['result']['data'])

if __name__ == "__main__":
    main()