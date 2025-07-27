from typing import Dict, List, Optional, Any
import logging
import random
import asyncio
from datetime import datetime, timedelta

from pydantic import BaseModel, Field
import sys
# 优先加载 Conda 环境的 mcp 模块
sys.path.insert(0, "c:\\Users\\LMT\\.conda\\envs\\FinGenius\\Lib\\site-packages")
import mcp
#from mcp import ClientSession, StdioServerParameters

print(sys.path)
print(mcp.__file__)

from src.tool.base import BaseTool
from src.tool.base import ToolResult
from src.tool.mcp_client import MCPClients
import json
from pathlib import Path


logger = logging.getLogger(__name__)


class MarketIndexToolInput(BaseModel):
    """大盘指数分析工具的输入参数"""
    
    index_code: Optional[str] = Field(
        None,
        description="指数代码，如'000001.SH'(上证指数)、'399001.SZ'(深证成指)、'399006.SZ'(创业板指)、'000688.SH'(科创50)、'HSI'(恒生指数)等",
    )
    
    period: str = Field(
        "daily",
        description="分析周期，可选值：'daily'(日线)、'weekly'(周线)、'monthly'(月线)",
    )
    
    days: int = Field(
        30,
        description="获取的历史数据天数，默认30天",
    )
    
    analysis_type: str = Field(
        "comprehensive",
        description="分析类型，可选值：'trend'(趋势分析)、'correlation'(相关性分析)、'comprehensive'(综合分析)",
    )
    
    stock_code: Optional[str] = Field(
        None,
        description="当进行相关性分析时，需要提供的个股代码",
    )


