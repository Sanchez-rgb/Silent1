# Word转PDF服务 - 完整使用说明

## 📋 项目概述

这是一个功能完整的Word转PDF在线服务，包含：
- ✅ 免费版（每天3次）
- ✅ 按次付费（1元/次）
- ✅ 月度会员（9.9元/月，无限次）
- ✅ 企业版（99元/月，API接口）

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- fastapi
- uvicorn
- sqlalchemy
- python-docx
- python-multipart

### 2. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

### 3. 访问服务

- 前端界面：http://localhost:8000
- API文档：http://localhost:8000/docs

## 📁 项目文件

```
├── main.py              # FastAPI主应用
├── db.py               # 数据库模型
├── converter.py         # 文档转换模块
├── index.html          # 前端界面
├── requirements.txt    # Python依赖
├── word2pdf.db         # SQLite数据库（自动创建）
└── README.md          # 本文件
```

## 🎯 功能说明

### 免费版
- 无需注册，每天3次转换
- 支持拖拽上传
- 文件大小限制：50MB

### 会员体系
| 套餐 | 价格 | 功能 |
|------|------|------|
| 免费版 | ¥0 | 每天3次 |
| 月度会员 | ¥9.9/月 | 无限次转换 |
| 年度会员 | ¥99/年 | 无限次转换 |
| 企业版 | ¥99/月 | API接口 + 后台管理 |

### API接口

#### 1. 用户注册
```bash
POST /api/register
{
  "phone": "13800138000",
  "password": "123456",
  "code": "123456"
}
```

#### 2. 用户登录
```bash
POST /api/login
{
  "phone": "13800138000",
  "password": "123456"
}
```

#### 3. 文档转换
```bash
POST /api/convert
Content-Type: multipart/form-data

file: [上传的doc/docx文件]
Authorization: Bearer {token}  # 可选
```

#### 4. 创建支付
```bash
POST /api/create_payment
{
  "amount": 9.9,
  "payment_type": "monthly"
}
```

#### 5. 企业API密钥
```bash
POST /api/enterprise/create_key
{
  "company_name": "我的公司",
  "quota": 1000
}
```

#### 6. 查询使用量
```bash
GET /api/enterprise/usage
Authorization: Bearer {api_key}
```

## 🗄️ 数据库表结构

### users（用户表）
- id: 主键
- phone: 手机号
- password_hash: 密码哈希
- is_vip: 是否VIP
- vip_type: VIP类型
- expiry_date: 到期时间

### conversion_records（转换记录）
- id: 主键
- user_id: 用户ID
- file_name: 文件名
- status: 状态
- is_paid: 是否付费
- created_at: 创建时间

### api_keys（API密钥）
- id: 主键
- user_id: 用户ID
- company_name: 公司名
- api_key: API密钥
- monthly_quota: 月度额度
- used_count: 已使用次数

## 💰 支付流程（模拟）

1. 用户点击购买 → 调用 `/api/create_payment`
2. 生成支付订单 → 返回订单号和二维码
3. 用户扫码支付 → 调用 `/api/payment_callback`
4. 支付成功 → 开通会员/增加额度

## 🔧 系统要求

### Windows
- Python 3.8+
- Microsoft Word 或 LibreOffice（用于转换）

### Linux/macOS
- Python 3.8+
- LibreOffice

### 安装LibreOffice（Linux）

```bash
# Ubuntu/Debian
sudo apt-get install libreoffice

# CentOS/RHEL
sudo yum install libreoffice
```

## 📱 移动端适配

前端界面完全响应式，支持：
- 手机浏览器直接使用
- 平板横竖屏切换
- 微信内嵌浏览器

## 🐛 常见问题

### Q: 转换失败？
A: 检查是否安装了Microsoft Word或LibreOffice

### Q: 文件上传失败？
A: 检查文件大小是否超过50MB，格式是否为.doc/.docx

### Q: 支付后没生效？
A: 刷新页面或重新登录

### Q: API调用失败？
A: 检查API密钥是否正确，是否在额度内

## 🚀 部署指南

### Railway部署
1. 推送到GitHub
2. Railway会自动构建Docker镜像
3. 配置环境变量（可选）

### 本地Docker部署
```bash
docker build -t word2pdf .
docker run -p 8000:8000 word2pdf
```

## 📞 技术支持

如有问题，请提交Issue或联系开发者。

---

**版本**: 2.0.0  
**更新时间**: 2024年  
**许可证**: MIT
