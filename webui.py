#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import json
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.theme import Theme

from src.config import config

class RichLogRenderer:
    """使用Rich库格式化日志文本"""
    
    def __init__(self):
        # 简单的控制台实例，不记录HTML
        self.console = Console()
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
    def render_log(self, message, log_type: str = "text") -> str:
        """格式化日志消息"""
        try:
            # 确保message是字符串
            if not isinstance(message, str):
                message = str(message)
            
            # 处理ANSI转义序列
            message = self.ansi_escape.sub('', message)
            
            # 处理markdown代码块中的内容
            def process_code_block(match):
                code_type = match.group(1)
                code_content = match.group(2)
                
                # 仅处理代码块中的HTML内容
                if '<' in code_content and '>' in code_content:
                    # 处理多行HTML内容 - 合并被分割的HTML标签
                    lines = code_content.splitlines()
                    merged_lines = []
                    in_html_tag = False
                    current_tag = ""
                    
                    for line in lines:
                        stripped = line.strip()
                        if "<" in stripped and ">" not in stripped:
                            # 开始HTML标签
                            in_html_tag = True
                            current_tag += stripped
                        elif in_html_tag and ">" in stripped:
                            # 结束HTML标签
                            current_tag += " " + stripped
                            merged_lines.append(current_tag)
                            in_html_tag = False
                            current_tag = ""
                        elif in_html_tag:
                            # HTML标签中间部分
                            current_tag += " " + stripped
                        else:
                            # 普通代码内容
                            merged_lines.append(stripped)
                    
                    # 重新组合处理后的代码内容
                    code_content = "\n".join(merged_lines)
                    # 转义HTML标签
                    code_content = code_content.replace("<", "&lt;").replace(">", "&gt;")
                
                return f"```{code_type}\n{code_content}\n```"
            
            # 处理markdown代码块
            if "```" in message:
                message = re.sub(r"```(\w*)\n(.*?)```", 
                            process_code_block,
                            message, 
                            flags=re.DOTALL)
            
            # 简单添加类型前缀
            if log_type == "info":
                return f"[INFO] {message}"
            elif log_type == "success":
                return f"[SUCCESS] {message}"
            elif log_type == "error":
                return f"[ERROR] {message}"
            elif log_type == "debug":
                return f"[DEBUG] {message}"
            return message
        except Exception as e:
            return f"{str(message)} (渲染错误: {str(e)})"

from main import EnhancedFinGeniusAnalyzer

