# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
期货公司持仓结构数据
封装东方财富期货公司持仓结构数据接口
"""

import pandas as pd
import requests
import json
import urllib.parse
from typing import Dict, Optional, Union, List
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

class FuturesCCJG:
    """
    东方财富期货公司持仓结构数据接口封装
    
    该类提供了获取东方财富网站期货公司持仓结构数据的功能。
    由于东方财富网站可能需要cookies验证，所以提供了设置和更新cookies的方法。
    
    基本用法:
        # 初始化
        ccjg = FuturesCCJG(cookies=cookies)
        
        # 获取数据
        df = ccjg.get_data(
            org_code="10102950",
            trade_date="2025-07-18",
            market_code="069001009"
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
    
    # 市场代码映射
    MARKET_MAPPING = {
        "上期所": "069001004",
        "大商所": "069001007",
        "郑商所": "069001008",
        "中金所": "069001009",
        "能源中心": "069001010",
        "广期所": "069001011"
    }
    
    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        初始化期货公司持仓结构数据接口
        
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
    
    def get_market_codes(self) -> Dict[str, str]:
        """
        获取所有交易市场代码
        
        返回:
            Dict[str, str]: 市场名称和代码的映射字典
        """
        return self.MARKET_MAPPING.copy()
        
    def get_data(
        self, 
        org_code: str, 
        trade_date: str, 
        market_code: Optional[str] = None,
        market_name: Optional[str] = None,
        sort_field: str = "SECURITY_CODE",
        sort_type: int = 1,
        page_size: int = 200,
        use_chinese_fields: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        获取期货公司持仓结构数据
        
        参数:
            org_code: 机构代码
            trade_date: 交易日期(YYYY-MM-DD)
            market_code: 交易市场代码，与market_name二选一
            market_name: 交易市场名称，与market_code二选一
            sort_field: 排序字段，默认按合约代码排序
            sort_type: 排序类型(1:升序,-1:降序)
            page_size: 每页数据量
            use_chinese_fields: 是否使用中文字段名，默认为True
            **kwargs: 其他过滤条件
            
        返回:
            pandas.DataFrame: 包含期货公司持仓结构数据的DataFrame
            
        异常:
            ValueError: 参数错误或数据获取失败
            requests.exceptions.RequestException: 网络请求异常
        """
        # 处理市场代码
        if market_code is None and market_name is None:
            raise ValueError("必须提供market_code或market_name参数")
        
        if market_name is not None:
            if market_name not in self.MARKET_MAPPING:
                raise ValueError(f"不支持的市场名称: {market_name}，支持的市场名称: {list(self.MARKET_MAPPING.keys())}")
            market_code = self.MARKET_MAPPING[market_name]
        
        # 构建基础参数
        params = {
            "reportName": self.report_name,
            "columns": self.default_columns,
            "source": "WEB",
            "client": "WEB",
            "pageNumber": 1,
            "pageSize": page_size,
            "sortColumns": sort_field,
            "sortTypes": sort_type
        }
        
        # 构建过滤条件
        filters = [
            f"(TRADE_MARKET_CODE=\"{market_code}\")",
            f"(ORG_CODE=\"{org_code}\")",
            f"(TRADE_DATE='{trade_date}')"
        ]
        
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
    
    def get_org_positions(
        self,
        org_code: str,
        trade_date: str,
        markets: Optional[List[str]] = None,
        use_chinese_fields: bool = True
    ) -> pd.DataFrame:
        """
        获取期货公司在多个市场的持仓数据
        
        参数:
            org_code: 机构代码
            trade_date: 交易日期(YYYY-MM-DD)
            markets: 市场名称列表，如["中金所", "上期所"]，默认为所有市场
            use_chinese_fields: 是否使用中文字段名，默认为True
            
        返回:
            pandas.DataFrame: 包含期货公司在多个市场的持仓数据的DataFrame
        """
        # 如果未指定市场，则使用所有市场
        if markets is None:
            markets = list(self.MARKET_MAPPING.keys())
        
        # 验证市场名称
        for market in markets:
            if market not in self.MARKET_MAPPING:
                raise ValueError(f"不支持的市场名称: {market}，支持的市场名称: {list(self.MARKET_MAPPING.keys())}")
        
        # 获取所有市场的数据
        all_data = []
        for market in markets:
            try:
                logger.info(f"获取 {market} 市场的数据...")
                df = self.get_data(
                    org_code=org_code,
                    trade_date=trade_date,
                    market_name=market,
                    use_chinese_fields=use_chinese_fields
                )
                if not df.empty:
                    # 添加市场名称列
                    market_col = "交易市场" if use_chinese_fields else "MARKET_NAME"
                    df[market_col] = market
                    all_data.append(df)
                    logger.info(f"成功获取 {market} 市场数据，行数: {len(df)}")
                else:
                    logger.warning(f"{market} 市场数据为空")
            except Exception as e:
                logger.error(f"获取 {market} 市场数据失败: {e}")
        
        # 合并所有数据
        if not all_data:
            logger.warning("所有市场数据均为空")
            return pd.DataFrame()
        
        result = pd.concat(all_data, ignore_index=True)
        logger.info(f"合并后总数据行数: {len(result)}")
        return result


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
    
    # 初始化
    cookies = get_eastmoney_cookies()
    ccjg = FuturesCCJG(cookies=cookies)
    
    print("="*50)
    print("东方财富期货公司持仓结构数据接口使用示例")
    print("="*50)
    print("\n1. 基本使用方法:")
    print("   ccjg = FuturesCCJG(cookies=cookies)")
    print("   df = ccjg.get_data(org_code='10102950', trade_date='2025-07-18', market_name='中金所')")
    print("\n2. 获取多个市场的数据:")
    print("   df = ccjg.get_org_positions(org_code='10102950', trade_date='2025-07-18', markets=['中金所', '上期所'])")
    print("\n3. 支持的市场:")
    for name, code in ccjg.get_market_codes().items():
        print(f"   {name}: {code}")
    print("\n4. 字段名语言选择:")
    print("   # 使用中文字段名(默认)")
    print("   df = ccjg.get_data(org_code='10102950', trade_date='2025-07-18', market_name='中金所', use_chinese_fields=True)")
    print("   # 使用英文字段名")
    print("   df = ccjg.get_data(org_code='10102950', trade_date='2025-07-18', market_name='中金所', use_chinese_fields=False)")
    print("="*50)
    
    # 检查cookies有效性
    print("\n检查cookies有效性:")
    if ccjg.is_cookies_valid():
        print("✅ Cookies有效")
    else:
        print("❌ Cookies无效或已过期")
        print("\n获取cookies指南:")
        print(ccjg.get_cookies_guide())
    print("="*50)
    
    def test_queries():
        """测试查询功能"""
        print("="*50)
        print("测试查询功能")
        print("="*50)
        
        # 测试单个市场查询
        try:
            print("\n1. 单个市场查询 (中金所):")
            df = ccjg.get_data(
                org_code="10102950",
                trade_date="2025-07-18",
                market_name="中金所",
                page_size=10
            )
            
            if df.empty:
                print("⚠️ 返回数据为空")
            else:
                print(f"✅ 获取成功, 数据量: {len(df)}")
                print("字段名:", list(df.columns))
                print("数据预览:")
                print(df.head(3))
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
        
        # 测试多市场查询
        try:
            print("\n2. 多市场查询 (中金所, 上期所):")
            df = ccjg.get_org_positions(
                org_code="10102950",
                trade_date="2025-07-18",
                markets=["中金所", "上期所"]
            )
            
            if df.empty:
                print("⚠️ 返回数据为空")
            else:
                print(f"✅ 获取成功, 数据量: {len(df)}")
                print("字段名:", list(df.columns))
                print("数据预览:")
                print(df.head(3))
                
                # 按市场分组统计
                market_col = "交易市场"
                if market_col in df.columns:
                    market_counts = df[market_col].value_counts()
                    print("\n各市场数据量:")
                    for market, count in market_counts.items():
                        print(f"   {market}: {count}条")
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
        
        # 测试字段名语言选择
        try:
            print("\n3. 字段名语言选择:")
            
            # 中文字段名
            print("\n   使用中文字段名:")
            df_cn = ccjg.get_data(
                org_code="10102950",
                trade_date="2025-07-18",
                market_name="中金所",
                page_size=5,
                use_chinese_fields=True
            )
            if not df_cn.empty:
                print(f"   获取成功, 数据量: {len(df_cn)}")
                print("   字段名:", list(df_cn.columns))
            
            # 英文字段名
            print("\n   使用英文字段名:")
            df_en = ccjg.get_data(
                org_code="10102950",
                trade_date="2025-07-18",
                market_name="中金所",
                page_size=5,
                use_chinese_fields=False
            )
            if not df_en.empty:
                print(f"   获取成功, 数据量: {len(df_en)}")
                print("   字段名:", list(df_en.columns))
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
        
        print("\n" + "="*50)
        print("测试完成")
        print("="*50)
    
    # 运行测试
    test_queries()