#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''东方财富网-融资融券-融资融券数据-融资融券余额'''

import logging
import requests
import json
import re
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


em_base_url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'


# 字段映射：英文字段名到中文字段名
FIELD_MAPPING = {
    # 板块信息
    "BOARD_CODE": "板块代码",
    "BOARD_NAME": "板块名称",
    "BOARD_TYPE": "板块类型",
    "BOARD_TYPE_CODE": "板块类型代码",
    "TRADE_DATE": "交易日期",
    "DIM_DATE": "交易日期",
    "STATISTICS_DATE": "统计日期",
    "DATE_MARK": "日期标记",
    
    # 融资数据
    "FIN_BALANCE": "融资余额",
    "FIN_BALANCE_DIFF": "融资余额差值",
    "FIN_BALANCE_RATIO": "融资余额占比",
    "FIN_BUY_AMT": "融资买入额",
    "FIN_REPAY_AMT": "融资偿还额",
    "FIN_NETBUY_AMT": "融资净买入额",
    "FIN_NETSELL_AMT": "融资净卖出额",
    
    # 融券数据
    "LOAN_BALANCE": "融券余额",
    "LOAN_BALANCE_VOL": "融券余量",
    "LOAN_SELL_VOL": "融券卖出量",
    "LOAN_REPAY_VOL": "融券偿还量",
    "LOAN_SELL_AMT": "融券卖出额",
    "LOAN_NETSELL_AMT": "融券净卖出额",
    
    # 总计数据
    "MARGIN_BALANCE": "融资融券余额",
    "NOTLIMITED_MARKETCAP_A": "流通市值",
    "BALANCE_RATIO": "余额比例",
    "MARGIN_TRADE_AMT": "融资融券交易额",
    "TRADE_AMT_RATIO": "交易额比例",
    
    # 账户相关数据
    "SECURITY_ORG_NUM": "证券机构数量",
    "OPERATEDEPT_NUM": "营业部数量",
    "PERSONAL_INVESTOR_NUM": "个人投资者数量(万)",
    "ORG_INVESTOR_NUM": "机构投资者数量",
    "INVESTOR_NUM": "投资者数量",
    "MARGINLIAB_INVESTOR_NUM": "融资融券负债投资者数量",
    "FUND_MARKET_CAP": "基金市值",
    "TOTAL_GUARANTEE": "总担保",
    "AVG_GUARANTEE_RATIO": "平均担保比例",
    "SCI_CLOSE_PRICE": "上证指数收盘价",
    "SCI_CHANGE_RATE": "上证指数变化率",
    "SUBSITUTION__CAP": "替代资本",
    
    # 沪市数据
    "H_RZYE": "沪市融资余额",
    "H_RQYL": "沪市融券余量",
    "H_RZMRE": "沪市融资买入额",
    "H_RQYE": "沪市融券余额",
    "H_RQMCL": "沪市融券卖出量",
    "H_LTSZ": "沪市流通市值",
    "H_RZYEZB": "沪市融资余额占比",
    "H_RZRQYE": "沪市融资融券余额",
    "H_RZRQYECZ": "沪市融资融券余额差值",
    
    # 深市数据
    "S_RZYE": "深市融资余额",
    "S_RQYL": "深市融券余量",
    "S_RZMRE": "深市融资买入额",
    "S_RQYE": "深市融券余额",
    "S_RQMCL": "深市融券卖出量",
    "S_LTSZ": "深市流通市值",
    "S_RZYEZB": "深市融资余额占比",
    "S_RZRQYE": "深市融资融券余额",
    "S_RZRQYECZ": "深市融资融券余额差值",
    
    # 北交所数据
    "B_RZYE": "北交所融资余额",
    "B_RQYL": "北交所融券余量",
    "B_RZMRE": "北交所融资买入额",
    "B_RQYE": "北交所融券余额",
    "B_RQMCL": "北交所融券卖出量",
    "B_LTSZ": "北交所流通市值",
    "B_RZYEZB": "北交所融资余额占比",
    "B_RZRQYE": "北交所融资融券余额",
    "B_RZRQYECZ": "北交所融资融券余额差值",
    
    # 总计数据（全市场）
    "TOTAL_LTSZ": "总流通市值",
    "TOTAL_RZYE": "总融资余额",
    "TOTAL_RZYEZB": "总融资余额占比",
    "TOTAL_RZMRE": "总融资买入额",
    "TOTAL_RQYE": "总融券余额",
    "TOTAL_RZRQYE": "总融资融券余额",
    "TOTAL_RZRQYECZ": "总融资融券余额差值",
    
    # 沪深合计数据
    "RZYE": "融资余额",
    "RZYEZB": "融资余额占比",
    "RZMRE": "融资买入额",
    "RQYE": "融券余额",
    "LTSZ": "流通市值",
    "RZRQYE": "融资融券余额",
    "RZRQYECZ": "融资融券余额差值",
    
    # 市场融资融券交易总量数据
    "NEW": "上证指数收盘点位",
    "ZDF": "上证指数涨跌幅",
    "ZDF3D": "上证指数3日涨跌幅",
    "ZDF5D": "上证指数5日涨跌幅",
    "ZDF10D": "上证指数10日涨跌幅",
    "RZCHE": "融资偿还额",
    "RZCHE3D": "融资偿还额3日",
    "RZCHE5D": "融资偿还额5日",
    "RZCHE10D": "融资偿还额10日",
    "RZJME": "融资净买入",
    "RZJME3D": "融资净买入3日",
    "RZJME5D": "融资净买入5日",
    "RZJME10D": "融资净买入10日",
    "RZMRE3D": "融资买入额3日",
    "RZMRE5D": "融资买入额5日",
    "RZMRE10D": "融资买入额10日",
    "RQCHL": "融券偿还量",
    "RQCHL3D": "融券偿还量3日",
    "RQCHL5D": "融券偿还量5日",
    "RQCHL10D": "融券偿还量10日",
    "RQMCL": "融券卖出量",
    "RQMCL3D": "融券卖出量3日",
    "RQMCL5D": "融券卖出量5日",
    "RQMCL10D": "融券卖出量10日",
    "RQJMG": "融券净卖出",
    "RQJMG3D": "融券净卖出3日",
    "RQJMG5D": "融券净卖出5日",
    "RQJMG10D": "融券净卖出10日",
    "RQYL": "融券余量"
}

