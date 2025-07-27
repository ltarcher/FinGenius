#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''融资融券行业板块数据获取示例（中文字段版）'''

from stock_rzrq import get_rzrq_industry_rank, get_rzrq_industry_detail
import json

def print_json(data):
    """格式化打印JSON数据"""
    print(json.dumps(data, ensure_ascii=False, indent=2))

def main():
    # 示例1：获取融资融券行业板块排行数据（默认按融资净买入额降序，使用中文字段）
    print("示例1：获取融资融券行业板块排行数据（默认按融资净买入额降序，使用中文字段）")
    industry_rank = get_rzrq_industry_rank(page=1, page_size=5, use_chinese_fields=True)
    if industry_rank:
        # 打印总页数和数据条数
        print(f"总页数: {industry_rank['result']['pages']}")
        print(f"总数据条数: {industry_rank['result']['count']}")
        
        # 打印前5条数据的关键信息
        print("\n行业板块排行数据:")
        for item in industry_rank['result']['data']:
            print(f"板块: {item['板块名称']}, "
                  f"日期: {item['交易日期']}, "
                  f"融资余额(元): {item['融资余额']}, "
                  f"融资净买入(元): {item['融资净买入额']}")
    
    print("\n" + "-" * 80 + "\n")
    
    # 示例2：获取特定行业板块的融资融券明细数据（以"通信设备"板块为例，使用中文字段）
    print("示例2：获取特定行业板块的融资融券明细数据（以'通信设备'板块为例，使用中文字段）")
    # 通信设备板块代码为448
    industry_detail = get_rzrq_industry_detail(board_code="448", page=1, page_size=5, use_chinese_fields=True)
    if industry_detail:
        # 打印总页数和数据条数
        print(f"总页数: {industry_detail['result']['pages']}")
        print(f"总数据条数: {industry_detail['result']['count']}")
        
        # 打印前5条数据的关键信息
        print("\n通信设备板块融资融券明细数据:")
        for item in industry_detail['result']['data']:
            print(f"日期: {item['交易日期']}, "
                  f"融资余额(元): {item['融资余额']}, "
                  f"融资买入额(元): {item['融资买入额']}, "
                  f"融资偿还额(元): {item['融资偿还额']}")
    
    # 示例3：按融资余额排序获取行业板块排行（使用中文字段）
    print("\n" + "-" * 80 + "\n")
    print("示例3：按融资余额排序获取行业板块排行（使用中文字段）")
    industry_rank_by_balance = get_rzrq_industry_rank(
        page=1, 
        page_size=5, 
        sort_column="FIN_BALANCE", 
        sort_type=-1,  # 降序
        use_chinese_fields=True
    )
    if industry_rank_by_balance:
        print("\n按融资余额排序的行业板块排行:")
        for item in industry_rank_by_balance['result']['data']:
            print(f"板块: {item['板块名称']}, "
                  f"融资余额(元): {item['融资余额']}, "
                  f"融资余额占比(%): {item['融资余额占比']}")
    
    # 示例4：获取融资融券行业板块排行数据（使用原始英文字段）
    print("\n" + "-" * 80 + "\n")
    print("示例4：获取融资融券行业板块排行数据（使用原始英文字段）")
    industry_rank_en = get_rzrq_industry_rank(page=1, page_size=2, use_chinese_fields=False)
    if industry_rank_en:
        print("\n使用英文字段的行业板块排行数据:")
        print_json(industry_rank_en['result']['data'])

if __name__ == "__main__":
    main()