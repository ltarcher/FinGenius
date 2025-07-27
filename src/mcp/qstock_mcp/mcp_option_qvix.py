import traceback
import logging
from mcp_instance import mcp
import index_option_qvix as qvix

# 配置日志
logger = logging.getLogger("mcp_option_qvix")

@mcp.tool()
async def get_50etf_qvix() -> list:
    """ 获取50ETF期权波动率指数QVIX日线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含50ETF期权波动率指数QVIX日线数据，
    Dict包含字段: ['date', 'open', 'high', 'low', 'close']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_50etf_qvix()
        
        logger.info(f"获取50ETF期权波动率指数QVIX日线数据")
        if df.empty:
            logger.warning(f"获取的50ETF期权波动率指数QVIX日线数据为空")
            return []
                
        logger.info(f"50ETF期权波动率指数QVIX日线数据获取成功: {df.shape[0]} 条记录")
        
        # 确保日期列是字符串格式
        df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取50ETF期权波动率指数QVIX日线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_50etf_min_qvix() -> list:
    """ 获取50ETF期权波动率指数QVIX分钟线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含50ETF期权波动率指数QVIX分钟线数据，
    Dict包含字段: ['time', 'qvix']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_50etf_min_qvix()
        
        logger.info(f"获取50ETF期权波动率指数QVIX分钟线数据")
        if df.empty:
            logger.warning(f"获取的50ETF期权波动率指数QVIX分钟线数据为空")
            return []
                
        logger.info(f"50ETF期权波动率指数QVIX分钟线数据获取成功: {df.shape[0]} 条记录")
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取50ETF期权波动率指数QVIX分钟线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_300etf_qvix() -> list:
    """ 获取300ETF期权波动率指数QVIX日线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含300ETF期权波动率指数QVIX日线数据，
    Dict包含字段: ['date', 'open', 'high', 'low', 'close']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_300etf_qvix()
        
        logger.info(f"获取300ETF期权波动率指数QVIX日线数据")
        if df.empty:
            logger.warning(f"获取的300ETF期权波动率指数QVIX日线数据为空")
            return []
                
        logger.info(f"300ETF期权波动率指数QVIX日线数据获取成功: {df.shape[0]} 条记录")
        
        # 确保日期列是字符串格式
        df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取300ETF期权波动率指数QVIX日线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_300etf_min_qvix() -> list:
    """ 获取300ETF期权波动率指数QVIX分钟线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含300ETF期权波动率指数QVIX分钟线数据，
    Dict包含字段: ['time', 'qvix']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_300etf_min_qvix()
        
        logger.info(f"获取300ETF期权波动率指数QVIX分钟线数据")
        if df.empty:
            logger.warning(f"获取的300ETF期权波动率指数QVIX分钟线数据为空")
            return []
                
        logger.info(f"300ETF期权波动率指数QVIX分钟线数据获取成功: {df.shape[0]} 条记录")
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取300ETF期权波动率指数QVIX分钟线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_500etf_qvix() -> list:
    """ 获取500ETF期权波动率指数QVIX日线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含500ETF期权波动率指数QVIX日线数据，
    Dict包含字段: ['date', 'open', 'high', 'low', 'close']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_500etf_qvix()
        
        logger.info(f"获取500ETF期权波动率指数QVIX日线数据")
        if df.empty:
            logger.warning(f"获取的500ETF期权波动率指数QVIX日线数据为空")
            return []
                
        logger.info(f"500ETF期权波动率指数QVIX日线数据获取成功: {df.shape[0]} 条记录")
        
        # 确保日期列是字符串格式
        df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取500ETF期权波动率指数QVIX日线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_500etf_min_qvix() -> list:
    """ 获取500ETF期权波动率指数QVIX分钟线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含500ETF期权波动率指数QVIX分钟线数据，
    Dict包含字段: ['time', 'qvix']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_500etf_min_qvix()
        
        logger.info(f"获取500ETF期权波动率指数QVIX分钟线数据")
        if df.empty:
            logger.warning(f"获取的500ETF期权波动率指数QVIX分钟线数据为空")
            return []
                
        logger.info(f"500ETF期权波动率指数QVIX分钟线数据获取成功: {df.shape[0]} 条记录")
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取500ETF期权波动率指数QVIX分钟线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_cyb_qvix() -> list:
    """ 获取创业板期权波动率指数QVIX日线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含创业板期权波动率指数QVIX日线数据，
    Dict包含字段: ['date', 'open', 'high', 'low', 'close']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_cyb_qvix()
        
        logger.info(f"获取创业板期权波动率指数QVIX日线数据")
        if df.empty:
            logger.warning(f"获取的创业板期权波动率指数QVIX日线数据为空")
            return []
                
        logger.info(f"创业板期权波动率指数QVIX日线数据获取成功: {df.shape[0]} 条记录")
        
        # 确保日期列是字符串格式
        df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取创业板期权波动率指数QVIX日线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_cyb_min_qvix() -> list:
    """ 获取创业板期权波动率指数QVIX分钟线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含创业板期权波动率指数QVIX分钟线数据，
    Dict包含字段: ['time', 'qvix']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_cyb_min_qvix()
        
        logger.info(f"获取创业板期权波动率指数QVIX分钟线数据")
        if df.empty:
            logger.warning(f"获取的创业板期权波动率指数QVIX分钟线数据为空")
            return []
                
        logger.info(f"创业板期权波动率指数QVIX分钟线数据获取成功: {df.shape[0]} 条记录")
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取创业板期权波动率指数QVIX分钟线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_kcb_qvix() -> list:
    """ 获取科创板期权波动率指数QVIX日线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含科创板期权波动率指数QVIX日线数据，
    Dict包含字段: ['date', 'open', 'high', 'low', 'close']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_kcb_qvix()
        
        logger.info(f"获取科创板期权波动率指数QVIX日线数据")
        if df.empty:
            logger.warning(f"获取的科创板期权波动率指数QVIX日线数据为空")
            return []
                
        logger.info(f"科创板期权波动率指数QVIX日线数据获取成功: {df.shape[0]} 条记录")
        
        # 确保日期列是字符串格式
        df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取科创板期权波动率指数QVIX日线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_kcb_min_qvix() -> list:
    """ 获取科创板期权波动率指数QVIX分钟线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含科创板期权波动率指数QVIX分钟线数据，
    Dict包含字段: ['time', 'qvix']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_kcb_min_qvix()
        
        logger.info(f"获取科创板期权波动率指数QVIX分钟线数据")
        if df.empty:
            logger.warning(f"获取的科创板期权波动率指数QVIX分钟线数据为空")
            return []
                
        logger.info(f"科创板期权波动率指数QVIX分钟线数据获取成功: {df.shape[0]} 条记录")
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取科创板期权波动率指数QVIX分钟线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_100etf_qvix() -> list:
    """ 获取深证100ETF期权波动率指数QVIX日线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含深证100ETF期权波动率指数QVIX日线数据，
    Dict包含字段: ['date', 'open', 'high', 'low', 'close']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_100etf_qvix()
        
        logger.info(f"获取深证100ETF期权波动率指数QVIX日线数据")
        if df.empty:
            logger.warning(f"获取的深证100ETF期权波动率指数QVIX日线数据为空")
            return []
                
        logger.info(f"深证100ETF期权波动率指数QVIX日线数据获取成功: {df.shape[0]} 条记录")
        
        # 确保日期列是字符串格式
        df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取深证100ETF期权波动率指数QVIX日线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_100etf_min_qvix() -> list:
    """ 获取深证100ETF期权波动率指数QVIX分钟线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含深证100ETF期权波动率指数QVIX分钟线数据，
    Dict包含字段: ['time', 'qvix']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_100etf_min_qvix()
        
        logger.info(f"获取深证100ETF期权波动率指数QVIX分钟线数据")
        if df.empty:
            logger.warning(f"获取的深证100ETF期权波动率指数QVIX分钟线数据为空")
            return []
                
        logger.info(f"深证100ETF期权波动率指数QVIX分钟线数据获取成功: {df.shape[0]} 条记录")
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取深证100ETF期权波动率指数QVIX分钟线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_300index_qvix() -> list:
    """ 获取中证300股指期权波动率指数QVIX日线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含中证300股指期权波动率指数QVIX日线数据，
    Dict包含字段: ['date', 'open', 'high', 'low', 'close']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_300index_qvix()
        
        logger.info(f"获取中证300股指期权波动率指数QVIX日线数据")
        if df.empty:
            logger.warning(f"获取的中证300股指期权波动率指数QVIX日线数据为空")
            return []
                
        logger.info(f"中证300股指期权波动率指数QVIX日线数据获取成功: {df.shape[0]} 条记录")
        
        # 确保日期列是字符串格式
        df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取中证300股指期权波动率指数QVIX日线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_300index_min_qvix() -> list:
    """ 获取中证300股指期权波动率指数QVIX分钟线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含中证300股指期权波动率指数QVIX分钟线数据，
    Dict包含字段: ['time', 'qvix']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_300index_min_qvix()
        
        logger.info(f"获取中证300股指期权波动率指数QVIX分钟线数据")
        if df.empty:
            logger.warning(f"获取的中证300股指期权波动率指数QVIX分钟线数据为空")
            return []
                
        logger.info(f"中证300股指期权波动率指数QVIX分钟线数据获取成功: {df.shape[0]} 条记录")
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取中证300股指期权波动率指数QVIX分钟线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_1000index_qvix() -> list:
    """ 获取中证1000股指期权波动率指数QVIX日线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含中证1000股指期权波动率指数QVIX日线数据，
    Dict包含字段: ['date', 'open', 'high', 'low', 'close']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_1000index_qvix()
        
        logger.info(f"获取中证1000股指期权波动率指数QVIX日线数据")
        if df.empty:
            logger.warning(f"获取的中证1000股指期权波动率指数QVIX日线数据为空")
            return []
                
        logger.info(f"中证1000股指期权波动率指数QVIX日线数据获取成功: {df.shape[0]} 条记录")
        
        # 确保日期列是字符串格式
        df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取中证1000股指期权波动率指数QVIX日线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_1000index_min_qvix() -> list:
    """ 获取中证1000股指期权波动率指数QVIX分钟线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含中证1000股指期权波动率指数QVIX分钟线数据，
    Dict包含字段: ['time', 'qvix']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_1000index_min_qvix()
        
        logger.info(f"获取中证1000股指期权波动率指数QVIX分钟线数据")
        if df.empty:
            logger.warning(f"获取的中证1000股指期权波动率指数QVIX分钟线数据为空")
            return []
                
        logger.info(f"中证1000股指期权波动率指数QVIX分钟线数据获取成功: {df.shape[0]} 条记录")
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取中证1000股指期权波动率指数QVIX分钟线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_50index_qvix() -> list:
    """ 获取上证50股指期权波动率指数QVIX日线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含上证50股指期权波动率指数QVIX日线数据，
    Dict包含字段: ['date', 'open', 'high', 'low', 'close']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_50index_qvix()
        
        logger.info(f"获取上证50股指期权波动率指数QVIX日线数据")
        if df.empty:
            logger.warning(f"获取的上证50股指期权波动率指数QVIX日线数据为空")
            return []
                
        logger.info(f"上证50股指期权波动率指数QVIX日线数据获取成功: {df.shape[0]} 条记录")
        
        # 确保日期列是字符串格式
        df['date'] = df['date'].astype(str)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取上证50股指期权波动率指数QVIX日线数据失败: {str(e)}")
        traceback.print_exc()
        return []

@mcp.tool()
async def get_50index_min_qvix() -> list:
    """ 获取上证50股指期权波动率指数QVIX分钟线数据
    参数：
    - 无
    返回：
    - List[Dict]: 包含上证50股指期权波动率指数QVIX分钟线数据，
    Dict包含字段: ['time', 'qvix']
    """
    try:
        # 调用index_option_qvix模块获取数据
        df = qvix.index_option_50index_min_qvix()
        
        logger.info(f"获取上证50股指期权波动率指数QVIX分钟线数据")
        if df.empty:
            logger.warning(f"获取的上证50股指期权波动率指数QVIX分钟线数据为空")
            return []
                
        logger.info(f"上证50股指期权波动率指数QVIX分钟线数据获取成功: {df.shape[0]} 条记录")
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"获取上证50股指期权波动率指数QVIX分钟线数据失败: {str(e)}")
        traceback.print_exc()
        return []