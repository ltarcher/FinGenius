# -*- coding:utf-8 -*-
# !/usr/bin/env python

"""
期货品种数据
封装东方财富期货品种数据接口
"""

import pandas as pd
import requests
import json
import re
import logging
from typing import Dict, Optional, Union, List

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

class FuturesList:
    """
    东方财富期货品种数据接口封装
    
    该类提供了获取东方财富网站期货品种数据的功能。
    """
    
    # 期货品种字段中英文映射字典
    FIELD_MAPPING = {
        "TRADE_MARKET_CODE": "交易市场代码",
        "TRADE_CODE": "交易代码",
        "TRADE_TYPE": "交易名称"
    }
    
    # 期货公司字段中英文映射字典
    ORG_FIELD_MAPPING = {
        "ORGNAME_PINYIN": "拼音名称",
        "ORG_NAME_ABBR": "公司简称",
        "ORG_CODE": "公司代码"
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
    
    # 交易所编号映射
    EXCHANGE_MSGID = {
        "上期所": "113",
        "大商所": "114",
        "郑商所": "115",
        "中金所": "220",
        "能源中心": "142"
    }
    
    # 交易所品种字段映射
    EXCHANGE_PRODUCT_MAPPING = {
        "mktid": "市场ID",
        "mktname": "市场名称",
        "mktshort": "市场简称",
        "rtime": "更新时间",
        "vcode": "品种代码",
        "vname": "品种名称",
        "vtype": "品种类型"
    }
    
    def __init__(self):
        """
        初始化期货品种数据接口
        """
        self.base_url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        self.exchange_products_url = "https://futsse-static.eastmoney.com/redis"
        self.report_name = "RPT_FUTU_POSITIONCODE"
        self.default_columns = "TRADE_MARKET_CODE,TRADE_CODE,TRADE_TYPE"
        self.timeout = 10
        self.retry_times = 3
        self.headers = headers.copy()
    
    def _extract_json_from_jsonp(self, jsonp_str: str) -> dict:
        """
        从JSONP响应中提取JSON数据
        
        参数:
            jsonp_str: JSONP格式的字符串
            
        返回:
            dict: 解析后的JSON数据
        """
        try:
            # 使用正则表达式提取JSON部分
            match = re.search(r'jQuery\d+_\d+\((.*)\)', jsonp_str)
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            else:
                # 如果不是JSONP格式，尝试直接解析JSON
                return json.loads(jsonp_str)
        except Exception as e:
            logger.error(f"从JSONP提取JSON失败: {e}")
            raise ValueError("无法从响应中提取有效的JSON数据")
    
    def get_market_codes(self) -> Dict[str, str]:
        """
        获取所有交易市场代码
        
        返回:
            Dict[str, str]: 市场名称和代码的映射字典
        """
        return self.MARKET_MAPPING.copy()
    
    def get_exchange_products(
        self,
        msgid: str,
        use_chinese_fields: bool = True
    ) -> pd.DataFrame:
        """
        获取交易所可交易品种列表
        
        参数:
            msgid: 交易所编号(如220表示中金所)
            use_chinese_fields: 是否使用中文字段名，默认为True
            
        返回:
            pandas.DataFrame: 包含交易所品种数据的DataFrame
            
        异常:
            ValueError: 参数错误或数据获取失败
            requests.exceptions.RequestException: 网络请求异常
        """
        try:
            # 构建请求参数
            params = {
                "msgid": msgid,
                "callbackName": f"jQuery{int(pd.Timestamp.now().timestamp() * 1000)}_{int(pd.Timestamp.now().timestamp() * 1000)}",
                "_": int(pd.Timestamp.now().timestamp() * 1000)
            }
            
            logger.info(f"获取交易所品种数据，交易所ID: {msgid}")
            response = requests.get(
                self.exchange_products_url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # 处理JSONP响应
            data = self._extract_json_from_jsonp(response.text)
            
            if not isinstance(data, list):
                logger.warning("返回数据格式不正确")
                return pd.DataFrame()
                
            # 转换为DataFrame
            df = pd.DataFrame(data)
            
            # 替换为中文字段名
            if use_chinese_fields:
                field_map = {k: v for k, v in self.EXCHANGE_PRODUCT_MAPPING.items() if k in df.columns}
                df = df.rename(columns=field_map)
                logger.info(f"已将字段名替换为中文，新字段: {list(df.columns)}")
            
            return df
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise ValueError("数据解析失败，请检查返回数据格式")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    def get_future_org_list(
        self,
        page_size: int = 200,
        use_chinese_fields: bool = True
    ) -> pd.DataFrame:
        """
        获取期货公司列表数据
        
        参数:
            page_size: 每页数据量，默认为200
            use_chinese_fields: 是否使用中文字段名，默认为True
            
        返回:
            pandas.DataFrame: 包含期货公司数据的DataFrame
            
        异常:
            ValueError: 数据获取失败
            requests.exceptions.RequestException: 网络请求异常
        """
        # 构建请求参数
        params = {
            "reportName": "RPT_FUTU_FUTUREORGLIST",
            "columns": "ORGNAME_PINYIN,ORG_NAME_ABBR,ORG_CODE",
            "source": "WEB",
            "client": "WEB",
            "pageNumber": 1,
            "pageSize": page_size,
            "sortColumns": "ORGNAME_PINYIN,PINYIN_ABBR",
            "sortTypes": "1,1",
            "callback": f"jQuery112308520314316664147_{int(pd.Timestamp.now().timestamp() * 1000)}"
        }
        
        # 发送请求
        for attempt in range(self.retry_times):
            try:
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # 处理JSONP响应
                data = self._extract_json_from_jsonp(response.text)

                if data.get("success") is False:
                    logger.error(f"数据获取失败: {data.get('message', '未知错误')}")
                    raise ValueError("数据获取失败，请检查参数或网络连接")
                
                # 检查数据有效性
                if not data or "result" not in data or "data" not in data["result"]:
                    logger.warning("返回数据为空")
                    return pd.DataFrame()
                
                # 转换为DataFrame
                df = pd.DataFrame(data["result"]["data"])
                logger.info(f"获取到期货公司数据行数: {len(df)}")
                
                # 替换为中文字段名
                if use_chinese_fields:
                    # 创建映射字典，仅包含DataFrame中存在的列
                    field_map = {k: v for k, v in self.ORG_FIELD_MAPPING.items() if k in df.columns}
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

    def get_futures_list(
        self,
        is_main_code: bool = True,
        use_chinese_fields: bool = True
    ) -> pd.DataFrame:
        """
        获取期货品种列表数据
        
        参数:
            is_main_code: 是否只获取主力合约，默认为True
            use_chinese_fields: 是否使用中文字段名，默认为True
            
        返回:
            pandas.DataFrame: 包含期货品种数据的DataFrame
            
        异常:
            ValueError: 数据获取失败
            requests.exceptions.RequestException: 网络请求异常
        """
        # 构建请求参数
        params = {
            "reportName": self.report_name,
            "columns": self.default_columns,
            "source": "WEB",
            "client": "WEB",
            "pageNumber": 1,
            "pageSize": 200,
            "callback": f"jQuery112308520314316664147_{int(pd.Timestamp.now().timestamp() * 1000)}"
        }
        
        # 添加主力合约过滤条件
        if is_main_code:
            params["filter"] = "(IS_MAINCODE=\"1\")"
        
        # 发送请求
        for attempt in range(self.retry_times):
            try:
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # 处理JSONP响应
                data = self._extract_json_from_jsonp(response.text)

                if data.get("success") is False:
                    logger.error(f"数据获取失败: {data.get('message', '未知错误')}")
                    raise ValueError("数据获取失败，请检查参数或网络连接")
                
                # 检查数据有效性
                if not data or "result" not in data or "data" not in data["result"]:
                    logger.warning("返回数据为空")
                    return pd.DataFrame()
                
                # 转换为DataFrame
                df = pd.DataFrame(data["result"]["data"])
                logger.info(f"获取到数据行数: {len(df)}")
                
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
    # 初始化
    futures_list = FuturesList()
    
    print("="*50)
    print("获取所有期货品种数据")
    df = futures_list.get_futures_list()
    print(df.head())
    
    print("="*50)
    print("获取期货公司列表数据")
    org_df = futures_list.get_future_org_list()
    print(org_df.head())
    
    print("="*50)
    print("获取交易所品种数据")
    # 使用常量获取中金所品种
    exchange_df = futures_list.get_exchange_products(msgid=FuturesList.EXCHANGE_MSGID["中金所"])
    print(exchange_df.head())
    
    print("="*50)
    print("获取上期所品种")
    shfe_df = futures_list.get_exchange_products(msgid=FuturesList.EXCHANGE_MSGID["上期所"])
    print(shfe_df.head())