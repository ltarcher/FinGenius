from contextlib import AsyncExitStack
from typing import Dict, List, Optional

import anyio
try:
    # Python 3.11+
    from exceptiongroup import ExceptionGroup
except ImportError:
    # 在 Python 3.10 及以下版本中，使用 BaseExceptionGroup 作为替代
    try:
        from anyio._backends._asyncio import BaseExceptionGroup as ExceptionGroup
    except ImportError:
        # 如果都不可用，创建一个简单的替代类
        class ExceptionGroup(Exception):
            pass

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import ListToolsResult, TextContent
from src.logger import logger
from src.tool.base import BaseTool, ToolResult
from src.tool.tool_collection import ToolCollection


class MCPClientTool(BaseTool):
    """Represents a tool proxy that can be called on the MCP server from the client side."""

    session: Optional[ClientSession] = None
    server_id: str = ""  # Add server identifier
    original_name: str = ""

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool by making a remote call to the MCP server."""
        if not self.session:
            return ToolResult(
                error="MCP server connection not available. This tool requires an active MCP server connection."
            )

        try:
            logger.info(f"Executing tool: {self.original_name}")
            result = await self.session.call_tool(self.original_name, kwargs)
            content_str = ", ".join(
                item.text for item in result.content if isinstance(item, TextContent)
            )
            return ToolResult(output=content_str or "No output returned.")
        except Exception as e:
            return ToolResult(error=f"Error executing tool: {str(e)}")


class MCPClients(ToolCollection):
    """
    A collection of tools that connects to multiple MCP servers and manages available tools through the Model Context Protocol.
    """

    sessions: Dict[str, ClientSession] = {}
    exit_stacks: Dict[str, AsyncExitStack] = {}
    description: str = "MCP client tools for server interaction"

    def __init__(self):
        super().__init__()  # Initialize with empty tools list
        self.name = "mcp"  # Keep name for backward compatibility

    async def connect_sse(self, server_url: str, server_id: str = "") -> None:
        """Connect to an MCP server using SSE transport."""
        if not server_url:
            raise ValueError("Server URL is required.")

        server_id = server_id or server_url

        # Always ensure clean disconnection before new connection
        if server_id in self.sessions:
            await self.disconnect(server_id)

        exit_stack = AsyncExitStack()
        self.exit_stacks[server_id] = exit_stack

        try:
            # 使用超时机制避免无限等待
            with anyio.move_on_after(30.0) as scope:
                streams_context = sse_client(url=server_url)
                streams = await exit_stack.enter_async_context(streams_context)
                session = await exit_stack.enter_async_context(ClientSession(*streams))
                self.sessions[server_id] = session
                
                if scope.cancel_called:
                    raise TimeoutError("Connection to SSE server timed out")
                
                await self._initialize_and_list_tools(server_id)
        except Exception as e:
            # 如果在设置过程中出现任何错误，确保清理资源
            logger.error(f"Error connecting to SSE server {server_id}: {e}")
            await self.disconnect(server_id)
            raise

    async def connect_stdio(
        self, command: str, args: List[str], server_id: str = ""
    ) -> None:
        """Connect to an MCP server using stdio transport."""
        if not command:
            raise ValueError("Server command is required.")

        server_id = server_id or command

        # Always ensure clean disconnection before new connection
        if server_id in self.sessions:
            await self.disconnect(server_id)

        exit_stack = AsyncExitStack()
        self.exit_stacks[server_id] = exit_stack

        try:
            # 使用超时机制避免无限等待
            with anyio.move_on_after(30.0) as scope:
                server_params = StdioServerParameters(command=command, args=args)
                stdio_transport = await exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                read, write = stdio_transport
                session = await exit_stack.enter_async_context(ClientSession(read, write))
                self.sessions[server_id] = session
                
                if scope.cancel_called:
                    raise TimeoutError("Connection to stdio server timed out")
                
                await self._initialize_and_list_tools(server_id)
        except Exception as e:
            # 如果在设置过程中出现任何错误，确保清理资源
            logger.error(f"Error connecting to stdio server {server_id}: {e}")
            await self.disconnect(server_id)
            raise

    async def _initialize_and_list_tools(self, server_id: str) -> None:
        """Initialize session and populate tool map."""
        session = self.sessions.get(server_id)
        if not session:
            raise RuntimeError(f"Session not initialized for server {server_id}")

        await session.initialize()
        response = await session.list_tools()

        # Create proper tool objects for each server tool
        for tool in response.tools:
            original_name = tool.name
            # Always prefix with server_id to ensure uniqueness
            tool_name = f"mcp_{server_id}_{original_name}"

            server_tool = MCPClientTool(
                name=tool_name,
                description=tool.description,
                parameters=tool.inputSchema,
                session=session,
                server_id=server_id,
                original_name=original_name,
            )
            self.tool_map[tool_name] = server_tool

        # Update tools tuple
        self.tools = tuple(self.tool_map.values())
        logger.info(
            f"Connected to server {server_id} with tools: {[tool.name for tool in response.tools]}"
        )

    async def list_tools(self) -> ListToolsResult:
        """List all available tools."""
        tools_result = ListToolsResult(tools=[])
        for session in self.sessions.values():
            response = await session.list_tools()
            tools_result.tools += response.tools
        return tools_result

    async def disconnect(self, server_id: str = "") -> None:
        """Disconnect from a specific MCP server or all servers if no server_id provided."""
        if server_id:
            if server_id in self.sessions:
                try:
                    exit_stack = self.exit_stacks.get(server_id)

                    # 先清理会话引用，减少异步关闭时的依赖
                    session = self.sessions.pop(server_id, None)
                    
                    # 关闭 exit stack 前先尝试关闭会话
                    if session:
                        try:
                            # 尝试优雅地关闭会话
                            await session.shutdown()
                        except Exception as e:
                            logger.warning(f"Error shutting down session for {server_id}: {e}")
                    
                    # 关闭 exit stack，处理所有异步清理错误
                    if exit_stack:
                        try:
                            # 使用超时机制避免无限等待
                            with anyio.move_on_after(5.0):
                                await exit_stack.aclose()
                        except (RuntimeError, ExceptionGroup, GeneratorExit, Exception) as e:
                            error_str = str(e)
                            # 处理所有已知的异步关闭错误
                            if any(msg in error_str.lower() for msg in [
                                "cancel scope", 
                                "generator didn't stop", 
                                "attempted to exit cancel scope",
                                "unhandled errors in a taskgroup",
                                "asyncgen",
                                "generatorexit"
                            ]):
                                logger.warning(
                                    f"Async cleanup error during disconnect from {server_id}, continuing with cleanup: {e}"
                                )
                            else:
                                logger.error(f"Unexpected error during disconnect: {e}")
                                # 不抛出异常，确保清理继续进行

                    # 确保清理所有引用，即使在出现异常的情况下
                    self.exit_stacks.pop(server_id, None)

                    # 移除与此服务器关联的工具
                    try:
                        self.tool_map = {
                            k: v
                            for k, v in self.tool_map.items()
                            if v.server_id != server_id
                        }
                        self.tools = tuple(self.tool_map.values())
                        logger.info(f"Disconnected from MCP server {server_id}")
                    except Exception as e:
                        logger.error(f"Error cleaning up tools for server {server_id}: {e}")
                except Exception as e:
                    logger.error(f"Error disconnecting from server {server_id}: {e}")
        else:
            # Disconnect from all servers in a deterministic order
            for sid in sorted(list(self.sessions.keys())):
                await self.disconnect(sid)
            self.tool_map = {}
            self.tools = tuple()
            logger.info("Disconnected from all MCP servers")
