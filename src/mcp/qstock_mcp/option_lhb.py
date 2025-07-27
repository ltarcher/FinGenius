# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
期权龙虎榜数据
封装东方财富期权龙虎榜数据接口
"""

import pandas as pd
import requests
import json
import time
from typing import Dict, Optional, List
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

class OptionLHB:
    """
    东方财富期权龙虎榜数据接口封装
    
    该类提供了获取东方财富网站期权龙虎榜数据的功能。
    """
    
    # 详细字段映射字典
    FIELD_MAPPING = {
        # 基础信息字段
        "TRADE_TYPE": "交易类型",
        "TRADE_DATE": "交易日期", 
        "SECURITY_CODE": "期权代码",
        "TARGET_NAME": "标的名称",
        "BILLBOARD_TYPE": "榜单类型",
        "OPTION_TYPE_CODE": "期权类型",
        "MEMBER_NAME_ABBR": "会员简称",
        "MEMBER_RANK": "会员排名",
        
        # 卖出相关字段
        "SELL_VOLUME": "卖出成交量",
        "SELL_VOLUME_CHANGE": "卖出成交量变化",
        "NET_SELL_VOLUME": "净卖出成交量",
        "SELL_VOLUME_RATIO": "卖出成交量占比(%)",
        "ORG_CODE": "机构代码",
        "SELL_POSITION": "卖出持仓量",
        "SELL_POSITION_CHANGE": "卖出持仓变化",
        "SELL_POSITION_RATIO": "卖出持仓占比(%)",
        "NET_SELL_POSITION": "净卖出持仓量",
        
        # 买入相关字段
        "BUY_VOLUME": "买入成交量",
        "BUY_VOLUME_CHANGE": "买入成交量变化",
        "NET_BUY_VOLUME": "净买入成交量",
        "BUY_VOLUME_RATIO": "买入成交量占比(%)",
        "BUY_POSITION": "买入持仓量",
        "BUY_POSITION_CHANGE": "买入持仓变化",
        "NET_BUY_POSITION": "净买入持仓量",
        "BUY_POSITION_RATIO": "买入持仓占比(%)",
        
        # 其他字段
        "OPTION_EXERCISE_PRICE": "行权价",
        "OPTION_EXPIRE_DATE": "到期日"
    }
    
    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        初始化期权龙虎榜数据接口
        
        参数:
            cookies: 请求时使用的cookies，字典格式
        """
        self.base_url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        self.report_name = "RPT_IF_BILLBOARD_TD"
        self.timeout = 10
        self.retry_times = 3
        self.headers = headers.copy()
        self.cookies = cookies or {}
    
    def set_cookies(self, cookies: Dict[str, str]) -> None:
        """设置请求cookies"""
        self.cookies.update(cookies)
        logger.info("已更新cookies")
    
    def is_cookies_valid(self) -> bool:
        """检查当前cookies是否有效"""
        try:
            response = requests.get(
                "https://data.eastmoney.com/",
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout
            )
            response.raise_for_status()
            return "用户登录" not in response.text and "请登录" not in response.text
        except Exception as e:
            logger.error(f"检查cookies时出错: {e}")
            return False
    
    @staticmethod
    def get_cookies_guide() -> str:
        """获取从浏览器获取cookies的指南"""
        return """如何获取东方财富网站的cookies:
1. 使用Chrome浏览器访问 https://data.eastmoney.com/
2. 按F12打开开发者工具
3. 切换到"Network"(网络)选项卡
4. 刷新页面
5. 在请求列表中找到主页面请求
6. 右键点击请求，选择"Copy" -> "Copy as cURL"
7. 从cURL命令中提取cookies部分(通常在-H "Cookie: xxx"部分)
8. 将cookies字符串解析为字典格式"""
        
    def get_data(
        self,
        security_code: str,
        trade_date: str,
        page_size: int = 200,
        use_chinese_fields: bool = True,
        sort_field: str = "MEMBER_RANK",
        sort_type: int = 1  # 1升序，-1降序
    ) -> pd.DataFrame:
        """
        获取期权龙虎榜数据
        
        参数:
            security_code: 期权代码(如510050)
            trade_date: 交易日期(YYYY-MM-DD)
            page_size: 每页数据量
            use_chinese_fields: 是否使用中文字段名
            sort_field: 排序字段
            sort_type: 排序方式(1升序，-1降序)
            
        返回:
            pandas.DataFrame: 包含期权龙虎榜数据的DataFrame
        """
        params = {
            "reportName": self.report_name,
            "columns": "ALL",
            "filter": f"(SECURITY_CODE=\"{security_code}\")(TRADE_DATE='{trade_date}')",
            "pageNumber": 1,
            "pageSize": page_size,
            "sortColumns": sort_field,
            "sortTypes": sort_type,
            "source": "IFBILLBOARD",
            "client": "WEB",
            "_": str(int(time.time() * 1000))
        }
        
        try:
            logger.info(f"请求期权龙虎榜数据，参数: {params}")
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = json.loads(response.text)
            
            if not data.get("success", False):
                error_msg = data.get("message", "未知错误")
                logger.error(f"数据获取失败: {error_msg}")
                return pd.DataFrame()
                
            if not data.get("result", {}).get("data"):
                logger.warning("返回数据为空")
                return pd.DataFrame()
            
            df = pd.DataFrame(data["result"]["data"])
            logger.info(f"获取到 {len(df)} 条数据, 字段: {list(df.columns)}")
            
            # 字段处理
            if use_chinese_fields:
                field_map = {k: v for k, v in self.FIELD_MAPPING.items() if k in df.columns}
                df = df.rename(columns=field_map)
                
                # 处理百分比字段
                for col in df.columns:
                    if "占比" in col and df[col].dtype in [int, float]:
                        df[col] = df[col] / 100
            
            # 日期字段转换
            date_col = "交易日期" if use_chinese_fields else "TRADE_DATE"
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col])
                
            return df
            
        except Exception as e:
            logger.error(f"获取数据时出错: {str(e)}")
            return pd.DataFrame()
    
    def get_etf_options_lhb(
        self,
        etf_code: str,
        trade_date: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        获取ETF期权龙虎榜数据
        
        参数:
            etf_code: ETF代码(如510050)
            trade_date: 交易日期(YYYY-MM-DD)
            **kwargs: 其他传递给get_data的参数
            
        返回:
            pandas.DataFrame: 包含ETF期权龙虎榜数据的DataFrame
        """
        return self.get_data(security_code=etf_code, trade_date=trade_date, **kwargs)


# 示例用法
if __name__ == "__main__":
    # 初始化(需要提供有效的cookies)
    lhb = OptionLHB(cookies={"your_cookie_key": "your_cookie_value"})
    
    # 获取50ETF期权龙虎榜数据
    df = lhb.get_etf_options_lhb(
        etf_code="510050",
        trade_date="2025-07-18",
        use_chinese_fields=True
    )
    
    if not df.empty:
        print("获取到的期权龙虎榜数据:")
        print(df.head())
        
        # 保存到CSV文件
        csv_file = "option_lhb_510050_20250718.csv"
        df.to_csv(csv_file, index=False, encoding="utf_8_sig")
        print(f"数据已保存到: {csv_file}")
    else:
        print("未能获取到数据，请检查参数或cookies是否有效")