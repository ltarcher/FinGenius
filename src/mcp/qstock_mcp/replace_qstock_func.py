#!/usr/bin/env python
# -*- encoding=utf8 -*-

import qstock
import pandas as pd
from datetime import datetime

from qstock.data.util import (request_header, session, market_num_dict,
                  trans_num, )

#替换qstock中的字典
trade_detail_dict = {
    'f12': '代码',
    'f14': '名称',
    'f3': '涨幅',
    'f2': '最新',
    'f15': '最高',
    'f16': '最低',
    'f17': '今开',
    'f8': '换手率',
    'f10': '量比',
    'f9': '市盈率',
    'f5': '成交量',
    'f6': '成交额',
    'f18': '昨收',
    'f20': '总市值',
    'f21': '流通市值',
    'f13': '编号',
    'f124': '更新时间戳',
}

# 期权列表字典
option_detail_dict = {
    "f1": "未知-0",
    "f2": "最新价",
    "f3": "涨幅",
    "f4": "涨跌额",
    "f5": "成交量",
    "f6": "成交额",
    "f12": "代码",
    "f13": "编号",
    "f14": "名称",
    "f17": "今开",
    "f28": "昨结",
    "f108": "持仓量", 
    "f152": "未知-2",
    "f161": "行权价",
    "f162": "剩余日",
    "f163": "日增",
    "f330": "未知-3",
    'f124': '更新时间戳',
}

#期权风险字典
option_risk_detail_dict = {
    #期权风险
    "f1": "未知-0",
    "f2": "最新价",
    "f3": "涨幅",
    "f12": "代码",
    "f13": "编号",
    "f14": "名称",
    'f302': '杠杆比率',
    'f303': '实际杠杆比率',
    'f325': 'Delta',
    'f326': 'Gamma',
    'f327': 'Vega',
    'f329': 'Rho',
    'f328': 'Theta',
    'f301': '到期日',
    'f152': '未知-2',
    'f154': '未知-4',
    'f124': '更新时间戳',
}

#期权价值字典
option_value_detail_dict = {
    #期权价值
    "f1": "未知-0",
    "f2": "最新价",
    "f3": "涨幅",
    "f12": "代码",
    "f13": "编号",
    "f14": "名称",
    'f152': '未知-2',
    "f249": "隐含波动率",
    "f298": "时间价值",
    "f299": "内在价值",
    "f300": "理论价格",
    "f301": "到期日",
    "f330": "未知-3",
    "f331": "标的代码",
    "f332": "未知-1",
    "f333": "标的名称",
    "f334": "标的最新价",
    "f335": "标的涨幅",
    "f336": "标的近1年波动率",
    'f124': '更新时间戳',
}

#期权市场代码
option_market_code =[ 
    { "market": 1, "code": "510500", "name": "中证500ETF期权"},
    { "market": 1, "code": "510300", "name": "沪深300ETF期权"},
    { "market": 1, "code": "510050", "name": "50ETF期权"},
    { "market": 1, "code": "588000", "name": "科创50期权"},
    { "market": 1, "code": "588080", "name": "科创板50期权"},
    { "market": 0, "code": "159919", "name": "沪深300ETF期权"},
    { "market": 0, "code": "159922", "name": "中证500ETF期权"},
    { "market": 0, "code": "159915", "name": "创业板ETF期权"},
]

#期权T型盘字典
#option_tboard_dict字段:f12,f13,f14,f1,f2,f4,f334,f330,f3,f152,f108,f5,f249,f250,f161,f340,f339,f341,f342,f343,f345,f344,f346,f347
option_tboard_dict = {
    "f1": "未知-0",
    "f12": "购代码",
    "f13": "编号",
    "f14": "购名称",
    "f2": "购最新价",
    "f4": "购涨跌额",
    "f334": "标的最新价",
    "f330": "未知-3",
    "f3": "购涨跌幅",
    "f152": "未知-2",
    "f108": "购持仓量",
    "f5": "购成交量",
    "f249": "购隐含波动率",
    "f250": "购折溢价率",
    "f161": "行权价",
    "f340": "沽名称",
    "f339": "沽代码",
    "f341": "沽最新价",
    "f342": "沽涨跌额",
    "f343": "沽涨跌幅",
    "f345": "沽持仓量",
    "f344": "沽成交量",
    "f346": "沽隐含波动率",
    "f347": "沽折溢价率",
}

