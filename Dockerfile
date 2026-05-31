# Word转PDF服务 Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（LibreOffice用于转换）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建临时目录
RUN mkdir -p /tmp/w2p_uploads /tmp/w2p_outputs

# 暴露端口
EXPOSE 8000

# 环境变量
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# 启动命令
CMD ["python", "main.py"]
