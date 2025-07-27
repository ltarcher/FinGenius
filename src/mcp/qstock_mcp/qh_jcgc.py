# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
期货建仓过程数据
封装东方财富期货建仓过程数据接口
"""

import pandas as pd
import requests
import json
import urllib.parse
from typing import Dict, Optional, Union, List, Tuple
from datetime import datetime, timedelta
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

class FuturesJCGC:
    """
    东方财富期货建仓过程数据接口封装
    
    该类提供了获取东方财富网站期货建仓过程数据的功能。
    由于东方财富网站可能需要cookies验证，所以提供了设置和更新cookies的方法。
    
    基本用法:
        # 初始化
        jcgc = FuturesJCGC(cookies=cookies)
        
        # 获取数据
        df = jcgc.get_data(
            security_code="IF2507",
            org_code="10102950",
            start_date="2025-06-01",
            end_date="2025-07-18"
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
        初始化期货建仓过程数据接口
        
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
        org_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        data_type: str = "0",
        page_size: int = 100,
        use_chinese_fields: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        获取期货建仓过程数据
        
        参数:
            security_code: 合约代码(如IF2507)
            org_code: 机构代码
            start_date: 开始日期(YYYY-MM-DD)，默认为None，表示不限制开始日期
            end_date: 结束日期(YYYY-MM-DD)，默认为None，表示不限制结束日期
            data_type: 数据类型(0:全部,2:特定类型)
            page_size: 每页数据量
            use_chinese_fields: 是否使用中文字段名，默认为True
            **kwargs: 其他过滤条件
            
        返回:
            pandas.DataFrame: 包含期货建仓过程数据的DataFrame
            
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
            "pageSize": page_size,
            "sortColumns": "TRADE_DATE",
            "sortTypes": "-1"  # 按日期降序排序
        }
        
        # 构建过滤条件
        filters = [
            f"(SECURITY_CODE=\"{security_code}\")",
            f"(ORG_CODE=\"{org_code}\")",
            f"(TYPE={data_type})"
        ]
        
        # 添加日期过滤条件
        if start_date:
            filters.append(f"(TRADE_DATE>='{start_date}')")
        if end_date:
            filters.append(f"(TRADE_DATE<='{end_date}')")
        
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
                
                # 按日期升序排序
                date_field = "交易日期" if use_chinese_fields else "TRADE_DATE"
                if date_field in df.columns:
                    df = df.sort_values(by=date_field)
                
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
    
    def get_position_history(
        self,
        security_code: str,
        org_code: str,
        days: int = 30,
        end_date: Optional[str] = None,
        use_chinese_fields: bool = True
    ) -> pd.DataFrame:
        """
        获取指定天数的持仓历史数据
        
        参数:
            security_code: 合约代码(如IF2507)
            org_code: 机构代码
            days: 获取的天数，默认30天
            end_date: 结束日期(YYYY-MM-DD)，默认为None，表示当前日期
            use_chinese_fields: 是否使用中文字段名，默认为True
            
        返回:
            pandas.DataFrame: 包含持仓历史数据的DataFrame
        """
        # 计算开始日期
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_date_obj = end_date_obj - timedelta(days=days)
        start_date = start_date_obj.strftime("%Y-%m-%d")
        
        logger.info(f"获取从 {start_date} 到 {end_date} 的持仓历史数据")
        
        return self.get_data(
            security_code=security_code,
            org_code=org_code,
            start_date=start_date,
            end_date=end_date,
            use_chinese_fields=use_chinese_fields
        )
    
    def get_multi_contracts_history(
        self,
        security_codes: List[str],
        org_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_chinese_fields: bool = True
    ) -> pd.DataFrame:
        """
        获取多个合约的建仓过程数据
        
        参数:
            security_codes: 合约代码列表
            org_code: 机构代码
            start_date: 开始日期(YYYY-MM-DD)，默认为None
            end_date: 结束日期(YYYY-MM-DD)，默认为None
            use_chinese_fields: 是否使用中文字段名，默认为True
            
        返回:
            pandas.DataFrame: 包含多个合约建仓过程数据的DataFrame
        """
        all_data = []
        for security_code in security_codes:
            try:
                logger.info(f"获取合约 {security_code} 的建仓过程数据...")
                df = self.get_data(
                    security_code=security_code,
                    org_code=org_code,
                    start_date=start_date,
                    end_date=end_date,
                    use_chinese_fields=use_chinese_fields
                )
                if not df.empty:
                    all_data.append(df)
                    logger.info(f"成功获取合约 {security_code} 数据，行数: {len(df)}")
                else:
                    logger.warning(f"合约 {security_code} 数据为空")
            except Exception as e:
                logger.error(f"获取合约 {security_code} 数据失败: {e}")
        
        # 合并所有数据
        if not all_data:
            logger.warning("所有合约数据均为空")
            return pd.DataFrame()
        
        result = pd.concat(all_data, ignore_index=True)
        logger.info(f"合并后总数据行数: {len(result)}")
        return result
    
    def calculate_position_change_rate(
        self,
        df: pd.DataFrame,
        use_chinese_fields: bool = True
    ) -> pd.DataFrame:
        """
        计算持仓变化率
        
        参数:
            df: 包含建仓过程数据的DataFrame
            use_chinese_fields: 是否使用中文字段名，默认为True
            
        返回:
            pandas.DataFrame: 添加了持仓变化率的DataFrame
        """
        # 复制DataFrame以避免修改原始数据
        result = df.copy()
        
        # 确定字段名
        lp_field = "多头持仓" if use_chinese_fields else "LONG_POSITION"
        sp_field = "空头持仓" if use_chinese_fields else "SHORT_POSITION"
        lp_change_rate_field = "多头持仓变化率" if use_chinese_fields else "LP_CHANGE_RATE"
        sp_change_rate_field = "空头持仓变化率" if use_chinese_fields else "SP_CHANGE_RATE"
        date_field = "交易日期" if use_chinese_fields else "TRADE_DATE"
        
        # 确保数据按日期排序
        if date_field in result.columns:
            result = result.sort_values(by=date_field)
        
        # 计算持仓变化率
        if lp_field in result.columns:
            result[lp_change_rate_field] = result[lp_field].pct_change() * 100
        
        if sp_field in result.columns:
            result[sp_change_rate_field] = result[sp_field].pct_change() * 100
        
        return result
    
    def get_position_summary(
        self,
        df: pd.DataFrame,
        use_chinese_fields: bool = True
    ) -> Dict[str, Dict[str, float]]:
        """
        获取持仓数据摘要
        
        参数:
            df: 包含建仓过程数据的DataFrame
            use_chinese_fields: 是否使用中文字段名，默认为True
            
        返回:
            Dict: 包含持仓数据摘要的字典
        """
        # 确定字段名
        lp_field = "多头持仓" if use_chinese_fields else "LONG_POSITION"
        sp_field = "空头持仓" if use_chinese_fields else "SHORT_POSITION"
        nlp_field = "净多头持仓" if use_chinese_fields else "NET_LONG_POSITION"
        date_field = "交易日期" if use_chinese_fields else "TRADE_DATE"
        
        summary = {}
        
        # 确保DataFrame不为空
        if df.empty:
            return summary
        
        # 获取最早和最晚日期
        if date_field in df.columns:
            start_date = df[date_field].min()
            end_date = df[date_field].max()
            date_range = (end_date - start_date).days
            
            summary["日期范围"] = {
                "开始日期": start_date.strftime("%Y-%m-%d"),
                "结束日期": end_date.strftime("%Y-%m-%d"),
                "天数": date_range
            }
        
        # 计算多头持仓摘要
        if lp_field in df.columns:
            summary["多头持仓"] = {
                "初始值": float(df[lp_field].iloc[0]) if not df.empty else 0,
                "最终值": float(df[lp_field].iloc[-1]) if not df.empty else 0,
                "最大值": float(df[lp_field].max()),
                "最小值": float(df[lp_field].min()),
                "平均值": float(df[lp_field].mean()),
                "变化量": float(df[lp_field].iloc[-1] - df[lp_field].iloc[0]) if not df.empty else 0,
                "变化率(%)": float((df[lp_field].iloc[-1] / df[lp_field].iloc[0] - 1) * 100) if not df.empty and df[lp_field].iloc[0] != 0 else 0
            }
        
        # 计算空头持仓摘要
        if sp_field in df.columns:
            summary["空头持仓"] = {
                "初始值": float(df[sp_field].iloc[0]) if not df.empty else 0,
                "最终值": float(df[sp_field].iloc[-1]) if not df.empty else 0,
                "最大值": float(df[sp_field].max()),
                "最小值": float(df[sp_field].min()),
                "平均值": float(df[sp_field].mean()),
                "变化量": float(df[sp_field].iloc[-1] - df[sp_field].iloc[0]) if not df.empty else 0,
                "变化率(%)": float((df[sp_field].iloc[-1] / df[sp_field].iloc[0] - 1) * 100) if not df.empty and df[sp_field].iloc[0] != 0 else 0
            }
        
        # 计算净多头持仓摘要
        if nlp_field in df.columns:
            summary["净多头持仓"] = {
                "初始值": float(df[nlp_field].iloc[0]) if not df.empty else 0,
                "最终值": float(df[nlp_field].iloc[-1]) if not df.empty else 0,
                "最大值": float(df[nlp_field].max()),
                "最小值": float(df[nlp_field].min()),
                "平均值": float(df[nlp_field].mean()),
                "变化量": float(df[nlp_field].iloc[-1] - df[nlp_field].iloc[0]) if not df.empty else 0
            }
        
        return summary


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
    jcgc = FuturesJCGC(cookies=cookies)
    
    print("="*50)
    print("东方财富期货建仓过程数据接口使用示例")
    print("="*50)
    print("\n1. 基本使用方法:")
    print("   jcgc = FuturesJCGC(cookies=cookies)")
    print("   df = jcgc.get_data(security_code='IF2507', org_code='10102950')")
    print("\n2. 获取指定日期范围的数据:")
    print("   df = jcgc.get_data(security_code='IF2507', org_code='10102950', start_date='2025-06-01', end_date='2025-07-18')")
    print("\n3. 获取最近N天的持仓历史:")
    print("   df = jcgc.get_position_history(security_code='IF2507', org_code='10102950', days=30)")
    print("\n4. 获取多个合约的建仓过程:")
    print("   df = jcgc.get_multi_contracts_history(security_codes=['IF2507', 'IF2508'], org_code='10102950')")
    print("\n5. 计算持仓变化率:")
    print("   df = jcgc.get_data(security_code='IF2507', org_code='10102950')")
    print("   df_with_rates = jcgc.calculate_position_change_rate(df)")
    print("\n6. 获取持仓数据摘要:")
    print("   summary = jcgc.get_position_summary(df)")
    print("\n7. 字段名语言选择:")
    print("   # 使用中文字段名(默认)")
    print("   df = jcgc.get_data(security_code='IF2507', org_code='10102950', use_chinese_fields=True)")
    print("   # 使用英文字段名")
    print("   df = jcgc.get_data(security_code='IF2507', org_code='10102950', use_chinese_fields=False)")
    print("="*50)
    
    # 检查cookies有效性
    print("\n检查cookies有效性:")
    if jcgc.is_cookies_valid():
        print("✅ Cookies有效")
    else:
        print("❌ Cookies无效或已过期")
        print("\n获取cookies指南:")
        print(jcgc.get_cookies_guide())
    print("="*50)
    
    def test_queries():
        """测试查询功能"""
        print("="*50)
        print("测试查询功能")
        print("="*50)
        
        # 测试基本查询
        try:
            print("\n1. 基本查询:")
            df = jcgc.get_data(
                security_code="IF2507",
                org_code="10102950",
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
        
        # 测试持仓历史查询
        try:
            print("\n2. 持仓历史查询:")
            df = jcgc.get_position_history(
                security_code="IF2507",
                org_code="10102950",
                days=15
            )
            
            if df.empty:
                print("⚠️ 返回数据为空")
            else:
                print(f"✅ 获取成功, 数据量: {len(df)}")
                print("数据预览:")
                print(df.head(3))
                
                # 计算持仓变化率
                df_with_rates = jcgc.calculate_position_change_rate(df)
                print("\n持仓变化率:")
                rate_cols = [col for col in df_with_rates.columns if '变化率' in col]
                if rate_cols:
                    print(df_with_rates[['交易日期', '多头持仓', '多头持仓变化率', '空头持仓', '空头持仓变化率']].head(3))
                
                # 获取持仓摘要
                summary = jcgc.get_position_summary(df)
                print("\n持仓数据摘要:")
                for category, stats in summary.items():
                    print(f"\n{category}:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
        
        # 测试多合约查询
        try:
            print("\n3. 多合约查询:")
            df = jcgc.get_multi_contracts_history(
                security_codes=["IF2507", "IF2508"],
                org_code="10102950",
                start_date="2025-06-01",
                end_date="2025-07-18"
            )
            
            if df.empty:
                print("⚠️ 返回数据为空")
            else:
                print(f"✅ 获取成功, 数据量: {len(df)}")
                
                # 按合约分组统计
                contract_col = "合约代码" if "合约代码" in df.columns else "SECURITY_CODE"
                if contract_col in df.columns:
                    contract_counts = df[contract_col].value_counts()
                    print("\n各合约数据量:")
                    for contract, count in contract_counts.items():
                        print(f"   {contract}: {count}条")
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
        
        print("\n" + "="*50)
        print("测试完成")
        print("="*50)
    
    # 运行测试
    test_queries()