# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
期货龙虎榜数据
封装东方财富期货龙虎榜数据接口
"""

import pandas as pd
import requests
import json
import urllib.parse
from typing import Dict, Optional, Union
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 默认请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://data.eastmoney.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive"
}

class FuturesLHB:
    """
    东方财富期货龙虎榜数据接口封装
    
    该类提供了获取东方财富网站期货龙虎榜数据的功能。
    由于东方财富网站可能需要cookies验证，所以提供了设置和更新cookies的方法。
    
    基本用法:
        # 初始化
        lhb = FuturesLHB(cookies=cookies)
        
        # 获取数据
        df = lhb.get_data(
            security_code="IF2509",
            trade_date="2025-07-18",
            sort_field="VOLUMERANK"
        )
    """
    
    # 字段中英文映射字典
    FIELD_MAPPING = {
        # 基础信息字段
        "SECUCODE": "证券代码",
        "SECURITY_CODE": "合约代码",
        "SECURITY_INNER_CODE": "证券内部编码",
        "TRADE_MARKET_CODE": "交易市场代码",
        "TRADE_DATE": "交易日期",
        "ORG_CODE": "机构代码",
        "MEMBER_NAME_ABBR": "会员简称",
        "TRADE_CODE": "交易代码",
        "CORRECODE": "对应代码",
        "ORG_NAME_ABBR_NEW": "机构简称",
        "TYPE": "数据类型",
        
        # 排名字段
        "VOLUMERANK": "成交量排名",
        "VOLUME_RANK": "成交量排名(备用)",
        "LPRANK": "多头持仓排名",
        "LP_RANK": "多头持仓排名(备用)",
        "SPRANK": "空头持仓排名",
        "SP_RANK": "空头持仓排名(备用)",
        "NLPRANK": "净多头排名",
        "NLP_RANK": "净多头排名(备用)",
        "LPUPRANK": "多头增仓排名",
        "LP_UP_RANK": "多头增仓排名(备用)",
        "LPDOWNRANK": "多头减仓排名",
        "LP_DOWN_RANK": "多头减仓排名(备用)",
        "NSPRANK": "净空头排名",
        "NSP_RANK": "净空头排名(备用)",
        "SPUPRANK": "空头增仓排名",
        "SP_UP_RANK": "空头增仓排名(备用)",
        "SPDOWNRANK": "空头减仓排名",
        "SP_DOWN_RANK": "空头减仓排名(备用)",
        
        # 数值字段
        "VOLUME": "成交量",
        "VOLUME_CHANGE": "成交量变化",
        "LONG_POSITION": "多头持仓",
        "LP_CHANGE": "多头持仓变化",
        "SHORT_POSITION": "空头持仓",
        "SP_CHANGE": "空头持仓变化",
        "NET_LONG_POSITION": "净多头持仓",
        "NLP_CHANGE": "净多头持仓变化",
        "NET_SHORT_POSITION": "净空头持仓",
        "NSP_CHANGE": "净空头持仓变化",
        "SETTLE_PRICE": "结算价",
        "LP_AVERAGE_PRICE": "多头平均价格",
        "SP_AVERAGE_PRICE": "空头平均价格"
    }
    
    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        初始化龙虎榜数据接口
        
        参数:
            cookies: 请求时使用的cookies，字典格式
        """
        self.base_url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        self.report_name = "RPT_FUTU_DAILYPOSITION"
        self.default_columns = "ALL"
        self.timeout = 10
        self.retry_times = 3
        self.headers = headers.copy()
        self.cookies = cookies or {}
    
    def set_cookies(self, cookies: Dict[str, str]) -> None:
        """
        设置请求cookies
        
        参数:
            cookies: 新的cookies字典
        """
        self.cookies.update(cookies)
        logger.info("已更新cookies")
    
    def is_cookies_valid(self) -> bool:
        """
        检查当前cookies是否有效
        
        返回:
            bool: cookies是否有效
        """
        try:
            # 发送一个简单请求来检查cookies是否有效
            response = requests.get(
                "https://data.eastmoney.com/IF/Data/Contract.html",
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # 检查响应中是否包含需要登录的标识
            if "用户登录" in response.text or "请登录" in response.text:
                logger.warning("Cookies无效或已过期")
                return False
            return True
        except Exception as e:
            logger.error(f"检查cookies时出错: {e}")
            return False
    
    @staticmethod
    def get_cookies_guide() -> str:
        """
        获取从浏览器获取cookies的指南
        
        返回:
            str: 获取cookies的指南
        """
        guide = """
如何获取东方财富网站的cookies:

1. 使用Chrome浏览器访问 https://data.eastmoney.com/IF/Data/Contract.html
2. 按F12打开开发者工具
3. 切换到"Network"(网络)选项卡
4. 刷新页面
5. 在请求列表中找到主页面请求
6. 右键点击请求，选择"Copy" -> "Copy as cURL"
7. 从cURL命令中提取cookies部分(通常在-H "Cookie: xxx"部分)
8. 将cookies字符串解析为字典格式

或者使用浏览器扩展如"EditThisCookie"直接导出cookies
        """
        return guide
        
    def get_data(
        self, 
        security_code: str, 
        trade_date: str, 
        data_type: str = "0", 
        sort_field: Optional[str] = None,
        page_size: int = 20,
        use_chinese_fields: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        获取龙虎榜数据
        
        参数:
            security_code: 合约代码(如IF2509)
            trade_date: 交易日期(YYYY-MM-DD)
            data_type: 数据类型(0:全部,2:特定类型)
            sort_field: 排序字段(如VOLUMERANK, LPRANK等)
            page_size: 每页数据量
            use_chinese_fields: 是否使用中文字段名，默认为True
            **kwargs: 其他过滤条件(如LP_CHANGE=">0")
            
        返回:
            pandas.DataFrame: 包含龙虎榜数据的DataFrame
            
        异常:
            ValueError: 参数错误或数据获取失败
            requests.exceptions.RequestException: 网络请求异常
        """
        # 构建基础参数
        params = {
            "reportName": self.report_name,
            "columns": self.default_columns,
            "source": "WEB",
            "client": "WEB",
            "pageNumber": 1,
            "pageSize": page_size
        }
        
        # 构建过滤条件
        filters = [
            f"(SECURITY_CODE=\"{security_code}\")",
            f"(TRADE_DATE='{trade_date}')",
            f"(TYPE={data_type})"
        ]
        
        # 添加排序条件
        if sort_field:
            params.update({
                "sortTypes": "1",
                "sortColumns": sort_field
            })
            filters.append(f"({sort_field}<>9999)")
        
        # 添加额外过滤条件
        for key, value in kwargs.items():
            filters.append(f"({key}{value})")
        
        # 组合所有过滤条件
        params["filter"] = "".join(filters)
        
        # 检查cookies是否设置
        if not self.cookies:
            logger.warning("未设置cookies，可能导致请求失败或数据不完整")
        
        # 发送请求
        for attempt in range(self.retry_times):
            try:
                # 构建完整URL
                query_string = urllib.parse.urlencode(params)
                full_url = f"{self.base_url}?{query_string}"
                
                logger.info(f"请求URL: {full_url}")
                logger.info(f"使用cookies: {True if self.cookies else False}")
                
                response = requests.get(
                    full_url,
                    headers=self.headers,
                    cookies=self.cookies,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()

                if data.get("success") is False:
                    logger.error(f"数据获取失败: {data.get('message', '未知错误')}")
                    raise ValueError("数据获取失败，请检查参数或网络连接")
                
                # 检查数据有效性
                if not data or "result" not in data or "data" not in data["result"]:
                    logger.warning("返回数据为空")
                    return pd.DataFrame()
                
                # 转换为DataFrame
                df = pd.DataFrame(data["result"]["data"])

                logger.info(f"获取到数据行数: {len(df)}， 列数: {len(df.columns)}，字段: {list(df.columns)}")
                
                # 转换日期字段
                if "TRADE_DATE" in df.columns:
                    df["TRADE_DATE"] = pd.to_datetime(df["TRADE_DATE"])
                
                # 替换为中文字段名
                if use_chinese_fields:
                    # 创建映射字典，仅包含DataFrame中存在的列
                    field_map = {k: v for k, v in self.FIELD_MAPPING.items() if k in df.columns}
                    # 重命名列
                    df = df.rename(columns=field_map)
                    logger.info(f"已将字段名替换为中文，新字段: {list(df.columns)}")
                
                return df
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                if attempt == self.retry_times - 1:
                    raise ValueError("数据解析失败，请检查返回数据格式")
            except requests.exceptions.RequestException as e:
                logger.error(f"请求失败(尝试 {attempt + 1}/{self.retry_times}): {e}")
                if attempt == self.retry_times - 1:
                    raise
            except Exception as e:
                logger.error(f"未知错误: {e}")
                raise

# 示例用法
if __name__ == "__main__":
    # 模拟获取cookies的函数
    def get_eastmoney_cookies():
        """
        模拟从浏览器获取东方财富网站cookies
        实际应用中，可以使用selenium或其他方法从浏览器获取
        """
        # 这里使用模拟数据，实际使用时应替换为真实cookies
        return {
            "JSESSIONID":"B9E35A3C0D2F38B0DC68F746CF27E47E"
        }
    
    # 示例1: 初始化时设置cookies
    cookies = get_eastmoney_cookies()
    lhb = FuturesLHB(cookies=cookies)
    
    # 示例2: 使用set_cookies方法更新cookies
    # lhb = FuturesLHB()  # 先不设置cookies
    # cookies = get_eastmoney_cookies()
    # lhb.set_cookies(cookies)  # 后续更新cookies
    
    print("="*50)
    print("东方财富期货龙虎榜数据接口使用示例")
    print("="*50)
    print("\n1. 基本使用方法:")
    print("   lhb = FuturesLHB(cookies=cookies)")
    print("   df = lhb.get_data(security_code='IF2509', trade_date='2025-07-18', sort_field='VOLUMERANK')")
    print("\n2. 更新cookies:")
    print("   lhb.set_cookies(new_cookies)")
    print("\n3. 检查cookies是否有效:")
    print("   is_valid = lhb.is_cookies_valid()")
    print("   if not is_valid:")
    print("       print(FuturesLHB.get_cookies_guide())")
    print("\n4. 字段名语言选择:")
    print("   # 使用中文字段名(默认)")
    print("   df = lhb.get_data(security_code='IF2509', trade_date='2025-07-18', use_chinese_fields=True)")
    print("   # 使用英文字段名")
    print("   df = lhb.get_data(security_code='IF2509', trade_date='2025-07-18', use_chinese_fields=False)")
    print("="*50)
    
    # 示例3: 检查cookies有效性
    print("\n检查cookies有效性:")
    if lhb.is_cookies_valid():
        print("✅ Cookies有效")
    else:
        print("❌ Cookies无效或已过期")
        print("\n获取cookies指南:")
        print(FuturesLHB.get_cookies_guide())
    print("="*50)
    
    def test_all_queries():
        """测试所有12种查询方式"""
        # 首先展示字段名语言选择的效果
        print("="*50)
        print("字段名语言选择示例")
        print("="*50)

        # 合约代码
        #security_code = "IF2509"
        security_code = "SN2508"
        
        try:
            # 使用中文字段名
            print("\n使用中文字段名(默认):")
            df_cn = lhb.get_data(
                security_code=security_code,
                trade_date="2025-07-18",
                sort_field="VOLUMERANK",
                page_size=5,
                use_chinese_fields=True
            )
            if not df_cn.empty:
                print(f"获取成功, 数据量: {len(df_cn)}")
                print("字段名:", list(df_cn.columns))
                print("数据预览:")
                print(df_cn.head(2))
            
            # 使用英文字段名
            print("\n使用英文字段名:")
            df_en = lhb.get_data(
                security_code=security_code,
                trade_date="2025-07-18",
                sort_field="VOLUMERANK",
                page_size=5,
                use_chinese_fields=False
            )
            if not df_en.empty:
                print(f"获取成功, 数据量: {len(df_en)}")
                print("字段名:", list(df_en.columns))
                print("数据预览:")
                print(df_en.head(2))
        except Exception as e:
            print(f"字段名语言选择示例失败: {str(e)}")
        
        print("="*50)
        print("开始测试12种查询方式...")
        print(f"合约: {security_code}, 日期: 2025-07-18")
        print("="*50)
        
        test_cases = [
            {
                "name": "成交量排名",
                "params": {"sort_field": "VOLUMERANK"}
            },
            {
                "name": "多头持仓排名",
                "params": {"sort_field": "LPRANK"}
            },
            {
                "name": "空头持仓排名",
                "params": {"sort_field": "SPRANK"}
            },
            {
                "name": "净多头排名",
                "params": {"sort_field": "NLPRANK"}
            },
            {
                "name": "多头增仓排名",
                "params": {"sort_field": "LPUPRANK", "LP_CHANGE": ">0"}
            },
            {
                "name": "多头减仓排名",
                "params": {"sort_field": "LPDOWNRANK", "LP_CHANGE": "<0"}
            },
            {
                "name": "净空头排名",
                "params": {"sort_field": "NSPRANK"}
            },
            {
                "name": "空头增仓排名",
                "params": {"sort_field": "SPUPRANK", "SP_CHANGE": ">0"}
            },
            {
                "name": "空头减仓排名",
                "params": {"sort_field": "SPDOWNRANK", "SP_CHANGE": "<0"}
            },
            {
                "name": "会员空头持仓排名",
                "params": {"data_type": "2", "sort_field": "SPRANK"}
            },
            {
                "name": "会员多头持仓排名",
                "params": {"data_type": "2", "sort_field": "LPRANK"}
            },
            {
                "name": "会员成交量排名",
                "params": {"data_type": "2", "sort_field": "VOLUMERANK"}
            }
        ]
        
        print("="*50)
        print("开始测试12种查询方式...")
        print(f"合约: {security_code}, 日期: 2025-07-18")
        print("="*50)
        
        success_count = 0
        for case in test_cases:
            try:
                print(f"\n测试用例: {case['name']}")
                print(f"参数: {case['params']}")
                
                df = lhb.get_data(
                    security_code=security_code,
                    trade_date="2025-07-18",
                    **case['params']
                )
                
                if df.empty:
                    print("⚠️ 返回数据为空")
                else:
                    print(f"✅ 获取成功, 数据量: {len(df)}")
                    print("前20行数据:")
                    print(df.head(n=20))
                    success_count += 1
                    
            except Exception as e:
                print(f"❌ 测试失败: {str(e)}")
        
        print("\n" + "="*50)
        print(f"测试完成, 成功: {success_count}/12")
        print("="*50)
    
    # 运行所有测试
    test_all_queries()