def convert_fields_to_chinese(data):
    """
    将数据中的英文字段名转换为中文字段名
    
    参数:
        data (dict): 包含英文字段名的数据
        
    返回:
        dict: 包含中文字段名的数据
    """
    if not data or not isinstance(data, dict):
        return data
    
    # 处理result.data数组中的每个对象
    if 'result' in data and 'data' in data['result'] and isinstance(data['result']['data'], list):
        chinese_data = []
        for item in data['result']['data']:
            chinese_item = {}
            for key, value in item.items():
                chinese_key = FIELD_MAPPING.get(key, key)  # 如果没有映射，保留原始键
                chinese_item[chinese_key] = value
            chinese_data.append(chinese_item)
        
        # 创建新的结果对象，保留原始结构但使用中文字段名的数据
        result = data['result'].copy()
        result['data'] = chinese_data
        
        # 创建新的响应对象
        response = data.copy()
        response['result'] = result
        return response
    
    return data

def get_rzrq_industry_rank(page=1, page_size=5, sort_column="FIN_NETBUY_AMT", sort_type=-1, board_type_code="006", use_chinese_fields=True):
    """
    获取东方财富网融资融券行业板块排行数据
    
    参数:
        page (int): 页码，默认为1
        page_size (int): 每页数量，默认为5
        sort_column (str): 排序列，默认为"FIN_NETBUY_AMT"（融资净买入额）
        sort_type (int): 排序类型，1为升序，-1为降序，默认为-1
        board_type_code (str): 板块类型代码，默认为"006"（财富通行业）
        use_chinese_fields (bool): 是否使用中文字段名，默认为True
    
    返回:
        dict: 包含融资融券行业板块排行数据的字典
    """
    try:
        # 构建请求参数
        params = {
            'callback': f'datatable{int(time.time() * 1000)}',  # 生成一个时间戳作为回调函数名
            'reportName': 'RPTA_WEB_BKJYMXN',
            'columns': 'ALL',
            'pageNumber': page,
            'pageSize': page_size,
            'sortColumns': sort_column,
            'sortTypes': sort_type,
            'stat': 1,
            'filter': f'(BOARD_TYPE_CODE="{board_type_code}")',
            '_': int(time.time() * 1000)  # 时间戳
        }
        
        # 发送请求
        logger.info(f"正在获取融资融券行业板块排行数据，页码：{page}，每页数量：{page_size}")
        response = requests.get(em_base_url, params=params)
        
        if response.status_code != 200:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return None
        
        # 提取JSON数据（从JSONP响应中）
        jsonp_data = response.text
        json_data_match = re.search(r'\((.*)\)', jsonp_data)
        
        if not json_data_match:
            logger.error("无法从JSONP响应中提取JSON数据")
            return None
        
        json_data = json.loads(json_data_match.group(1))
        
        # 检查API返回是否成功
        if not json_data.get('success'):
            logger.error(f"API返回错误：{json_data.get('message')}")
            return None
        
        # 如果需要使用中文字段名，则转换字段
        if use_chinese_fields:
            return convert_fields_to_chinese(json_data)
        
        return json_data
    
    except Exception as e:
        logger.error(f"获取融资融券行业板块排行数据时发生错误：{str(e)}")
        return None