# 期权溢价字典
# fields: f1,f2,f3,f12,f13,f14,f161,f250,f330,f331,f332,f333,f334,f335,f337,f301,f152
option_premium_dict = {
    "f1": "未知-0",
    "f2": "最新价",
    "f3": "涨跌幅",
    "f12": "代码",
    "f13": "编号",
    "f14": "名称",
    "f161": "行权价",
    "f250": "折溢价率",
    "f330": "未知-3",
    "f331": "标的代码",
    "f332": "未知-1",
    "f333": "标的名称",
    "f334": "标的最新价",
    "f335": "标的涨跌幅",
    "f337": "盈亏平衡价",
    "f301": "到期日",
    "f152": "未知-2",
}

# 获取某指定市场所有标的最新行情指标
def bso_market_realtime(market='沪深A', trade_detail_dict=trade_detail_dict, fltt='2'):
    """
    获取沪深市场最新行情总体情况（涨跌幅、换手率等信息）
     market表示行情名称或列表，默认沪深A股
    '沪深京A':沪深京A股市场行情; '沪深A':沪深A股市场行情;'沪A':沪市A股市场行情
    '深A':深市A股市场行情;北A :北证A股市场行情;'可转债':沪深可转债市场行情;
    '期权':期权市场行情;'期权风险':期权风险市场行情;
    '期货':期货市场行情;'创业板':创业板市场行情;'美股':美股市场行情;
    '港股':港股市场行情;'中概股':中国概念股市场行情;'新股':沪深新股市场行情;
    '科创板':科创板市场行情;'沪股通' 沪股通市场行情;'深股通':深股通市场行情;
    '行业板块':行业板块市场行情;'概念板块':概念板块市场行情;
    '沪深指数':沪深系列指数市场行情;'上证指数':上证系列指数市场行情
    '深证指数':深证系列指数市场行情;'ETF' ETF基金市场行情;'LOF' LOF 基金市场行情
    """
    # 市场与编码
    market_dict = {
        'stock': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23',
        '沪深A': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23',
        '上证A': 'm:1 t:2,m:1 t:23',
        '沪A': 'm:1 t:2,m:1 t:23',
        '深证A': 'm:0 t:6,m:0 t:80',
        '深A': 'm:0 t:6,m:0 t:80',
        '北证A': 'm:0 t:81 s:2048',
        '北A': 'm:0 t:81 s:2048',
        '创业板': 'm:0 t:80',
        '科创板': 'm:1 t:23',
        '沪深京A': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048',
        '沪股通': 'b:BK0707',
        '深股通': 'b:BK0804',
        '风险警示板': 'm:0 f:4,m:1 f:4',
        '两网及退市': 'm:0 s:3',
        '新股': 'm:0 f:8,m:1 f:8',
        '美股': 'm:105,m:106,m:107',
        '港股': 'm:128 t:3,m:128 t:4,m:128 t:1,m:128 t:2',
        '英股': 'm:155 t:1,m:155 t:2,m:155 t:3,m:156 t:1,m:156 t:2,m:156 t:5,m:156 t:6,m:156 t:7,m:156 t:8',
        '中概股': 'b:MK0201',
        '中国概念股': 'b:MK0201',
        '地域板块': 'm:90 t:1 f:!50',
        '地域': 'm:90 t:1 f:!50',
        '行业板块': 'm:90 t:2 f:!50',
        '行业': 'm:90 t:2 f:!50',
        '概念板块': 'm:90 t:3 f:!50',
        '概念': 'm:90 t:3 f:!50',
        '上证指数': 'm:1 s:2',
        '上证系列指数': 'm:1 s:2',
        '深证指数': 'm:0 t:5',
        '深证系列指数': 'm:0 t:5',
        '沪深指数': 'm:1 s:2,m:0 t:5',
        '沪深系列指数': 'm:1 s:2,m:0 t:5',
        'bond': 'b:MK0354',
        '债券': 'b:MK0354',
        '可转债': 'b:MK0354',
        'future': 'm:113,m:114,m:115,m:8,m:142',
        '期货': 'm:113,m:114,m:115,m:8,m:142',
        #'期权': 'm:10,m:140,m:141,m:151,m:163,m:226',   #原来qstock中没有期权市场
        '期权': 'm:10', #只看ETF期权
        '期权风险': 'm:10', #只看ETF期权
        'ETF': 'b:MK0021,b:MK0022,b:MK0023,b:MK0024',
        'LOF': 'b:MK0404,b:MK0405,b:MK0406,b:MK0407', }

    fs = market_dict[market]

    fields = ",".join(trade_detail_dict.keys())
    params = {
        'pn': '1',    #页数
        'pz': '200',  #服务器限制单页最多200
        'po': '1',
        'np': '1',
        'fltt': fltt,
        'invt': '2',
        'fid': 'f3',#排序字段
        'fs': fs,
        'fields': fields,
    }
    count = 0
    url = 'http://push2.eastmoney.com/api/qt/clist/get'
    json_response = session.get(url,
                                headers=request_header,
                                params=params).json()
    df = pd.DataFrame(json_response['data']['diff'])
    count = len(json_response['data']['diff'])
    if count == 0:
        return pd.DataFrame()
    
    #根据json_response['data']['total']重复获取数据
    total_count = json_response['data']['total']
    if count < total_count:
        for i in range(2, int(total_count / 200) + 2):
            params["pn"] = i
            json_response = session.get(url, headers=request_header, params=params).json()
            df = pd.concat([df, pd.DataFrame(json_response['data']['diff'])], ignore_index=True)
    
    df = df.rename(columns=trade_detail_dict)
    df = df[trade_detail_dict.values()]
    df['ID'] = df['编号'].astype(str) + '.' + df['代码'].astype(str)
    df['市场'] = df['编号'].astype(str).apply(
        lambda x: market_num_dict.get(x))
    #如果更新时间戳存在，则将时间戳转换为时间
    if '更新时间戳' in df.columns:
        df['时间'] = df['更新时间戳'].apply(lambda x: str(datetime.fromtimestamp(x)))
        del df['更新时间戳']
    del df['编号']
    del df['ID']
    del df['市场']
    #移除列名包含"未知"的列
    df = df.loc[:, df.columns.str.contains('未知') == False]

    return df

