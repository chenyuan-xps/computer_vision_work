# -*- coding: utf-8 -*-
"""
=====================================================================
基于 Streamlit + Pandas + Plotly 的数据分析可视化网站
课程：可视化导论 课程作业
---------------------------------------------------------------------
功能模块：
  1. 数据加载：内置鸢尾花默认数据集 + 用户上传 CSV
  2. Pandas 分析（每一项分析都配有对应可视化，"表格 + 图表 + 自动结论"）：
       数据集概览：指标卡 / 字段类型占比图 / 内存占用图
       表格预览：色阶条件格式（pandas Styler）
       多列筛选：区间/类别筛选 + 分布高亮与散点高亮实时联动
       统计描述：色阶 describe 表 + 对应箱线图 + 离散度结论
       缺失值检测：率色阶表 + 缺失位置矩阵 + 演示缺失注入 + 重复行明细
       分组聚合：groupby / pivot_table，表格与柱状图/热力图联动
  3. Plotly 交互式可视化：
       "分析问题向导"（按问题自动出图并给出文字解读）+ 10 种自由图表，
       图表自带统计标注（趋势线 / 均值·中位数参考线 / 离群点）
  4. 数据故事线（可视化图表页默认模式）：按"分布→构成→类别差异→变量关系→小结"
       五章叙事，每章配图表与自动结论，末章由 Pandas 自动汇总"关键发现"
  5. 侧边栏中文 / 英文一键切换，白天 / 夜间模式一键换肤，页面所有文字一一对应
  6. 5 个页面通过顶部导航栏（st.navigation, position="top"）切换：
     概览 / 数据预览与筛选（预览+筛选合并）/ 统计与数据质量（描述+缺失重复合并）
     / 分组聚合 / 可视化图表
作者：（请在此处填写姓名学号）
=====================================================================
"""

from pathlib import Path  # 路径处理，跨平台兼容（Windows / macOS / Linux）

import numpy as np       # NumPy：相关系数、最小二乘拟合、随机抽样
import pandas as pd      # Pandas：数据分析核心库，DataFrame 数据结构
import plotly.express as px  # Plotly Express：高层 API，一行代码生成交互式图表
import plotly.graph_objects as go  # Plotly 底层图形对象：图层叠加、参考线
import streamlit as st   # Streamlit：快速构建数据 Web 应用的框架

# ---------------------------------------------------------------------
# 0. 页面基础配置（必须是第一条 Streamlit 命令）
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Data Analysis & Visualization",  # 浏览器标签页标题
    layout="wide",                               # 宽屏布局，图表展示更舒适
    initial_sidebar_state="expanded",            # 侧边栏默认展开
)

# ---------------------------------------------------------------------
# 0.1 页面视觉美化：按白天/夜间主题注入 CSS，让标题、指标卡、导航栏色彩更鲜明
#     （使用 data-testid 选择器，比 Streamlit 随机类名稳定）
# ---------------------------------------------------------------------
# 主题状态：app_theme_dark = False 白天模式 / True 夜间模式（开关在侧边栏）
if "app_theme_dark" not in st.session_state:
    st.session_state["app_theme_dark"] = False

LIGHT_THEME_CSS = """
    /* ===== 白天模式：白底 + 蓝色科技光晕，层次分明不寡淡 ===== */
    html, body, .stApp {
        background-color: #ffffff !important;
        color: #1f2937;
    }
    /* 主内容区：顶部蓝色 + 金色双色光晕，向下渐变为纯白 */
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"] {
        background:
            radial-gradient(1100px 480px at 8% -10%, rgba(28,126,214,0.14), transparent 60%),
            radial-gradient(820px 380px at 95% -8%, rgba(245,179,1,0.12), transparent 55%),
            linear-gradient(180deg, #ecf4ff 0%, #f6faff 260px, #ffffff 62%) !important;
        color: #1f2937;
    }
    /* 顶部 header / 导航栏：白色半透明毛玻璃 */
    [data-testid="stAppHeader"], [data-testid="stHeader"] {
        background: rgba(255,255,255,0.82) !important;
        backdrop-filter: blur(10px);
        border-bottom: 1px solid #d7e6f8;
    }
    /* 侧边栏：浅蓝纵向渐变面板 */
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background: linear-gradient(180deg, #e4efff 0%, #f3f8ff 55%, #eef5ff 100%) !important;
        color: #1f2937;
    }
    [data-testid="stSidebarContent"] { border-right: 1px solid #d7e6f8; }
    h2, h3, h4, h5, label { color: #16324f; }
    /* 主标题：深空蓝→青→金渐变文字 + 蓝色光晕 */
    [data-testid="stAppViewContainer"] h1 {
        background: linear-gradient(90deg, #0b3d91, #1c7ed6, #22b8cf, #e8a317);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: 1px;
        filter: drop-shadow(0 3px 14px rgba(28,126,214,0.28));
    }
    /* 二级标题：蓝色卡片条；三级标题：蓝青渐变下划线 */
    [data-testid="stAppViewContainer"] h2 {
        background: linear-gradient(90deg, rgba(28,126,214,0.12), rgba(34,184,207,0.06) 55%, transparent);
        border-left: 4px solid #1c7ed6;
        padding: 9px 14px;
        border-radius: 0 10px 10px 0;
    }
    [data-testid="stAppViewContainer"] h3 {
        border-bottom: 2px solid;
        border-image: linear-gradient(90deg, #1c7ed6, #22b8cf, #f5b301, transparent) 1;
        padding-bottom: 6px;
    }
    /* 指标卡：浅蓝渐变底 + 金条 + 蓝色阴影，hover 上浮 */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #e5f0ff 100%);
        border: 1px solid #d7e6f8;
        border-left: 6px solid #f5b301;
        border-radius: 12px;
        padding: 12px 16px;
        box-shadow: 0 3px 12px rgba(28, 126, 214, 0.16);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(28, 126, 214, 0.26);
    }
    [data-testid="stMetricValue"] { color: #0b5fb3 !important; font-weight: 800; }
    /* 侧边栏标题配色 */
    [data-testid="stSidebar"] h2 { color: #0b5fb3; }
    /* 顶部导航：hover 浅蓝底，当前页蓝金渐变胶囊 + 金色下划线 */
    [data-testid="stTopNavLink"] {
        border-radius: 10px;
        padding: 6px 12px;
        font-weight: 600;
        transition: background 0.15s ease;
    }
    [data-testid="stTopNavLink"]:hover { background: rgba(28,126,214,0.10); }
    [data-testid="stTopNavLink"][aria-current],
    [data-testid="stTopNavLink"][aria-current="page"],
    a[data-testid="stTopNavLink"][aria-current="page"] {
        background: linear-gradient(135deg, rgba(28,126,214,0.14), rgba(245,179,1,0.14)) !important;
        color: #0b3d91 !important;
        box-shadow: inset 0 -3px 0 #f5b301;
    }
    /* 主按钮：蓝色渐变 */
    button[kind="primary"], .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #1c7ed6, #0b3d91) !important;
        border: none !important;
        color: #ffffff !important;
        box-shadow: 0 3px 10px rgba(28,126,214,0.35);
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #228ae6, #1c5fc0) !important;
        color: #ffffff !important;
    }
    /* 折叠面板 / 提示框浅蓝卡片化 */
    [data-testid="stExpander"] {
        background: #f3f8ff;
        border: 1px solid #d7e6f8;
        border-radius: 10px;
    }
    [data-testid="stAlert"] { border-radius: 10px; }
    [data-testid="stDataFrame"], [data-testid="stDataFrameResizable"] {
        border: 1px solid #d7e6f8;
        border-radius: 8px;
        overflow: hidden;
    }
    /* 链接用科技蓝 */
    a { color: #1c7ed6; }
    a:hover { color: #e8a317; }
"""

DARK_THEME_CSS = """
    /* ===== 夜间模式：深空蓝黑 + 科技光效，所有文字保证可读 ===== */
    html, body, .stApp {
        background-color: #0a1628 !important;
        color: #dbe7f5;
    }
    /* 主内容区：深蓝黑底 + 顶部蓝/金双色科技光晕 */
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"] {
        background:
            radial-gradient(1100px 520px at 6% -12%, rgba(28,126,214,0.28), transparent 60%),
            radial-gradient(820px 400px at 96% -10%, rgba(245,179,1,0.10), transparent 55%),
            linear-gradient(180deg, #0b1c36 0%, #0a1628 340px, #081122 100%) !important;
        color: #dbe7f5;
    }
    /* —— 文字颜色：穷举 Streamlit 各文字容器，杜绝黑底黑字 —— */
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] span,
    [data-testid="stAppViewContainer"] li,
    [data-testid="stAppViewContainer"] td,
    [data-testid="stAppViewContainer"] th,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] td,
    [data-testid="stMarkdownContainer"] th,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stVerticalBlock"] p,
    [data-testid="stVerticalBlock"] span,
    h2, h3, h4, h5, h6, label,
    [data-baseweb="menu"] li,
    [data-baseweb="select"] *,
    [data-baseweb="input"] *,
    [data-baseweb="slider"] *,
    [data-testid="stRadio"] label p,
    [data-testid="stCheckbox"] label p,
    [data-testid="stToggle"] label p,
    [data-testid="stSelectbox"] label,
    [data-testid="stMultiSelect"] label,
    [data-testid="stSlider"] label,
    [data-testid="stNumberInput"] label {
        color: #dbe7f5;
    }
    [data-testid="stCaptionContainer"],
    [data-testid="stAppViewContainer"] small { color: #93aac8 !important; }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p { color: #b7c9e0 !important; }
    /* 链接亮蓝，悬停金色 */
    a, a:visited { color: #74c0fc !important; }
    a:hover { color: #ffd166 !important; }
    /* 顶部 header 与导航栏 */
    [data-testid="stAppHeader"], [data-testid="stHeader"] {
        background: rgba(10, 22, 40, 0.82) !important;
        backdrop-filter: blur(10px);
        border-bottom: 1px solid #1d3557;
    }
    [data-testid="stHeader"] button, [data-testid="stMainMenu"] button,
    [data-testid="stMainMenu"] svg { color: #dbe7f5 !important; background: transparent !important; }
    [data-testid="stDeployButton"] { display: none; }
    /* 侧边栏：深蓝纵向渐变面板 */
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background: linear-gradient(180deg, #10274a 0%, #0d2140 55%, #0a1c38 100%) !important;
        color: #dbe7f5;
    }
    [data-testid="stSidebarContent"] { border-right: 1px solid #1d3557; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] li { color: #dbe7f5 !important; }
    [data-testid="stSidebar"] h2 { color: #74c0fc; }
    /* 主标题：亮蓝→青→金渐变 + 发光 */
    [data-testid="stAppViewContainer"] h1 {
        background: linear-gradient(90deg, #74c0fc, #38bdf8, #22d3ee, #ffd166);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: 1px;
        filter: drop-shadow(0 0 16px rgba(56,189,248,0.35));
    }
    /* 二 / 三级标题卡片化 */
    [data-testid="stAppViewContainer"] h2 {
        background: linear-gradient(90deg, rgba(28,126,214,0.22), rgba(34,184,207,0.08) 55%, transparent);
        border-left: 4px solid #4dabf7;
        padding: 9px 14px;
        border-radius: 0 10px 10px 0;
        color: #dbe7f5;
    }
    [data-testid="stAppViewContainer"] h3 {
        border-bottom: 2px solid;
        border-image: linear-gradient(90deg, #4dabf7, #22d3ee, #f5b301, transparent) 1;
        padding-bottom: 6px;
    }
    /* 指标卡：深蓝渐变底 + 金条 + 蓝色发光，hover 上浮 */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0e2140 0%, #132c50 100%) !important;
        border: 1px solid #24426b;
        border-left: 6px solid #f5b301;
        border-radius: 12px;
        padding: 12px 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.45), inset 0 0 24px rgba(28,126,214,0.08) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(28,126,214,0.35) !important;
    }
    [data-testid="stMetricValue"] { color: #74c0fc !important; font-weight: 800; }
    /* 顶部导航：hover 蓝底，当前页蓝金胶囊 + 金色下划线 */
    [data-testid="stTopNavLink"] {
        border-radius: 10px;
        padding: 6px 12px;
        font-weight: 600;
        color: #93aac8;
    }
    [data-testid="stTopNavLink"]:hover { background: rgba(77,171,247,0.14); color: #dbe7f5; }
    [data-testid="stTopNavLink"][aria-current],
    [data-testid="stTopNavLink"][aria-current="page"],
    a[data-testid="stTopNavLink"][aria-current="page"] {
        background: linear-gradient(135deg, rgba(28,126,214,0.30), rgba(245,179,1,0.18)) !important;
        color: #74c0fc !important;
        box-shadow: inset 0 -3px 0 #f5b301;
    }
    /* 主按钮蓝色渐变 */
    button[kind="primary"], .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #1c7ed6, #0b3d91) !important;
        border: none !important;
        color: #ffffff !important;
        box-shadow: 0 3px 12px rgba(28,126,214,0.45);
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #228ae6, #1c5fc0) !important;
        color: #ffffff !important;
    }
    /* 次按钮：深蓝描边胶囊 —— 夜间不能保留默认白底，否则浅字几乎看不见 */
    button[kind="secondary"], .stButton button[kind="secondary"] {
        background: linear-gradient(135deg, #10274a, #0c1f3d) !important;
        border: 1px solid #2f517e !important;
        color: #dbe7f5 !important;
    }
    .stButton button[kind="secondary"] p,
    .stButton button[kind="secondary"] span,
    .stButton button[kind="secondary"] div { color: #dbe7f5 !important; }
    button[kind="secondary"]:hover,
    .stButton button[kind="secondary"]:hover {
        background: #1b3a63 !important;
        border-color: #4dabf7 !important;
        color: #ffffff !important;
    }
    .stButton button[kind="secondary"]:hover p,
    .stButton button[kind="secondary"]:hover span { color: #ffffff !important; }
    button[kind="secondary"]:active {
        background: #234a7d !important;
        border-color: #74c0fc !important;
        color: #ffffff !important;
    }
    /* 数据表格容器（canvas 内部用反色滤镜深色化） */
    [data-testid="stDataFrame"], [data-testid="stDataFrameResizable"] {
        background-color: #0d2140;
        border: 1px solid #24426b;
        border-radius: 8px;
        overflow: hidden;
    }
    /* invert(1)+hue-rotate(180deg) 数学上保持色相不变：白底变黑、黑字变白，蓝金仍为蓝金 */
    [data-testid="stDataFrame"] canvas,
    [data-testid="stDataFrameResizable"] canvas {
        filter: invert(1) hue-rotate(180deg) saturate(0.9);
        border-radius: 4px;
    }
    /* 折叠面板 / 提示框 / 分割线 */
    [data-testid="stExpander"] {
        background-color: #0e2140 !important;
        border: 1px solid #24426b;
        border-radius: 10px;
    }
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: #74c0fc !important; }
    [data-testid="stAlert"] { background-color: #0e2140 !important; border-radius: 10px; }
    [data-testid="stAlert"] p, [data-testid="stAlert"] span { color: #dbe7f5 !important; }
    hr { border-color: #24426b !important; }
    /* Plotly 图表容器透明（图表自身已通过 plotly_dark + show_plotly 深色化） */
    [data-testid="stPlotlyChart"] { background: transparent; }
    /* BaseWeb 输入控件深色化 */
    [data-baseweb="input"], [data-baseweb="select"] > div,
    [data-baseweb="text-area"] {
        background-color: #0a1628 !important;
        border-color: #2f517e !important;
        color: #dbe7f5 !important;
    }
    [data-baseweb="input"] input, [data-baseweb="select"] input {
        color: #dbe7f5 !important;
        caret-color: #74c0fc;
    }
    [data-baseweb="menu"], [data-baseweb="popover"], [data-baseweb="tooltip-inner"],
    [data-baseweb="tooltip"] {
        background-color: #10274a !important;
        color: #dbe7f5 !important;
        border: 1px solid #24426b !important;
    }
    [data-baseweb="menu"] li { color: #dbe7f5 !important; }
    [data-baseweb="menu"] li:hover, [aria-selected="true"] {
        background-color: #1b3a63 !important;
    }
    /* 下拉框已选值、单选 / 多选标签、滑块刻度 */
    [data-baseweb="select"] [data-testid="stText"] { color: #dbe7f5 !important; }
    [data-baseweb="tag"] { background-color: #1b3a63 !important; color: #dbe7f5 !important; }
    [data-baseweb="tick"] * { color: #93aac8 !important; }
    [data-testid="stTickBar"] *, [data-testid="stThumbValueLabel"] { color: #dbe7f5 !important; }
"""


