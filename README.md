<p align="center">
  <h1 align="center">🔮 MingLi Engine</h1>
  <p align="center">
    <strong>命理预测引擎 — 八字 · 紫微 · 奇门 · 大模型四轮推演</strong>
  </p>
  <p align="center">
    <a href="#-快速开始">快速开始</a> ·
    <a href="#-支持的模型">模型配置</a> ·
    <a href="#-系统架构">系统架构</a> ·
    <a href="#-api-接口">API 文档</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-Web%20UI-green.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/LLM-DeepSeek%20%7C%20Qwen%20%7C%20GLM%20%7C%20Ollama-orange.svg" alt="LLM">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
  </p>
</p>

---

> ### ⚠️ 免责声明 / Disclaimer
>
> **非营利性与学术研究**：本程序仅供编程学习、历法研究及传统文化爱好者技术交流使用。
>
> **不作为决策依据**：生成的预测报告内容由大语言模型基于概率生成，不代表客观事实，不具有医疗、法律、财务等专业咨询建议功能。
>
> **禁止非法用途**：严禁将本软件用于封建迷信诈骗、非法经营等违反国家法律法规的行为。使用者利用本工具从事任何违法活动，后果由使用者自行承担，开发者概不负责。

---

## ✨ 特性

- 🎯 **八字排盘** — 四柱干支、十神、藏干、格局、喜用神，节气精确判断（支持1900-2100年）
- 🌟 **紫微斗数** — 14主星安星、四化、辅星，自动公历转农历
- 🌀 **奇门遁甲** — 阴阳遁、九宫、八门九星
- 🧠 **大模型四轮推演** — 格局定性 → 三系交叉验证 → 流年推演 → 个性化路径
- 🌐 **Web UI** — 开箱即用的可视化界面，支持模型在线切换
- 🤖 **多模型支持** — DeepSeek / 通义千问 / 智谱GLM / Kimi / 文心一言 / Claude / Ollama 本地部署

---

## 🚀 快速开始

### Windows

```
1. 双击 "安装依赖并启动.bat"   （首次运行，自动安装依赖）
   或
   双击 "快速启动.bat"          （已安装依赖后）
```

### macOS / Linux

```bash
chmod +x start.sh
./start.sh
```

启动后浏览器自动打开 **http://localhost:18766**

> 无需任何 LLM 配置即可排盘（八字/紫微/奇门）。生成报告需要配置至少一个大模型。

---

## ⚙️ 支持的模型

进入 Web UI 后，点击右上角 **⚙ 齿轮图标** 即可在线切换模型，无需修改任何文件。

| 提供商 | 说明 | 推荐度 |
|--------|------|--------|
| **DeepSeek** | 性价比最高，推荐首选 | ⭐⭐⭐⭐⭐ |
| **通义千问** | 阿里云 DashScope | ⭐⭐⭐⭐⭐ |
| **智谱 GLM** | GLM-4 系列 | ⭐⭐⭐⭐ |
| **Kimi** | 月之暗面，长文本能力强 | ⭐⭐⭐⭐ |
| **文心一言** | 百度，需 access_token | ⭐⭐⭐ |
| **OpenAI** | GPT-4o / GPT-4 | ⭐⭐⭐⭐ |
| **Claude** | Anthropic Claude | ⭐⭐⭐⭐ |
| **Ollama** | 本地部署，完全离线，无需 API Key | ⭐⭐⭐⭐⭐ |
| **自定义** | 任意 OpenAI 兼容接口 | ⭐⭐⭐ |

### 环境变量配置（可选）

复制 `.env.example` 为 `.env`，填入 API Key：

```bash
cp mingli_engine/.env.example mingli_engine/.env
```

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx
QWEN_API_KEY=sk-xxxxxxxxxxxx
GLM_API_KEY=xxxxxxxxxxxx.xxxxxx
```

> 配置后 Web UI 会自动识别已填写的 Key 并标记为「已配置」。

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────┐
│              L1 用户交互层                        │
│         FastAPI + Web UI (HTML/JS)               │
├─────────────────────────────────────────────────┤
│              L2 本地计算层 (零LLM)                │
│   八字排盘 │ 紫微斗数 │ 奇门遁甲 │ 大运流年       │
├─────────────────────────────────────────────────┤
│              L3 大模型推演层                      │
│   R1格局定性 → R2交叉验证 → R3流年 → R4路径      │
├─────────────────────────────────────────────────┤
│              L4 报告组装层                        │
│   八模块完整报告 · 五行能量图 · 十二宫位          │
└─────────────────────────────────────────────────┘
```