def get_rzrq_industry_detail(board_code, start_date=None, end_date=None, page=1, page_size=20, use_chinese_fields=True):
    """
    获取特定行业板块的融资融券明细数据
    
    参数:
        board_code (str): 板块代码
        start_date (str): 开始日期，格式为'YYYY-MM-DD'，默认为None
        end_date (str): 结束日期，格式为'YYYY-MM-DD'，默认为None
        page (int): 页码，默认为1
        page_size (int): 每页数量，默认为20
        use_chinese_fields (bool): 是否使用中文字段名，默认为True
    
    返回:
        dict: 包含特定行业板块融资融券明细数据的字典
    """
    try:
        # 构建过滤条件
        filter_conditions = [f"(BOARD_CODE=\"{board_code}\")"]
        if start_date:
            filter_conditions.append(f"(TRADE_DATE>='{start_date}')")
        if end_date:
            filter_conditions.append(f"(TRADE_DATE<='{end_date}')")
        
        filter_str = " and ".join(filter_conditions)
        
        # 构建请求参数
        params = {
            'callback': f'datatable{int(time.time() * 1000)}',
            'reportName': 'RPTA_WEB_BKJYMXN',
            'columns': 'ALL',
            'pageNumber': page,
            'pageSize': page_size,
            'sortColumns': 'TRADE_DATE',
            'sortTypes': -1,  # 按日期降序
            'stat': 1,
            'filter': filter_str,
            '_': int(time.time() * 1000)
        }
        
        # 发送请求
        logger.info(f"正在获取板块{board_code}的融资融券明细数据")
        response = requests.get(em_base_url, params=params)
        
        if response.status_code != 200:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return None
        
        # 提取JSON数据（从JSONP响应中）
        jsonp_data = response.text
        json_data_match = re.search(r'\((.*)\)', jsonp_data)
        
        if not json_data_match:
            logger.error("无法从JSONP响应中提取JSON数据")
            return None
        
        json_data = json.loads(json_data_match.group(1))
        
        # 检查API返回是否成功
        if not json_data.get('success'):
            logger.error(f"API返回错误：{json_data.get('message')}")
            return None
        
        # 如果需要使用中文字段名，则转换字段
        if use_chinese_fields:
            return convert_fields_to_chinese(json_data)
        
        return json_data
    
    except Exception as e:
        logger.error(f"获取行业板块融资融券明细数据时发生错误：{str(e)}")
        return None


