# 小红书定时任务系统

## 功能介绍

这是一个自动定时任务系统，用于定期采集和分析小红书博主的笔记评论数据。主要功能包括：

- 定时执行任务（每天凌晨 02:00）
- 读取关注博主信息
- 获取博主最新笔记
- 爬取笔记评论（前20条）
- 使用 SnowNLP 进行情感分析
- 将分析结果存储到 SQLite 数据库

## 项目文件

| 文件名 | 说明 |
|--------|------|
| `xiaohongshu_scheduler.py` | 主程序文件，包含定时任务逻辑 |
| `init_db.py` | 数据库初始化脚本 |
| `simple_test.py` | 简单测试脚本 |
| `reset_check_time.py` | 重置博主检查时间 |
| `requirements.txt` | Python 依赖包 |
| `xiaohongshu.db` | SQLite 数据库文件（自动生成） |

## 安装依赖

```bash
pip install -r requirements.txt
```

或单独安装：

```bash
pip install fastapi uvicorn snownlp schedule
```

## 快速开始

### 1. 初始化数据库

```bash
python init_db.py
```

### 2. 立即测试运行

```bash
python simple_test.py
```

### 3. 启动定时任务

```bash
python xiaohongshu_scheduler.py
```

程序将在每天凌晨 02:00 自动执行任务。

## 数据库表结构

### `followed_blogs` - 关注博主表

| 字段 | 类型 | 说明 |
|------|------|------|
| blogger_id | TEXT | 博主ID（主键） |
| blogger_name | TEXT | 博主名称 |
| last_check_time | DATETIME | 上次检查时间 |
| created_at | DATETIME | 创建时间 |

### `comments_analysis` - 评论分析表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增ID（主键） |
| blogger_id | TEXT | 博主ID |
| blogger_name | TEXT | 博主名称 |
| note_id | TEXT | 笔记ID |
| note_title | TEXT | 笔记标题 |
| note_publish_time | DATETIME | 笔记发布时间 |
| comment_id | TEXT | 评论ID |
| comment_text | TEXT | 评论内容 |
| sentiment | TEXT | 情感标签（positive/neutral/negative） |
| confidence | REAL | 置信度分数 |
| created_at | DATETIME | 创建时间 |

### `notes` - 笔记表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增ID（主键） |
| note_id | TEXT | 笔记ID（唯一） |
| blogger_id | TEXT | 博主ID |
| blogger_name | TEXT | 博主名称 |
| title | TEXT | 笔记标题 |
| content | TEXT | 笔记内容 |
| publish_time | DATETIME | 发布时间 |
| created_at | DATETIME | 创建时间 |

## 如何添加关注的博主

使用 Python 脚本添加博主：

```python
import sqlite3

conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()

cursor.execute('''
    INSERT OR IGNORE INTO followed_blogs (blogger_id, blogger_name, last_check_time)
    VALUES (?, ?, ?)
''', ('your_blogger_id', '博主姓名', '2024-01-01 00:00:00'))

conn.commit()
conn.close()
```

## 自定义配置

### 修改执行时间

编辑 `xiaohongshu_scheduler.py` 文件：

```python
# 每天 02:00 执行
schedule.every().day.at("02:00").do(run_task)

# 改为每天 08:30 执行
schedule.every().day.at("08:30").do(run_task)

# 改为每小时执行一次
schedule.every().hour.do(run_task)

# 改为每天执行一次（不指定具体时间）
schedule.every().day.do(run_task)
```

### 替换真实的小红书 API

当前使用模拟 API (`XiaohongshuMockAPI`)，如需对接真实 API，请修改：

```python
class XiaohongshuAPI:
    def get_blogger_notes(self, blogger_id):
        # 在这里实现真实的小红书 API 调用
        pass
```

## 工具脚本

### 重置检查时间

```bash
python reset_check_time.py
```

此脚本会将所有博主的最后检查时间重置为 `2024-01-01 00:00:00`，让定时任务重新处理所有笔记。

### 简单测试

```bash
python simple_test.py
```

快速测试整个流程是否正常工作。

## 数据查询示例

### 查询所有评论分析

```python
import sqlite3

conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM comments_analysis ORDER BY id DESC')
for row in cursor.fetchall():
    print(row)

conn.close()
```

### 按情感标签统计

```python
import sqlite3

conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT sentiment, COUNT(*) 
    FROM comments_analysis 
    GROUP BY sentiment
''')

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()
```

### 查询特定博主的数据

```python
import sqlite3

conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT * FROM comments_analysis 
    WHERE blogger_id = 'blogger_001'
''')

for row in cursor.fetchall():
    print(row)

conn.close()
```

## 注意事项

1. **定时任务需要后台运行** - 建议使用进程管理工具（如 systemd、nohup 等）
2. **SnowNLP 是中文情感分析库** - 对中文内容效果更好
3. **数据库文件路径** - 默认为当前目录下的 `xiaohongshu.db`
4. **错误处理** - 任务会捕获异常并打印堆栈信息，但不会停止程序

## 后台运行方式

### Windows

使用 `pythonw` 或创建服务：

```bash
pythonw xiaohongshu_scheduler.py
```

### Linux/Mac

使用 nohup：

```bash
nohup python xiaohongshu_scheduler.py > scheduler.log 2>&1 &
```

或使用 screen/tmux 等终端复用工具。

## 扩展建议

1. 添加数据可视化图表
2. 添加邮件/消息通知功能
3. 添加去重逻辑避免重复分析
4. 添加数据导出功能（CSV/Excel）
5. 实现真实的小红书 API 对接（需要账号）
6. 添加日志记录功能