### 设计原则

1. **排盘层与推演层严格分离** — LLM 不参与数值计算，保证排盘精确性
2. **每轮 Prompt 单一任务** — 防止复杂度过载导致输出质量下降
3. **矛盾不强行调和** — 诚实性优先于一致性，如实呈现不同体系的差异
4. **θ心性参数只做过滤排序** — 避免迎合偏好，保证客观性

---

## 📁 项目结构

```
mingli_engine/
├── main.py                 # FastAPI 入口 & REST API
├── config.py               # LLM 提供商 & 模型配置
├── .env.example            # 环境变量模板
├── requirements.txt        # Python 依赖
├── engines/                # 本地计算引擎（零 LLM 依赖）
│   ├── bazi_engine.py      # 八字排盘（四柱/十神/藏干/格局/喜用神）
│   ├── ziwei_engine.py     # 紫微斗数（14主星/四化/辅星）
│   ├── qimen_engine.py     # 奇门遁甲（阴阳遁/九宫/八门九星）
│   ├── dayun_engine.py     # 大运流年
│   ├── personality_engine.py  # 心性测试 θ 参数
│   ├── chart_builder.py    # 数据编排（排盘入口）
│   └── lunar_utils.py      # 大模型辅助农历转换
├── llm/                    # 大模型推演层
│   ├── client.py           # 统一 LLM 客户端（9大提供商）
│   ├── round1_pattern.py   # R1 格局定性
│   ├── round2_cross.py     # R2 三系交叉验证
│   ├── round3_liunian.py   # R3 流年推演
│   └── round4_paths.py     # R4 个性化路径
├── assembler/              # 报告组装层
│   ├── report_assembler.py # 报告生成器
│   └── templates/          # 报告模板
├── data/                   # 数据层
│   └── jieqi_table.json    # 节气数据表
└── frontend/               # Web UI
    ├── index.html          # 主页（问卷+排盘）
    └── report.html         # 报告展示页
```

---

## 📡 API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/questions` | GET | 获取心性测试问卷 |
| `/api/bazi` | POST | 八字排盘（不调用 LLM） |
| `/api/personality` | POST | 计算心性参数 |
| `/api/chart-data` | POST | 构建完整排盘数据 |
| `/api/generate-report` | POST | 异步生成完整报告 |
| `/api/task/{task_id}` | GET | 查询报告生成状态 |
| `/api/llm/providers` | GET | 获取所有 LLM 提供商 |
| `/api/llm/models/{provider}` | GET | 获取可用模型列表 |
| `/api/llm/config` | POST | 保存模型配置 |
| `/api/llm/test` | POST | 测试模型连接 |
| `/api/health` | GET | 健康检查 |

### 示例：八字排盘

```bash
curl -X POST http://localhost:18766/api/bazi \
  -H "Content-Type: application/json" \
  -d '{"year":1988,"month":12,"day":10,"hour":14,"minute":10,"gender":"male"}'
```

---

## 🛠 技术栈

| 层 | 技术 |
|----|------|
| Web 后端 | FastAPI + uvicorn |
| LLM 推演 | DeepSeek / Qwen / GLM / Claude / Ollama |
| 前端 | 原生 HTML/CSS/JS + Chart.js |
| 数据存储 | JSON + SQLite（历史记录）|

---

## 📋 依赖安装

```bash
pip install -r mingli_engine/requirements.txt
```

主要依赖：`fastapi`, `uvicorn`, `httpx`, `python-dotenv`, `openai`, `anthropic`, `jieba`

---

## 📝 更新日志

- **v1.5** — 紫微斗数 + 奇门遁甲 + Web UI + 五行能量图 + 多模型支持 + Ollama 本地部署
- **v1.0** — 八字排盘 + 大运流年 + LLM 四轮推演 + 基础报告

---

## 📄 License

MIT License