def get_rzrq_history(start_date=None, end_date=None, page=1, page_size=10, use_chinese_fields=True):
    """
    获取融资融券交易历史明细数据（沪深北三市场）
    
    参数:
        start_date (str): 开始日期，格式为'YYYY-MM-DD'，默认为None
        end_date (str): 结束日期，格式为'YYYY-MM-DD'，默认为None
        page (int): 页码，默认为1
        page_size (int): 每页数量，默认为10
        use_chinese_fields (bool): 是否使用中文字段名，默认为True
    
    返回:
        dict: 包含融资融券交易历史明细数据的字典
    """
    try:
        # 构建过滤条件
        filter_conditions = []
        if start_date:
            filter_conditions.append(f"(DIM_DATE>='{start_date}')")
        if end_date:
            filter_conditions.append(f"(DIM_DATE<='{end_date}')")
        
        filter_str = " and ".join(filter_conditions) if filter_conditions else ""
        
        # 构建请求参数
        params = {
            'callback': f'datatable{int(time.time() * 1000)}',
            'reportName': 'RPTA_RZRQ_LSDB',
            'columns': 'ALL',
            'source': 'WEB',
            'pageNumber': page,
            'pageSize': page_size,
            'sortColumns': 'DIM_DATE',
            'sortTypes': -1,  # 按日期降序
            '_': int(time.time() * 1000)
        }
        
        # 如果有过滤条件，添加到参数中
        if filter_str:
            params['filter'] = filter_str
        
        # 发送请求
        logger.info(f"正在获取融资融券交易历史明细数据，页码：{page}，每页数量：{page_size}")
        response = requests.get(em_base_url, params=params)
        
        if response.status_code != 200:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return None
        
        # 提取JSON数据（从JSONP响应中）
        jsonp_data = response.text
        json_data_match = re.search(r'\((.*)\)', jsonp_data)
        
        if not json_data_match:
            logger.error("无法从JSONP响应中提取JSON数据")
            return None
        
        json_data = json.loads(json_data_match.group(1))
        
        # 检查API返回是否成功
        if not json_data.get('success'):
            logger.error(f"API返回错误：{json_data.get('message')}")
            return None
        
        # 如果需要使用中文字段名，则转换字段
        if use_chinese_fields:
            return convert_fields_to_chinese(json_data)
        
        return json_data
    
    except Exception as e:
        logger.error(f"获取融资融券交易历史明细数据时发生错误：{str(e)}")
        return None


def get_rzrq_market_summary(start_date=None, end_date=None, page=1, page_size=10, use_chinese_fields=True):
    """
    获取市场融资融券交易总量数据（含上证指数和融资融券汇总数据）
    
    参数:
        start_date (str): 开始日期，格式为'YYYY-MM-DD'，默认为None
        end_date (str): 结束日期，格式为'YYYY-MM-DD'，默认为None
        page (int): 页码，默认为1
        page_size (int): 每页数量，默认为10
        use_chinese_fields (bool): 是否使用中文字段名，默认为True
    
    返回:
        dict: 包含市场融资融券交易总量数据的字典
    """
    try:
        # 构建过滤条件
        filter_conditions = []
        if start_date:
            filter_conditions.append(f"(DIM_DATE>='{start_date}')")
        if end_date:
            filter_conditions.append(f"(DIM_DATE<='{end_date}')")
        
        filter_str = " and ".join(filter_conditions) if filter_conditions else ""
        
        # 构建请求参数
        params = {
            'callback': f'datatable{int(time.time() * 1000)}',
            'reportName': 'RPTA_RZRQ_LSHJ',
            'columns': 'ALL',
            'source': 'WEB',
            'pageNumber': page,
            'pageSize': page_size,
            'sortColumns': 'DIM_DATE',
            'sortTypes': -1,  # 按日期降序
            '_': int(time.time() * 1000)
        }
        
        # 如果有过滤条件，添加到参数中
        if filter_str:
            params['filter'] = filter_str
        
        # 发送请求
        logger.info(f"正在获取市场融资融券交易总量数据，页码：{page}，每页数量：{page_size}")
        response = requests.get(em_base_url, params=params)
        
        if response.status_code != 200:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return None
        
        # 提取JSON数据（从JSONP响应中）
        jsonp_data = response.text
        json_data_match = re.search(r'\((.*)\)', jsonp_data)
        
        if not json_data_match:
            logger.error("无法从JSONP响应中提取JSON数据")
            return None
        
        json_data = json.loads(json_data_match.group(1))
        
        # 检查API返回是否成功
        if not json_data.get('success'):
            logger.error(f"API返回错误：{json_data.get('message')}")
            return None
        
        # 如果需要使用中文字段名，则转换字段
        if use_chinese_fields:
            return convert_fields_to_chinese(json_data)
        
        return json_data
    
    except Exception as e:
        logger.error(f"获取市场融资融券交易总量数据时发生错误：{str(e)}")
        return None


