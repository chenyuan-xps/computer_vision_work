# 数据分析可视化网站（Streamlit + Pandas + Plotly）

> 可视化导论课程作业 —— 一个零代码交互式数据分析与可视化平台。
> 打开网页即自动加载经典的鸢尾花（Iris）数据集，也可以上传任意 CSV 文件进行分析。

---

## 一、项目简介

本项目基于 **Streamlit** 快速搭建 Web 界面，以 **Pandas** 作为数据分析引擎，
用 **Plotly** 绘制可交互图表，实现了从“数据加载 → 数据理解 → 筛选查询 →
统计分析 → 可视化展示”的完整数据分析闭环，并支持 **中文 / 英文一键切换**。

## 二、功能亮点

| 模块 | 功能 | 对应 Pandas / Plotly 能力 |
| --- | --- | --- |
| 数据加载 | 打开网页自动加载 150 条鸢尾花默认数据；支持上传自己的 CSV（自动兼容 UTF-8 / GBK 编码） | `pd.read_csv` |
| 数据集概览 | 指标卡展示行数、列数、数值列/类别列数量、缺失数、重复行数；字段类型表；前 5 行速览 | `df.shape`、`df.dtypes`、`df.head`、`df.isna`、`df.duplicated` |
| 数据表格预览 | 自由勾选展示列、滑块控制显示行数、一键下载当前视图 | 列选择、`df.head(n)`、`df.to_csv` |
| 多列筛选 | 可同时对多列叠加条件：数值列用双向滑块做区间筛选，类别列用多选框筛选；结果可导出 | 布尔索引、`between`、`isin`、多条件逻辑与 |
| 统计描述 | 数值列输出 count/mean/std/min/四分位数/max；类别列输出 unique/top/freq | `df.describe()` |
| 缺失值检测 | 总体缺失指标 + 逐列缺失数量/比例明细表 + 缺失分布柱状图 | `df.isna().sum()` |
| 交互式可视化 | **10 种图表自由切换**：柱状图、折线图、面积图、散点图、**3D 散点图**、直方图、箱线图、小提琴图、饼图、密度热力图；X/Y/Z 轴自由选择；可选分组着色；直方图可调分箱数 | `plotly.express` 全家桶，配合 `groupby().mean()` 聚合 |
| 可视化总览 | 新增独立标签页，**零配置自动生成组合仪表盘**：相关系数热力图、各数值列分布直方图网格、按类别分组的箱线图网格、散点矩阵（scatter matrix）、类别占比环形图 | `df.corr()`、`px.imshow`、`px.scatter_matrix` 等 |
| 视觉设计 | 彩虹渐变标题、渐变指标卡（左侧彩条+阴影）、彩色标签页；图表统一使用 Bold/Vivid 高饱和调色板与 Turbo 连续色带，色彩鲜明适合投影展示 | 自定义 CSS + Plotly 调色板 |
| 双语切换 | 侧边栏 中文 / English 一键切换，全部标签、提示、图表标题一一对应 | i18n 字典方案 |
| 交互细节 | 图表支持悬停查看数值、3D 图鼠标拖动旋转、框选缩放、图例点击过滤、导出 PNG；筛选结果/预览可下载 CSV | Plotly 工具栏 + Streamlit download_button |

### 默认数据集说明

`default_data.csv` 为经典 **Iris 鸢尾花数据集**（150 行 × 5 列），字段含义：

| 字段 | 含义 |
| --- | --- |
| sepal_length | 花萼长度（cm） |
| sepal_width | 花萼宽度（cm） |
| petal_length | 花瓣长度（cm） |
| petal_width | 花瓣宽度（cm） |
| species | 类别：setosa（山鸢尾）/ versicolor（变色鸢尾）/ virginica（维吉尼亚鸢尾），各 50 条 |

## 三、技术栈与项目结构

```
computer_vision_work/
├── app.py             # 主程序：7 个标签页 + 10 种图表（含详细中文注释）
├── default_data.csv   # 默认鸢尾花数据集（150 条）
├── requirements.txt   # Python 依赖清单
└── README.md          # 功能说明文档（本文件）
```

依赖（共 3 个，无需 sklearn，默认数据直接随源码提供）：

```
streamlit>=1.47   # Web 应用框架
pandas>=2.0       # 数据分析
plotly>=5.18      # 交互式图表
```

## 四、本地运行

### 1. 准备环境

