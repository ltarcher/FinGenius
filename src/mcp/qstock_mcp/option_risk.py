# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
期权风险数据
封装东方财富期权风险数据接口
"""

import pandas as pd
import requests
import json
import time
from typing import Dict, Optional
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

class OptionRisk:
    """
    东方财富期权风险数据接口封装
    
    该类提供了获取东方财富网站期权风险数据的功能。
    由于东方财富网站可能需要cookies验证，所以提供了设置和更新cookies的方法。
    """
    
    # 字段映射字典
    FIELD_MAPPING = {
        "f12": "代码",
        "f14": "名称",
        "f2": "最新价",
        "f3": "涨跌幅",
        "f301": "到期日",
        "f302": "杠杆比率",
        "f303": "实际杠杆比率",
        "f325": "Delta",
        "f326": "Gemma",
        "f327": "Vega",
        "f329": "Rho",
        "f328": "Theta",
        "f152": "未知-2",
        "f154": "未知-4",
        "f1": "未知-1",
        "f13": "期权市场"   #10
    }
    
    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        初始化期权风险数据接口
        
        参数:
            cookies: 请求时使用的cookies，字典格式
        """
        self.base_url = "https://push2.eastmoney.com/api/qt/clist/get"
        self.default_fields = "f1,f2,f3,f12,f13,f14,f302,f303,f325,f326,f327,f329,f328,f301,f152,f154"
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
            response = requests.get(
                "https://data.eastmoney.com/",
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout
            )
            response.raise_for_status()
            
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
        return """
如何获取东方财富网站的cookies:

1. 使用Chrome浏览器访问 https://data.eastmoney.com/
2. 按F12打开开发者工具
3. 切换到"Network"(网络)选项卡
4. 刷新页面
5. 在请求列表中找到主页面请求
6. 右键点击请求，选择"Copy" -> "Copy as cURL"
7. 从cURL命令中提取cookies部分(通常在-H "Cookie: xxx"部分)
8. 将cookies字符串解析为字典格式

或者使用浏览器扩展如"EditThisCookie"直接导出cookies
        """
        
    def get_data(
        self, 
        market_type: str = "10",  # 10表示ETF市场
        page_size: int = 50,
        page_number: int = 1,
        sort_field: str = "f3",  # 默认按涨跌幅排序
        sort_direction: int = 1,   # 1升序，-1降序
        use_chinese_fields: bool = True
    ) -> pd.DataFrame:
        """
        获取期权风险数据
        
        参数:
            market_type: 市场类型(10:ETF)
            page_size: 每页数据量
            page_number: 页码
            sort_field: 排序字段
            sort_direction: 排序方向
            use_chinese_fields: 是否使用中文字段名
            
        返回:
            pandas.DataFrame: 包含期权风险数据的DataFrame
        """
        params = {
            "fid": sort_field,
            "po": sort_direction,
            "pz": page_size,
            "pn": page_number,
            "np": 1,
            "fltt": 2,
            "invt": 2,
            "ut": "8dec03ba335b81bf4ebdf7b29ec27d15",
            "fields": self.default_fields,
            "fs": f"m:{market_type}",
            "_": str(int(time.time() * 1000))
        }
                
        for attempt in range(self.retry_times):
            try:
                logger.info(f"请求URL: {self.base_url}")
                logger.info(f"请求参数: {params}")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=self.headers,
                    cookies=self.cookies,
                    timeout=self.timeout
                )
                response.raise_for_status()
                json_str = response.text
                data = json.loads(json_str)
                
                if "data" not in data:
                    raise ValueError("数据获取失败")
                
                if not data["data"] or "diff" not in data["data"]:
                    logger.warning("返回数据为空")
                    return pd.DataFrame()
                
                df = pd.DataFrame(data["data"]["diff"])

                logger.info(f"获取到 {len(df)} 条数据, 字段: {list(df.columns)}")
                
                # 替换为中文字段名
                if use_chinese_fields:
                    field_map = {k: v for k, v in self.FIELD_MAPPING.items() if k in df.columns}
                    df = df.rename(columns=field_map)
                
                # 去掉包含未知字段
                unknown_fields = [col for col in df.columns if "未知" in col]
                if unknown_fields:
                    logger.warning(f"发现未知字段: {unknown_fields}，将从结果中删除")
                    df = df.drop(columns=unknown_fields)
                
                # 处理百分比字段
                if "涨跌幅" in df.columns:
                    df["涨跌幅"] = df["涨跌幅"] / 100
                elif "f3" in df.columns:
                    df["f3"] = df["f3"] / 100
                
                return df
                
            except Exception as e:
                logger.error(f"请求失败(尝试 {attempt + 1}/{self.retry_times}): {e}")
                if attempt == self.retry_times - 1:
                    raise
    
    def get_multi_pages(
        self,
        market_type: str = "10",
        max_pages: int = 5,
        use_chinese_fields: bool = True
    ) -> pd.DataFrame:
        """
        获取多页期权风险数据
        
        参数:
            market_type: 市场类型
            max_pages: 最大获取页数
            use_chinese_fields: 是否使用中文字段名
            
        返回:
            pandas.DataFrame: 合并后的数据
        """
        all_data = []
        page_number = 1
        
        while page_number <= max_pages:
            try:
                df = self.get_data(
                    market_type=market_type,
                    page_number=page_number,
                    use_chinese_fields=use_chinese_fields
                )
                
                if df.empty:
                    break
                    
                all_data.append(df)
                page_number += 1
                
                # 如果获取的数据少于每页数量，说明是最后一页
                if len(df) < 50:
                    break
                    
            except Exception as e:
                logger.error(f"获取第 {page_number} 页数据失败: {e}")
                break
        
        if not all_data:
            return pd.DataFrame()
            
        return pd.concat(all_data, ignore_index=True)

    def get_etf_options_data(
        self,
        use_chinese_fields: bool = True
    ) -> pd.DataFrame:
        """
        获取主要ETF期权的风险数据
        
        参数:
            use_chinese_fields: 是否使用中文字段名，默认为True
            
        返回:
            pandas.DataFrame: 包含主要ETF期权风险数据的DataFrame
        """
        # 获取ETF市场数据
        df = self.get_multi_pages(
            market_type="10",
            max_pages=2,
            use_chinese_fields=use_chinese_fields
        )
        
        if df.empty:
            return df
            
        # 主要ETF列表
        main_etfs = [
            "510050",  # 上证50ETF
            "510300",  # 沪深300ETF
            "159919",  # 沪深300ETF(深)
            "510500",  # 中证500ETF
            "588000",  # 科创50ETF
            "588080",  # 科创板50ETF
            "159915"   # 创业板ETF
        ]
        
        # 根据字段名语言选择对应的代码列
        code_col = "代码" if use_chinese_fields else "f12"
        
        # 过滤出主要ETF
        df = df[df[code_col].isin(main_etfs)]
        logger.info(f"过滤后主要ETF数据行数: {len(df)}")
        
        return df


# 示例用法
if __name__ == "__main__":
    # 模拟cookies
    cookies = {"JSESSIONID": "B9E35A3C0D2F38B0DC68F746CF27E47E"}
    
    risk = OptionRisk(cookies=cookies)
    
    print("="*50)
    print("东方财富期权风险数据接口使用示例")
    print("="*50)
    
    # 测试基本数据获取
    try:
        print("\n1. 获取ETF期权风险数据:")
        df = risk.get_data()
        print(f"获取成功, 数据量: {len(df)}")
        print(df.head())
        
        # 获取多页数据
        print("\n2. 获取多页ETF期权风险数据:")
        df_multi = risk.get_multi_pages(max_pages=10)
        print(f"获取成功, 总数据量: {len(df_multi)}")
        print(df_multi.head())
        
        # 获取主要ETF期权数据
        print("\n3. 获取主要ETF期权风险数据:")
        df_etf = risk.get_etf_options_data()
        print(f"获取成功, 数据量: {len(df_etf)}")
        print(df_etf)
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
    
    print("="*50)