def get_rzrq_concept_rank(page=1, page_size=50, sort_column="FIN_NETBUY_AMT", sort_type=-1, use_chinese_fields=True):
    """
    获取东方财富网融资融券概念板块排行数据
    
    参数:
        page (int): 页码，默认为1
        page_size (int): 每页数量，默认为50
        sort_column (str): 排序列，默认为"FIN_NETBUY_AMT"（融资净买入额）
        sort_type (int): 排序类型，1为升序，-1为降序，默认为-1
        use_chinese_fields (bool): 是否使用中文字段名，默认为True
    
    返回:
        dict: 包含融资融券概念板块排行数据的字典
    """
    try:
        # 构建请求参数
        params = {
            'callback': f'datatable{int(time.time() * 1000)}',  # 生成一个时间戳作为回调函数名
            'reportName': 'RPTA_WEB_BKJYMXN',
            'columns': 'ALL',
            'pageNumber': page,
            'pageSize': page_size,
            'sortColumns': sort_column,
            'sortTypes': sort_type,
            'stat': 1,
            'filter': '(BOARD_TYPE_CODE="006")',  # 财富通概念板块
            '_': int(time.time() * 1000)  # 时间戳
        }
        
        # 发送请求
        logger.info(f"正在获取融资融券概念板块排行数据，页码：{page}，每页数量：{page_size}")
        response = requests.get(em_base_url, params=params)
        
        if response.status_code != 200:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return None
        
        # 提取JSON数据（从JSONP响应中）
        jsonp_data = response.text
        json_data_match = re.search(r'\((.*)\)', jsonp_data)
        
        if not json_data_match:
            logger.error("无法从JSONP响应中提取JSON数据")
            return None
        
        json_data = json.loads(json_data_match.group(1))
        
        # 检查API返回是否成功
        if not json_data.get('success'):
            logger.error(f"API返回错误：{json_data.get('message')}")
            return None
        
        # 如果需要使用中文字段名，则转换字段
        if use_chinese_fields:
            return convert_fields_to_chinese(json_data)
        
        return json_data
    
    except Exception as e:
        logger.error(f"获取融资融券概念板块排行数据时发生错误：{str(e)}")
        return None


def get_rzrq_account_data(page=1, page_size=50, sort_column="STATISTICS_DATE", sort_type=-1, 
                         start_date=None, end_date=None, use_chinese_fields=True):
    """
    获取两融账户信息数据
    
    参数:
        page (int): 页码，默认为1
        page_size (int): 每页数量，默认为50
        sort_column (str): 排序列，默认为"STATISTICS_DATE"（统计日期）
        sort_type (int): 排序类型，1为升序，-1为降序，默认为-1
        start_date (str): 开始日期，格式为'YYYY-MM-DD'，默认为None
        end_date (str): 结束日期，格式为'YYYY-MM-DD'，默认为None
        use_chinese_fields (bool): 是否使用中文字段名，默认为True
    
    返回:
        dict: 包含两融账户信息数据的字典
    """
    try:
        # 构建过滤条件
        filter_conditions = []
        if start_date:
            filter_conditions.append(f"(STATISTICS_DATE>='{start_date}')")
        if end_date:
            filter_conditions.append(f"(STATISTICS_DATE<='{end_date}')")
        
        filter_str = " and ".join(filter_conditions) if filter_conditions else ""
        
        # 构建请求参数
        params = {
            'callback': f'datatable{int(time.time() * 1000)}',
            'reportName': 'RPTA_WEB_MARGIN_DAILYTRADE',
            'columns': 'ALL',
            'pageNumber': page,
            'pageSize': page_size,
            'sortColumns': sort_column,
            'sortTypes': sort_type,
            '_': int(time.time() * 1000)
        }
        
        # 如果有过滤条件，添加到参数中
        if filter_str:
            params['filter'] = filter_str
        
        # 发送请求
        logger.info(f"正在获取两融账户信息数据，页码：{page}，每页数量：{page_size}")
        response = requests.get(em_base_url, params=params)
        
        if response.status_code != 200:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return None
        
        # 提取JSON数据（从JSONP响应中）
        jsonp_data = response.text
        json_data_match = re.search(r'\((.*)\)', jsonp_data)
        
        if not json_data_match:
            logger.error("无法从JSONP响应中提取JSON数据")
            return None
        
        json_data = json.loads(json_data_match.group(1))
        
        # 检查API返回是否成功
        if not json_data.get('success'):
            logger.error(f"API返回错误：{json_data.get('message')}")
            return None
        
        # 如果需要使用中文字段名，则转换字段
        if use_chinese_fields:
            return convert_fields_to_chinese(json_data)
        
        return json_data
    
    except Exception as e:
        logger.error(f"获取两融账户信息数据时发生错误：{str(e)}")
        return None