def inject_theme_css() -> None:
    """按当前主题注入对应的美化 CSS（白天白底 / 夜间深色）。"""
    css = DARK_THEME_CSS if st.session_state["app_theme_dark"] else LIGHT_THEME_CSS
    st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)


inject_theme_css()


# ---------------------------------------------------------------------
# 1. 国际化（i18n）：所有页面文字统一放入字典，中文 / 英文一一对应
#    使用方式：t("key") 即取出当前语言下的文案
# ---------------------------------------------------------------------
TEXTS = {
    "zh": {
        # ---- 通用 ----
        "app_title": "数据分析与可视化平台",
        "app_subtitle": "Streamlit + Pandas + Plotly ｜ 可视化导论课程作业",
        "language": "界面语言 / Language",
        "theme_toggle": "夜间模式（深色背景）",
        "none": "无（不分组）",
        "auto_insight": "自动解读",
        "vline_mean": "均值",
        "vline_median": "中位数",
        "ols_label": "趋势线 y = {slope}x + {intercept}",
        # ---- 侧边栏：数据源 ----
        "sidebar_header": "数据源",
        "source_default": "内置鸢尾花数据集",
        "source_upload": "上传我的 CSV 文件",
        "upload_tip": "选择一个 CSV 文件（UTF-8 编码，第一行为表头）",
        "using_default": "当前使用：内置鸢尾花数据集（150 条记录）",
        "using_upload": "当前使用上传文件：",
        "dataset_info": "打开网页会自动加载默认数据；切换上方选项即可分析自己的 CSV 文件。",
        "load_error": "文件读取失败，请确认是标准 CSV 文件（建议 UTF-8 编码）。",
        # ---- 顶部导航各页面 ----
        "tab_overview": "数据集概览",
        "tab_preview": "数据预览与筛选",
        "tab_filter": "多列筛选",
        "tab_describe": "统计与数据质量",
        "tab_missing": "缺失与重复",
        "tab_group": "分组聚合",
        "tab_chart": "可视化图表",
        "tab_dashboard": "可视化总览",
        # ---- 概览 ----
        "metric_rows": "行数（记录数）",
        "metric_cols": "列数（字段数）",
        "metric_num": "数值型列",
        "metric_cat": "文本/类别型列",
        "metric_missing": "缺失单元格",
        "metric_dup": "重复行",
        "dtype_title": "字段类型一览（df.dtypes）",
        "ov_viz_title": "字段构成与内存占用可视化",
        "ov_dtype_pie": "字段类型构成",
        "ov_memory": "各字段内存占用（df.memory_usage）",
        "mem_bytes": "内存占用（字节）",
        "col_name": "字段名",
        "col_dtype": "Pandas 数据类型",
        "col_kind": "类型说明",
        "kind_num": "数值型",
        "kind_cat": "文本/类别型",
        "head_title": "前 5 行数据速览（df.head()）",
        # ---- 表格预览 ----
        "preview_cols": "选择要展示的列（不选则显示全部列）",
        "preview_rows": "展示前 N 行",
        "preview_dim": "当前视图维度：",
        "preview_style": "为数值列添加色阶条件格式（颜色越蓝数值越大，pandas Styler）",
        # ---- 筛选 + 预览（本页只保留一次筛选，表格与图表共用其结果）----
        "filter_section_title": "① 数据筛选（本页唯一筛选入口，下方表格与图表均随结果联动）",
        "preview_section_title": "② 筛选结果预览",
        "chart_section_title": "③ 筛选结果图表（全部基于当前筛选结果）",
        "filter_cols_cond": "选择需要添加筛选条件的列（可多选；不选则使用全部数据）",
        "filter_empty": "没有符合筛选条件的记录，请放宽条件后重试。",
        "download_filter": "下载筛选结果为 CSV",
        "filter_num_tip": "数值范围（拖动滑块，闭区间）",
        "filter_cat_tip": "勾选要保留的类别（不选视为全部保留）",
        "filter_before": "筛选前记录数",
        "filter_after": "筛选后记录数",
        "filter_keep_pct": "保留比例",
        "filter_obs": "分布直方图字段（数值型）",
        "filter_scatter_x": "散点图 X 字段",
        "filter_scatter_y": "散点图 Y 字段",
        "filter_no_cond_hint": "当前未设置筛选条件，展示全部 {n} 条记录；"
                               "添加条件后，下方预览与图表会自动收缩为命中子集。",
        "filter_no_num": "当前数据集没有数值列，无法绘制分布图。",
        "filter_chart_empty": "筛选结果为空，暂无可绘制的数据，请放宽筛选条件。",
        # ---- 统计描述 ----
        "desc_num_title": "数值型字段统计描述（df.describe()，色阶=同统计量下的字段对比）",
        "desc_cat_title": "类别型字段统计描述",
        "desc_no_cat": "数据集中没有类别型字段。",
        "desc_no_num": "数据集中没有数值型字段。",
        "desc_help": "count=非空个数 ｜ mean=均值 ｜ std=标准差 ｜ min=最小值 ｜ "
                     "25%/50%/75%=分位数 ｜ max=最大值",
        "desc_box_title": "各数值字段箱线图（与上表一一对应：中线=50% 中位数，"
                          "箱体=25%~75% 分位数，须线=正常范围，圆点=离群值）",
        "desc_spread_title": "离散程度自动解读",
        "desc_spread_std": "标准差最大的字段是 {col}（std = {v}），绝对波动最大。",
        "desc_spread_cv": "变异系数（std ÷ |mean|）最大的字段是 {col}（CV = {pct}），"
                          "相对离散程度最高。",
        # ---- 缺失值 / 重复行 ----
        "miss_summary": "缺失值总览",
        "miss_total_cells": "数据单元格总数",
        "miss_total_missing": "缺失值总数",
        "miss_ratio": "整体缺失率",
        "miss_table_title": "各字段缺失值明细（df.isna()，蓝色越深缺失越严重）",
        "miss_col": "字段名",
        "miss_count": "缺失数量",
        "miss_pct": "缺失比例",
        "miss_chart_title": "各字段缺失数量分布图",
        "miss_clean": "数据集非常完整，没有检测到任何缺失值。",
        "miss_inject": "注入演示用缺失值（仅本页临时展示，不修改原始数据）",
        "miss_inject_tip": "已随机将约 6% 的单元格临时置为空值，用于演示缺失值图表；"
                           "取消勾选即恢复真实数据。",
        "miss_matrix_title": "缺失位置矩阵（每行一条记录、每列一个字段，金色=缺失）",
        "miss_matrix_sample": "记录较多，仅随机抽样 400 行展示缺失位置。",
        "dup_title": "重复行检测（df.duplicated）",
        "dup_detail_title": "重复行明细（df.duplicated(keep=False)，保留原索引便于定位）",
        "dup_clean": "没有检测到重复行。",
        "dup_found": "检测到 {n} 行重复记录，下表列出了所有重复行本身。",
        # ---- 分组聚合 ----
        "grp_intro": "Pandas groupby / pivot_table：选择分组字段、数值字段与聚合方式，"
                     "聚合表格与图表实时联动。",
        "grp_by": "分组字段（groupby 列）",
        "grp_val": "数值字段（被聚合的列）",
        "grp_agg": "聚合方式（agg）",
        "grp_pivot": "透视列（可选，生成二维 pivot_table 热力图）",
        "grp_table_title": "聚合结果表",
        "grp_chart_title": "聚合结果柱状图（按数值降序）",
        "grp_heat_title": "二维透视表热力图",
        "grp_empty": "当前选择下没有可聚合的结果（可能是该字段缺失值过多）。",
        "agg_mean": "平均值",
        "agg_median": "中位数",
        "agg_sum": "求和",
        "agg_min": "最小值",
        "agg_max": "最大值",
        "agg_std": "标准差",
        "agg_count": "非空计数",
        "grp_insight_top": "“{top}”组的 {col} {agg}最高（{tv}）；"
                           "“{bot}”组最低（{bv}）。",
        "grp_insight_pivot": "在 {by} × {pivot} 的组合中，{col} 的{agg}最高的是"
                             "“{a} × {b}”，数值为 {v}。",
        # ---- 可视化 ----
        "chart_mode": "分析方式",
        "mode_story": "数据故事线（推荐）",
        "mode_wizard": "分析问题向导",
        "mode_free": "自由作图",
        "story_intro": "按「分布 → 构成 → 差异 → 关系 → 小结」的经典分析顺序，"
                       "每一步用一张图回答一个问题，并给出自动解读；"
                       "可直接作为分析报告的叙事主线。",
        "story_s_dist": "① 单变量分布",
        "story_s_share": "② 类别构成",
        "story_s_diff": "③ 类别差异",
        "story_s_relation": "④ 变量关系",
        "story_s_summary": "⑤ 故事小结",
        "story_g_dist": "第一步先看单个数值字段：数据集中在哪个范围？"
                        "均值（金色虚线）与中位数（蓝色实线）是否重合？分布是否偏态？",
        "story_g_share": "再看样本由哪些类别构成、各占多少，判断类别是否均衡。",
        "story_g_diff": "不同类别在关键指标上差距有多大？柱状图比较组均值，"
                        "箱线图看组内分布形态与离群点。",
        "story_g_relation": "最后看两个数值字段是否一起变化："
                            "散点走向、相关系数与金色虚线的线性趋势线给出答案。",
        "story_g_summary": "把前面各章看到的关键数字汇总成结论。",
        "story_prev": "上一章",
        "story_next": "下一章",
        "story_restart": "重新走一遍",
        "story_progress": "第 {cur} / {total} 章",
        "story_end_tip": "故事线到此结束。若想验证其他猜想，"
                         "可切换到「自由作图」继续探索任意字段组合。",
        "wizard_q": "你想回答什么问题？",
        "q_compare": "哪个类别的某项数值指标最大？差异有多大？",
        "q_relation": "两个数值字段之间是否相关？",
        "q_dist": "某个数值字段是如何分布的？",
        "q_groupdist": "不同类别在某指标上的分布有差异吗？（含离群点）",
        "q_share": "各类别的记录数量占比如何？",
        "wizard_cat": "类别字段（X 轴）",
        "wizard_num": "数值字段（Y 轴）",
        "wizard_num_x": "数值字段（X 轴）",
        "wizard_need_cat": "该问题需要一个类别字段，但当前数据集没有类别列。",
        "wizard_need_num": "该问题需要至少一个数值字段。",
        "wizard_need_two_num": "该问题需要两个不同的数值字段。",
        "chart_type": "图表类型",
        "chart_bar": "柱状图（类别对比 / 分组汇总）",
        "chart_line": "折线图（趋势变化）",
        "chart_area": "面积图（累积趋势）",
        "chart_scatter": "散点图（两变量相关性）",
        "chart_scatter3d": "3D 散点图（三变量关系）",
        "chart_hist": "直方图（单变量分布）",
        "chart_box": "箱线图（分布与离群点）",
        "chart_violin": "小提琴图（分布密度形态）",
        "chart_pie": "饼图（类别占比）",
        "chart_density": "密度热力图（双变量密度）",
        "chart_x": "X 轴字段",
        "chart_y": "Y 轴字段（数值型）",
        "chart_z": "Z 轴字段（数值型）",
        "chart_color": "分组着色字段（可选）",
        "chart_nbins": "直方图分箱数量",
        "chart_tip": "柱状图 / 折线图 / 面积图会自动按 X 轴分组，"
                     "对 Y 轴数值求均值（pandas groupby）；"
                     "柱状图建议 X 轴选择类别字段。",
        "chart_same_axis": "X 轴与 Y 轴不能相同，请重新选择。",
        "no_numeric_cols": "数据集中没有数值型列，无法绘制数值图表。",
        "chart_generic_tip": "更换 X / Y 轴字段即可从不同角度探索数据；"
                             "图表支持悬停查看数值、框选缩放、导出图片。",
        "chart_pie_tip": "饼图只需选择 X 轴字段，自动统计各类别的记录数占比。",
        "chart_scatter3d_tip": "3D 散点图需选择 X、Y、Z 三个数值字段，"
                               "可用鼠标拖动旋转立体查看。",
        "chart_density_tip": "密度热力图需选择 X、Y 两个数值字段，"
                             "颜色越亮表示该区间样本越密集。",
        "chart_3d_numeric": "3D 散点图的 X、Y、Z 三个字段都必须是数值型。",
        "chart_density_numeric": "密度热力图的 X、Y 两个字段都必须是数值型。",
        "chart_render": "生成的交互式图表（可缩放、悬停、导出图片）",
        "bar_name": "柱状图",
        "line_name": "折线图",
        "area_name": "面积图",
        "scatter_name": "散点图",
        "scatter3d_name": "3D 散点图",
        "hist_name": "直方图",
        "box_name": "箱线图",
        "violin_name": "小提琴图",
        "pie_name": "饼图",
        "density_name": "密度热力图",
        "count_label": "记录数",
        "axis_x_label": "X 轴",
        "axis_y_label": "Y 轴",
        "mean_suffix": "（均值）",
        "chart_x_num_warn": "提示：X 轴为数值型且取值很多时，柱状图可能较密集，可尝试类别字段。",
        # ---- 自动结论文案 ----
        "degree_big": "显著",
        "degree_mid": "较明显",
        "degree_small": "不大",
        "ins_strong_pos": "强正",
        "ins_strong_neg": "强负",
        "ins_mid_pos": "中等程度正",
        "ins_mid_neg": "中等程度负",
        "ins_weak_pos": "弱正",
        "ins_weak_neg": "弱负",
        "ins_none_rel": "几乎不存在线性",
        "ins_group": "按 {x} 分组后，“{top}”的 {y} 平均值最高（{tv}），"
                     "“{bot}”最低（{bv}），最高约为最低的 {ratio} 倍，"
                     "类别间差异{degree}。",
        "ins_group_diff": "按 {x} 分组后，“{top}”的 {y} 平均值最高（{tv}），"
                          "“{bot}”最低（{bv}），两者相差 {diff}。",
        "ins_corr": "{x} 与 {y} 的皮尔逊相关系数 r = {r}，呈{strength}相关。",
        "ins_corr_line": "图中金色虚线为最小二乘线性拟合趋势线。",
        "ins_hist": "{x} 的均值为 {mean}、中位数为 {median}，分布{shape}。"
                    "金色虚线为均值，蓝色实线为中位数。",
        "shape_right": "右偏（存在偏大的极端值）",
        "shape_left": "左偏（存在偏小的极端值）",
        "shape_symmetric": "大致对称",
        "ins_box": "按 {x} 分组，“{grp}”组 {y} 的四分位距最大（IQR = {iqr}），"
                   "分布最分散；按 1.5 倍 IQR 准则共检出 {n} 个离群点。",
        "ins_box_zero": "按 {x} 分组，“{grp}”组 {y} 的四分位距最大（IQR = {iqr}），"
                        "分布最分散；按 1.5 倍 IQR 准则未检出离群点。",
        "ins_pie": "“{top}”的记录数最多，共 {cnt} 条，占全部记录的 {pct}。",
        # ---- 可视化总览（数据故事线 + 关键发现）----
        "dash_intro": "本页按“数据构成 → 单变量分布 → 类别差异 → 变量关系”的顺序"
                      "自动生成图表，并在顶部给出由 Pandas 计算的关键发现。",
        "findings_title": "关键发现（由 Pandas 自动计算生成）",
        "dash_sec1": "一、数据构成：类别字段占比",
        "dash_sec2": "二、单变量分布：数值字段直方图（金色虚线=均值，蓝色实线=中位数）",
        "dash_sec3": "三、类别差异：分组箱线图（分布差异与离群点）",
        "dash_sec4": "四、变量关系：相关系数热力图与散点矩阵",
        "fd_corr": "相关性最强的两个数值字段是 {a} 与 {b}（r = {r}），呈{strength}相关。",
        "fd_group": "不同 {cat} 类别间差异最大的指标是 {col}："
                    "最高组“{top}”（{tv}）约为最低组“{bot}”（{bv}）的 {ratio} 倍。",
        "fd_cv": "相对离散程度最高的字段是 {col}（变异系数 CV = {pct}）。",
        "miss_none": "无缺失值",
        "miss_some": "存在 {n} 个缺失单元格（{pct}）",
        "dup_none": "无重复行",
        "dup_some": "存在 {n} 行重复",
        "fd_quality": "数据质量：{missing_text}；{dup_text}。",
        "dash_corr_title": "数值字段相关系数热力图",
        "dash_corr_help": "颜色越接近金色表示正相关越强，越接近深蓝表示负相关越强。",
        "dash_dist_title": "各数值字段分布直方图",
        "dash_box_title": "按类别分组的箱线图",
        "dash_matrix_title": "散点矩阵（两两数值字段关系）",
        "dash_pie_title": "类别字段占比环形图",
        "dash_no_category": "当前数据集没有类别字段，已跳过分组箱线图与占比环形图。",
        "dash_corr_need": "相关系数热力图需要至少 2 个数值字段。",
        "dash_need_num": "当前数据集没有数值字段，无法生成该图表。",
    },
    "en": {
        # ---- common ----
        "app_title": "Data Analysis & Visualization",
        "app_subtitle": "Streamlit + Pandas + Plotly | Visualization Course Project",
        "language": "Language / 界面语言",
        "theme_toggle": "Dark mode",
        "none": "None (no grouping)",
        "auto_insight": "Auto insight",
        "vline_mean": "Mean",
        "vline_median": "Median",
        "ols_label": "Trend y = {slope}x + {intercept}",
        # ---- sidebar: data source ----
        "sidebar_header": "Data Source",
        "source_default": "Built-in Iris dataset",
        "source_upload": "Upload my CSV file",
        "upload_tip": "Choose a CSV file (UTF-8 encoded, header in the first row)",
        "using_default": "Using: built-in Iris dataset (150 records)",
        "using_upload": "Using uploaded file: ",
        "dataset_info": "The default dataset loads automatically; "
                        "switch the option above to analyze your own CSV.",
        "load_error": "Failed to read the file. Please make sure it is a valid CSV (UTF-8 recommended).",
        # ---- tabs ----
        "tab_overview": "Overview",
        "tab_preview": "Preview & Filter",
        "tab_filter": "Filtering",
        "tab_describe": "Stats & Data Quality",
        "tab_missing": "Missing & Duplicates",
        "tab_group": "Group & Pivot",
        "tab_chart": "Visualization",
        "tab_dashboard": "Chart Gallery",
        # ---- overview ----
        "metric_rows": "Rows (records)",
        "metric_cols": "Columns (fields)",
        "metric_num": "Numeric columns",
        "metric_cat": "Text/categorical columns",
        "metric_missing": "Missing cells",
        "metric_dup": "Duplicate rows",
        "dtype_title": "Column data types (df.dtypes)",
        "ov_viz_title": "Column composition and memory usage",
        "ov_dtype_pie": "Column type composition",
        "ov_memory": "Memory usage by column (df.memory_usage)",
        "mem_bytes": "Memory (bytes)",
        "col_name": "Column",
        "col_dtype": "Pandas dtype",
        "col_kind": "Type",
        "kind_num": "Numeric",
        "kind_cat": "Text/Categorical",
        "head_title": "First 5 rows (df.head())",
        # ---- preview ----
        "preview_cols": "Columns to display (leave empty to show all)",
        "preview_rows": "Show first N rows",
        "preview_dim": "Current view shape:",
        "preview_style": "Add color-scale formatting to numeric columns "
                         "(darker blue = larger value, pandas Styler)",
        # ---- filtering + preview (one filter set shared by table and charts) ----
        "filter_section_title": "1. Filters (the only filter set on this page — the table and charts below all react to it)",
        "preview_section_title": "2. Preview of the filtered data",
        "chart_section_title": "3. Charts of the filtered data",
        "filter_cols_cond": "Select columns to filter on (multi-select; empty = use all data)",
        "filter_empty": "No records match the filters. Try relaxing the conditions.",
        "download_filter": "Download filtered results as CSV",
        "filter_num_tip": "Numeric range (drag the sliders, closed interval)",
        "filter_cat_tip": "Keep selected categories (empty = keep all)",
        "filter_before": "Records before",
        "filter_after": "Records after",
        "filter_keep_pct": "Retained ratio",
        "filter_obs": "Histogram field (numeric)",
        "filter_scatter_x": "Scatter X field",
        "filter_scatter_y": "Scatter Y field",
        "filter_no_cond_hint": "No filter is active yet — showing all {n} records. "
                               "Add conditions below and the preview and charts shrink to the matched subset.",
        "filter_no_num": "No numeric column available for the distribution charts.",
        "filter_chart_empty": "The filtered subset is empty — nothing to chart. Try relaxing the filters.",
        # ---- statistics ----
        "desc_num_title": "Numeric columns summary (df.describe(); compare columns within each statistic)",
        "desc_cat_title": "Categorical columns summary",
        "desc_no_cat": "No categorical columns in this dataset.",
        "desc_no_num": "No numeric columns in this dataset.",
        "desc_help": "count=non-null | mean=average | std=standard deviation | min=minimum | "
                     "25%/50%/75%=quantiles | max=maximum",
        "desc_box_title": "Box plots of numeric columns (matching the table above: "
                          "center line=median, box=25%-75% quantiles, whiskers=range, dots=outliers)",
        "desc_spread_title": "Auto insight on spread",
        "desc_spread_std": "{col} has the largest standard deviation (std = {v}), "
                           "i.e. the largest absolute fluctuation.",
        "desc_spread_cv": "{col} has the largest coefficient of variation "
                          "(std / |mean|, CV = {pct}), i.e. the highest relative dispersion.",
        # ---- missing / duplicates ----
        "miss_summary": "Missing value summary",
        "miss_total_cells": "Total cells",
        "miss_total_missing": "Total missing",
        "miss_ratio": "Overall missing rate",
        "miss_table_title": "Missing values by column (df.isna(); darker blue = more missing)",
        "miss_col": "Column",
        "miss_count": "Missing count",
        "miss_pct": "Missing rate",
        "miss_chart_title": "Missing count by column",
        "miss_clean": "The dataset is complete: no missing values detected.",
        "miss_inject": "Inject demo missing values (display only on this page; raw data is untouched)",
        "miss_inject_tip": "About 6% of cells have been temporarily set to missing to demo the charts; "
                           "uncheck to restore the real data.",
        "miss_matrix_title": "Missing-location matrix (rows = records, columns = fields; gold = missing)",
        "miss_matrix_sample": "Too many records: a random sample of 400 rows is shown.",
        "dup_title": "Duplicate rows (df.duplicated)",
        "dup_detail_title": "Duplicate row details (df.duplicated(keep=False); original index kept)",
        "dup_clean": "No duplicate rows detected.",
        "dup_found": "{n} duplicate records detected; the table lists every duplicated row.",
        # ---- group & pivot ----
        "grp_intro": "Pandas groupby / pivot_table: pick a grouping field, a numeric field and "
                     "an aggregation; the table and chart update together.",
        "grp_by": "Grouping field (groupby column)",
        "grp_val": "Numeric field (column to aggregate)",
        "grp_agg": "Aggregation (agg)",
        "grp_pivot": "Pivot column (optional; builds a 2-D pivot_table heatmap)",
        "grp_table_title": "Aggregated table",
        "grp_chart_title": "Aggregation bar chart (descending)",
        "grp_heat_title": "2-D pivot heatmap",
        "grp_empty": "Nothing to aggregate with the current selection "
                     "(the chosen column may have too many missing values).",
        "agg_mean": "mean",
        "agg_median": "median",
        "agg_sum": "sum",
        "agg_min": "minimum",
        "agg_max": "maximum",
        "agg_std": "standard deviation",
        "agg_count": "non-null count",
        "grp_insight_top": "Group “{top}” has the highest {agg} of {col} ({tv}); "
                           "group “{bot}” has the lowest ({bv}).",
        "grp_insight_pivot": "Across {by} × {pivot}, the highest {agg} of {col} is "
                             "“{a} × {b}” with {v}.",
        # ---- visualization ----
        "chart_mode": "Analysis mode",
        "mode_story": "Data storyline (recommended)",
        "mode_wizard": "Question wizard",
        "mode_free": "Free charting",
        "story_intro": "Follow the classic order — distribution → composition → "
                       "group differences → relationships → summary. Each step answers "
                       "one question with a chart and an auto insight; the steps can "
                       "serve directly as the narrative of an analysis report.",
        "story_s_dist": "1. Distribution",
        "story_s_share": "2. Composition",
        "story_s_diff": "3. Group differences",
        "story_s_relation": "4. Relationships",
        "story_s_summary": "5. Summary",
        "story_g_dist": "Start with a single numeric field: where do values concentrate? "
                        "Does the mean (gold dashed) match the median (blue solid)? Is it skewed?",
        "story_g_share": "Then look at how records split across categories and whether "
                         "the groups are balanced.",
        "story_g_diff": "How much do categories differ on key metrics? Bars compare group "
                        "means; box plots show within-group spread and outliers.",
        "story_g_relation": "Finally, do two numeric fields move together? Point pattern, "
                            "correlation and the gold dashed trend line give the answer.",
        "story_g_summary": "The key numbers from the previous steps collected as conclusions.",
        "story_prev": "Previous",
        "story_next": "Next",
        "story_restart": "Restart",
        "story_progress": "Step {cur} / {total}",
        "story_end_tip": "End of the storyline. Switch to “Free charting” to test any "
                         "other hypothesis with arbitrary field combinations.",
        "wizard_q": "What question do you want to answer?",
        "q_compare": "Which category has the highest value of a numeric metric? How big is the gap?",
        "q_relation": "Are two numeric fields correlated?",
        "q_dist": "How is a numeric field distributed?",
        "q_groupdist": "Do categories differ in the distribution of a metric? (with outliers)",
        "q_share": "What is the share of each category?",
        "wizard_cat": "Category field (X axis)",
        "wizard_num": "Numeric field (Y axis)",
        "wizard_num_x": "Numeric field (X axis)",
        "wizard_need_cat": "This question needs a categorical column, but the dataset has none.",
        "wizard_need_num": "This question needs at least one numeric field.",
        "wizard_need_two_num": "This question needs two distinct numeric fields.",
        "chart_type": "Chart type",
        "chart_bar": "Bar chart (category comparison / grouped summary)",
        "chart_line": "Line chart (trend over a series)",
        "chart_area": "Area chart (cumulative trend)",
        "chart_scatter": "Scatter plot (correlation of two variables)",
        "chart_scatter3d": "3D scatter plot (three-variable relationship)",
        "chart_hist": "Histogram (distribution of one variable)",
        "chart_box": "Box plot (distribution and outliers)",
        "chart_violin": "Violin plot (distribution shape)",
        "chart_pie": "Pie chart (category share)",
        "chart_density": "Density heatmap (bivariate density)",
        "chart_x": "X-axis column",
        "chart_y": "Y-axis column (numeric)",
        "chart_z": "Z-axis column (numeric)",
        "chart_color": "Group/color column (optional)",
        "chart_nbins": "Number of histogram bins",
        "chart_tip": "Bar/line/area charts automatically group by the X column and "
                     "average the Y values (pandas groupby). "
                     "A categorical X column is recommended for bar charts.",
        "chart_same_axis": "X and Y cannot be the same column.",
        "no_numeric_cols": "No numeric columns available for plotting.",
        "chart_generic_tip": "Change the X / Y columns to explore the data from different angles; "
                             "charts support hover, zoom and PNG export.",
        "chart_pie_tip": "A pie chart only needs an X column; it counts the share of each category.",
        "chart_scatter3d_tip": "A 3D scatter plot needs three numeric columns (X, Y, Z); "
                               "drag with the mouse to rotate.",
        "chart_density_tip": "A density heatmap needs two numeric columns (X, Y); "
                             "brighter colors mean denser samples.",
        "chart_3d_numeric": "All three columns (X, Y, Z) of a 3D scatter must be numeric.",
        "chart_density_numeric": "Both X and Y columns of a density heatmap must be numeric.",
        "chart_render": "Interactive chart (zoom, hover, download as PNG)",
        "bar_name": "Bar chart",
        "line_name": "Line chart",
        "area_name": "Area chart",
        "scatter_name": "Scatter plot",
        "scatter3d_name": "3D scatter plot",
        "hist_name": "Histogram",
        "box_name": "Box plot",
        "violin_name": "Violin plot",
        "pie_name": "Pie chart",
        "density_name": "Density heatmap",
        "count_label": "Count",
        "axis_x_label": "X axis",
        "axis_y_label": "Y axis",
        "mean_suffix": " (mean)",
        "chart_x_num_warn": "Tip: a numeric X with many unique values may produce a dense bar chart; try a categorical column.",
        # ---- auto insight templates ----
        "degree_big": "substantial",
        "degree_mid": "noticeable",
        "degree_small": "small",
        "ins_strong_pos": "strong positive",
        "ins_strong_neg": "strong negative",
        "ins_mid_pos": "moderate positive",
        "ins_mid_neg": "moderate negative",
        "ins_weak_pos": "weak positive",
        "ins_weak_neg": "weak negative",
        "ins_none_rel": "almost no linear",
        "ins_group": "Grouped by {x}, “{top}” has the highest mean {y} ({tv}) and "
                     "“{bot}” the lowest ({bv}); the highest is about {ratio} times "
                     "the lowest, so between-category differences are {degree}.",
        "ins_group_diff": "Grouped by {x}, “{top}” has the highest mean {y} ({tv}) and "
                          "“{bot}” the lowest ({bv}); the gap is {diff}.",
        "ins_corr": "The Pearson correlation between {x} and {y} is r = {r}, "
                    "indicating a {strength} correlation.",
        "ins_corr_line": "The gold dashed line is the ordinary least-squares trend line.",
        "ins_hist": "The mean of {x} is {mean} and the median is {median}; "
                    "the distribution is {shape}. Gold dashed = mean, blue solid = median.",
        "shape_right": "right-skewed (with some large extremes)",
        "shape_left": "left-skewed (with some small extremes)",
        "shape_symmetric": "roughly symmetric",
        "ins_box": "Grouped by {x}, “{grp}” has the largest interquartile range of {y} "
                   "(IQR = {iqr}), i.e. the widest spread; {n} outliers are detected "
                   "with the 1.5×IQR rule.",
        "ins_box_zero": "Grouped by {x}, “{grp}” has the largest interquartile range of {y} "
                        "(IQR = {iqr}), i.e. the widest spread; no outliers are detected "
                        "with the 1.5×IQR rule.",
        "ins_pie": "“{top}” is the largest group with {cnt} records, {pct} of the total.",
        # ---- chart gallery (storyline + key findings) ----
        "dash_intro": "Charts are organized as composition → distributions → "
                      "between-category differences → variable relationships, "
                      "with Pandas-computed key findings on top.",
        "findings_title": "Key findings (computed automatically with Pandas)",
        "dash_sec1": "1. Composition: shares of categorical fields",
        "dash_sec2": "2. Univariate distributions: histograms (gold dashed = mean, blue solid = median)",
        "dash_sec3": "3. Between-category differences: grouped box plots",
        "dash_sec4": "4. Variable relationships: correlation heatmap and scatter matrix",
        "fd_corr": "The two most correlated numeric fields are {a} and {b} "
                   "(r = {r}), a {strength} correlation.",
        "fd_group": "Across {cat} categories, {col} differs the most: the top group "
                    "“{top}” ({tv}) is about {ratio} times the bottom group “{bot}” ({bv}).",
        "fd_cv": "{col} has the highest relative dispersion (coefficient of variation CV = {pct}).",
        "miss_none": "no missing values",
        "miss_some": "{n} missing cells ({pct})",
        "dup_none": "no duplicate rows",
        "dup_some": "{n} duplicate rows",
        "fd_quality": "Data quality: {missing_text}; {dup_text}.",
        "dash_corr_title": "Correlation heatmap of numeric columns",
        "dash_corr_help": "Gold means stronger positive correlation; deep blue means stronger negative correlation.",
        "dash_dist_title": "Distribution histograms of numeric columns",
        "dash_box_title": "Box plots grouped by category",
        "dash_matrix_title": "Scatter matrix (pairwise numeric relationships)",
        "dash_pie_title": "Category share donut charts",
        "dash_no_category": "No categorical column in this dataset; grouped box plots and donut charts are skipped.",
        "dash_corr_need": "A correlation heatmap needs at least 2 numeric columns.",
        "dash_need_num": "No numeric column available for this chart.",
    },
}

