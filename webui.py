#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import json
import sys
import time
import io
from typing import Any, Dict, List, Optional

import streamlit as st
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax

from src.config import config

from main import EnhancedFinGeniusAnalyzer

def generate_html_report(results: Dict[str, Any]) -> str:
    """根据分析结果生成HTML报告"""
    stock_code = results.get("stock_code", "")
    recommendation = results.get("recommendation", "")
    risk_score = results.get("risk_score", 0)
    value_score = results.get("value_score", 0)
    target_price = results.get("target_price", "")
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_code} 分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 1000px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; }}
        .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 15px; border-radius: 5px; background: #f8f9fa; }}
        .recommendation {{ padding: 15px; background: #e8f4fd; border-left: 5px solid #3498db; margin: 20px 0; }}
        .expert-analysis {{ margin-top: 30px; }}
        .expert {{ margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
        .risk-low {{ color: #27ae60; }}
        .risk-medium {{ color: #f39c12; }}
        .risk-high {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{stock_code} 股票分析报告</h1>
        <div>生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}</div>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <h3>风险评分</h3>
            <p class="{'risk-low' if risk_score < 4 else 'risk-medium' if risk_score < 7 else 'risk-high'}">
                {risk_score}/10
            </p>
        </div>
        <div class="metric">
            <h3>价值评分</h3>
            <p>{value_score}/10</p>
        </div>
        <div class="metric">
            <h3>目标价格</h3>
            <p>{target_price}</p>
        </div>
    </div>
    
    <div class="recommendation">
        <h2>投资建议</h2>
        <p>{recommendation}</p>
    </div>
    
    <div class="expert-analysis">
        <h2>专家分析</h2>
        {''.join(
            f'<div class="expert"><h3>{expert}</h3><p>{analysis}</p></div>'
            for expert, analysis in results.get('expert_analysis', {}).items()
        )}
    </div>
    
    <div class="vote-results">
        <h2>投票结果</h2>
        <table border="1" cellpadding="5" cellspacing="0" style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background-color: #3498db; color: white;">
                    <th>专家</th>
                    <th>投票</th>
                    <th>理由</th>
                </tr>
            </thead>
            <tbody>
                {''.join(
                    f'<tr><td>{vote["expert"]}</td><td>{vote["vote"]}</td><td>{vote["reason"]}</td></tr>'
                    for vote in results.get('vote_results', [])
                )}
            </tbody>
        </table>
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

# 创建一个专门的日志渲染器类，用于处理ANSI控制符号
class RichLogRenderer:
    """使用rich库渲染带有ANSI控制符号的日志"""
    
    def __init__(self):
        """初始化日志渲染器"""
        self.console = Console(
            color_system="truecolor",
            width=100,  # 初始宽度，会根据容器自动调整
            highlight=True,
            record=True,
            markup=True
        )
    
    def render_text(self, text, syntax=None):
        """渲染文本，支持ANSI控制符号"""
        string_io = io.StringIO()
        console = Console(
            file=string_io,
            color_system="truecolor",
            width=100,
            highlight=True,
            markup=True
        )
        
        if syntax:
            # 如果指定了语法，使用Syntax渲染
            console.print(Syntax(text, syntax, theme="monokai"))
        else:
            # 否则直接打印文本
            console.print(text)
        
        # 获取HTML输出
        html = string_io.getvalue()
        return html
    
    def render_to_html(self, text, style=None):
        """将文本渲染为HTML，保留ANSI颜色和格式"""
        string_io = io.StringIO()
        console = Console(
            file=string_io,
            color_system="truecolor",
            width=100,
            highlight=True,
            markup=True
        )
        
        if style:
            console.print(text, style=style)
        else:
            console.print(text)
        
        # 获取HTML输出并转换为适合Streamlit的格式
        html = string_io.getvalue()
        # 将ANSI转义序列转换为HTML
        return f"""<pre style="white-space: pre-wrap; word-wrap: break-word; 
                  font-family: 'Courier New', monospace; margin: 0; padding: 8px; 
                  border-radius: 4px; background-color: #f0f2f6;">{html}</pre>"""


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
    /* 美化日志显示的样式 */
    .rich-log-container {{
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        word-wrap: break-word;
        background-color: #1e1e1e;
        color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        overflow-x: auto;
        width: 100%;
    }}
    .rich-log-container pre {{
        margin: 0;
        padding: 0;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
    }}
    .log-entry {{
        margin-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 8px;
    }}
    .log-timestamp {{
        color: #888;
        font-size: 0.85em;
        margin-right: 8px;
    }}
    .log-agent {{
        font-weight: bold;
        color: #4caf50;
        margin-right: 8px;
    }}
    .log-message {{
        color: #f0f0f0;
    }}
    .log-speak {{
        border-left: 3px solid #2196F3;
        padding-left: 8px;
    }}
    .log-vote {{
        border-left: 3px solid #4CAF50;
        padding-left: 8px;
    }}
    .log-console {{
        border-left: 3px solid #FFC107;
        padding-left: 8px;
        font-family: 'Courier New', monospace;
    }}
    /* 确保代码块和日志内容自动换行 */
    pre {{
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
    }}
    /* 美化控制台输出 */
    .console-output {{
        font-family: 'Courier New', monospace;
        background-color: #1e1e1e;
        color: #f0f0f0;
        padding: 8px;
        border-radius: 4px;
        margin: 4px 0;
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
        
        # 添加额外的CSS样式，确保日志显示美观
        st.markdown("""
        <style>
        /* 确保日志容器内的内容自动换行并适应宽度 */
        .rich-log-container {
            width: 100%;
            overflow-x: auto;
        }
        /* 确保代码和ANSI颜色正确显示 */
        .rich-log-container pre {
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            width: 100%;
        }
        /* 调整日志条目的间距 */
        .log-entry {
            padding: 4px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
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
        
        # 增强的Streamlit可视化器，带实时日志功能
        class StreamlitVisualizer:
            def __init__(self):
                if 'log_messages' not in st.session_state:
                    st.session_state.log_messages = []
                if 'console_output' not in st.session_state:
                    st.session_state.console_output = []
                self.last_update = time.time()
                self.original_stdout = sys.stdout
                sys.stdout = self  # 重定向标准输出
                
                # 初始化Rich日志渲染器
                self.log_renderer = RichLogRenderer()
                
            def write(self, message):
                """捕获控制台输出，支持ANSI控制符号"""
                if message.strip():
                    timestamp = time.strftime("%H:%M:%S")
                    
                    # 使用Rich渲染ANSI控制符号
                    rendered_message = self.log_renderer.render_text(message)
                    
                    log_entry = {
                        "time": timestamp,
                        "message": message,
                        "rendered_message": rendered_message,
                        "type": "console"
                    }
                    st.session_state.console_output.append(log_entry)
                    self._update_console_display()

                    # 同时也输出到控制台
                    self.original_stdout.write(message)
                
            def flush(self):
                pass
        
            def show_progress_update(self, title: str, message: str = ""):
                update_progress(f"{title}: {message}", st.session_state.app_state.current_progress)
            
            def show_debate_message(self, agent: str, message: str, message_type: str):
                # 将消息添加到队列，带时间戳和类型
                timestamp = time.strftime("%H:%M:%S")
                
                # 使用Rich渲染消息，保留格式
                rendered_message = self.log_renderer.render_text(message)
                
                log_entry = {
                    "time": timestamp,
                    "agent": agent,
                    "message": message,
                    "rendered_message": rendered_message,
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
                # 使用空容器进行动态更新
                if 'log_container' not in st.session_state:
                    st.session_state.log_container = st.empty()
            
                with st.session_state.log_container.container():
                    # 创建一个HTML容器来显示所有日志
                    html_logs = []
                    html_logs.append('<div class="rich-log-container">')
                    
                    # 合并显示所有消息
                    all_messages = []
                    
                    # 添加专家消息
                    for msg in st.session_state.log_messages[-15:]:
                        if msg["type"] == "speak":
                            all_messages.append({
                                "time": msg['time'],
                                "type": "专家发言",
                                "agent": msg['agent'],
                                "content": msg.get('rendered_message', msg['message']),
                                "raw_content": msg['message'],
                                "style": "log-speak"
                            })
                        elif msg["type"] == "vote":
                            all_messages.append({
                                "time": msg['time'],
                                "type": "专家投票",
                                "agent": msg['agent'],
                                "content": msg.get('rendered_message', msg['message']),
                                "raw_content": msg['message'],
                                "style": "log-vote"
                            })
                    
                    # 添加控制台输出
                    for msg in st.session_state.console_output[-10:]:
                        all_messages.append({
                            "time": msg['time'],
                            "type": "系统输出",
                            "content": msg.get('rendered_message', msg['message']),
                            "raw_content": msg['message'],
                            "style": "log-console"
                        })
                    
                    # 按时间戳排序
                    all_messages.sort(key=lambda x: x['time'])
                    
                    # 生成HTML日志
                    for msg in all_messages[-25:]:  # 显示最近的25条合并消息
                        html_logs.append(f'<div class="log-entry {msg["style"]}">')
                        html_logs.append(f'<span class="log-timestamp">{msg["time"]}</span>')
                        
                        if "agent" in msg:
                            html_logs.append(f'<span class="log-agent">{msg["agent"]}</span>')
                        
                        if msg["style"] == "log-speak":
                            icon = "💬"
                        elif msg["style"] == "log-vote":
                            icon = "✅"
                        else:
                            icon = "🖥️"
                            
                        html_logs.append(f'<span class="log-message">{icon} {msg["content"]}</span>')
                        html_logs.append('</div>')
                    
                    html_logs.append('</div>')
                    
                    # 使用st.markdown显示HTML日志
                    st.markdown(''.join(html_logs), unsafe_allow_html=True)
                
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
            # 创建Rich日志渲染器
            log_renderer = RichLogRenderer()
            
            # 创建一个HTML容器来显示所有日志
            html_logs = []
            html_logs.append('<div class="rich-log-container">')
            
            # 合并显示所有消息
            all_messages = []
            
            # 添加专家消息
            if 'log_messages' in st.session_state:
                for msg in st.session_state.log_messages:
                    if msg["type"] == "speak":
                        rendered_message = msg.get('rendered_message', 
                                                  log_renderer.render_text(msg['message']))
                        all_messages.append({
                            "time": msg['time'],
                            "type": "专家发言",
                            "agent": msg['agent'],
                            "content": rendered_message,
                            "raw_content": msg['message'],
                            "style": "log-speak"
                        })
                    elif msg["type"] == "vote":
                        rendered_message = msg.get('rendered_message', 
                                                  log_renderer.render_text(msg['message']))
                        all_messages.append({
                            "time": msg['time'],
                            "type": "专家投票",
                            "agent": msg['agent'],
                            "content": rendered_message,
                            "raw_content": msg['message'],
                            "style": "log-vote"
                        })
            
            # 添加控制台输出
            if 'console_output' in st.session_state:
                for msg in st.session_state.console_output:
                    rendered_message = msg.get('rendered_message', 
                                              log_renderer.render_text(msg['message']))
                    all_messages.append({
                        "time": msg['time'],
                        "type": "系统输出",
                        "content": rendered_message,
                        "raw_content": msg['message'],
                        "style": "log-console"
                    })
            
            # 按时间戳排序
            all_messages.sort(key=lambda x: x['time'])
            
            # 生成HTML日志
            for msg in all_messages:
                html_logs.append(f'<div class="log-entry {msg["style"]}">')
                html_logs.append(f'<span class="log-timestamp">{msg["time"]}</span>')
                
                if "agent" in msg:
                    html_logs.append(f'<span class="log-agent">{msg["agent"]}</span>')
                
                if msg["style"] == "log-speak":
                    icon = "💬"
                elif msg["style"] == "log-vote":
                    icon = "✅"
                else:
                    icon = "🖥️"
                    
                html_logs.append(f'<span class="log-message">{icon} {msg["content"]}</span>')
                html_logs.append('</div>')
            
            html_logs.append('</div>')
            
            # 使用st.markdown显示HTML日志
            st.markdown(''.join(html_logs), unsafe_allow_html=True)

    st.success("分析完成!")
    results = st.session_state.app_state.analysis_results
    
    # 显示关键指标
    st.subheader("📊 综合分析结果")
    
    # 显示股票代码和分析时间
    st.markdown(f"**股票代码**: {results.get('stock_code', '未知')}")
    st.markdown(f"**分析耗时**: {results.get('analysis_time', 0):.2f}秒")
    
    # 显示专家共识
    if 'expert_consensus' in results:
        st.metric("专家共识", results['expert_consensus'])
    
    # 显示投票结果
    if 'battle_result' in results and 'vote_count' in results['battle_result']:
        votes = results['battle_result']['vote_count']
        total_votes = sum(votes.values())
        if total_votes > 0:
            bullish_pct = (votes.get('bullish', 0) / total_votes) * 100
            bearish_pct = (votes.get('bearish', 0) / total_votes) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("看涨比例", f"{bullish_pct:.1f}%")
            with col2:
                st.metric("看跌比例", f"{bearish_pct:.1f}%")
    
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