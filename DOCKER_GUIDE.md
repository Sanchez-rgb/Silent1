# Docker 部署指南

## 📋 前置要求

### 1. 安装 Docker

**Windows / macOS:**
- 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop)
- 安装并启动 Docker Desktop

**Linux (Ubuntu):**
```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组（避免每次使用sudo）
sudo usermod -aG docker $USER
```

### 2. 验证安装

```bash
docker --version
docker-compose --version
```

## 🚀 快速开始

### 方法一：使用 Docker Compose（推荐）

```bash
# 1. 构建并启动服务
docker-compose up -d

# 2. 查看日志
docker-compose logs -f

# 3. 停止服务
docker-compose down

# 4. 重新构建（代码更新后）
docker-compose up -d --build
```

### 方法二：使用 Docker 命令

```bash
# 1. 构建镜像
docker build -t word2pdf .

# 2. 运行容器
docker run -d \
  --name word2pdf-service \
  -p 8000:8000 \
  -e PORT=8000 \
  -v $(pwd)/word2pdf.db:/app/word2pdf.db \
  word2pdf

# 3. 查看日志
docker logs -f word2pdf-service

# 4. 停止服务
docker stop word2pdf-service

# 5. 删除容器
docker rm word2pdf-service
```

## 🌐 访问服务

启动成功后，访问：
- **前端界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 📁 目录结构

```
.
├── Dockerfile              # Docker镜像配置
├── docker-compose.yml     # Docker Compose配置
├── main.py               # FastAPI应用
├── db.py                 # 数据库模型
├── converter.py          # 文档转换器
├── index.html            # 前端界面
└── requirements.txt      # Python依赖
```

## 🔧 常用命令

### 查看容器状态
```bash
docker ps
```

### 进入容器内部
```bash
docker exec -it word2pdf-service /bin/bash
```

### 查看容器日志
```bash
# 实时日志
docker-compose logs -f

# 最近100行日志
docker-compose logs --tail 100

# 特定容器日志
docker logs word2pdf-service
```

### 重启服务
```bash
docker-compose restart
```

### 清理资源
```bash
# 停止并删除容器
docker-compose down

# 删除镜像
docker rmi word2pdf

# 删除所有未使用的镜像
docker image prune -f
```

## 🐛 故障排查

### 问题1: 端口被占用
```
Error: error while attempting to bind on address ('0.0.0.0', 8000)
```

**解决方案:**
```bash
# 方法1: 修改docker-compose.yml中的端口
ports:
  - "8001:8000"  # 使用8001端口

# 方法2: 停止占用8000端口的进程
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

### 问题2: 权限错误
```
Permission denied: '/app/word2pdf.db'
```

**解决方案:**
```bash
# 方法1: 修改文件权限
chmod 777 word2pdf.db

# 方法2: 在docker-compose.yml中添加用户
user: "1000:1000"
```

### 问题3: 转换功能不工作

**可能原因:** LibreOffice未正确安装

**解决方案:**
```bash
# 进入容器检查
docker exec -it word2pdf-service /bin/bash

# 检查LibreOffice
libreoffice --version

# 如果未安装，在Dockerfile中添加
RUN apt-get update && apt-get install -y libreoffice
```

### 问题4: 数据库连接失败

**解决方案:**
```bash
# 检查数据库文件是否存在
ls -la word2pdf.db

# 重建数据库
rm word2pdf.db
docker-compose up -d
```

## 🔐 生产环境部署

### 使用环境变量
```bash
# 创建.env文件
cat > .env << EOF
PORT=8000
PYTHONUNBUFFERED=1
EOF

# 使用env文件启动
docker-compose --env-file .env up -d
```

### 配置反向代理（Nginx）
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### HTTPS配置（Let's Encrypt）
```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 📊 监控和日志

### 查看资源使用
```bash
docker stats
```

### 设置日志轮转
在 `docker-compose.yml` 中添加:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🧹 清理和重置

### 完全重置环境
```bash
# 停止所有容器
docker-compose down

# 删除所有数据卷
docker-compose down -v

# 删除所有镜像
docker rmi $(docker images -q)

# 重新构建
docker-compose up -d --build
```

## 💡 高级配置

### 使用多阶段构建（减小镜像大小）
```dockerfile
# 构建阶段
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 运行阶段
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["python", "main.py"]
```

### 使用GPU加速（可选）
```yaml
services:
  word2pdf:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## 📞 获取帮助

如果遇到问题：
1. 查看日志: `docker-compose logs`
2. 检查容器状态: `docker ps -a`
3. 查看Docker文档: https://docs.docker.com/

## ✅ 部署检查清单

- [ ] Docker已安装并运行
- [ ] 端口8000未被占用（或已修改配置）
- [ ] 文件权限正确
- [ ] 数据库文件可访问
- [ ] 服务正常启动
- [ ] 前端可访问
- [ ] 转换功能正常

---

**版本**: 2.0.0  
**更新时间**: 2024年