def generate_html_report(results: Dict[str, Any]) -> str:
    """根据分析结果生成HTML报告，匹配main.py中的报告结构"""
    stock_code = results.get("stock_code", "未知股票")
    battle_result = results.get("battle_result", {})
    research_results = {k: v for k, v in results.items() 
                       if k not in ["stock_code", "analysis_time", "battle_result"]}
    
    # 计算投票比例（更健壮的处理方式）
    vote_count = battle_result.get("vote_count", {})
    if not isinstance(vote_count, dict):
        vote_count = {}
    
    # 确保获取正确的投票数值
    bull_cnt = int(vote_count.get("bullish", 0))
    bear_cnt = int(vote_count.get("bearish", 0))
    total_votes = bull_cnt + bear_cnt
    
    # 处理除零情况和无效数据
    if total_votes > 0:
        bull_pct = round(bull_cnt / total_votes * 100, 1)
        bear_pct = round(bear_cnt / total_votes * 100, 1)
    else:
        bull_pct = bear_pct = 0.0
        bull_cnt = bear_cnt = 0
    
    # 确保比例总和为100%
    if total_votes > 0 and (bull_pct + bear_pct) != 100:
        diff = 100 - (bull_pct + bear_pct)
        bull_pct += diff  # 将差值加到看涨比例上
    
    # 生成研究结果部分
    research_sections = []
    for key, value in research_results.items():
        if isinstance(value, dict):
            content = "<ul>" + "".join(f"<li><strong>{k}:</strong> {v}</li>" 
                                     for k, v in value.items()) + "</ul>"
        else:
            content = str(value)
        research_sections.append(f"""
        <div class="research-section">
            <h3>{key.replace('_', ' ').title()}</h3>
            <div class="research-content">{content}</div>
        </div>
        """)
    
    # 生成辩论历史部分
    debate_history = ""
    if battle_result.get("debate_history"):
        debate_history = "<div class='debate-history'><h3>辩论历史</h3><ul>"
        for msg in battle_result["debate_history"]:
            debate_history += f"""
            <li class="debate-message">
                <strong>{msg.get('agent', '未知专家')}:</strong>
                <span>{msg.get('content', '')}</span>
            </li>
            """
        debate_history += "</ul></div>"
    
    # 生成关键辩论点
    battle_highlights = ""
    if battle_result.get("battle_highlights"):
        battle_highlights = "<div class='battle-highlights'><h3>关键辩论点</h3><ul>"
        for highlight in battle_result["battle_highlights"]:
            battle_highlights += f"""
            <li class="highlight">
                <strong>{highlight.get('agent', '未知专家')}:</strong>
                <span>{highlight.get('point', '')}</span>
            </li>
            """
        battle_highlights += "</ul></div>"
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_code} 分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 1000px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .vote-summary {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .vote-metrics {{ display: flex; justify-content: space-around; text-align: center; }}
        .bullish {{ color: #27ae60; }}
        .bearish {{ color: #e74c3c; }}
        .research-section {{ margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
        .debate-message, .highlight {{ margin: 10px 0; padding: 10px; background: #fff; border-left: 3px solid #3498db; }}
        .final-decision {{ font-size: 1.2em; font-weight: bold; margin: 15px 0; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{stock_code} 股票分析报告</h1>
        <div class="timestamp">生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}</div>
    </div>
    
    <div class="vote-summary">
        <h2>专家投票结果</h2>
        <div class="final-decision">
            最终结论: {'看涨' if battle_result.get('final_decision') == 'bullish' else '看跌' if battle_result.get('final_decision') == 'bearish' else '持平'}
        </div>
        <div class="vote-metrics">
            <div class="bullish">
                <div>看涨比例</div>
                <div>{bull_pct}% ({bull_cnt}票)</div>
            </div>
            <div class="bearish">
                <div>看跌比例</div>
                <div>{bear_pct}% ({bear_cnt}票)</div>
            </div>
        </div>
    </div>
    
    <h2>专家辩论</h2>
    {debate_history}
    {battle_highlights}

    <h2>研究分析结果</h2>
    {''.join(research_sections)}
    
    <div class="timestamp" style="margin-top: 30px;">
        分析耗时: {results.get('analysis_time', 0):.2f}秒 | 
        工具调用: {results.get('total_tool_calls', 0)}次 | 
        LLM调用: {results.get('total_llm_calls', 0)}次
    </div>
    
    <div style="margin-top: 20px; font-size: 0.8em; color: #95a5a6; border-top: 1px solid #eee; padding-top: 10px;">
        免责声明: 本报告由AI生成，仅供参考，不构成投资建议
    </div>
</body>
</html>"""
    
    return html

# 全局状态管理类
class AppState:
    def __init__(self):
        self.analysis_started = False  # 分析是否已开始
        self.analysis_completed = False  # 分析是否已完成
        self.current_progress = 0  # 当前进度值
        self.max_progress = 100  # 最大进度值
        self.analysis_results = None  # 分析结果存储
        self.error_message = None  # 错误信息
        self.analysis_task = None  # 分析任务对象
        self.should_stop = False  # 是否应该停止分析

# 初始化Streamlit应用
def init_app():
    st.set_page_config(
        page_title="FinGenius - AI金融分析系统",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 初始化会话状态
    if 'app_state' not in st.session_state:
        st.session_state.app_state = AppState()
    if 'log_messages' not in st.session_state:
        st.session_state.log_messages = []
    if 'console_output' not in st.session_state:
        st.session_state.console_output = []

    # 加载配置文件
    try:
        st.session_state.config = config
    except Exception as e:
        st.error(f"配置加载失败: {str(e)}")
        st.stop()

# 显示应用标题和描述
def show_header():
    st.title("📈 FinGenius - AI金融分析系统")
    st.markdown("""
    **FinGenius** 是一个基于AI的金融分析系统，通过多个专家代理协作分析股票，
    提供全面的投资建议和风险评估。
    """)
    st.divider()

# 显示用户输入区域
def show_input_area():
    st.subheader("分析参数设置")
    
    col1, col2 = st.columns(2)
    with col1:
        stock_code = st.text_input(
            "股票代码",
            placeholder="例如: 000001.SZ",
            help="输入要分析的股票代码，格式如: 000001.SZ 或 600000.SH"
        )
    
    with col2:
        analysis_mode = st.selectbox(
            "分析模式",
            options=["全面分析", "快速分析", "深度分析"],
            index=0,
            help="选择分析深度和范围"
        )
    
    col3, col4 = st.columns(2)
    with col3:
        max_steps = st.number_input(
            "最大分析步数",
            min_value=1,
            max_value=20,
            value=5,
            help="控制每个专家的最大分析步骤"
        )
    
    with col4:
        debate_rounds = st.number_input(
            "辩论轮次",
            min_value=1,
            max_value=10,
            value=3,
            help="专家辩论的轮次"
        )
    
    return {
        "stock_code": stock_code,
        "analysis_mode": analysis_mode,
        "max_steps": max_steps,
        "debate_rounds": debate_rounds
    }

def set_expander_height(expander_label, height_px=200):
    """
    设置指定标签的expander的最大高度，并添加滚动控制功能
    
    参数:
    - expander_label: expander的标签文本
    - height_px: 限制的高度（像素）
    """
    # 转义CSS选择器中的特殊字符
    escaped_label = expander_label.replace(".", "\\.").replace(":", "\\:")
    
    # 初始化自动滚动状态
    if f'auto_scroll_{expander_label}' not in st.session_state:
        st.session_state[f'auto_scroll_{expander_label}'] = True

    # 生成CSS和JavaScript代码
    css_js = f"""
    <style>
    div[data-testid="stExpander"] {{
        max-height: {height_px}px !important;
        overflow-y: auto !important;
        position: relative;
    }}
    div[data-testid="stExpander"] > div {{
        max-height: {height_px}px !important;
        overflow-y: auto !important;
    }}
    div[data-testid="stExpanderDetails"] {{
        max-height: calc({height_px}px - 60px) !important;
        overflow-y: auto !important;
    }}
    .scroll-control-btn {{
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 100;
        background-color: #f0f2f6;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
        cursor: pointer;
    }}
    .scroll-control-btn:hover {{
        background-color: #e6e6e6;
    }}
    </style>
    
    <script>
    function initExpanderScroll() {{
        // 滚动控制状态
        let autoScrollEnabled = {str(st.session_state[f'auto_scroll_{expander_label}']).lower()};
        let userScrolled = false;
        let scrollTimeout = null;
        let lastScrollHeight = 0;
        
        // 获取expander容器 - 更精确的选择器
        const expander = document.querySelector('div[data-testid="stExpanderDetails"] > div');
        const expanderContainer = document.querySelector('div[data-testid="stExpander"]');
        
        if (!expander || !expanderContainer) {{
            console.warn('Expander container not found');
            return;
        }}
        
        // 创建控制按钮
        const scrollControlBtn = document.createElement('button');
        scrollControlBtn.className = 'scroll-control-btn';
        scrollControlBtn.textContent = autoScrollEnabled ? '⏸ 暂停滚动' : '▶ 启用滚动';
        scrollControlBtn.onclick = function() {{
            autoScrollEnabled = !autoScrollEnabled;
            this.textContent = autoScrollEnabled ? '⏸ 暂停滚动' : '▶ 启用滚动';
            // 更新session状态
            const updateEvent = new CustomEvent('updateScrollState', {{
                detail: {{ enabled: autoScrollEnabled }}
            }});
            document.dispatchEvent(updateEvent);
        }};
        expanderContainer.appendChild(scrollControlBtn);
        
        // 监听状态更新事件
        document.addEventListener('updateScrollState', function(e) {{
            autoScrollEnabled = e.detail.enabled;
            scrollControlBtn.textContent = autoScrollEnabled ? '⏸ 暂停滚动' : '▶ 启用滚动';
        }});
        
        // 添加滚动事件监听
        expander.addEventListener('scroll', function() {{
            // 用户手动滚动时暂停自动滚动
            if (!userScrolled && autoScrollEnabled) {{
                userScrolled = true;
            }}
            
            // 清除之前的定时器
            if (scrollTimeout) clearTimeout(scrollTimeout);
            
            // 如果用户滚动到底部，恢复自动滚动
            scrollTimeout = setTimeout(() => {{
                const {{scrollTop, scrollHeight, clientHeight}} = this;
                const isAtBottom = scrollHeight - scrollTop <= clientHeight + 5;
                
                if (isAtBottom && autoScrollEnabled) {{
                    userScrolled = false;
                }}
            }}, 200);
        }});
        
        // 自动滚动函数
        function autoScrollToBottom() {{
            if (autoScrollEnabled && !userScrolled && expander) {{
                const currentScrollHeight = expander.scrollHeight;
                // 只有内容高度变化时才滚动
                if (currentScrollHeight > lastScrollHeight) {{
                    expander.scrollTop = currentScrollHeight;
                    lastScrollHeight = currentScrollHeight;
                }}
            }}
            setTimeout(autoScrollToBottom, 100); // 更频繁的检查
        }}
        
        // 启动自动滚动
        autoScrollToBottom();
        
        // 添加MutationObserver监听内容变化
        const observer = new MutationObserver(() => {{
            if (autoScrollEnabled && !userScrolled && expander) {{
                const currentScrollHeight = expander.scrollHeight;
                if (currentScrollHeight > lastScrollHeight) {{
                    expander.scrollTop = currentScrollHeight;
                    lastScrollHeight = currentScrollHeight;
                }}
            }}
        }});
        
        observer.observe(expander, {{
            childList: true,
            subtree: true,
            characterData: true
        }});
    }}
    
    // 确保Streamlit组件渲染完成后初始化
    const initWhenReady = () => {{
        const checkInterval = setInterval(() => {{
            if (document.querySelector('div[data-testid="stExpanderDetails"]')) {{
                clearInterval(checkInterval);
                initExpanderScroll();
            }}
        }}, 100);
    }};
    
    if (document.readyState === 'complete') {{
        initWhenReady();
    }} else {{
        window.addEventListener('load', initWhenReady);
    }}
    
    // 监听来自Streamlit的状态更新
    document.addEventListener('updateScrollStateFromPython', function(e) {{
        const event = new CustomEvent('updateScrollState', {{
            detail: {{ enabled: e.detail.enabled }}
        }});
        document.dispatchEvent(event);
    }});
    </script>
    """
    
    # 使用markdown注入CSS和JS
    st.markdown(css_js, unsafe_allow_html=True)

# 主函数
def main():
    init_app()
    show_header()
    
    # 显示输入区域并获取参数
    input_params = show_input_area()
    
    # 初始化会话状态变量
    if 'analysis_started' not in st.session_state:
        st.session_state.analysis_started = False
    if 'analysis_completed' not in st.session_state:
        st.session_state.analysis_completed = False
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False
    if 'should_stop' not in st.session_state:
        st.session_state.should_stop = False
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'console_output' not in st.session_state:
        st.session_state.console_output = []
    
    # 分析控制按钮
    col1, col2 = st.columns(2)
    
    # 开始分析按钮
    with col1:
        start_disabled = st.session_state.analysis_running  # 仅在分析运行时禁用
        if st.button("开始分析", type="primary", disabled=start_disabled):
            st.session_state.analysis_started = True
            st.session_state.analysis_completed = False
            st.session_state.error_message = None
            st.session_state.should_stop = False
            st.session_state.analysis_running = True
            st.rerun()
    
    # 停止分析按钮
    with col2:
        if st.session_state.analysis_started:
            stop_disabled = st.session_state.analysis_completed or not st.session_state.analysis_running
            if st.button("停止分析", type="secondary", disabled=stop_disabled, key="stop_button"):
                st.session_state.should_stop = True
                st.warning("正在停止分析...")
    
    # 如果分析正在运行，执行分析
    if st.session_state.analysis_running and not st.session_state.analysis_completed:
        try:
            with st.spinner("正在分析中..."):
                # 执行分析
                results = asyncio.run(run_analysis(input_params))
                if results:  # 如果分析成功完成
                    st.session_state.analysis_completed = True
                    st.session_state.analysis_results = results
                st.session_state.analysis_running = False
                st.rerun()  # 重新渲染页面以显示结果
        except Exception as e:
            st.session_state.error_message = str(e)
            st.session_state.analysis_running = False
            st.error(f"分析失败: {str(e)}")

    # 显示分析状态
    if st.session_state.app_state.analysis_started:
        show_analysis_status()
    
    # 显示结果
    if st.session_state.app_state.analysis_completed:
        show_analysis_results()

async def run_analysis(params: Dict[str, Any]):
    """使用EnhancedFinGeniusAnalyzer执行实际的股票分析"""
    try:
        # 在开始前检查是否应该停止分析
        if st.session_state.app_state.should_stop:
            st.session_state.app_state.analysis_started = False
            return None

        # 初始化分析器
        analyzer = EnhancedFinGeniusAnalyzer()
        
        # 添加定期检查停止请求的函数
        async def check_stop():
            while not st.session_state.app_state.should_stop:
                await asyncio.sleep(0.5)
            raise asyncio.CancelledError("分析已停止")
        
        # 创建进度条和状态容器
        progress_bar = st.progress(0)
        status_container = st.empty()
        st.session_state.log_container = st.expander("实时分析日志", expanded=True)
        set_expander_height("实时分析日志", height_px=600)
        
        # 创建专家状态占位符
        expert_status_placeholder = st.empty()
        
        # 更新进度和状态
        def update_progress(message: str, progress: int = 0):
            progress_bar.progress(progress)
            status_container.text(message)
        
        # 更新专家状态
        def update_expert_status(experts: Dict[str, str]):
            with expert_status_placeholder.container():
                st.subheader("专家状态")
                cols = st.columns(3)
                for i, (name, status) in enumerate(experts.items()):
                    cols[i % 3].metric(name, status)
        
        # 增强的Streamlit可视化器，带Rich支持的实时日志功能
        class StreamlitVisualizer:
            def __init__(self):
                # 使用已初始化的会话状态变量，不再重新初始化
                # 这些变量应该在 init_app() 中已经初始化
                self.last_update = time.time()
                self.original_stdout = sys.stdout
                self.renderer = RichLogRenderer()
                sys.stdout = self  # 重定向标准输出
                
            def write(self, message):
                """捕获控制台输出并处理ANSI转义序列"""
                try:
                    if not message or not str(message).strip():
                        return
                        
                    # 确保message是字符串，处理Rich对象和其他非字符串类型
                    if not isinstance(message, str):
                        if hasattr(message, '__rich_console__'):
                            from rich.console import Console
                            console = Console()
                            with console.capture() as capture:
                                console.print(message)
                            message = capture.get()
                        elif hasattr(message, '__str__'):
                            message = str(message)
                        else:
                            message = repr(message)
                    
                    # 处理可能的多行消息
                    message = message.replace('\r\n', '\n').replace('\r', '\n')
                    
                    timestamp = time.strftime("%H:%M:%S")
                    html_content = self.renderer.render_log(message)
                    
                    log_entry = {
                        "time": timestamp,
                        "message": message,
                        "html": html_content,
                        "type": "console"
                    }
                    # 确保 console_output 已初始化
                    if 'console_output' not in st.session_state:
                        st.session_state.console_output = []
                    st.session_state.console_output.append(log_entry)
                    self._update_console_display()

                    # 同时也输出到控制台
                    self.original_stdout.write(message)
                except Exception as e:
                    self.original_stdout.write(f"Error processing log message: {str(e)}\n")
                
            def flush(self):
                pass
        
            def show_progress_update(self, title: str, message: str = ""):
                # 确保所有参数都是字符串
                title_str = str(title) if title is not None else ""
                message_str = str(message) if message is not None else ""
                progress = st.session_state.app_state.current_progress
                
                # 更新进度
                update_progress(f"{title_str}: {message_str}", progress)
            
            def show_debate_message(self, agent: str, message: str, message_type: str):
                """显示专家辩论消息"""
                timestamp = time.strftime("%H:%M:%S")
                styled_message = f"[{timestamp}] [{agent}] {message}"
                html_content = self.renderer.render_log(styled_message, message_type)
                
                log_entry = {
                    "time": timestamp,
                    "agent": agent,
                    "message": message,
                    "html": html_content,
                    "type": message_type
                }
                st.session_state.log_messages.append(log_entry)
            
                # 保持日志大小合理
                if len(st.session_state.log_messages) > 100:
                    st.session_state.log_messages = st.session_state.log_messages[-50:]
            
                # 限制更新频率(每秒最多5次)
                if time.time() - self.last_update > 0.2:
                    self._update_log_display()
                    self.last_update = time.time()
        
            def _update_log_display(self):
                """更新日志显示"""
                if 'log_container' not in st.session_state:
                    st.session_state.log_container = st.empty()
            
                with st.session_state.log_container.container():
                    st.markdown('<div class="log-container">', unsafe_allow_html=True)
                    
                    # 合并显示所有消息
                    all_messages = []
                    
                    # 添加专家消息
                    if 'log_messages' in st.session_state:
                        all_messages.extend(st.session_state.log_messages[-15:])
                    
                    # 添加控制台输出
                    if 'console_output' in st.session_state:
                        all_messages.extend(st.session_state.console_output[-10:])
                    
                    # 按时间戳排序并显示
                    all_messages.sort(key=lambda x: x['time'])
                    for msg in all_messages[-25:]:  # 显示最近的25条合并消息
                        if 'html' in msg:
                            st.markdown(f'<div class="log-message">{msg["html"]}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="log-message">{msg["message"]}</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                    # 自动滚动到底部
                    st.markdown(
                        """
                        <script>
                            window.scrollTo(0, document.body.scrollHeight);
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
            
            def _update_console_display(self):
                """更新控制台输出显示"""
                if time.time() - self.last_update > 0.5:  # 限制更新频率
                    self._update_log_display()
                    self.last_update = time.time()
        
        # Replace console visualizer with streamlit version
        visualizer = StreamlitVisualizer()
        
        # Create tasks
        stop_check_task = asyncio.create_task(check_stop())
        analysis_task = asyncio.create_task(
            analyzer.analyze_stock(
                stock_code=params["stock_code"],
                max_steps=params["max_steps"],
                debate_rounds=params["debate_rounds"]
            )
        )

        try:
            # 运行分析并更新进度
            update_progress("开始分析...", 10)
            done, pending = await asyncio.wait(
                [stop_check_task, analysis_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # 处理结果或取消
            if analysis_task in done:
                results = analysis_task.result()
                # 更新最终状态
                st.session_state.app_state.analysis_completed = True
                st.session_state.app_state.analysis_results = results
            else:
                analysis_task.cancel()
                raise asyncio.CancelledError("分析已停止")

        except asyncio.CancelledError:
            st.session_state.app_state.analysis_started = False
            st.session_state.app_state.error_message = "分析已停止"
            raise
        except Exception as e:
            st.session_state.app_state.error_message = str(e)
            raise
        finally:
            # 清理任务
            for task in pending:
                task.cancel()
            stop_check_task.cancel()
            
            # 恢复标准输出
            if hasattr(visualizer, 'original_stdout'):
                sys.stdout = visualizer.original_stdout
        
        # 显示完成状态
        update_progress("分析完成!", 100)
        st.balloons()
        
    except Exception as e:
        st.session_state.app_state.error_message = str(e)
        st.error(f"分析失败: {str(e)}")

# 显示分析状态
def show_analysis_status():
    if st.session_state.app_state.error_message:
        st.error(st.session_state.app_state.error_message)
        return
    
    if not st.session_state.app_state.analysis_completed:
        with st.expander("实时分析日志", expanded=True):
            st.info("分析正在进行中...")
            # 这里将添加实时日志显示

# 显示分析结果
def show_analysis_results():
    # 显示日志容器(折叠状态)
    if 'log_messages' in st.session_state or 'console_output' in st.session_state:
        with st.expander("分析日志", expanded=False):  # 设置为False保持折叠
            # 添加日志容器样式
            st.markdown("""
            <style>
                .log-container {
                    font-family: 'Courier New', monospace;
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    max-height: 600px;
                    overflow-y: auto;
                }
                .log-message {
                    margin: 5px 0;
                    line-height: 1.5;
                    white-space: pre-wrap;
                    word-break: break-word;
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="log-container">', unsafe_allow_html=True)
            
            # 合并显示所有消息
            all_messages = []
            
            # 添加专家消息
            if 'log_messages' in st.session_state:
                all_messages.extend(st.session_state.log_messages)
            
            # 添加控制台输出
            if 'console_output' in st.session_state:
                all_messages.extend(st.session_state.console_output)
            
            # 按时间戳排序并显示
            all_messages.sort(key=lambda x: x['time'])
            
            # 使用RichLogRenderer渲染没有HTML内容的消息
            renderer = RichLogRenderer()
            
            for msg in all_messages:
                if 'html' in msg:
                    st.markdown(f'<div class="log-message">{msg["html"]}</div>', unsafe_allow_html=True)
                elif 'message' in msg:
                    # 根据消息类型选择渲染方式
                    log_type = "text"
                    if msg.get('type') == "speak":
                        log_type = "info"
                        styled_message = f"[{msg['time']}] 💬 {msg['agent']}: {msg['message']}"
                    elif msg.get('type') == "vote":
                        log_type = "success"
                        styled_message = f"[{msg['time']}] ✅ {msg['agent']}: {msg['message']}"
                    else:
                        styled_message = f"[{msg['time']}] {msg['message']}"
                    
                    html_content = renderer.render_log(styled_message, log_type)
                    st.markdown(f'<div class="log-message">{html_content}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    st.success("分析完成!")
    results = st.session_state.app_state.analysis_results
    
    # 显示关键指标
    st.subheader("📊 综合分析结果")
    
    # 显示股票代码和分析时间
    st.markdown(f"**股票代码**: {results.get('stock_code', '未知')}")
    st.markdown(f"**分析耗时**: {results.get('analysis_time', 0):.2f}秒")
    
    # 显示最终结果和投票详情
    battle_result = results.get('battle_result', {})
    vote_count = battle_result.get('vote_count', {})
    
    # 获取最终结论
    final_decision = battle_result.get('final_decision', '无结果')
    decision_text = '看涨' if final_decision == 'bullish' else '看跌' if final_decision == 'bearish' else '无明确结论'
    
    # 计算投票比例
    bull_cnt = int(vote_count.get('bullish', 0))
    bear_cnt = int(vote_count.get('bearish', 0))
    total_votes = bull_cnt + bear_cnt
    
    if total_votes > 0:
        bull_pct = round(bull_cnt / total_votes * 100, 1)
        bear_pct = round(bear_cnt / total_votes * 100, 1)
    else:
        bull_pct = bear_pct = 0.0
    
    # 显示最终结论
    st.metric("最终结论", decision_text)
    
    # 显示投票详情
    col1, col2 = st.columns(2)
    with col1:
        st.metric("看涨比例", 
                f"{bull_pct}%",
                f"{bull_cnt}票")
    with col2:
        st.metric("看跌比例", 
                f"{bear_pct}%", 
                f"{bear_cnt}票")
    
    # 显示详细结果
    with st.expander("详细分析结果"):
        tab1, tab2 = st.tabs(["研究结果", "辩论记录"])
        
        with tab1:
            # 显示研究阶段结果
            for key, value in results.items():
                if key not in ['stock_code', 'analysis_time', 'battle_result', 'expert_consensus']:
                    st.subheader(f"{key.replace('_', ' ').title()}")
                    if isinstance(value, dict):
                        st.json(value)
                    else:
                        st.write(value)
        
        with tab2:
            # 显示辩论阶段结果
            if 'battle_result' in results:
                battle_data = results['battle_result']
                if 'debate_history' in battle_data:
                    st.subheader("辩论历史")
                    for msg in battle_data['debate_history']:
                        st.markdown(f"**{msg.get('agent', '未知专家')}**: {msg.get('content', '')}")
                
                if 'battle_highlights' in battle_data:
                    st.subheader("关键辩论点")
                    for highlight in battle_data['battle_highlights']:
                        st.markdown(f"- **{highlight.get('agent', '未知专家')}**: {highlight.get('point', '')}")
    
    # 报告下载按钮
    st.subheader("📥 报告下载")
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="下载JSON报告",
            data=json.dumps(results, indent=2, ensure_ascii=False),
            file_name=f"{results['stock_code']}_analysis_report.json",
            mime="application/json"
        )
    
    with col2:
        # Generate HTML report
        html_report = generate_html_report(results)
        st.download_button(
            label="下载HTML报告",
            data=html_report,
            file_name=f"{results['stock_code']}_analysis_report.html",
            mime="text/html"
        )

if __name__ == "__main__":
    import threading
    import os
    
    def run_main():
        try:
            main()
        except KeyboardInterrupt:
            pass
    
    def signal_handler(signum, frame):
        print("\n应用程序正在停止...")
        if hasattr(st.session_state, 'app_state') and st.session_state.app_state.analysis_task:
            st.session_state.app_state.should_stop = True
        os._exit(0)
    
    # 只在主线程中设置信号处理
    if threading.current_thread() is threading.main_thread():
        import signal
        signal.signal(signal.SIGINT, signal_handler)
    
    run_main()