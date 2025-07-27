# mcp_instance.py
from mcp.server.fastmcp import FastMCP
import logging

# 配置日志
logger = logging.getLogger("mcp_instance")

# 创建MCP服务器实例
mcp = FastMCP("FreqOption MCP Server", version="0.1.0")

# 导出mcp实例
__all__ = ['mcp']

logger.info("MCP实例已创建")