# 分析问题向导：问题代号 -> 自动选用的图表类型
WIZARD_MAP = {
    "compare": "bar",
    "relation": "scatter",
    "dist": "hist",
    "groupdist": "box",
    "share": "pie",
}

# 分组聚合可选的聚合方式：内部代码 -> i18n 文案键
AGG_OPTIONS = ["mean", "median", "sum", "min", "max", "std", "count"]
AGG_LABEL_KEY = {agg: f"agg_{agg}" for agg in AGG_OPTIONS}

# ---------------------------------------------------------------------
# 2. 通用工具函数
# ---------------------------------------------------------------------

# 默认数据集 CSV 与 app.py 放在同一目录下，pathlib 保证跨平台路径正确
DEFAULT_CSV = Path(__file__).parent / "default_data.csv"


@st.cache_data
def load_default_data() -> pd.DataFrame:
    """读取内置鸢尾花数据集。

    使用 @st.cache_data 装饰器：首次读取后缓存结果，
    后续切换页面 / 重新渲染时直接从缓存取，避免重复读盘。
    """
    return pd.read_csv(DEFAULT_CSV)


@st.cache_data
def load_uploaded_data(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """解析用户上传的 CSV 文件字节流。

    国内 Excel 另存的 CSV 常为 GBK 编码，因此按
    UTF-8 → GBK 的顺序尝试，提升作业演示时的兼容性。
    """
    # io.BytesIO 把内存中的字节包装成文件对象，供 pd.read_csv 读取
    import io

    for encoding in ("utf-8", "gbk"):
        try:
            return pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
        except UnicodeDecodeError:
            continue  # 当前编码不匹配，尝试下一种
    # 两种编码都失败时，抛出异常由上层捕获并提示用户
    raise ValueError("unsupported encoding")


def dtype_kind_label(dtype, lang: str) -> str:
    """把 Pandas 的 dtype 归类为“数值型 / 类别型”的本地化说明文字。"""
    if pd.api.types.is_numeric_dtype(dtype):
        return TEXTS[lang]["kind_num"]
    return TEXTS[lang]["kind_cat"]


def make_download_csv(df: pd.DataFrame) -> str:
    """把 DataFrame 转成可下载的 CSV 字符串。

    utf-8-sig 会在文件头加入 BOM，用 Windows 版 Excel 打开时中文不乱码。
    """
    return df.to_csv(index=False).encode("utf-8-sig")


def f2(value) -> str:
    """统一的两位小数格式化，空值返回字符串 NaN，避免模板里出现大串小数。"""
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return str(value)


def correlation_strength(r: float, t: dict) -> str:
    """按相关系数绝对值大小返回本地化的强弱/正负描述词。"""
    ar = abs(r)
    if ar < 0.2:
        return t["ins_none_rel"]
    if ar >= 0.7:
        band = "strong"
    elif ar >= 0.4:
        band = "mid"
    else:
        band = "weak"
    sign = "pos" if r >= 0 else "neg"
    return t[f"ins_{band}_{sign}"]


def count_iqr_outliers(series: pd.Series) -> int:
    """按箱线图的 1.5 倍 IQR 准则统计离群点个数。"""
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return 0
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return int(((s < low) | (s > high)).sum())


def add_dist_reference_lines(fig, series, t: dict) -> None:
    """在直方图上叠加均值（金色虚线）与中位数（蓝色实线）两条参考线。"""
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return
    fig.add_vline(
        x=float(s.mean()),
        line=dict(color="#f5b301", width=2, dash="dash"),
        annotation_text=t["vline_mean"],
        annotation_position="top left",
        annotation_font=dict(color="#c79100"),
    )
    fig.add_vline(
        x=float(s.median()),
        line=dict(color="#1c7ed6", width=2),
        annotation_text=t["vline_median"],
        annotation_position="bottom right",
        annotation_font=dict(color="#1c7ed6"),
    )


def build_insight(chart_type: str, data: pd.DataFrame, x_col: str, y_col,
                  lang: str):
    """根据图表类型，用 Pandas 计算并返回一句本地化的自动结论文字。

    结论完全由数据动态计算，不写死任何数字；无法计算时返回 None。
    """
    t = TEXTS[lang]

    # 柱状图 / 折线图 / 面积图：groupby 求均值后比较最高组与最低组
    if chart_type in ("bar", "line", "area"):
        if y_col is None or x_col == y_col:
            return None
        grouped = data.groupby(x_col, dropna=False)[y_col].mean().dropna()
        if grouped.shape[0] < 2:
            return None
        top_cat, top_val = grouped.idxmax(), float(grouped.max())
        bot_cat, bot_val = grouped.idxmin(), float(grouped.min())
        if bot_val > 0:
            ratio = top_val / bot_val
            if ratio >= 2:
                degree = t["degree_big"]
            elif ratio >= 1.3:
                degree = t["degree_mid"]
            else:
                degree = t["degree_small"]
            return t["ins_group"].format(
                x=x_col, top=top_cat, bot=bot_cat, y=y_col,
                tv=f2(top_val), bv=f2(bot_val), ratio=f2(ratio), degree=degree,
            )
        return t["ins_group_diff"].format(
            x=x_col, top=top_cat, bot=bot_cat, y=y_col,
            tv=f2(top_val), bv=f2(bot_val), diff=f2(top_val - bot_val),
        )

    # 散点图 / 密度热力图：皮尔逊相关系数
    if chart_type in ("scatter", "density"):
        if y_col is None or x_col == y_col:
            return None
        if not (pd.api.types.is_numeric_dtype(data[x_col])
                and pd.api.types.is_numeric_dtype(data[y_col])):
            return None
        sub = data[[x_col, y_col]].dropna()
        if sub.shape[0] < 3:
            return None
        r = float(np.corrcoef(sub[x_col], sub[y_col])[0, 1])
        text = t["ins_corr"].format(
            x=x_col, y=y_col, r=f2(r),
            strength=correlation_strength(r, t),
        )
        if chart_type == "scatter":
            text += " " + t["ins_corr_line"]
        return text

    # 直方图：均值 / 中位数 / 偏态
    if chart_type == "hist":
        if not pd.api.types.is_numeric_dtype(data[x_col]):
            return None
        s = data[x_col].dropna()
        if s.empty:
            return None
        mean_v, median_v = float(s.mean()), float(s.median())
        if mean_v > median_v * 1.02:
            shape = t["shape_right"]
        elif mean_v < median_v * 0.98:
            shape = t["shape_left"]
        else:
            shape = t["shape_symmetric"]
        return t["ins_hist"].format(
            x=x_col, mean=f2(mean_v), median=f2(median_v), shape=shape,
        )

    # 箱线图 / 小提琴图：四分位距最大的组 + 离群点总数
    if chart_type in ("box", "violin"):
        if y_col is None or x_col == y_col:
            return None
        q1 = data.groupby(x_col, dropna=False)[y_col].quantile(0.25)
        q3 = data.groupby(x_col, dropna=False)[y_col].quantile(0.75)
        iqr = (q3 - q1).dropna()
        if iqr.empty:
            return None
        widest = iqr.idxmax()
        n_outliers = 0
        for _, group_values in data.groupby(x_col, dropna=False)[y_col]:
            n_outliers += count_iqr_outliers(group_values)
        template = t["ins_box"] if n_outliers > 0 else t["ins_box_zero"]
        return template.format(
            x=x_col, grp=widest, y=y_col, iqr=f2(iqr.max()), n=n_outliers,
        )

    # 饼图：占比最大的类别
    if chart_type == "pie":
        counts = data[x_col].value_counts()
        if counts.empty:
            return None
        total = int(counts.sum())
        top_cat, top_n = counts.index[0], int(counts.iloc[0])
        pct = f"{top_n / total * 100:.1f}%" if total else "0.0%"
        return t["ins_pie"].format(top=top_cat, cnt=top_n, pct=pct)

    return None


# ===== 全站统一配色：深空蓝 + 科技金（蓝/青/金，不含红橙系） =====
# 主分类调色板：前 3 色蓝/金/青对比最强，鸢尾花三类刚好一一对应
COLOR_SEQUENCE = [
    "#1c7ed6",  # 科技蓝
    "#f5b301",  # 科技金
    "#22b8cf",  # 青蓝
    "#0b3d91",  # 深空蓝
    "#e8a317",  # 暗金
    "#74c0fc",  # 浅天蓝
    "#364fc7",  # 靛蓝
    "#90c2ff",  # 淡蓝
    "#0a6fb8",  # 深海蓝
    "#ffd166",  # 亮金
]
# 备用分类调色板（折线/小提琴等与主图表同页出现时仍和谐统一）
COLOR_SEQUENCE_ALT = [
    "#0b3d91", "#22b8cf", "#e8a317", "#364fc7",
    "#74c0fc", "#c0a062", "#1c7ed6", "#90c2ff",
]
# 连续型渐变：深空蓝 → 蓝 → 青 → 科技金（密度热力图等）
CONTINUOUS_SCALE = [
    (0.00, "#031a33"),
    (0.30, "#0b3d91"),
    (0.60, "#1c7ed6"),
    (0.82, "#38bdf8"),
    (1.00, "#f5b301"),
]
# 发散型配色：深蓝（负）→ 浅蓝灰（0）→ 金（正），用于相关系数热力图
DIVERGING_BLUE_GOLD = [[0, "#0b3d91"], [0.5, "#cfe0f5"], [1, "#e8a317"]]

# 图表类型 -> 是否需要 Y 轴（直方图、饼图只需一个变量）
CHART_TYPES_NO_Y = ("hist", "pie")


def show_plotly(fig, **kwargs):
    """全站统一的 Plotly 出图入口（所有页面都必须通过它出图）。

    两个关键作用：
    1. ``theme=None``：阻止 Streamlit 用自带浅色 "streamlit" 主题覆盖图表模板
       —— 否则夜间模式下即使图表设置了 plotly_dark，仍会被强制渲染成白底；
    2. 按当前白天 / 夜间主题统一纸张、绘图区、网格线与刻度文字颜色，
       让图表背景与页面融为一体，不再出现刺眼白块。
    """
    if st.session_state["app_theme_dark"]:
        # 夜间：纸张全透明融入深蓝黑页面，绘图区用深一档的蓝做出层次
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#0f2342",
            font=dict(color="#cfe0f5"),
            legend_bgcolor="rgba(14,33,64,0.75)",
        )
        fig.update_xaxes(gridcolor="#24426b", zerolinecolor="#3d5d85",
                         linecolor="#3d5d85", tickfont_color="#9fb8d8",
                         title_font_color="#cfe0f5")
        fig.update_yaxes(gridcolor="#24426b", zerolinecolor="#3d5d85",
                         linecolor="#3d5d85", tickfont_color="#9fb8d8",
                         title_font_color="#cfe0f5")
        fig.update_coloraxes(colorbar_bgcolor="rgba(0,0,0,0)",
                             colorbar_tickfont_color="#9fb8d8",
                             colorbar_title_font_color="#cfe0f5")
        fig.update_scenes(bgcolor="rgba(14,33,64,0.35)")
    else:
        # 白天：纸张透明，绘图区极浅蓝，呼应整体科技蓝配色
        fig.update_layout(
            paper_bgcolor="rgba(255,255,255,0)",
            plot_bgcolor="#f3f8ff",
            font=dict(color="#243b55"),
        )
        fig.update_xaxes(gridcolor="#e1ecfa", zerolinecolor="#bcd2ec",
                         linecolor="#9fb8d8", tickfont_color="#4a5a70",
                         title_font_color="#243b55")
        fig.update_yaxes(gridcolor="#e1ecfa", zerolinecolor="#bcd2ec",
                         linecolor="#9fb8d8", tickfont_color="#4a5a70",
                         title_font_color="#243b55")
        fig.update_coloraxes(colorbar_bgcolor="rgba(255,255,255,0)",
                             colorbar_tickfont_color="#4a5a70",
                             colorbar_title_font_color="#243b55")
    st.plotly_chart(fig, theme=None, **kwargs)