class MarketIndexTool(BaseTool):
    """大盘指数分析工具，用于分析主要市场指数的走势及其对个股的影响"""
    
    name: str = "market_index_analysis"
    description: str = "分析上证指数、恒生指数、创业板、科创板等大盘指数走势，评估市场整体趋势及其对个股的影响"
    input_schema: type = MarketIndexToolInput
    mcp_clients: Any = None
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # 默认配置（安全保守策略）
        DEFAULT_CONFIG = {
            "enabled": False,
            "mcpServers": {
                "mcp_stock": {
                    "enabled": True,
                    "type": "sse",
                    "url": "http://localhost:8000/sse"
                }
            }
        }
        
        # 加载配置（文件不存在时使用默认值）
        config_path = Path(__file__).parent.parent.parent / "config" / "extra_mcp.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._mcp_config = json.load(f)
        except FileNotFoundError:
            self._mcp_config = DEFAULT_CONFIG
 
        self._enabled = self._mcp_config.get("enabled", False)
        self.mcp_clients = MCPClients() if self._enabled else None
        self._initialized = False

        if self._enabled:
            # 避免在已有事件循环中调用asyncio.run()
            asyncio.create_task(self._sync_initialize())
                
    async def _sync_initialize(self):
        """同步初始化包装方法"""
        await self.initialize()
        self._initialized = True
        
    async def initialize(self):
        """异步初始化MCP客户端连接"""
        if not self._enabled:
            self._initialized = True
            return
            
        try:
            # 确保 MCP 客户端已创建
            if not hasattr(self, 'mcp_clients') or not self.mcp_clients:
                self.mcp_clients = MCPClients()
                
            # 初始化启用的服务器
            for server_name, server_config in self._mcp_config["mcpServers"].items():
                if server_config.get("enabled", True):
                    try:
                        if server_config.get("type") == "sse":
                            await self.mcp_clients.connect_sse(server_config["url"])
                        elif server_config.get("type") == "stdio":
                            await self.mcp_clients.connect_stdio(
                                server_config["command"], 
                                server_config.get("args", [])
                            )
                    except Exception as e:
                        logger.error(f"连接 MCP 服务器 {server_name} 失败: {str(e)}")
                        continue
            
            self._initialized = True
        except Exception as e:
            logger.error(f"初始化 MCP 客户端失败: {str(e)}")
            self._initialized = False
            raise
    
    async def call_mcp_tool(self, tool_name: str, **kwargs) -> Any:
        """调用MCP服务器上的工具"""
        if not hasattr(self, "mcp_clients") or not self.mcp_clients:
            raise Exception("MCP客户端未初始化")
            
        try:
            result = await self.mcp_clients.execute(tool_name, kwargs)
            return result
        except Exception as e:
            logger.error(f"调用MCP工具 {tool_name} 失败: {str(e)}")
            raise
    
    def _process_index_data(self, realtime_data: List[Dict], history_data: List[Dict]) -> Dict[str, Any]:
        """处理从MCP获取的指数数据，转换为分析所需的格式"""
        processed_data = {}
        
        # 处理实时数据
        for item in realtime_data:
            code = item.get("代码")
            if not code:
                continue
                
            processed_data[code] = {
                "name": item.get("名称", ""),
                "latest_price": item.get("最新", 0),
                "change_percent": item.get("涨幅", 0),
                "high": item.get("最高", 0),
                "low": item.get("最低", 0),
                "open": item.get("今开", 0),
                "volume": item.get("成交量", 0),
                "turnover": item.get("成交额", 0),
                "prev_close": item.get("昨收", 0),
                "time": item.get("时间", "")
            }
        
        # 处理历史数据
        for item in history_data:
            date = item.get("日期")
            if not date:
                continue
                
            for code, data in processed_data.items():
                if "history" not in data:
                    data["history"] = []
                    
                data["history"].append({
                    "date": date,
                    "turnover": item.get("成交额", 0)
                })
        
        return processed_data
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        try:
            # 确保工具已初始化
            if not self._initialized:
                await self.initialize()
                self._initialized = True
                
            # 验证输入参数
            input_params = self.input_schema(**kwargs)
            
            # 调用 _run 方法
            return await self._run(
                index_code=input_params.index_code,
                period=input_params.period,
                days=input_params.days,
                analysis_type=input_params.analysis_type,
                stock_code=input_params.stock_code
            )
        except Exception as e:
            logger.error(f"执行工具 {self.name} 失败: {str(e)}")
            return ToolResult(error=f"执行工具失败: {str(e)}")

    async def _run(self, index_code: Optional[str] = None, period: str = "daily", 
                  days: int = 30, analysis_type: str = "comprehensive", 
                  stock_code: Optional[str] = None) -> ToolResult:
        """运行大盘指数分析工具

        Args:
            index_code: 指数代码，如'000001.SH'(上证指数)
            period: 分析周期，可选值：'daily'、'weekly'、'monthly'
            days: 获取的历史数据天数
            analysis_type: 分析类型，可选值：'trend'、'correlation'、'comprehensive'
            stock_code: 当进行相关性分析时，需要提供的个股代码

        Returns:
            包含分析结果的ToolResult对象
        """
        try:
            logger.info(f"开始分析大盘指数: {index_code or '所有主要指数'}, 周期: {period}, 天数: {days}")
            
            # 获取实时指数数据
            realtime_data = await self.call_mcp_tool("get_index_realtime_data", codes=index_code)
            
            # 获取历史数据
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            history_data = await self.call_mcp_tool(
                "get_turnover_history_data", 
                start_date=start_date, 
                end_date=end_date
            )
            
            # 处理数据
            index_data = self._process_index_data(realtime_data, history_data)
            
            # 根据分析类型执行不同的分析
            if analysis_type == "trend":
                result = self._analyze_trend(index_data)
            elif analysis_type == "correlation" and stock_code:
                result = self._analyze_correlation(index_data, stock_code)
            else:  # comprehensive
                result = self._analyze_comprehensive(index_data, stock_code)
            
            logger.info(f"大盘指数分析完成: {index_code or '所有主要指数'}")
            return ToolResult(success=True, data=result)
            
        except Exception as e:
            logger.error(f"大盘指数分析失败: {str(e)}")
            return ToolResult(
                success=False,
                error=f"大盘指数分析失败: {str(e)}",
                data={"error": str(e)}
            )
    
    def _generate_single_index_data(self, index_name: str, period: str, days: int) -> Dict[str, Any]:
        """生成单个指数的模拟数据"""
        # 生成日期序列
        end_date = datetime.now()
        if period == "daily":
            start_date = end_date - timedelta(days=days)
            date_interval = timedelta(days=1)
        elif period == "weekly":
            start_date = end_date - timedelta(days=days * 7)
            date_interval = timedelta(days=7)
        else:  # monthly
            start_date = end_date - timedelta(days=days * 30)
            date_interval = timedelta(days=30)
        
        # 生成价格序列
        base_price = 3000 + random.randint(-500, 500)  # 基础价格
        volatility = 0.01  # 波动率
        trend = random.choice([-0.0005, 0, 0.0005])  # 趋势
        
        prices = []
        volumes = []
        dates = []
        
        current_date = start_date
        current_price = base_price
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # 只考虑工作日
                dates.append(current_date.strftime("%Y-%m-%d"))
                
                # 生成价格
                change = current_price * (random.normalvariate(trend, volatility))
                current_price += change
                prices.append(round(current_price, 2))
                
                # 生成成交量
                volume = int(random.normalvariate(100000000, 20000000))
                volumes.append(volume)
            
            current_date += date_interval
        
        # 计算一些技术指标
        ma5 = self._calculate_moving_average(prices, 5)
        ma10 = self._calculate_moving_average(prices, 10)
        ma20 = self._calculate_moving_average(prices, 20)
        
        return {
            "name": index_name,
            "period": period,
            "dates": dates,
            "prices": prices,
            "volumes": volumes,
            "technical_indicators": {
                "ma5": ma5,
                "ma10": ma10,
                "ma20": ma20,
                "rsi": round(random.uniform(30, 70), 2),
                "kdj": {
                    "k": round(random.uniform(30, 70), 2),
                    "d": round(random.uniform(30, 70), 2),
                    "j": round(random.uniform(30, 70), 2),
                }
            },
            "summary": {
                "start_price": prices[0],
                "end_price": prices[-1],
                "highest": max(prices),
                "lowest": min(prices),
                "change_percent": round((prices[-1] - prices[0]) / prices[0] * 100, 2),
                "volatility": round(self._calculate_volatility(prices) * 100, 2),
            }
        }
    
    def _calculate_moving_average(self, prices: List[float], window: int) -> List[float]:
        """计算移动平均线"""
        result = []
        for i in range(len(prices)):
            if i < window - 1:
                result.append(None)
            else:
                window_avg = sum(prices[i-window+1:i+1]) / window
                result.append(round(window_avg, 2))
        return result
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """计算价格波动率"""
        if len(prices) < 2:
            return 0
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        mean_return = sum(returns) / len(returns)
        squared_deviations = [(r - mean_return) ** 2 for r in returns]
        variance = sum(squared_deviations) / len(squared_deviations)
        return variance ** 0.5
    
    def _analyze_trend(self, index_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析指数趋势"""
        results = {}
        
        for code, data in index_data.items():
            prices = data["prices"]
            ma5 = data["technical_indicators"]["ma5"]
            ma10 = data["technical_indicators"]["ma10"]
            ma20 = data["technical_indicators"]["ma20"]
            
            # 判断趋势
            if prices[-1] > ma5[-1] > ma10[-1] > ma20[-1]:
                trend = "强势上涨"
                strength = "强"
            elif prices[-1] > ma5[-1] and ma5[-1] > ma10[-1]:
                trend = "上涨"
                strength = "中"
            elif prices[-1] < ma5[-1] < ma10[-1] < ma20[-1]:
                trend = "强势下跌"
                strength = "强"
            elif prices[-1] < ma5[-1] and ma5[-1] < ma10[-1]:
                trend = "下跌"
                strength = "中"
            else:
                trend = "震荡"
                strength = "弱"
            
            # 计算趋势持续性
            trend_consistency = self._calculate_trend_consistency(prices)
            
            results[code] = {
                "name": data["name"],
                "trend": trend,
                "strength": strength,
                "consistency": trend_consistency,
                "change_percent": data["summary"]["change_percent"],
                "technical_signals": {
                    "ma_cross": self._check_ma_cross(ma5, ma10),
                    "price_position": "站上所有均线" if prices[-1] > ma20[-1] else "站上短期均线" if prices[-1] > ma5[-1] else "跌破所有均线",
                    "volume_trend": "放量" if data["volumes"][-1] > sum(data["volumes"][-6:-1]) / 5 * 1.2 else "缩量" if data["volumes"][-1] < sum(data["volumes"][-6:-1]) / 5 * 0.8 else "平稳"
                }
            }
        
        return {
            "analysis_type": "trend",
            "results": results,
            "market_overview": self._generate_market_overview(results)
        }
    
    def _analyze_correlation(self, index_data: Dict[str, Any], stock_code: str) -> Dict[str, Any]:
        """分析指数与个股的相关性"""
        # 模拟个股数据
        stock_data = self._generate_single_index_data(f"股票{stock_code}", "daily", len(index_data[list(index_data.keys())[0]]["prices"]))
        
        results = {}
        for code, data in index_data.items():
            # 计算相关系数
            correlation = self._calculate_correlation(data["prices"], stock_data["prices"])
            
            # 判断相关性强度
            if abs(correlation) > 0.8:
                strength = "极强"
            elif abs(correlation) > 0.6:
                strength = "强"
            elif abs(correlation) > 0.4:
                strength = "中等"
            elif abs(correlation) > 0.2:
                strength = "弱"
            else:
                strength = "极弱"
            
            # 判断相关性方向
            direction = "正相关" if correlation > 0 else "负相关"
            
            results[code] = {
                "name": data["name"],
                "correlation": round(correlation, 2),
                "strength": strength,
                "direction": direction,
                "beta": round(random.uniform(0.5, 1.5), 2),  # 模拟Beta值
                "impact_level": "高" if abs(correlation) > 0.7 else "中" if abs(correlation) > 0.4 else "低"
            }
        
        return {
            "analysis_type": "correlation",
            "stock_code": stock_code,
            "results": results,
            "summary": self._generate_correlation_summary(results, stock_code)
        }
    
    def _analyze_comprehensive(self, index_data: Dict[str, Any], stock_code: Optional[str] = None) -> Dict[str, Any]:
        """综合分析指数趋势和相关性"""
        # 趋势分析
        trend_analysis = self._analyze_trend(index_data)
        
        # 如果提供了股票代码，则进行相关性分析
        correlation_analysis = None
        if stock_code:
            correlation_analysis = self._analyze_correlation(index_data, stock_code)
        
        # 生成综合分析结果
        results = {}
        for code, data in index_data.items():
            result = {
                "name": data["name"],
                "trend": trend_analysis["results"][code]["trend"],
                "change_percent": data["summary"]["change_percent"],
                "technical_indicators": data["technical_indicators"],
                "summary": data["summary"],
            }
            
            if correlation_analysis:
                result.update({
                    "correlation": correlation_analysis["results"][code]["correlation"],
                    "impact_on_stock": correlation_analysis["results"][code]["impact_level"]
                })
            
            results[code] = result
        
        # 生成综合分析报告
        comprehensive_report = self._generate_comprehensive_report(results, stock_code)
        
        return {
            "analysis_type": "comprehensive",
            "stock_code": stock_code,
            "results": results,
            "market_overview": trend_analysis["market_overview"],
            "comprehensive_report": comprehensive_report
        }
    
    def _calculate_trend_consistency(self, prices: List[float]) -> str:
        """计算趋势的一致性"""
        if len(prices) < 5:
            return "数据不足"
        
        # 计算最近几天的价格变化方向
        changes = [1 if prices[i] > prices[i-1] else -1 if prices[i] < prices[i-1] else 0 
                  for i in range(1, len(prices))]
        
        # 计算最近5天的变化方向一致性
        recent_changes = changes[-5:]
        positive_count = sum(1 for c in recent_changes if c > 0)
        negative_count = sum(1 for c in recent_changes if c < 0)
        
        if positive_count >= 4:
            return "持续上涨"
        elif negative_count >= 4:
            return "持续下跌"
        elif positive_count == 3 and negative_count == 2:
            return "震荡偏强"
        elif positive_count == 2 and negative_count == 3:
            return "震荡偏弱"
        else:
            return "震荡"
    
    def _check_ma_cross(self, ma5: List[float], ma10: List[float]) -> str:
        """检查均线交叉情况"""
        if len(ma5) < 2 or len(ma10) < 2:
            return "数据不足"
        
        # 检查最近两天的均线交叉
        if ma5[-2] <= ma10[-2] and ma5[-1] > ma10[-1]:
            return "金叉"
        elif ma5[-2] >= ma10[-2] and ma5[-1] < ma10[-1]:
            return "死叉"
        else:
            return "无交叉"
    
    def _calculate_correlation(self, series1: List[float], series2: List[float]) -> float:
        """计算两个序列的相关系数"""
        # 确保两个序列长度相同
        min_length = min(len(series1), len(series2))
        series1 = series1[-min_length:]
        series2 = series2[-min_length:]
        
        # 计算均值
        mean1 = sum(series1) / len(series1)
        mean2 = sum(series2) / len(series2)
        
        # 计算协方差和标准差
        covariance = sum((series1[i] - mean1) * (series2[i] - mean2) for i in range(min_length))
        std1 = (sum((x - mean1) ** 2 for x in series1)) ** 0.5
        std2 = (sum((x - mean2) ** 2 for x in series2)) ** 0.5
        
        # 计算相关系数
        if std1 == 0 or std2 == 0:
            return 0
        return covariance / (std1 * std2)
    
    def _generate_market_overview(self, trend_results: Dict[str, Any]) -> str:
        """生成市场概览"""
        # 统计上涨和下跌的指数数量
        up_count = sum(1 for data in trend_results.values() if "上涨" in data["trend"])
        down_count = sum(1 for data in trend_results.values() if "下跌" in data["trend"])
        
        # 判断市场整体趋势
        if up_count > down_count * 2:
            market_trend = "强势上涨"
        elif up_count > down_count:
            market_trend = "温和上涨"
        elif down_count > up_count * 2:
            market_trend = "强势下跌"
        elif down_count > up_count:
            market_trend = "温和下跌"
        else:
            market_trend = "震荡整理"
        
        # 生成市场概览文本
        overview = f"市场整体呈{market_trend}趋势，{up_count}个指数上涨，{down_count}个指数下跌。"
        
        # 添加主要指数表现
        for code, data in trend_results.items():
            if "000001.SH" in code or "399001.SZ" in code or "HSI" in code:
                overview += f"{data['name']}呈{data['trend']}趋势，变动{data['change_percent']}%。"
        
        return overview
    
    def _generate_correlation_summary(self, correlation_results: Dict[str, Any], stock_code: str) -> str:
        """生成相关性分析摘要"""
        # 找出相关性最强的指数
        strongest_correlation = max(correlation_results.values(), key=lambda x: abs(x["correlation"]))
        
        # 生成摘要文本
        summary = f"股票{stock_code}与{strongest_correlation['name']}的相关性最强，为{strongest_correlation['correlation']}，呈{strongest_correlation['direction']}关系。"
        
        # 添加其他指数的相关性
        high_impact_indices = [data for data in correlation_results.values() if data["impact_level"] == "高"]
        if high_impact_indices:
            summary += f"以下指数对该股票影响较大：" + "、".join([f"{data['name']}({data['correlation']})" for data in high_impact_indices])
        
        return summary
    
    def _generate_comprehensive_report(self, results: Dict[str, Any], stock_code: Optional[str] = None) -> str:
        """生成综合分析报告"""
        # 生成市场整体分析
        market_analysis = "# 大盘指数分析报告\n\n## 市场整体情况\n\n"
        
        # 统计上涨和下跌的指数数量
        up_indices = [data for data in results.values() if "上涨" in data["trend"]]
        down_indices = [data for data in results.values() if "下跌" in data["trend"]]
        
        market_analysis += f"当前市场中，{len(up_indices)}个指数上涨，{len(down_indices)}个指数下跌。"
        
        if len(up_indices) > len(down_indices):
            market_analysis += "市场整体呈上涨趋势，投资者情绪偏向乐观。\n\n"
        elif len(down_indices) > len(up_indices):
            market_analysis += "市场整体呈下跌趋势，投资者情绪偏向谨慎。\n\n"
        else:
            market_analysis += "市场整体呈震荡趋势，投资者情绪中性。\n\n"
        
        # 添加主要指数分析
        market_analysis += "## 主要指数分析\n\n"
        for code, data in results.items():
            market_analysis += f"### {data['name']}\n\n"
            market_analysis += f"- **趋势**：{data['trend']}\n"
            market_analysis += f"- **涨跌幅**：{data['change_percent']}%\n"
            market_analysis += f"- **技术指标**：MA5={data['technical_indicators']['ma5'][-1]}，MA10={data['technical_indicators']['ma10'][-1]}，RSI={data['technical_indicators']['rsi']}\n\n"
        
        # 如果提供了股票代码，添加对该股票的影响分析
        if stock_code:
            market_analysis += f"## 对{stock_code}的影响分析\n\n"
            
            # 找出相关性最强的指数
            strongest_correlation = None
            strongest_value = 0
            
            for code, data in results.items():
                if "correlation" in data and abs(data["correlation"]) > strongest_value:
                    strongest_value = abs(data["correlation"])
                    strongest_correlation = data
            
            if strongest_correlation:
                market_analysis += f"{stock_code}与{strongest_correlation['name']}的相关性最强，相关系数为{strongest_correlation['correlation']}。\n\n"
                
                if strongest_correlation["correlation"] > 0:
                    market_analysis += f"这表明{stock_code}与{strongest_correlation['name']}呈正相关关系，当{strongest_correlation['name']}上涨时，{stock_code}也倾向于上涨。\n\n"
                else:
                    market_analysis += f"这表明{stock_code}与{strongest_correlation['name']}呈负相关关系，当{strongest_correlation['name']}上涨时，{stock_code}倾向于下跌。\n\n"
            
            # 添加投资建议
            market_analysis += "## 投资建议\n\n"
            
            # 基于市场趋势和相关性给出建议
            if len(up_indices) > len(down_indices):
                if stock_code and strongest_correlation and strongest_correlation["correlation"] > 0:
                    market_analysis += f"鉴于市场整体呈上涨趋势，且{stock_code}与主要指数呈正相关关系，建议关注{stock_code}的上涨机会。\n\n"
                elif stock_code and strongest_correlation and strongest_correlation["correlation"] < 0:
                    market_analysis += f"虽然市场整体呈上涨趋势，但{stock_code}与主要指数呈负相关关系，建议谨慎对待{stock_code}的投资机会。\n\n"
                else:
                    market_analysis += "鉴于市场整体呈上涨趋势，建议关注顺势而为的投资机会。\n\n"
            else:
                if stock_code and strongest_correlation and strongest_correlation["correlation"] > 0:
                    market_analysis += f"鉴于市场整体呈下跌趋势，且{stock_code}与主要指数呈正相关关系，建议谨慎对待{stock_code}的投资风险。\n\n"
                elif stock_code and strongest_correlation and strongest_correlation["correlation"] < 0:
                    market_analysis += f"虽然市场整体呈下跌趋势，但{stock_code}与主要指数呈负相关关系，可能会有逆势表现，建议密切关注。\n\n"
                else:
                    market_analysis += "鉴于市场整体呈下跌趋势，建议控制仓位，谨慎投资。\n\n"
        
        return market_analysis