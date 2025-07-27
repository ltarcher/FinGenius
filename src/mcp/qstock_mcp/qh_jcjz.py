# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
期货价差矩阵数据
封装东方财富期货价差矩阵数据接口
"""

import pandas as pd
import requests
import json
import re
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 默认请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://futures.eastmoney.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive"
}

class FuturesJCJZ:
    """
    东方财富期货价差矩阵数据接口封装
    
    该类提供了获取东方财富网站期货价差矩阵数据的功能。
    
    字段映射:
    - dm: 合约代码
    - name: 合约名称
    - p: 最新价
    - zde: 涨跌额
    - h: 最高价
    - l: 最低价
    - o: 开盘价
    - vol: 成交量
    - ccl: 持仓量
    - zjsj: 昨结算
    - sc: 品种代码
    - uid: 唯一标识
    """
    
    # 字段中英文映射字典
    FIELD_MAPPING = {
        "dm": "合约代码",
        "name": "合约名称",
        "p": "最新价",
        "zde": "涨跌额",
        "h": "最高价",
        "l": "最低价",
        "o": "开盘价",
        "vol": "成交量",
        "ccl": "持仓量",
        "zjsj": "昨结算",
        "sc": "品种代码",
        "uid": "唯一标识"
    }
    
    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        初始化价差矩阵数据接口
        
        参数:
            cookies: 请求时使用的cookies，字典格式
        """
        self.base_url = "https://futsseapi.eastmoney.com/list/variety/{sc}/{page}"
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
                "https://futures.eastmoney.com/",
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout
            )
            response.raise_for_status()
            return "用户登录" not in response.text
        except Exception as e:
            logger.error(f"检查cookies时出错: {e}")
            return False
    
    @staticmethod
    def _extract_json_from_jsonp(jsonp_str: str) -> dict:
        """
        从JSONP响应中提取JSON数据
        
        参数:
            jsonp_str: JSONP格式的字符串
            
        返回:
            dict: 解析后的JSON数据
        """
        try:
            match = re.search(r'jQuery\d+_\d+\((.*)\)', jsonp_str)
            if match:
                return json.loads(match.group(1))
            return json.loads(jsonp_str)
        except Exception as e:
            logger.error(f"JSONP解析失败: {e}")
            raise ValueError("无法解析JSONP响应")

    def get_price_matrix(
        self,
        variety_code: int,
        page: int = 1,
        page_size: int = 100,
        use_chinese_fields: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        获取期货价差矩阵数据
        
        参数:
            variety_code: 品种代码(如113表示沪铜)
            page: 页码，默认为1
            page_size: 每页数据量，默认为100
            use_chinese_fields: 是否使用中文字段名，默认为True
            **kwargs: 其他查询参数(如orderBy, sort等)
            
        返回:
            pandas.DataFrame: 包含价差矩阵数据的DataFrame
            
        异常:
            ValueError: 参数错误或数据获取失败
            requests.exceptions.RequestException: 网络请求异常
        """
        # 构建请求参数
        params = {
            "orderBy": "dm",
            "sort": "asc",
            "pageSize": page_size,
            "pageIndex": page - 1,
            "token": "8163b6a9200dc68c03113094df2db2c7",
            "field": "name,p,zde,uid,sc,dm,o,h,l,vol,ccl,zjsj",
            "callbackName": f"jQuery{int(pd.Timestamp.now().timestamp() * 1000)}_{int(pd.Timestamp.now().timestamp() * 1000)}",
            "_": int(pd.Timestamp.now().timestamp() * 1000)
        }
        params.update(kwargs)
        
        # 构建完整URL
        url = self.base_url.format(sc=variety_code, page=page)
        
        # 发送请求
        for attempt in range(self.retry_times):
            try:
                logger.info(f"请求价差矩阵数据: {url}")
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    cookies=self.cookies,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # 处理JSONP响应
                data = self._extract_json_from_jsonp(response.text)
                
                if not data or "list" not in data:
                    logger.warning("返回数据为空")
                    return pd.DataFrame()
                
                # 转换为DataFrame
                df = pd.DataFrame(data["list"])
                
                # 替换为中文字段名
                if use_chinese_fields:
                    field_map = {k: v for k, v in self.FIELD_MAPPING.items() if k in df.columns}
                    df = df.rename(columns=field_map)
                
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
    # 初始化
    jcjz = FuturesJCJZ()
    
    print("="*50)
    print("东方财富期货价差矩阵数据接口使用示例")
    print("="*50)
    
    # 获取沪铜价差矩阵数据
    print("\n1. 获取沪铜(113)价差矩阵数据:")
    try:
        df = jcjz.get_price_matrix(variety_code=113)
        if not df.empty:
            print(f"获取成功, 数据量: {len(df)}")
            print("字段名:", list(df.columns))
            print("数据预览:")
            print(df.head())
    except Exception as e:
        print(f"获取失败: {e}")
    
    # 使用中文字段名
    print("\n2. 使用中文字段名:")
    try:
        df_cn = jcjz.get_price_matrix(
            variety_code=113,
            use_chinese_fields=True
        )
        if not df_cn.empty:
            print("字段名:", list(df_cn.columns))
            print(df_cn.head(2))
    except Exception as e:
        print(f"获取失败: {e}")
    
    # 使用英文字段名
    print("\n3. 使用英文字段名:")
    try:
        df_en = jcjz.get_price_matrix(
            variety_code=113,
            use_chinese_fields=False
        )
        if not df_en.empty:
            print("字段名:", list(df_en.columns))
            print(df_en.head(2))
    except Exception as e:
        print(f"获取失败: {e}")
    
    print("="*50)