def build_figure(chart_type: str, data: pd.DataFrame, x_col: str, y_col, z_col,
                 color_col, nbins, lang: str):
    """按图表类型构建 Plotly 图表对象，构建失败时返回 None。

    把 10 种图表的构建逻辑集中在此函数中，避免页面主体代码过度嵌套。
    散点图自动叠加 OLS 趋势线、直方图自动叠加均值/中位数参考线。
    """
    t = TEXTS[lang]
    x_label = f"{t['axis_x_label']}: {x_col}"
    y_label = f"{t['axis_y_label']}: {y_col}"
    fig = None

    if chart_type == "bar":
        # 按 X 分组后对 Y 求均值（pandas groupby）：解决同一类别下多条记录的聚合问题
        plot_df = (
            data.groupby(x_col, as_index=False, dropna=False)[y_col]
            .mean()
            .sort_values(by=y_col, ascending=False)  # 柱体从高到低排列
        )
        fig = px.bar(
            plot_df, x=x_col, y=y_col,
            # 分组聚合后原有分组列已不存在，这里做一次存在性判断
            color=color_col if color_col in plot_df.columns else None,
            title=f"{t['bar_name']}: {x_col} vs {y_col}{t['mean_suffix']}",
            labels={x_col: x_label, y_col: y_label},
            color_discrete_sequence=COLOR_SEQUENCE,
        )

    elif chart_type == "line":
        # 同样按 X 分组求均值，再按 X 升序连接，体现“趋势”
        plot_df = (
            data.groupby(x_col, as_index=False, dropna=False)[y_col]
            .mean()
            .sort_values(by=x_col)
        )
        fig = px.line(
            plot_df, x=x_col, y=y_col, markers=True,
            color=color_col if color_col in plot_df.columns else None,
            title=f"{t['line_name']}: {x_col} vs {y_col}{t['mean_suffix']}",
            labels={x_col: x_label, y_col: y_label},
            color_discrete_sequence=COLOR_SEQUENCE_ALT,
        )

    elif chart_type == "area":
        # 面积图 = 折线图 + 填充色，适合表现累积/整体趋势
        plot_df = (
            data.groupby(x_col, as_index=False, dropna=False)[y_col]
            .mean()
            .sort_values(by=x_col)
        )
        fig = px.area(
            plot_df, x=x_col, y=y_col, markers=True,
            color=color_col if color_col in plot_df.columns else None,
            title=f"{t['area_name']}: {x_col} vs {y_col}{t['mean_suffix']}",
            labels={x_col: x_label, y_col: y_label},
            color_discrete_sequence=COLOR_SEQUENCE,
        )

    elif chart_type == "scatter":
        # 逐点绘制原始记录，观察两个变量的相关性
        fig = px.scatter(
            data, x=x_col, y=y_col, color=color_col,
            opacity=0.78,  # 半透明：点重叠时可看出密度
            title=f"{t['scatter_name']}: {x_col} vs {y_col}",
            labels={x_col: x_label, y_col: y_label},
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        # 两个字段均为数值时，用 numpy 一次最小二乘拟合，叠加趋势线（无需额外依赖）
        if (pd.api.types.is_numeric_dtype(data[x_col])
                and pd.api.types.is_numeric_dtype(data[y_col])):
            sub = data[[x_col, y_col]].dropna()
            if sub.shape[0] >= 2 and sub[x_col].nunique() >= 2:
                slope, intercept = np.polyfit(sub[x_col], sub[y_col], 1)
                xs = np.linspace(sub[x_col].min(), sub[x_col].max(), 50)
                fig.add_trace(
                    go.Scatter(
                        x=xs, y=slope * xs + intercept, mode="lines",
                        name=t["ols_label"].format(slope=f2(slope),
                                                   intercept=f2(intercept)),
                        line=dict(color="#f5b301", width=2.5, dash="dash"),
                        hovertemplate="x=%{x:.2f}<br>y=%{y:.2f}<extra></extra>",
                    )
                )

    elif chart_type == "scatter3d":
        # 3D 散点：同时观察三个数值变量的关系，可旋转查看
        fig = px.scatter_3d(
            data, x=x_col, y=y_col, z=z_col, color=color_col,
            opacity=0.8,
            title=f"{t['scatter3d_name']}: {x_col} / {y_col} / {z_col}",
            labels={x_col: x_label, y_col: y_label,
                    z_col: f"{t['chart_z']}: {z_col}"},
            color_discrete_sequence=COLOR_SEQUENCE,
        )

    elif chart_type == "hist":
        # 直方图：只看一个变量的频数分布，marginal 须线标出每个样本位置
        fig = px.histogram(
            data, x=x_col, color=color_col, nbins=nbins,
            title=f"{t['hist_name']}: {x_col}",
            labels={x_col: x_label},
            color_discrete_sequence=COLOR_SEQUENCE,
            marginal="rug",
        )
        # 数值字段才叠加均值 / 中位数参考线
        if pd.api.types.is_numeric_dtype(data[x_col]):
            add_dist_reference_lines(fig, data[x_col], t)

    elif chart_type == "box":
        # 箱线图：展示四分位数、中位数与离群点
        fig = px.box(
            data, x=x_col, y=y_col, color=color_col, points="outliers",
            title=f"{t['box_name']}: {y_col} ~ {x_col}",
            labels={x_col: x_label, y_col: y_label},
            color_discrete_sequence=COLOR_SEQUENCE,
        )

    elif chart_type == "violin":
        # 小提琴图：箱线图 + 密度曲线，能看到分布的具体形态
        fig = px.violin(
            data, x=x_col, y=y_col, color=color_col,
            box=True, points="outliers",
            title=f"{t['violin_name']}: {y_col} ~ {x_col}",
            labels={x_col: x_label, y_col: y_label},
            color_discrete_sequence=COLOR_SEQUENCE_ALT,
        )

    elif chart_type == "pie":
        # 饼图：先统计各类别记录数，再画占比环形图
        counts = data[x_col].value_counts().reset_index()
        counts.columns = [x_col, t["count_label"]]
        fig = px.pie(
            counts, names=x_col, values=t["count_label"], hole=0.45,
            title=f"{t['pie_name']}: {x_col}",
            color_discrete_sequence=COLOR_SEQUENCE,
        )

    elif chart_type == "density":
        # 密度热力图：用颜色深浅表示两个数值变量联合分布的密集程度
        fig = px.density_heatmap(
            data, x=x_col, y=y_col,
            color_continuous_scale=CONTINUOUS_SCALE,
            title=f"{t['density_name']}: {x_col} vs {y_col}",
            labels={x_col: x_label, y_col: y_label},
        )

    return fig


def recommend_corr_pair(data: pd.DataFrame, num_cols):
    """返回相关系数绝对值最大的两个数值字段名 (a, b)；不足两列时返回 None。"""
    if len(num_cols) < 2:
        return None
    corr = data[num_cols].corr(numeric_only=True)
    best_pair, best_abs = None, -1.0
    for i in range(len(num_cols)):
        for j in range(i + 1, len(num_cols)):
            value = corr.iloc[i, j]
            if pd.notna(value) and abs(value) > best_abs:
                best_abs, best_pair = abs(value), (num_cols[i], num_cols[j])
    return best_pair


def recommend_contrast_column(data: pd.DataFrame, num_cols, cat_col: str):
    """返回在指定类别字段上组间均值差异倍数最大的数值列名。

    用于故事线“类别差异”章的默认推荐字段；无法计算倍数时回退到第一个数值列。
    """
    best = None  # (ratio, col)
    for col in num_cols:
        grouped = data.groupby(cat_col, dropna=False)[col].mean().dropna()
        if grouped.shape[0] < 2:
            continue
        low_v = float(grouped.min())
        if low_v <= 0:  # 均值含非正数时倍数没有解释意义
            continue
        ratio = float(grouped.max()) / low_v
        if best is None or ratio > best[0]:
            best = (ratio, col)
    return best[1] if best is not None else num_cols[0]


def strongest_corr_finding(data: pd.DataFrame, num_cols, t: dict):
    """返回相关系数绝对值最大的一对数值字段的结论文字；不足两列时返回 None。"""
    best_pair = recommend_corr_pair(data, num_cols)
    if best_pair is None:
        return None
    a, b = best_pair
    r = float(data[[a, b]].corr(numeric_only=True).iloc[0, 1])
    return t["fd_corr"].format(
        a=a, b=b, r=f2(r), strength=correlation_strength(r, t),
    )


def group_contrast_finding(data: pd.DataFrame, num_cols, cat_cols, t: dict):
    """在第一个类别字段上，找出组间均值差异倍数最大的数值字段。"""
    if not cat_cols or not num_cols:
        return None
    cat = cat_cols[0]
    best = None  # (ratio, value_col, top_cat, top_val, bot_cat, bot_val)
    for col in num_cols:
        grouped = data.groupby(cat, dropna=False)[col].mean().dropna()
        if grouped.shape[0] < 2:
            continue
        low_v = float(grouped.min())
        if low_v <= 0:  # 均值含非正数时倍数没有解释意义，跳过
            continue
        ratio = float(grouped.max()) / low_v
        if best is None or ratio > best[0]:
            best = (ratio, col, grouped.idxmax(), float(grouped.max()),
                    grouped.idxmin(), low_v)
    if best is None:
        return None
    ratio, col, top_cat, top_v, bot_cat, bot_v = best
    return t["fd_group"].format(
        cat=cat, col=col, top=top_cat, bot=bot_cat,
        tv=f2(top_v), bv=f2(bot_v), ratio=f2(ratio),
    )


def cv_finding(data: pd.DataFrame, num_cols, t: dict):
    """返回变异系数最大的字段结论；均值为 0 无法计算时返回 None。"""
    best_col, best_cv = None, None
    for col in num_cols:
        mean_abs = abs(float(data[col].mean()))
        if mean_abs < 1e-9:
            continue
        cv = float(data[col].std()) / mean_abs * 100
        if best_cv is None or cv > best_cv:
            best_col, best_cv = col, cv
    if best_col is None:
        return None
    return t["fd_cv"].format(col=best_col, pct=f"{best_cv:.1f}%")


def build_key_findings(data: pd.DataFrame, num_cols, cat_cols,
                       missing_total: int, duplicate_total: int,
                       total_cells: int, t: dict):
    """汇总总览页顶部的“关键发现”卡片文案列表。"""
    findings = []
    corr_text = strongest_corr_finding(data, num_cols, t)
    if corr_text:
        findings.append(corr_text)
    contrast_text = group_contrast_finding(data, num_cols, cat_cols, t)
    if contrast_text:
        findings.append(contrast_text)
    cv_text = cv_finding(data, num_cols, t)
    if cv_text:
        findings.append(cv_text)
    # 数据质量一条：缺失 + 重复
    if missing_total == 0:
        missing_text = t["miss_none"]
    else:
        pct = f"{missing_total / total_cells * 100:.2f}%" if total_cells else "0.00%"
        missing_text = t["miss_some"].format(n=missing_total, pct=pct)
    dup_text = t["dup_none"] if duplicate_total == 0 else t["dup_some"].format(
        n=duplicate_total)
    findings.append(t["fd_quality"].format(missing_text=missing_text,
                                           dup_text=dup_text))
    return findings


# ---------------------------------------------------------------------
# 3. 侧边栏：语言切换 + 数据源选择
# ---------------------------------------------------------------------
with st.sidebar:
    # 语言选择放在侧边栏最顶部，切换后整页文案立即变化
    lang = st.radio(
        label="Language / 界面语言",
        options=["zh", "en"],
        format_func=lambda code: "中文" if code == "zh" else "English",
        horizontal=True,
    )
    t = TEXTS[lang]  # t("key") 不方便带参数，这里直接用字典取值：t["key"]

    # 白天 / 夜间模式：开关状态由 Streamlit 自动持久化，切换即整页重渲染
    st.toggle(t["theme_toggle"], key="app_theme_dark")

    st.divider()
    st.header(t["sidebar_header"])

    # 数据源二选一：内置数据 / 自己上传
    source = st.radio(
        label=t["sidebar_header"],
        options=["default", "upload"],
        format_func=lambda code: t["source_default"] if code == "default" else t["source_upload"],
        label_visibility="collapsed",  # 复用标题文字，隐藏重复的 label
    )

    df = None  # 主数据集，后续所有分析都基于它
    upload_key = ""

    if source == "upload":
        uploaded = st.file_uploader(
            label=t["upload_tip"], type=["csv"], accept_multiple_files=False
        )
        if uploaded is not None:
            try:
                # read() 读出文件字节；传入文件名是为了让缓存按文件区分
                df = load_uploaded_data(uploaded.read(), uploaded.name)
                upload_key = uploaded.name
                st.caption(f"{t['using_upload']}**{uploaded.name}**")
            except Exception:
                st.error(t["load_error"])
        else:
            # 还没选文件时，自动回退到默认数据集，保证页面始终有数据
            df = load_default_data()
            st.info(t["dataset_info"])
    else:
        df = load_default_data()
        st.caption(t["using_default"])

# 防御性处理：确保任何情况下 df 都是有效的 DataFrame
if df is None:
    df = load_default_data()

# 预先把列按类型分为两组，多个页面都会用到
all_columns = df.columns.tolist()
numeric_columns = df.select_dtypes(include="number").columns.tolist()
categorical_columns = [c for c in all_columns if c not in numeric_columns]

# 跨页面共享的总体指标（提升为全局，供概览/缺失/总览/故事线多个页面复用）
missing_total = int(df.isna().sum().sum())       # 全表缺失单元格数
duplicate_total = int(df.duplicated().sum())     # 重复行数
total_cells_all = df.shape[0] * df.shape[1]      # 单元格总数

# 当前主题对应的 Plotly 模板：夜间模式用深色模板，与页面背景融为一体
PLOTLY_TEMPLATE = "plotly_dark" if st.session_state["app_theme_dark"] else "plotly_white"

# ---------------------------------------------------------------------
# 4. 页面主标题（多页面应用中由每个页面函数调用，保证每页标题一致）
# ---------------------------------------------------------------------
def render_page_header() -> None:
    """在每个页面顶部渲染统一的渐变主标题与副标题。"""
    st.title(t["app_title"])
    st.caption(t["app_subtitle"])

# =====================================================================
# 5. 页面一：数据集概览（顶部导航第 1 项）
#    指标卡 + 字段类型占比图 + 内存占用图 + dtypes 表 + 前 5 行
# =====================================================================
def page_overview():
    render_page_header()
    # 5.1 顶部指标卡：st.metric 以大字号突出关键数字
    # （missing_total / duplicate_total 为跨页面共享的全局变量）

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric(t["metric_rows"], df.shape[0])
    col2.metric(t["metric_cols"], df.shape[1])
    col3.metric(t["metric_num"], len(numeric_columns))
    col4.metric(t["metric_cat"], len(categorical_columns))
    col5.metric(t["metric_missing"], missing_total)
    col6.metric(t["metric_dup"], duplicate_total)

    st.divider()

    # 5.2 pandas 元信息的可视化：类型构成环形图 + 各列内存占用条形图
    st.subheader(t["ov_viz_title"])
    ov_left, ov_right = st.columns(2)

    with ov_left:
        # 数值型 / 类别型列数构成（df.dtypes 的归类统计）
        dtype_counts = pd.Series(
            {t["kind_num"]: len(numeric_columns),
             t["kind_cat"]: len(categorical_columns)}
        )
        fig_dtype = px.pie(
            names=dtype_counts.index,
            values=dtype_counts.values,
            hole=0.5,
            title=t["ov_dtype_pie"],
            color=dtype_counts.index,
            color_discrete_map={t["kind_num"]: "#1c7ed6", t["kind_cat"]: "#f5b301"},
        )
        fig_dtype.update_layout(template=PLOTLY_TEMPLATE, height=360,
                                margin=dict(t=50))
        show_plotly(fig_dtype, width="stretch")

    with ov_right:
        # 各字段内存占用：df.memory_usage(deep=True)，横向条形从大到小
        # 按字段类型分类着色（蓝=数值列，金=类别列），避免连续色阶低端发白
        mem = df.memory_usage(deep=True, index=False).sort_values()
        mem_kinds = [dtype_kind_label(df[c].dtype, lang) for c in mem.index]
        fig_mem = px.bar(
            x=mem.values, y=mem.index, orientation="h",
            labels={"x": t["mem_bytes"], "y": t["col_name"], "color": t["col_kind"]},
            title=t["ov_memory"],
            color=mem_kinds,
            color_discrete_map={
                t["kind_num"]: "#1c7ed6",
                t["kind_cat"]: "#f5b301",
            },
        )
        fig_mem.update_layout(template=PLOTLY_TEMPLATE, height=360,
                              margin=dict(t=50), legend_title_text=t["col_kind"])
        show_plotly(fig_mem, width="stretch")

    st.divider()

    # 5.3 字段类型表：把 df.dtypes 整理成 DataFrame 展示
    st.subheader(t["dtype_title"])
    dtype_df = pd.DataFrame(
        {
            t["col_name"]: all_columns,
            t["col_dtype"]: [str(df[c].dtype) for c in all_columns],
            t["col_kind"]: [dtype_kind_label(df[c].dtype, lang) for c in all_columns],
        }
    )
    st.dataframe(dtype_df, width="stretch", hide_index=True)

    # 5.4 前 5 行速览
    st.subheader(t["head_title"])
    st.dataframe(df.head(), width="stretch")

# =====================================================================
# 6. 页面二：数据预览与筛选
#    全页只有一次筛选：数值列区间滑块 / 类别列多选，多条件“逻辑与”；
#    筛选结果 filtered_df 同时驱动预览表格、直方图与散点图
# =====================================================================
def page_preview():
    render_page_header()

    # =================================================================
    # 板块一：数据筛选 —— 本页唯一的筛选入口
    # 数值列 → 区间滑块；类别列 → 多选；多个条件“逻辑与”叠加
    # =================================================================
    st.subheader(t["filter_section_title"])
    condition_columns = st.multiselect(
        label=t["filter_cols_cond"], options=all_columns, key="filter_cond_cols"
    )

    # 从原始数据副本开始逐个条件收缩；本页表格与图表都只使用这份结果
    filtered_df = df.copy()

    # 每个被选中的列生成一个对应类型的输入控件
    for col in condition_columns:
        st.markdown(f"**`{col}`**")
        if pd.api.types.is_numeric_dtype(df[col]):
            # 数值型：最小值/最大值双端滑块做闭区间筛选（边界忽略缺失值）
            col_min = float(df[col].min())
            col_max = float(df[col].max())
            low, high = st.slider(
                label=f"{col} — {t['filter_num_tip']}",
                min_value=col_min,
                max_value=col_max,
                value=(col_min, col_max),  # 默认完整区间，等价于不过滤
                key=f"num_filter_{col}",
            )
            # 布尔索引：只保留区间内的行
            filtered_df = filtered_df[filtered_df[col].between(low, high)]
        else:
            # 类别/文本型：multiselect 勾选要保留的类别
            # dropna() 避免 NaN 出现在选项中；sort_values 让选项有序
            options = sorted(df[col].dropna().unique().tolist())
            picked = st.multiselect(
                label=f"{col} — {t['filter_cat_tip']}",
                options=options,
                default=options,  # 默认全选，等价于不过滤
                key=f"cat_filter_{col}",
            )
            if picked:
                filtered_df = filtered_df[filtered_df[col].isin(picked)]

    # 筛选前后样本量对比：每次调整条件，收缩效果立刻可见
    n_before, n_after = df.shape[0], filtered_df.shape[0]
    keep_ratio = n_after / n_before if n_before else 0.0
    fc1, fc2, fc3 = st.columns(3)
    fc1.metric(t["filter_before"], n_before)
    fc2.metric(t["filter_after"], n_after)
    fc3.metric(t["filter_keep_pct"], f"{keep_ratio * 100:.1f}%")
    st.progress(keep_ratio)
    if not condition_columns:
        st.caption(t["filter_no_cond_hint"].format(n=n_before))

    st.divider()

    # =================================================================
    # 板块二：筛选结果预览（只展示 filtered_df，不再有脱离筛选的表格）
    # =================================================================
    st.subheader(t["preview_section_title"])
    if filtered_df.empty:
        # 条件过严时给出友好提示，下载按钮一并禁用
        st.warning(t["filter_empty"])
        result_all = filtered_df
    else:
        # 展示列 / 行数 / 色阶三个控件收成一行，排版更紧凑
        pc_col, pr_col, ps_col = st.columns([2, 1.2, 1.3])
        with pc_col:
            # multiselect 留空时显示全部列
            selected_preview_cols = st.multiselect(
                label=t["preview_cols"],
                options=all_columns,
                default=all_columns,
                key="preview_cols",
            )
        with pr_col:
            # 行数上限随筛选结果动态收缩；结果不足 5 行时直接全部展示
            n_avail = filtered_df.shape[0]
            max_rows = min(100, n_avail)
            if n_avail > 5:
                n_rows = st.slider(
                    t["preview_rows"], min_value=5, max_value=max_rows,
                    value=min(20, max_rows), step=5,
                )
            else:
                n_rows = n_avail
        with ps_col:
            use_style = st.checkbox(t["preview_style"], value=True)

        view_cols = selected_preview_cols  # 留空时显示全部列
        result_all = filtered_df[view_cols] if view_cols else filtered_df
        preview_df = result_all.head(n_rows)
        st.caption(
            f"{t['preview_dim']} {preview_df.shape[0]} × {preview_df.shape[1]}"
            f"（{t['filter_after']} {n_after}）"
        )

        if use_style:
            # pandas Styler：数值列蓝白色阶 + 浮点两位小数，表格本身也是一种可视化
            float_cols = [
                c for c in preview_df.columns
                if pd.api.types.is_float_dtype(preview_df[c])
            ]
            if float_cols:
                styler = (
                    preview_df.style
                    .background_gradient(cmap="Blues", subset=float_cols)
                    .format({c: "{:,.2f}" for c in float_cols})
                )
                st.dataframe(styler, width="stretch", hide_index=True)
            else:
                st.dataframe(preview_df, width="stretch", hide_index=True)
        else:
            st.dataframe(preview_df, width="stretch", hide_index=True)

    # 导出当前筛选命中的全部记录（按所选列）
    st.download_button(
        label=t["download_filter"],
        data=make_download_csv(result_all),
        file_name="filtered.csv",
        mime="text/csv",
        disabled=filtered_df.empty,
    )

    st.divider()

    # =================================================================
    # 板块三：筛选结果图表 —— 直方图与散点图全部基于 filtered_df
    # 复用统一绘图函数：直方图自带均值/中位数参考线，散点自带 OLS 趋势线
    # =================================================================
    st.subheader(t["chart_section_title"])
    if not numeric_columns:
        st.info(t["filter_no_num"])
    elif filtered_df.empty:
        st.info(t["filter_chart_empty"])
    else:
        obs_col, sx_col, sy_col = st.columns(3)
        with obs_col:
            observe_col = st.selectbox(
                t["filter_obs"], options=numeric_columns, key="filter_obs_col"
            )
        with sx_col:
            scatter_x = st.selectbox(
                t["filter_scatter_x"], options=numeric_columns,
                key="filter_scatter_x_col",
            )
        with sy_col:
            sy_index = min(1, len(numeric_columns) - 1)
            scatter_y = st.selectbox(
                t["filter_scatter_y"], options=numeric_columns, index=sy_index,
                key="filter_scatter_y_col",
            )

        # 单变量分布直方图（筛选后样本非空才绘制）
        if filtered_df[observe_col].dropna().shape[0] > 0:
            fig_filter_hist = build_figure(
                "hist", filtered_df, observe_col, None, None, None, 30, lang
            )
            show_plotly(fig_filter_hist, width="stretch")
            st.info(
                f"**{t['auto_insight']}**\n\n"
                + build_insight("hist", filtered_df, observe_col, None, lang)
            )

        # 双变量散点图（至少 2 个有效点且 X 有变化才绘制）
        scatter_sub = filtered_df[[scatter_x, scatter_y]].dropna()
        if scatter_sub.shape[0] >= 2 and scatter_sub[scatter_x].nunique() >= 2:
            fig_filter_scatter = build_figure(
                "scatter", filtered_df, scatter_x, scatter_y,
                None, None, None, lang
            )
            show_plotly(fig_filter_scatter, width="stretch")
            st.info(
                f"**{t['auto_insight']}**\n\n"
                + build_insight(
                    "scatter", filtered_df, scatter_x, scatter_y, lang
                )
            )

# =====================================================================
# 8. 页面四：统计描述 df.describe()
#    色阶统计表 + 对应箱线图 + 离散程度自动结论，三者互相印证
# =====================================================================
def page_describe():
    render_page_header()
    st.caption(t["desc_help"])

    # 8.1 数值型字段：count/mean/std/min/分位数/max（按统计量分列做色阶）
    st.subheader(t["desc_num_title"])
    if numeric_columns:
        desc_num = df[numeric_columns].describe().T
        # .T 后每行一个字段、每列一个统计量；按列上色 = 同一统计量下跨字段对比
        st.dataframe(
            desc_num.style.format("{:,.2f}").background_gradient(cmap="Blues"),
            width="stretch",
        )

        # 8.2 与统计表一一对应的箱线图：中位数/四分位数/离群点直接可见
        st.subheader(t["desc_box_title"])
        melted = df[numeric_columns].melt(
            var_name="__field", value_name="__value"
        )
        fig_desc_box = px.box(
            melted, x="__field", y="__value", color="__field",
            points="outliers", color_discrete_sequence=COLOR_SEQUENCE,
        )
        fig_desc_box.update_layout(
            template=PLOTLY_TEMPLATE, height=430,
            xaxis_title=t["col_name"], yaxis_title="",
            margin=dict(t=50), showlegend=False,
        )
        show_plotly(fig_desc_box, width="stretch")

        # 8.3 离散程度自动解读：标准差（绝对波动）+ 变异系数（相对波动）
        st.subheader(t["desc_spread_title"])
        std_series = df[numeric_columns].std()
        std_col = std_series.idxmax()
        st.info(t["desc_spread_std"].format(col=std_col, v=f2(std_series.max())))
        cv_text = cv_finding(df, numeric_columns, t)
        if cv_text:
            st.info(cv_text)
    else:
        st.info(t["desc_no_num"])

    # 8.4 类别型字段：count/unique/top/freq（没有类别列时给提示）
    st.subheader(t["desc_cat_title"])
    if categorical_columns:
        desc_cat = df[categorical_columns].describe().T
        grad_subset = [c for c in ("unique", "freq") if c in desc_cat.columns]
        st.dataframe(
            desc_cat.style.background_gradient(cmap="Blues", subset=grad_subset),
            width="stretch",
        )
    else:
        st.info(t["desc_no_cat"])

    # =================================================================
    # 同页第二板块：缺失值与重复行检测（原独立页面合并进“统计与数据质量”）
    # 指标 + 率色阶表 + 柱状图 + 缺失位置矩阵；
    # 可临时注入缺失值演示；底部展示重复行明细
    # =================================================================
    st.divider()
    # 9.1 演示开关：随机置空约 6% 单元格，仅本页生效，不改原始数据
    inject_missing = st.checkbox(t["miss_inject"], value=False)
    if inject_missing:
        miss_work_df = df.copy()
        rng = np.random.default_rng(7)  # 固定随机种子，每次演示结果一致
        inject_mask = rng.random(miss_work_df.shape) < 0.06
        miss_work_df = miss_work_df.mask(inject_mask)
        st.caption(t["miss_inject_tip"])
    else:
        miss_work_df = df

    total_cells = miss_work_df.shape[0] * miss_work_df.shape[1]
    page_missing_total = int(miss_work_df.isna().sum().sum())
    missing_ratio = (page_missing_total / total_cells * 100) if total_cells else 0.0

    # 9.2 三个总体指标
    st.subheader(t["miss_summary"])
    c1, c2, c3 = st.columns(3)
    c1.metric(t["miss_total_cells"], total_cells)
    c2.metric(t["miss_total_missing"], page_missing_total)
    c3.metric(t["miss_ratio"], f"{missing_ratio:.2f}%")

    # 9.3 逐字段明细表：缺失数量 + 缺失比例（数值列，供蓝色色阶使用）
    st.subheader(t["miss_table_title"])
    miss_df = pd.DataFrame(
        {
            t["miss_col"]: all_columns,
            t["miss_count"]: [int(miss_work_df[c].isna().sum()) for c in all_columns],
            t["miss_pct"]: [
                float(miss_work_df[c].isna().sum()) / miss_work_df.shape[0] * 100
                if miss_work_df.shape[0] else 0.0
                for c in all_columns
            ],
        }
    )
    miss_styler = (
        miss_df.style
        .format({t["miss_pct"]: lambda v: f"{v:.2f}%"})
        .background_gradient(cmap="Blues",
                             subset=[t["miss_count"], t["miss_pct"]])
    )
    st.dataframe(miss_styler, width="stretch", hide_index=True)

    if page_missing_total == 0:
        # 数据完整（且未注入演示缺失）时显示成功提示
        st.success(t["miss_clean"])
    else:
        # 9.4 各列缺失数量柱状图（只画存在缺失的列）
        miss_plot_df = miss_df[miss_df[t["miss_count"]] > 0]
        # 实心科技金柱体：缺失数较少时也清晰可见（连续色阶低端会发白）
        fig_miss = px.bar(
            miss_plot_df,
            x=t["miss_col"],
            y=t["miss_count"],
            title=t["miss_chart_title"],
            color_discrete_sequence=["#f5b301"],
        )
        fig_miss.update_traces(
            marker=dict(line=dict(color="#c79100", width=1.2)),
            text=miss_plot_df[t["miss_count"]],
            textposition="outside",
        )
        fig_miss.update_layout(template=PLOTLY_TEMPLATE, margin=dict(t=50))
        show_plotly(fig_miss, width="stretch")

        # 9.5 缺失位置矩阵：missingno 风格，金色格子标出缺失发生的行列位置
        st.subheader(t["miss_matrix_title"])
        na_matrix = miss_work_df.isna()
        if na_matrix.shape[0] > 400:
            na_matrix = na_matrix.sample(n=400, random_state=7)
            st.caption(t["miss_matrix_sample"])
        fig_na = px.imshow(
            na_matrix,
            color_continuous_scale=(["#1d3a63", "#f5b301"]
                                    if st.session_state["app_theme_dark"]
                                    else ["#90c2ff", "#f5b301"]),
            zmin=0, zmax=1, aspect="auto",
        )
        fig_na.update_layout(
            template=PLOTLY_TEMPLATE, height=520,
            xaxis_title=t["col_name"], yaxis_title="",
            margin=dict(t=50), coloraxis_showscale=False,
        )
        show_plotly(fig_na, width="stretch")

    st.divider()

    # 9.6 重复行检测（始终基于原始数据，与缺失注入无关）
    st.subheader(t["dup_title"])
    if duplicate_total == 0:
        st.success(t["dup_clean"])
    else:
        st.markdown(t["dup_found"].format(n=duplicate_total))
        st.subheader(t["dup_detail_title"])
        st.dataframe(df[df.duplicated(keep=False)], width="stretch")

# =====================================================================
# 10. 页面六：分组聚合（groupby / pivot_table）
#     一维分组聚合：表 + 柱状图；二维透视：色阶表 + 热力图
# =====================================================================
def page_group():
    render_page_header()
    st.caption(t["grp_intro"])

    if not numeric_columns:
        st.info(t["no_numeric_cols"])
    else:
        g_left, g_right = st.columns(2)
        with g_left:
            # 分组列：优先类别字段，但允许选任意列
            default_group_index = (
                all_columns.index(categorical_columns[0])
                if categorical_columns else 0
            )
            group_col = st.selectbox(
                t["grp_by"], options=all_columns,
                index=default_group_index, key="grp_by_col",
            )
            agg_func = st.selectbox(
                t["grp_agg"], options=AGG_OPTIONS,
                format_func=lambda code: t[AGG_LABEL_KEY[code]],
                key="grp_agg_func",
            )
        with g_right:
            value_col = st.selectbox(
                t["grp_val"], options=numeric_columns, key="grp_val_col"
            )
            # 透视列只能选与分组列不同的其他类别字段
            pivot_candidates = [c for c in categorical_columns if c != group_col]
            pivot_col = st.selectbox(
                t["grp_pivot"],
                options=[None] + pivot_candidates,
                format_func=lambda c: t["none"] if c is None else c,
                key="grp_pivot_col",
            )

        agg_label = t[AGG_LABEL_KEY[agg_func]]

        if pivot_col is None:
            # ---- 一维 groupby：分组 -> 选定聚合函数 ----
            agg_df = (
                df.groupby(group_col, dropna=False)[value_col]
                .agg(agg_func)
                .reset_index()
                .sort_values(by=value_col, ascending=False)
            )
            if agg_df.empty:
                st.warning(t["grp_empty"])
            else:
                st.subheader(t["grp_table_title"])
                st.dataframe(
                    agg_df.style
                    .format({value_col: "{:,.2f}"})
                    .bar(subset=[value_col], color="#74c0fc"),
                    width="stretch",
                    hide_index=True,
                )

                fig_grp = px.bar(
                    agg_df, x=group_col, y=value_col,
                    color=group_col,
                    color_discrete_sequence=COLOR_SEQUENCE,
                    title=f"{group_col} → {value_col}（{agg_label}）",
                )
                fig_grp.update_layout(template=PLOTLY_TEMPLATE, height=440,
                                      margin=dict(t=50), showlegend=False)
                show_plotly(fig_grp, width="stretch")

                # 自动结论：最高组 / 最低组
                top_row, bot_row = agg_df.iloc[0], agg_df.iloc[-1]
                st.info(
                    t["grp_insight_top"].format(
                        top=top_row[group_col], bot=bot_row[group_col],
                        col=value_col, agg=agg_label,
                        tv=f2(top_row[value_col]), bv=f2(bot_row[value_col]),
                    )
                )
        else:
            # ---- 二维 pivot_table：行=分组列，列=透视列，值=聚合结果 ----
            pivot_df = df.pivot_table(
                index=group_col, columns=pivot_col, values=value_col,
                aggfunc=agg_func,
            )
            if pivot_df.empty:
                st.warning(t["grp_empty"])
            else:
                st.subheader(t["grp_table_title"])
                st.dataframe(
                    pivot_df.style
                    .format("{:,.2f}")
                    .background_gradient(cmap="Blues"),
                    width="stretch",
                )

                st.subheader(t["grp_heat_title"])
                fig_pivot = px.imshow(
                    pivot_df, text_auto=".2f", aspect="auto",
                    # 自定义蓝色三段板：最低值即为可见淡蓝，不会像 Blues 低端近白
                    color_continuous_scale=[
                        (0.0, "#dbeafe"), (0.5, "#74c0fc"), (1.0, "#08306b")],
                    labels=dict(x=pivot_col, y=group_col, color=agg_label),
                )
                fig_pivot.update_layout(template=PLOTLY_TEMPLATE,
                                        height=max(360, 55 * len(pivot_df.index)),
                                        margin=dict(t=50))
                show_plotly(fig_pivot, width="stretch")

                # 自动结论：整张透视表中数值最高的组合
                stacked = pivot_df.stack().dropna()
                if not stacked.empty:
                    (top_a, top_b), top_v = stacked.idxmax(), float(stacked.max())
                    st.info(
                        t["grp_insight_pivot"].format(
                            by=group_col, pivot=pivot_col, agg=agg_label,
                            col=value_col, a=top_a, b=top_b, v=f2(top_v),
                        )
                    )

# =====================================================================
# 11. 页面七：Plotly 交互式可视化（本作业的重点模块）
#     三种分析方式：
#       数据故事线：分布→构成→差异→关系→小结，章节式引导分析叙事
#       分析问题向导：选问题自动出图；自由作图：10 种图表任意搭配
#     所有图表配统计标注，并在图下方给出自动结论文字
# =====================================================================
def page_chart():
    render_page_header()
    # 11.0 分析方式：故事线（默认）/ 问题向导 / 自由作图
    chart_mode = st.radio(
        label=t["chart_mode"],
        options=["story", "wizard", "free"],
        format_func=lambda code: {
            "story": t["mode_story"],
            "wizard": t["mode_wizard"],
            "free": t["mode_free"],
        }[code],
        horizontal=True,
        key="chart_mode",
    )

    def _style_story_fig(fig, height: int = 500):
        """故事线图表的统一样式：白底、高饱和配色、留白适合投影截图。"""
        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            height=height,
            colorway=COLOR_SEQUENCE,
            font=dict(size=13),
            title_font=dict(size=18),
            margin=dict(t=70, l=50, r=30, b=50),
        )
        return fig

    if chart_mode == "story":
        # -------------------------------------------------------------
        # 11.1 数据故事线：按经典分析顺序一章一章走，逻辑连贯
        # -------------------------------------------------------------
        st.caption(t["story_intro"])

        # 根据当前数据集具备的字段类型，动态生成可走的章节
        story_steps = []
        if numeric_columns:
            story_steps.append(("dist", "story_s_dist"))
        if categorical_columns:
            story_steps.append(("share", "story_s_share"))
        if numeric_columns and categorical_columns:
            story_steps.append(("diff", "story_s_diff"))
        if len(numeric_columns) >= 2:
            story_steps.append(("relation", "story_s_relation"))
        story_steps.append(("summary", "story_s_summary"))

        # 章节进度保存在 session_state，刷新页面后仍停留在当前章
        if "story_step" not in st.session_state:
            st.session_state.story_step = 0
        # 数据集切换导致章节数变化时做边界保护
        st.session_state.story_step = min(
            int(st.session_state.story_step), len(story_steps) - 1
        )
        cur = st.session_state.story_step
        step_key = story_steps[cur][0]

        # 顶部章节导航条：当前章高亮，点击章节名可直接跳转
        nav_cols = st.columns(len(story_steps))
        for i, (skey, stitle_key) in enumerate(story_steps):
            if nav_cols[i].button(
                t[stitle_key],
                key=f"story_nav_{skey}",
                use_container_width=True,
                type="primary" if i == cur else "secondary",
            ):
                st.session_state.story_step = i
                st.rerun()

        st.progress((cur + 1) / len(story_steps))
        st.subheader(t[story_steps[cur][1]])
        st.caption(t[f"story_g_{step_key}"])

        # ---- 第一章：单变量分布（直方图 + 均值/中位数参考线）----
        if step_key == "dist":
            pick_col, _ = st.columns([1, 3])
            dist_field = pick_col.selectbox(
                t["wizard_num_x"], options=numeric_columns,
                key="story_dist_field",
            )
            fig_story = build_figure(
                "hist", df, dist_field, None, None, None, 25, lang
            )
            show_plotly(_style_story_fig(fig_story, 520), width="stretch")
            st.info(
                f"**{t['auto_insight']}**\n\n"
                + build_insight("hist", df, dist_field, None, lang)
            )

        # ---- 第二章：类别构成（占比环形图）----
        elif step_key == "share":
            pick_col, _ = st.columns([1, 3])
            share_field = pick_col.selectbox(
                t["wizard_cat"], options=categorical_columns,
                key="story_share_field",
            )
            fig_story = build_figure(
                "pie", df, share_field, None, None, None, None, lang
            )
            show_plotly(_style_story_fig(fig_story, 500), width="stretch")
            st.info(
                f"**{t['auto_insight']}**\n\n"
                + build_insight("pie", df, share_field, None, lang)
            )

        # ---- 第三章：类别差异（组均值柱状图 + 分组箱线图）----
        elif step_key == "diff":
            c_cat, c_val, _ = st.columns([1, 1, 2])
            diff_cat = c_cat.selectbox(
                t["wizard_cat"], options=categorical_columns,
                key="story_diff_cat",
            )
            # 默认推荐“组间均值差异倍数最大”的数值字段，引导最有信息量的对比
            reco_val = recommend_contrast_column(
                df, numeric_columns, diff_cat
            )
            diff_val = c_val.selectbox(
                t["wizard_num"], options=numeric_columns,
                index=numeric_columns.index(reco_val),
                key="story_diff_val",
            )
            fig_bar = build_figure(
                "bar", df, diff_cat, diff_val, None, None, None, lang
            )
            fig_box = build_figure(
                "box", df, diff_cat, diff_val, None, diff_cat, None, lang
            )
            chart_l, chart_r = st.columns(2)
            with chart_l:
                show_plotly(_style_story_fig(fig_bar, 440), width="stretch")
            with chart_r:
                show_plotly(_style_story_fig(fig_box, 440), width="stretch")
            st.info(
                f"**{t['auto_insight']}**\n\n"
                + build_insight("bar", df, diff_cat, diff_val, lang)
            )
            box_insight = build_insight("box", df, diff_cat, diff_val, lang)
            if box_insight:
                st.info(box_insight)

        # ---- 第四章：变量关系（散点图 + OLS 趋势线 + 相关系数）----
        elif step_key == "relation":
            # 默认推荐全表相关性最强的一对数值字段
            pair = recommend_corr_pair(df, numeric_columns)
            c_x, c_y, _ = st.columns([1, 1, 2])
            rel_x = c_x.selectbox(
                t["wizard_num_x"], options=numeric_columns,
                index=numeric_columns.index(pair[0]),
                key="story_rel_x",
            )
            rel_y = c_y.selectbox(
                t["wizard_num"], options=numeric_columns,
                index=numeric_columns.index(pair[1]),
                key="story_rel_y",
            )
            if rel_x == rel_y:
                st.warning(t["chart_same_axis"])
            else:
                rel_color = categorical_columns[0] if categorical_columns else None
                fig_story = build_figure(
                    "scatter", df, rel_x, rel_y, None, rel_color, None, lang
                )
                show_plotly(_style_story_fig(fig_story, 520), width="stretch")
                st.info(
                    f"**{t['auto_insight']}**\n\n"
                    + build_insight("scatter", df, rel_x, rel_y, lang)
                )

        # ---- 第五章：故事小结（自动汇总各章关键数字）----
        elif step_key == "summary":
            total_cells_story = df.shape[0] * df.shape[1]
            findings = build_key_findings(
                df, numeric_columns, categorical_columns,
                missing_total, duplicate_total, total_cells_story, t,
            )
            for idx, finding in enumerate(findings, start=1):
                st.info(f"**{idx}.** {finding}")
            st.caption(t["story_end_tip"])

        # 底部章节导航：上一章 / 进度 / 下一章（末章右侧变为重新开始）
        st.divider()
        nav_l, nav_m, nav_r = st.columns([1, 2, 1])
        if cur > 0:
            if nav_l.button(t["story_prev"], key="story_prev_btn"):
                st.session_state.story_step -= 1
                st.rerun()
        # 进度文字：水平居中 + 与两侧按钮垂直对齐（caption 默认左对齐且基线偏高）
        nav_m.markdown(
            "<div style='text-align:center;padding-top:11px;"
            "font-size:15px;font-weight:600;color:#8a9bb4;'>"
            + t["story_progress"].format(cur=cur + 1, total=len(story_steps))
            + "</div>",
            unsafe_allow_html=True,
        )
        if step_key == "summary":
            if nav_r.button(t["story_restart"], key="story_restart_btn"):
                st.session_state.story_step = 0
                st.rerun()
        else:
            if nav_r.button(t["story_next"], key="story_next_btn",
                            type="primary"):
                st.session_state.story_step += 1
                st.rerun()

    else:
        # 左列放控件（约 1/3 宽），右列放图表（约 2/3 宽），形成“操作台 + 画布”布局
        control_col, chart_col = st.columns([1, 2])

        # 两种模式下最终都产出这组绘图参数
        chart_type = None
        x_col = y_col = z_col = color_col = None
        nbins = None
        error_key = None

        with control_col:
            if chart_mode == "wizard":
                # ---- 问题向导：选问题 -> 只暴露该问题必需的字段 ----
                question = st.selectbox(
                    label=t["wizard_q"],
                    options=list(WIZARD_MAP.keys()),
                    format_func=lambda code: t[f"q_{code}"],
                )
                chart_type = WIZARD_MAP[question]

                if chart_type in ("bar", "box"):
                    if not categorical_columns:
                        error_key = "wizard_need_cat"
                    elif not numeric_columns:
                        error_key = "wizard_need_num"
                    else:
                        x_col = st.selectbox(t["wizard_cat"], options=categorical_columns,
                                            key="wiz_x_cat")
                        y_col = st.selectbox(t["wizard_num"], options=numeric_columns,
                                            key="wiz_y_num")
                        # 箱线图按类别着色，柱状图保持统一配色
                        color_col = x_col if chart_type == "box" else None

                elif chart_type == "scatter":
                    if len(numeric_columns) < 2:
                        error_key = "wizard_need_two_num"
                    else:
                        x_col = st.selectbox(t["wizard_num_x"], options=numeric_columns,
                                            key="wiz_scatter_x")
                        y_col = st.selectbox(
                            t["wizard_num"], options=numeric_columns,
                            index=min(2, len(numeric_columns) - 1),
                            key="wiz_scatter_y",
                        )
                        if x_col == y_col:
                            error_key = "chart_same_axis"
                        # 若存在类别字段，散点默认按类别着色，便于看出分组聚簇
                        color_col = categorical_columns[0] if categorical_columns else None
                        nbins = None

                elif chart_type == "hist":
                    if not numeric_columns:
                        error_key = "wizard_need_num"
                    else:
                        x_col = st.selectbox(t["wizard_num_x"], options=numeric_columns,
                                            key="wiz_hist_x")
                        nbins = st.slider(t["chart_nbins"], 5, 80, value=20, step=5)

                elif chart_type == "pie":
                    if not categorical_columns:
                        error_key = "wizard_need_cat"
                    else:
                        x_col = st.selectbox(t["wizard_cat"], options=categorical_columns,
                                            key="wiz_pie_x")

            else:
                # ---- 自由作图：原有的 10 种图表与 X/Y/Z/颜色自由选择 ----
                chart_type = st.selectbox(
                    label=t["chart_type"],
                    options=[
                        "bar", "line", "area", "scatter", "scatter3d",
                        "hist", "box", "violin", "pie", "density",
                    ],
                    format_func=lambda code: {
                        "bar": t["chart_bar"],
                        "line": t["chart_line"],
                        "area": t["chart_area"],
                        "scatter": t["chart_scatter"],
                        "scatter3d": t["chart_scatter3d"],
                        "hist": t["chart_hist"],
                        "box": t["chart_box"],
                        "violin": t["chart_violin"],
                        "pie": t["chart_pie"],
                        "density": t["chart_density"],
                    }[code],
                )

                # 默认把第一个类别字段作为 X 轴（如鸢尾花的 species），
                # 保证打开页面时柱状图默认可用，且不会与 Y 轴默认列重复
                default_x_index = (
                    all_columns.index(categorical_columns[0]) if categorical_columns else 0
                )
                x_col = st.selectbox(
                    label=t["chart_x"],
                    options=all_columns,
                    index=default_x_index,
                    key="chart_x",
                )

                # 直方图 / 饼图只需要一个变量，因此不显示 Y 轴选择
                if chart_type not in CHART_TYPES_NO_Y:
                    if numeric_columns:
                        y_col = st.selectbox(
                            label=t["chart_y"], options=numeric_columns, key="chart_y"
                        )
                    else:
                        st.warning(t["no_numeric_cols"])

                # 仅 3D 散点图需要第三个数值字段
                if chart_type == "scatter3d":
                    if len(numeric_columns) >= 3:
                        z_col = st.selectbox(
                            label=t["chart_z"],
                            options=numeric_columns,
                            index=2,  # 默认第 3 个数值字段，避免与 X / Y 默认选择重复
                            key="chart_z",
                        )
                    else:
                        st.warning(t["no_numeric_cols"])

                # 分组着色（可选）：在选项前追加“无”
                color_col = st.selectbox(
                    label=t["chart_color"],
                    options=[None] + all_columns,
                    format_func=lambda c: t["none"] if c is None else c,
                    key="chart_color",
                )

                # 直方图专属参数：分箱数量
                if chart_type == "hist":
                    nbins = st.slider(t["chart_nbins"], 5, 80, value=20, step=5)

                # 按图表类型给出对应的操作提示
                tip_map = {
                    "bar": t["chart_tip"],
                    "line": t["chart_tip"],
                    "area": t["chart_tip"],
                    "scatter": t["chart_x_num_warn"],
                    "scatter3d": t["chart_scatter3d_tip"],
                    "pie": t["chart_pie_tip"],
                    "density": t["chart_density_tip"],
                }
                st.caption(tip_map.get(chart_type, t["chart_generic_tip"]))

                # 自由作图模式下的参数校验（向导模式已在分支内完成校验）
                if chart_type in ("bar", "line", "area", "scatter", "box", "violin"):
                    if y_col is None:
                        error_key = "no_numeric_cols"
                    elif x_col == y_col:
                        error_key = "chart_same_axis"
                elif chart_type == "scatter3d":
                    if (z_col is None or x_col not in numeric_columns
                            or y_col not in numeric_columns):
                        error_key = "chart_3d_numeric"
                    elif len({x_col, y_col, z_col}) < 3:
                        error_key = "chart_same_axis"
                elif chart_type == "density":
                    if y_col is None or x_col not in numeric_columns:
                        error_key = "chart_density_numeric"
                    elif x_col == y_col:
                        error_key = "chart_same_axis"

        with chart_col:
            if error_key:
                st.warning(t[error_key])
            else:
                fig = build_figure(
                    chart_type, df, x_col, y_col, z_col, color_col, nbins, lang
                )
                if fig is not None:
                    # 统一白色底 + 鲜明配色，保证投影与截图时对比度足够
                    fig.update_layout(
                        template=PLOTLY_TEMPLATE,
                        height=560,
                        colorway=COLOR_SEQUENCE,
                        font=dict(size=13),
                        title_font=dict(size=18),
                        margin=dict(t=70, l=50, r=30, b=50),
                    )
                    st.subheader(t["chart_render"])
                    show_plotly(fig, width="stretch")

                    # 图下方给出由 Pandas 计算的自动结论，让“图”回答具体问题
                    insight = build_insight(chart_type, df, x_col, y_col, lang)
                    if insight:
                        st.info(f"**{t['auto_insight']}**\n\n{insight}")

# ---------------------------------------------------------------------
# 13. 顶部导航栏（st.navigation, position="top"）
#     5 个页面以顶部标签形式切换；页面函数共享同一次运行中的
#     df / t / lang / PLOTLY_TEMPLATE 等全局状态
#     （预览+筛选、统计描述+缺失重复已分别合并；可视化总览已下线）
# ---------------------------------------------------------------------
navigation = st.navigation(
    [
        st.Page(page_overview, title=t["tab_overview"],
                icon=":material/monitoring:", url_path="overview"),
        st.Page(page_preview, title=t["tab_preview"],
                icon=":material/table_chart:", url_path="preview"),
        st.Page(page_describe, title=t["tab_describe"],
                icon=":material/query_stats:", url_path="describe"),
        st.Page(page_group, title=t["tab_group"],
                icon=":material/pivot_table_chart:", url_path="group"),
        st.Page(page_chart, title=t["tab_chart"],
                icon=":material/insights:", url_path="chart"),
    ],
    position="top",
)
navigation.run()
