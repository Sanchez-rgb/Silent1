# 小红书情感分析平台

一个专业的小红书笔记情感分析系统，包含前端界面和后端API。

## 功能特性

- 📝 **笔记采集** - 添加小红书笔记内容和作者
- 🧠 **情感分析** - 使用SnowNLP进行中文情感分析
- 📊 **数据统计** - 实时情感分布统计和可视化图表
- 💾 **数据存储** - SQLite数据库存储所有笔记记录
- 🔍 **筛选搜索** - 按情感类型筛选和内容搜索
- 📥 **数据导出** - 导出JSON格式数据文件
- 🗑️ **删除管理** - 单条删除和批量清空功能

## 技术栈

### 前端
- HTML5 + CSS3 + JavaScript
- Chart.js (图表可视化)
- Inter字体 (美观UI)

### 后端
- Python 3.7+
- FastAPI (Web框架)
- SnowNLP (中文情感分析)
- SQLite (数据库)
- Uvicorn (ASGI服务器)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

或者使用uvicorn直接启动：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问应用

打开浏览器访问：`http://localhost:8000`

## API接口文档

启动服务后，访问：`http://localhost:8000/docs` 查看完整的API文档（Swagger UI）

### 主要接口

#### POST /analyze
分析笔记情感

**请求参数：**
```json
{
  "content": "笔记内容",
  "author": "作者名称（可选）"
}
```

**响应：**
```json
{
  "sentiment": "positive|neutral|negative",
  "confidence": 0.85,
  "id": 1
}
```

#### GET /stats
获取统计数据和笔记列表

**响应：**
```json
{
  "total_notes": 10,
  "positive": 6,
  "neutral": 2,
  "negative": 2,
  "notes": [...]
}
```

#### DELETE /notes/{note_id}
删除指定笔记

#### DELETE /notes
清空所有笔记

## 项目结构

```
.
├── main.py              # FastAPI后端服务
├── index.html           # 前端界面
├── requirements.txt     # Python依赖
├── README.md           # 项目说明
└── xiaohongshu.db      # SQLite数据库（自动生成）
```

## 情感分析说明

使用SnowNLP进行中文情感分析：
- **正面 (positive)**: 置信度 > 0.6
- **中性 (neutral)**: 0.4 ≤ 置信度 ≤ 0.6
- **负面 (negative)**: 置信度 < 0.4

## 扩展功能

### 切换到百度AI情感分析

如需使用更准确的百度AI情感分析，可以修改`main.py`中的`analyze_sentiment_snownlp`函数，替换为百度AI的API调用。

### 其他AI服务支持

可以轻松扩展支持：
- 阿里云NLP
- 腾讯云NLP
- HuggingFace模型
