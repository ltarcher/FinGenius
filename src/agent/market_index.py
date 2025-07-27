from typing import Any, List, Optional

from pydantic import Field

from src.agent.mcp import MCPAgent
from src.prompt.market_index import MARKET_INDEX_SYSTEM_PROMPT
from src.prompt.mcp import NEXT_STEP_PROMPT_ZN
from src.schema import Message
from src.tool import Terminate, ToolCollection
from src.tool.market_index import MarketIndexTool


class MarketIndexAgent(MCPAgent):
    """大盘指数分析智能体，专注于分析主要市场指数走势及其对个股的影响"""

    name: str = "market_index_agent"
    description: str = "分析上证指数、恒生指数、创业板、科创板等大盘指数走势，评估市场整体趋势及其对个股的影响"

    system_prompt: str = MARKET_INDEX_SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT_ZN

    # 初始化工具集
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            MarketIndexTool(),
            Terminate(),
        )
    )
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])

    async def run(
        self, request: Optional[str] = None, stock_code: Optional[str] = None
    ) -> Any:
        """运行大盘指数分析

        Args:
            request: 可选的初始请求。如果提供，将覆盖stock_code参数。
            stock_code: 要分析的股票代码

        Returns:
            包含大盘指数分析结果的字典
        """
        # 如果提供了stock_code但没有提供request，则根据stock_code创建请求
        if stock_code and not request:
            # 设置关于正在分析的股票的系统消息
            self.memory.add_message(
                Message.system_message(
                    f"你正在分析大盘指数走势及其对股票 {stock_code} 的影响。请分析主要市场指数的趋势，并评估它们对该股票的潜在影响。"
                )
            )
            request = f"请分析当前大盘指数（上证指数、恒生指数、创业板、科创板等）的走势，并评估它们对 {stock_code} 的影响。"

        # 调用父类实现
        return await super().run(request)