def bso_option_realtime(market='期权', trade_detail_dict=trade_detail_dict, fltt='1', fid='f3'):
    # 市场与编码
    market_dict = {
        '期权': 'm:10', #只看ETF期权
        '期权风险': 'm:10', #只看ETF期权
    }

    fs = market_dict[market]

    fields = ",".join(trade_detail_dict.keys())
    params = {
        'pn': '1',    #页数
        'pz': '200',  #服务器限制单页最多200
        'po': '1',
        'np': '1',
        'fltt': fltt,
        'invt': '2',
        'fid': fid,#排序字段
        'fs': fs,
        'fields': fields,
    }
    count = 0
    url = 'http://push2.eastmoney.com/api/qt/clist/get'
    json_response = session.get(url,
                                headers=request_header,
                                params=params).json()
    df = pd.DataFrame(json_response['data']['diff'])
    count = len(json_response['data']['diff'])
    if count == 0:
        return pd.DataFrame()
    
    #根据json_response['data']['total']重复获取数据
    total_count = json_response['data']['total']
    if count < total_count:
        for i in range(2, int(total_count / 200) + 2):
            params["pn"] = i
            json_response = session.get(url, headers=request_header, params=params).json()
            df = pd.concat([df, pd.DataFrame(json_response['data']['diff'])], ignore_index=True)
    
    df = df.rename(columns=trade_detail_dict)
    df = df[trade_detail_dict.values()]
    #如果更新时间戳存在，则将时间戳转换为时间
    if '更新时间戳' in df.columns:
        df['时间'] = df['更新时间戳'].apply(lambda x: str(datetime.fromtimestamp(x)))
        del df['更新时间戳']
    del df['编号']
    #移除列名包含"未知"的列
    df = df.loc[:, df.columns.str.contains('未知') == False]
    if fltt == '1':
        #期权列表的最新价需要/10000
        df['最新价'] = df['最新价'].apply(lambda x: x / 10000)
        df['涨幅'] = df['涨幅'].apply(lambda x: x / 100)
        df['涨跌额'] = df['涨跌额'].apply(lambda x: x / 10000)

    return df

# 获取所有期权市场到期日信息
def bso_option_expire_all():
    '''
    获取所有期权市场到期日信息
    '''
    df = pd.DataFrame()
    for item in option_market_code:
        df = pd.concat([df, bso_option_expire_info(item['code'], item['market'])], ignore_index=True)
    return df