需要 Python 3.9 及以上版本（官网下载安装：<https://www.python.org/downloads/>，
安装 Windows 版时勾选 **Add Python to PATH**）。

### 2. 安装依赖

在项目文件夹中打开终端（Windows 在地址栏输入 `cmd` 回车，或 PowerShell）：

```bash
# （推荐）创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 安装依赖
pip install -r requirements.txt
# 若下载慢，可使用清华镜像源：
# pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 启动网站

```bash
streamlit run app.py
```

浏览器会自动打开 <http://localhost:8501> ，即可看到自动加载的鸢尾花数据集。
停止服务：在终端按 `Ctrl + C`。

## 五、Streamlit 免费部署（获取公网链接）

使用 Streamlit 官方免费托管平台 **Community Cloud**（需能访问国际网络）：

1. **注册 GitHub 账号**：<https://github.com>
2. **新建仓库并上传文件**：
   - 点击右上角 `+` → `New repository`，仓库名例如 `iris-visualization`，设为 Public；
   - 上传本项目的 **三个文件**：`app.py`、`requirements.txt`、`default_data.csv`
     （可直接拖拽到网页上传，或用 `git push`）。
3. **注册并登录 Streamlit Community Cloud**：<https://share.streamlit.io>
   （用 GitHub 账号授权登录即可，免费额度对课程作业完全够用）。
4. **部署应用**：
   - 点击 `New app`；
   - 选择刚创建的仓库、分支保持 `main`；
   - Main file path 填 `app.py`；
   - 点击 `Deploy!`，等待 1~2 分钟构建完成。
5. **获取公网链接**：部署成功后得到形如
   `https://你的用户名-iris-visualization.streamlit.app` 的网址，
   任何人都可以访问，可直接提交给老师；在应用右上角菜单中还可设置自定义访问权限。
6. **更新代码**：以后只要把新代码 push 到 GitHub，在网页右上角菜单点 `Reboot`
   即自动重新部署。

> 注意：免费平台休眠后首次打开需等待几十秒冷启动，属正常现象。

## 六、5 分钟演示视频讲解建议

可按“数据 → 分析 → 可视化 → 特色”的顺序录制：

1. **25 秒**：打开公网链接，展示自动加载鸢尾花数据、彩虹渐变标题与宽屏布局；
2. **30 秒**：概览页看 150×5 的规模、字段类型；切换英文再切回中文，展示双语能力；
3. **40 秒**：预览页勾选列、拖动行数滑块；筛选页演示“花瓣长度区间 + 类别”多条件筛选并下载 CSV；
4. **30 秒**：统计描述与缺失值检测页；
5. **80 秒（亮点）**：可视化总览页，强调“零配置自动生成 11 张图”：
   - 相关系数热力图：指出 petal_length 与 petal_width 相关系数高达 0.96；
   - 滚动展示分布直方图网格、分组箱线图网格；
   - 散点矩阵中三类鸢尾花明显分群；环形图显示三类各占 1/3；
6. **80 秒（重点）**：自定义可视化页依次切换图表类型
   - 柱状图：X = species，Y = petal_length（自动按类别求均值）；
   - 散点图：X = petal_length，Y = petal_width，着色 = species，展示分群；
   - 箱线图 / 小提琴图：展示三类鸢尾花的分布差异与离群点；
   - 3D 散点图：选三个数值字段，鼠标拖动旋转；
   - 饼图、密度热力图快速切换；演示悬停、缩放、导出 PNG；
7. **15 秒**：上传一个自己的 CSV 文件，说明平台具有通用性，收尾。

## 七、核心实现要点（答辩可讲）

- 所有页面文案集中在 `TEXTS` 字典中，中文/英文使用相同的 key，切换语言即切换整套文案；
- 用 `@st.cache_data` 缓存数据读取结果，避免重复 IO；
- 多列筛选通过循环动态生成控件，并用布尔索引逐列收缩 DataFrame；
- 柱状图/折线图/面积图先用 `groupby().mean()` 聚合，解决“一类别多记录”的问题；
- 10 种图表的构建逻辑统一收敛到 `build_figure()` 函数中，按图表类型分发，
  主页面只负责参数校验与渲染，避免深层 if-else 嵌套；
- 可视化总览页全部自动生成：`df.corr()` 计算相关系数矩阵、
  `df.sample()` 对大数据集抽样后再画散点矩阵防止卡顿；
- 上传的 CSV 自动尝试 UTF-8、GBK 两种编码，导出文件使用 `utf-8-sig` 保证 Excel 打开不乱码。
