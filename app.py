# -*- coding: utf-8 -*-
"""
=====================================================================
基于 Streamlit + Pandas + Plotly 的数据分析可视化网站
课程：可视化导论 课程作业
---------------------------------------------------------------------
功能模块：
  1. 数据加载：内置鸢尾花默认数据集 + 用户上传 CSV
  2. Pandas 分析：表格预览 / 数据集概览 / 统计描述 / 多列筛选 / 缺失值检测
  3. Plotly 交互式可视化（共 10 种图表，X / Y / Z 轴自由选择）：
     柱状图 / 折线图 / 面积图 / 散点图 / 3D 散点图 /
     直方图 / 箱线图 / 小提琴图 / 饼图 / 密度热力图
  4. 可视化总览：无需手动配置，自动生成相关系数热力图、分布直方图网格、
     分组箱线图、散点矩阵、类别占比环形图，一次看清数据全貌
  5. 侧边栏中文 / 英文一键切换，页面所有文字一一对应
作者：（请在此处填写姓名学号）
=====================================================================
"""

from pathlib import Path  # 路径处理，跨平台兼容（Windows / macOS / Linux）

import pandas as pd      # Pandas：数据分析核心库，DataFrame 数据结构
import plotly.express as px  # Plotly Express：高层 API，一行代码生成交互式图表
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
# 0.1 页面视觉美化：注入一段 CSS，让标题、指标卡、标签页色彩更鲜明
#     （使用 data-testid 选择器，比 Streamlit 随机类名稳定）
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* 主标题：彩色渐变文字，作为整页的视觉焦点 */
    [data-testid="stAppViewContainer"] h1 {
        background: linear-gradient(90deg, #ff4d6d, #ff922b, #51cf66, #4dabf7, #9775fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: 1px;
    }
    /* 指标卡：浅蓝渐变底 + 左侧彩条 + 阴影，让关键数字更醒目 */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #eef3ff 100%);
        border-left: 6px solid #4dabf7;
        border-radius: 12px;
        padding: 12px 16px;
        box-shadow: 0 2px 10px rgba(77, 171, 247, 0.18);
    }
    [data-testid="stMetricValue"] { color: #1c7ed6; font-weight: 800; }
    /* 标签页：加大间距，选中项加彩色文字与下划线 */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 14px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #1c7ed6 !important;
        border-bottom: 3px solid #1c7ed6;
    }
    /* 侧边栏标题配色 */
    [data-testid="stSidebar"] h2 { color: #1c7ed6; }
    </style>
    """,
    unsafe_allow_html=True,
)

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
        "none": "无（不分组）",
        # ---- 侧边栏：数据源 ----
        "sidebar_header": "数据源",
        "source_default": "内置鸢尾花数据集",
        "source_upload": "上传我的 CSV 文件",
        "upload_tip": "选择一个 CSV 文件（UTF-8 编码，第一行为表头）",
        "using_default": "当前使用：内置鸢尾花数据集（150 条记录）",
        "using_upload": "当前使用上传文件：",
        "dataset_info": "打开网页会自动加载默认数据；切换上方选项即可分析自己的 CSV 文件。",
        "load_error": "文件读取失败，请确认是标准 CSV 文件（建议 UTF-8 编码）。",
        # ---- 标签页 ----
        "tab_overview": "数据集概览",
        "tab_preview": "数据表格预览",
        "tab_filter": "多列筛选",
        "tab_describe": "统计描述",
        "tab_missing": "缺失值检测",
        "tab_chart": "可视化图表",
        # ---- 概览 ----
        "metric_rows": "行数（记录数）",
        "metric_cols": "列数（字段数）",
        "metric_num": "数值型列",
        "metric_cat": "文本/类别型列",
        "metric_missing": "缺失单元格",
        "metric_dup": "重复行",
        "dtype_title": "字段类型一览（df.dtypes）",
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
        "download_preview": "下载当前视图为 CSV",
        # ---- 筛选 ----
        "filter_cols_show": "第 1 步：选择需要展示的列",
        "filter_cols_cond": "第 2 步：选择需要添加筛选条件的列（可多选）",
        "filter_result_title": "筛选结果",
        "filter_result_dim": "符合条件的记录：",
        "filter_empty": "没有符合筛选条件的记录，请放宽条件后重试。",
        "download_filter": "下载筛选结果为 CSV",
        "filter_num_tip": "数值范围（拖动滑块，闭区间）",
        "filter_cat_tip": "勾选要保留的类别（不选视为全部保留）",
        # ---- 统计描述 ----
        "desc_num_title": "数值型字段统计描述（df.describe()）",
        "desc_cat_title": "类别型字段统计描述",
        "desc_no_cat": "数据集中没有类别型字段。",
        "desc_help": "count=非空个数 ｜ mean=均值 ｜ std=标准差 ｜ min=最小值 ｜ "
                     "25%/50%/75%=分位数 ｜ max=最大值",
        # ---- 缺失值 ----
        "miss_summary": "缺失值总览",
        "miss_total_cells": "数据单元格总数",
        "miss_total_missing": "缺失值总数",
        "miss_ratio": "整体缺失率",
        "miss_table_title": "各字段缺失值明细（df.isna()）",
        "miss_col": "字段名",
        "miss_count": "缺失数量",
        "miss_pct": "缺失比例",
        "miss_chart_title": "各字段缺失数量分布图",
        "miss_clean": "数据集非常完整，没有检测到任何缺失值。",
        # ---- 可视化 ----
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
        # ---- 可视化总览（自动生成组合图表）----
        "tab_dashboard": "可视化总览",
        "dash_intro": "本页无需任何手动配置，自动为当前数据集生成一组组合图表，"
                      "一次看清数据的分布、相关性与类别构成。",
        "dash_corr_title": "数值字段相关系数热力图",
        "dash_corr_help": "颜色越暖（红）表示正相关越强，越冷（蓝）表示负相关越强。",
        "dash_dist_title": "各数值字段分布直方图",
        "dash_box_title": "按类别分组的箱线图（分布差异与离群点）",
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
        "none": "None (no grouping)",
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
        "tab_preview": "Data Preview",
        "tab_filter": "Filtering",
        "tab_describe": "Statistics",
        "tab_missing": "Missing Values",
        "tab_chart": "Visualization",
        # ---- overview ----
        "metric_rows": "Rows (records)",
        "metric_cols": "Columns (fields)",
        "metric_num": "Numeric columns",
        "metric_cat": "Text/categorical columns",
        "metric_missing": "Missing cells",
        "metric_dup": "Duplicate rows",
        "dtype_title": "Column data types (df.dtypes)",
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
        "download_preview": "Download current view as CSV",
        # ---- filtering ----
        "filter_cols_show": "Step 1: Select columns to display",
        "filter_cols_cond": "Step 2: Select columns to filter on (multi-select)",
        "filter_result_title": "Filtered results",
        "filter_result_dim": "Matching records:",
        "filter_empty": "No records match the filters. Try relaxing the conditions.",
        "download_filter": "Download filtered results as CSV",
        "filter_num_tip": "Numeric range (drag the sliders, closed interval)",
        "filter_cat_tip": "Keep selected categories (empty = keep all)",
        # ---- statistics ----
        "desc_num_title": "Numeric columns summary (df.describe())",
        "desc_cat_title": "Categorical columns summary",
        "desc_no_cat": "No categorical columns in this dataset.",
        "desc_help": "count=non-null | mean=average | std=standard deviation | min=minimum | "
                     "25%/50%/75%=quantiles | max=maximum",
        # ---- missing values ----
        "miss_summary": "Missing value summary",
        "miss_total_cells": "Total cells",
        "miss_total_missing": "Total missing",
        "miss_ratio": "Overall missing rate",
        "miss_table_title": "Missing values by column (df.isna())",
        "miss_col": "Column",
        "miss_count": "Missing count",
        "miss_pct": "Missing rate",
        "miss_chart_title": "Missing count by column",
        "miss_clean": "The dataset is complete: no missing values detected.",
        # ---- visualization ----
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
        # ---- chart gallery (auto-generated combined charts) ----
        "tab_dashboard": "Chart Gallery",
        "dash_intro": "No configuration needed: this page automatically builds a set of combined charts "
                      "so you can see distributions, correlations and category composition at a glance.",
        "dash_corr_title": "Correlation heatmap of numeric columns",
        "dash_corr_help": "Warmer (red) means stronger positive correlation; cooler (blue) means stronger negative correlation.",
        "dash_dist_title": "Distribution histograms of numeric columns",
        "dash_box_title": "Box plots grouped by category (distribution differences and outliers)",
        "dash_matrix_title": "Scatter matrix (pairwise numeric relationships)",
        "dash_pie_title": "Category share donut charts",
        "dash_no_category": "No categorical column in this dataset; grouped box plots and donut charts are skipped.",
        "dash_corr_need": "A correlation heatmap needs at least 2 numeric columns.",
        "dash_need_num": "No numeric column available for this chart.",
    },
}

# ---------------------------------------------------------------------
# 2. 通用工具函数
# ---------------------------------------------------------------------

# 默认数据集 CSV 与 app.py 放在同一目录下，pathlib 保证跨平台路径正确
DEFAULT_CSV = Path(__file__).parent / "default_data.csv"


@st.cache_data
def load_default_data() -> pd.DataFrame:
    """读取内置鸢尾花数据集。

    使用 @st.cache_data 装饰器：首次读取后缓存结果，
    后续切换标签页 / 重新渲染时直接从缓存取，避免重复读盘。
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


# 鲜明配色方案：选用 Plotly 内置的高饱和度调色板，让图表色彩更醒目
COLOR_SEQUENCE = px.colors.qualitative.Bold       # 主分类调色板（高饱和、对比强）
COLOR_SEQUENCE_ALT = px.colors.qualitative.Vivid  # 备用分类调色板（与主色调区分）
CONTINUOUS_SCALE = "Turbo"                        # 连续型渐变（密度热力图等）

# 图表类型 -> 是否需要 Y 轴（直方图、饼图只需一个变量）
CHART_TYPES_NO_Y = ("hist", "pie")


def build_figure(chart_type: str, data: pd.DataFrame, x_col: str, y_col, z_col,
                 color_col, nbins, lang: str):
    """按图表类型构建 Plotly 图表对象，构建失败时返回 None。

    把 10 种图表的构建逻辑集中在此函数中，避免页面主体代码过度嵌套。
    """
    t = TEXTS[lang]
    x_label = f"{t['axis_x_label']}: {x_col}"
    y_label = f"{t['axis_y_label']}: {y_col}"
    fig = None

    if chart_type == "bar":
        # 按 X 分组后对 Y 求均值（pandas groupby）：解决同一类别下多条记录的聚合问题
        plot_df = (
            data.groupby(x_col, as_index=False)[y_col]
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
            data.groupby(x_col, as_index=False)[y_col].mean().sort_values(by=x_col)
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
            data.groupby(x_col, as_index=False)[y_col].mean().sort_values(by=x_col)
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

# 预先把列按类型分为两组，多个标签页都会用到
all_columns = df.columns.tolist()
numeric_columns = df.select_dtypes(include="number").columns.tolist()
categorical_columns = [c for c in all_columns if c not in numeric_columns]

# ---------------------------------------------------------------------
# 4. 页面主标题
# ---------------------------------------------------------------------
st.title(t["app_title"])
st.caption(t["app_subtitle"])

# 用 7 个标签页组织全部功能，交互清晰，适合课堂演示
(
    tab_overview,
    tab_preview,
    tab_filter,
    tab_describe,
    tab_missing,
    tab_chart,
    tab_dashboard,
) = st.tabs(
    [
        t["tab_overview"],
        t["tab_preview"],
        t["tab_filter"],
        t["tab_describe"],
        t["tab_missing"],
        t["tab_chart"],
        t["tab_dashboard"],
    ]
)

# =====================================================================
# 5. 标签页一：数据集概览
#    展示 shape、dtypes、前 5 行等 Pandas 基础信息
# =====================================================================
with tab_overview:
    # 5.1 顶部指标卡：st.metric 以大字号突出关键数字
    missing_total = int(df.isna().sum().sum())       # 全表缺失单元格数：isna 两次求和
    duplicate_total = int(df.duplicated().sum())     # 重复行数

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric(t["metric_rows"], df.shape[0])
    col2.metric(t["metric_cols"], df.shape[1])
    col3.metric(t["metric_num"], len(numeric_columns))
    col4.metric(t["metric_cat"], len(categorical_columns))
    col5.metric(t["metric_missing"], missing_total)
    col6.metric(t["metric_dup"], duplicate_total)

    st.divider()

    # 5.2 字段类型表：把 df.dtypes 整理成 DataFrame 展示
    st.subheader(t["dtype_title"])
    dtype_df = pd.DataFrame(
        {
            t["col_name"]: all_columns,
            t["col_dtype"]: [str(df[c].dtype) for c in all_columns],
            t["col_kind"]: [dtype_kind_label(df[c].dtype, lang) for c in all_columns],
        }
    )
    st.dataframe(dtype_df, width="stretch", hide_index=True)

    # 5.3 前 5 行速览
    st.subheader(t["head_title"])
    st.dataframe(df.head(), width="stretch")

# =====================================================================
# 6. 标签页二：数据表格预览
#    自由选择展示列 + 控制展示行数 + 结果下载
# =====================================================================
with tab_preview:
    # multiselect 留空时显示全部列（默认即为全部列，方便直接查看）
    selected_preview_cols = st.multiselect(
        label=t["preview_cols"],
        options=all_columns,
        default=all_columns,
        key="preview_cols",
    )
    # 滑块控制 head 的行数，范围 5~100，默认 20
    n_rows = st.slider(t["preview_rows"], min_value=5, max_value=100, value=20, step=5)

    preview_df = df[selected_preview_cols].head(n_rows)
    st.caption(f"{t['preview_dim']} {preview_df.shape[0]} × {preview_df.shape[1]}")
    st.dataframe(preview_df, width="stretch", hide_index=True)

    # 把当前视图导出为 CSV
    st.download_button(
        label=t["download_preview"],
        data=make_download_csv(preview_df),
        file_name="preview.csv",
        mime="text/csv",
    )

# =====================================================================
# 7. 标签页三：多列筛选
#    数值列 → 区间滑块；类别列 → 多选；多个条件用“逻辑与”叠加
# =====================================================================
with tab_filter:
    # 7.1 选择要展示的列
    show_columns = st.multiselect(
        label=t["filter_cols_show"],
        options=all_columns,
        default=all_columns,
        key="filter_show_cols",
    )

    # 7.2 选择要参与筛选的列（可多选，实现“多列筛选”）
    condition_columns = st.multiselect(
        label=t["filter_cols_cond"], options=all_columns, key="filter_cond_cols"
    )

    # 从原始数据的副本开始，逐个条件收缩结果集
    filtered_df = df.copy()

    # 每个被选中的列生成一个对应类型的输入控件
    for col in condition_columns:
        st.markdown(f"**`{col}`**")
        if pd.api.types.is_numeric_dtype(df[col]):
            # 数值型：用最小值/最大值滑块做闭区间筛选
            # min()/max() 用 skipna=True（默认），缺失值不会干扰边界
            col_min = float(df[col].min())
            col_max = float(df[col].max())
            low, high = st.slider(
                label=f"{col} — {t['filter_num_tip']}",
                min_value=col_min,
                max_value=col_max,
                value=(col_min, col_max),  # 默认选中完整区间
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

    st.divider()
    # 7.3 结果展示（仅显示用户选择的列）
    st.subheader(t["filter_result_title"])
    result_df = filtered_df[show_columns] if show_columns else filtered_df
    st.caption(f"{t['filter_result_dim']} **{result_df.shape[0]}**")

    if result_df.empty:
        # 条件过严时给出友好提示
        st.warning(t["filter_empty"])
    else:
        st.dataframe(result_df, width="stretch", hide_index=True)

    # 筛选结果同样支持下载
    st.download_button(
        label=t["download_filter"],
        data=make_download_csv(result_df),
        file_name="filtered.csv",
        mime="text/csv",
        disabled=result_df.empty,
    )

# =====================================================================
# 8. 标签页四：统计描述 df.describe()
# =====================================================================
with tab_describe:
    st.caption(t["desc_help"])

    # 8.1 数值型字段：count/mean/std/min/分位数/max
    st.subheader(t["desc_num_title"])
    # .T 转置后：每行一个字段，每列一个统计量，阅读更方便
    st.dataframe(df.describe().T, width="stretch")

    # 8.2 类别型字段：count/unique/top/freq（没有类别列时给提示）
    st.subheader(t["desc_cat_title"])
    if categorical_columns:
        st.dataframe(
            df[categorical_columns].describe().T,
            width="stretch",
        )
    else:
        st.info(t["desc_no_cat"])

# =====================================================================
# 9. 标签页五：缺失值检测
# =====================================================================
with tab_missing:
    total_cells = df.shape[0] * df.shape[1]
    missing_ratio = (missing_total / total_cells * 100) if total_cells else 0.0

    # 9.1 三个总体指标
    c1, c2, c3 = st.columns(3)
    c1.metric(t["miss_total_cells"], total_cells)
    c2.metric(t["miss_total_missing"], missing_total)
    c3.metric(t["miss_ratio"], f"{missing_ratio:.2f}%")

    # 9.2 逐字段明细表：缺失数量 + 缺失比例
    st.subheader(t["miss_table_title"])
    miss_df = pd.DataFrame(
        {
            t["miss_col"]: all_columns,
            t["miss_count"]: [int(df[c].isna().sum()) for c in all_columns],
            t["miss_pct"]: [
                f"{df[c].isna().sum() / df.shape[0] * 100:.2f}%" if df.shape[0] else "0.00%"
                for c in all_columns
            ],
        }
    )
    st.dataframe(miss_df, width="stretch", hide_index=True)

    # 9.3 用 Plotly 柱状图可视化各列缺失数量（数据完整时不画图，改显示成功提示）
    if missing_total == 0:
        st.success(t["miss_clean"])
    else:
        # 只画存在缺失的列，避免空列干扰
        miss_plot_df = miss_df[miss_df[t["miss_count"]] > 0]
        fig_miss = px.bar(
            miss_plot_df,
            x=t["miss_col"],
            y=t["miss_count"],
            title=t["miss_chart_title"],
            color=t["miss_count"],
            color_continuous_scale="Reds",
        )
        fig_miss.update_layout(template="plotly_white")
        st.plotly_chart(fig_miss, width="stretch")

# =====================================================================
# 10. 标签页六：Plotly 交互式可视化（本作业的重点模块）
#     共 10 种图表：柱状图 / 折线图 / 面积图 / 散点图 / 3D 散点图 /
#     直方图 / 箱线图 / 小提琴图 / 饼图 / 密度热力图；X、Y、Z 轴自由选择
# =====================================================================
with tab_chart:
    # 左列放控件（约 1/3 宽），右列放图表（约 2/3 宽），形成“操作台 + 画布”布局
    control_col, chart_col = st.columns([1, 2])

    with control_col:
        # 10.1 图表类型（共 10 种）
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

        # 10.2 X 轴：任意字段均可（类别或数值）
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

        # 10.3 Y 轴：直方图 / 饼图只需要一个变量，因此不显示 Y 轴选择
        y_col = None
        if chart_type not in CHART_TYPES_NO_Y:
            if numeric_columns:
                y_col = st.selectbox(
                    label=t["chart_y"], options=numeric_columns, key="chart_y"
                )
            else:
                # 上传的数据若全是文本列，无法画数值图表，给出明确提示
                st.warning(t["no_numeric_cols"])

        # 10.4 Z 轴：仅 3D 散点图需要第三个数值字段
        z_col = None
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

        # 10.5 分组着色（可选）：在选项前追加“无”
        color_options = [None] + all_columns
        color_col = st.selectbox(
            label=t["chart_color"],
            options=color_options,
            format_func=lambda c: t["none"] if c is None else c,
            key="chart_color",
        )

        # 10.6 直方图专属参数：分箱数量
        nbins = None
        if chart_type == "hist":
            nbins = st.slider(t["chart_nbins"], 5, 80, value=20, step=5)

        # 10.7 按图表类型给出对应的操作提示
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

    with chart_col:
        # 参数校验：不同图表对字段类型的要求不同，先判断再绘图
        error_key = None
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

        if error_key:
            st.warning(t[error_key])
        else:
            fig = build_figure(
                chart_type, df, x_col, y_col, z_col, color_col, nbins, lang
            )
            if fig is not None:
                # 统一白色底 + 鲜明配色，保证投影与截图时对比度足够
                fig.update_layout(
                    template="plotly_white",
                    height=560,
                    colorway=COLOR_SEQUENCE,
                    font=dict(size=13),
                    title_font=dict(size=18),
                    margin=dict(t=70, l=50, r=30, b=50),
                )
                st.subheader(t["chart_render"])
                st.plotly_chart(fig, width="stretch")

# =====================================================================
# 11. 标签页七：可视化总览（自动生成组合图表，无需手动配置）
#     相关系数热力图 / 分布直方图网格 / 分组箱线图 /
#     散点矩阵 / 类别占比环形图
# =====================================================================
with tab_dashboard:
    st.caption(t["dash_intro"])

    # 11.1 相关系数热力图：一眼看出哪些字段同向或反向变化
    st.subheader(t["dash_corr_title"])
    if len(numeric_columns) >= 2:
        corr = df[numeric_columns].corr(numeric_only=True)
        fig_corr = px.imshow(
            corr,
            text_auto=".2f",                  # 每个格子直接标注相关系数
            aspect="auto",
            color_continuous_scale="RdBu_r",  # 红=正相关，蓝=负相关，对比强烈
            zmin=-1,
            zmax=1,
        )
        fig_corr.update_layout(template="plotly_white", height=470,
                               margin=dict(t=60))
        st.plotly_chart(fig_corr, width="stretch")
        st.caption(t["dash_corr_help"])
    else:
        st.info(t["dash_corr_need"])

    # 11.2 分布直方图网格：每个数值字段一张，按类别着色
    st.subheader(t["dash_dist_title"])
    if numeric_columns:
        main_cat = categorical_columns[0] if categorical_columns else None
        dist_cols = st.columns(2)
        for i, col in enumerate(numeric_columns):
            with dist_cols[i % 2]:
                fig_dist = px.histogram(
                    df, x=col, nbins=25, color=main_cat,
                    color_discrete_sequence=COLOR_SEQUENCE,
                    title=f"{t['hist_name']}: {col}",
                )
                fig_dist.update_layout(template="plotly_white", height=330,
                                       margin=dict(t=50))
                st.plotly_chart(fig_dist, width="stretch")
    else:
        st.info(t["dash_need_num"])

    # 11.3 分组箱线图网格：看各字段在不同类别下的分布差异与离群点
    st.subheader(t["dash_box_title"])
    if numeric_columns and categorical_columns:
        main_cat = categorical_columns[0]
        box_cols = st.columns(2)
        for i, col in enumerate(numeric_columns):
            with box_cols[i % 2]:
                fig_box = px.box(
                    df, x=main_cat, y=col, color=main_cat, points="outliers",
                    color_discrete_sequence=COLOR_SEQUENCE,
                    title=f"{t['box_name']}: {col} ~ {main_cat}",
                )
                fig_box.update_layout(template="plotly_white", height=330,
                                      margin=dict(t=50))
                st.plotly_chart(fig_box, width="stretch")
    else:
        st.info(t["dash_no_category"])

    # 11.4 散点矩阵：所有数值字段两两组合的散点图，快速发现相关性
    st.subheader(t["dash_matrix_title"])
    if len(numeric_columns) >= 2:
        # 数据量较大时先抽样，避免浏览器渲染卡顿
        matrix_df = df.sample(n=min(len(df), 1500), random_state=42)
        fig_matrix = px.scatter_matrix(
            matrix_df,
            dimensions=numeric_columns,
            color=categorical_columns[0] if categorical_columns else None,
            opacity=0.7,
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        fig_matrix.update_layout(
            template="plotly_white",
            height=320 + 130 * len(numeric_columns),
            margin=dict(t=60),
        )
        st.plotly_chart(fig_matrix, width="stretch")
    else:
        st.info(t["dash_need_num"])

    # 11.5 类别占比环形图：最多展示前 3 个类别字段
    st.subheader(t["dash_pie_title"])
    if categorical_columns:
        pie_cols = st.columns(min(len(categorical_columns), 3))
        for i, col in enumerate(categorical_columns[:3]):
            with pie_cols[i]:
                counts = df[col].value_counts().reset_index()
                counts.columns = [col, t["count_label"]]
                fig_pie = px.pie(
                    counts, names=col, values=t["count_label"], hole=0.45,
                    color_discrete_sequence=COLOR_SEQUENCE,
                    title=f"{t['pie_name']}: {col}",
                )
                fig_pie.update_layout(template="plotly_white", height=360,
                                      margin=dict(t=50))
                st.plotly_chart(fig_pie, width="stretch")
    else:
        st.info(t["dash_no_category"])