# 获取指定期权代码到期日信息
def bso_option_expire_info(code, market=0):
    '''
    code: 期权代码
    market: 1 上交所，0 深交所
    '''
    params = (
        ('mspt', 1),
        ('secid', '{}.{}'.format(market, code)),
    )

    url = 'http://push2.eastmoney.com/api/qt/stock/get'
    json_response = session.get(url,
                                headers=request_header,
                                params=params).json()
    if not 'data' in json_response or json_response['data'] is None:
        return pd.DataFrame()
    df = pd.DataFrame(json_response['data']['optionExpireInfo'])
    df = df.rename(columns={'date': '到期日', 'days': '剩余日'})
    df["市场"] = market_num_dict.get(str(market))
    df["代码"] = code
    df["到期日"] = df["到期日"].astype(str)
    return df

#获取所有月份期权T型看板

def bso_option_tboard_all():
    '''
    获取所有月份期权T型看板
    '''
    df = pd.DataFrame()
    month = bso_option_expire_all()['到期日'].unique()
    for item in month:
        df = pd.concat([df, bso_option_tboard_month(item[:-2])], ignore_index=True)
    df = df.rename(columns=option_tboard_dict)

    return df

#获取所有期权T型看板

def bso_option_tboard_month(expire_month):
    '''
    获取指定月份所有期权T型看板
    '''
    df = pd.DataFrame()
    for item in option_market_code:
        df = pd.concat([df, bso_option_tboard(item['code'], item['market'], expire_month)], ignore_index=True)
    return df

#获取T型期权看板
def bso_option_tboard(code, market, expire_month):
    '''
    code: 期权标的代码
    market: 1 上交所，0 深交所
    '''
    fields = ",".join(option_tboard_dict.keys())
    params = {
        'mspt': '1',
        'secid': '{}.{}'.format(market, code),
        'exti': expire_month,
        'pn': '1',
        'pz': '200',
        'po': '0',
        'np': '1',
        'fltt': '1',
        'invt': '2',
        'fid': 'f161',  #排序字段
        'spt': '9',
        'fields': fields,
        'dect': '1'
    }
    count = 0
    url = 'http://push2.eastmoney.com/api/qt/slist/get'
    json_response = session.get(url,
                                headers=request_header,
                                params=params).json()
    df = pd.DataFrame(json_response['data']['diff'])
    count = len(json_response['data']['diff'])
    if count == 0:
        return pd.DataFrame()
    
    #根据json_response['data']['total']重复获取数据
    total_count = json_response['data']['total']
    if count < total_count:
        for i in range(2, int(total_count / 200) + 2):
            params["pn"] = i
            json_response = session.get(url, headers=request_header, params=params).json()
            df = pd.concat([df, pd.DataFrame(json_response['data']['diff'])], ignore_index=True)

    df = df.rename(columns=option_tboard_dict)
    df = df[option_tboard_dict.values()]
    df['市场'] = df['编号'].astype(str).apply(
        lambda x: market_num_dict.get(x))
    df['时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    del df['编号']
    del df['市场']
    #移除列名包含"未知"的列
    df = df.loc[:, df.columns.str.contains('未知') == False]
    df["到期日"] = expire_month
    #部分字段需要转换
    #最新价需要除以10000
    df['购最新价'] = df['购最新价'].apply(lambda x: x / 10000 if x != '-' else x)
    df['沽最新价'] = df['沽最新价'].apply(lambda x: x / 10000 if x != '-' else x)
    df['购涨跌幅'] = df['购涨跌幅'].apply(lambda x: x / 100 if x != '-' else x)
    df['沽涨跌幅'] = df['沽涨跌幅'].apply(lambda x: x / 100 if x != '-' else x)
    df['购涨跌额'] = df['购涨跌额'].apply(lambda x: x / 10000 if x != '-' else x)
    df['沽涨跌额'] = df['沽涨跌额'].apply(lambda x: x / 10000 if x != '-' else x)
    df['购隐含波动率'] = df['购隐含波动率'].apply(lambda x: x / 100 if x != '-' else x)
    df['沽隐含波动率'] = df['沽隐含波动率'].apply(lambda x: x / 100 if x != '-' else x)
    df['购折溢价率'] = df['购折溢价率'].apply(lambda x: x / 100 if x != '-' else x)
    df['沽折溢价率'] = df['沽折溢价率'].apply(lambda x: x / 100 if x != '-' else x)
    return df