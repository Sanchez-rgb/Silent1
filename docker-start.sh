#!/bin/bash

# Word转PDF服务 - Docker快速启动脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}[错误] Docker未安装${NC}"
        echo "请先安装Docker Desktop: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}[错误] Docker Compose未安装${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}[OK] Docker已安装${NC}"
}

# 检查Docker是否运行
check_docker_running() {
    if ! docker ps &> /dev/null; then
        echo -e "${RED}[错误] Docker未运行${NC}"
        echo "请启动Docker Desktop"
        exit 1
    fi
    echo -e "${GREEN}[OK] Docker已运行${NC}"
}

# 构建并启动
build_start() {
    echo -e "\n${YELLOW}[1/3] 正在构建Docker镜像...${NC}"
    docker build -t word2pdf .
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 构建失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] 镜像构建完成${NC}"
    
    echo -e "\n${YELLOW}[2/3] 正在启动服务...${NC}"
    docker-compose up -d
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 启动失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] 服务已启动${NC}"
    
    echo -e "\n${YELLOW}[3/3] 等待服务就绪...${NC}"
    sleep 5
    
    echo -e "\n${GREEN}====================================${NC}"
    echo -e "${GREEN}服务启动成功！${NC}"
    echo -e "${GREEN}====================================${NC}"
    echo ""
    echo "前端界面: http://localhost:8000"
    echo "API文档:   http://localhost:8000/docs"
    echo ""
    echo "查看日志: docker-compose logs -f"
    echo "停止服务: docker-compose down"
}

# 启动服务
start() {
    echo -e "\n${YELLOW}正在启动服务...${NC}"
    docker-compose up -d
    echo -e "${GREEN}[OK] 服务已启动${NC}"
}

# 停止服务
stop() {
    echo -e "\n${YELLOW}正在停止服务...${NC}"
    docker-compose down
    echo -e "${GREEN}[OK] 服务已停止${NC}"
}

# 查看日志
logs() {
    echo -e "\n${YELLOW}正在打开日志 (按 Ctrl+C 退出)...${NC}"
    docker-compose logs -f
}

# 重新构建
rebuild() {
    echo -e "\n${YELLOW}正在清理旧容器...${NC}"
    docker-compose down
    
    echo -e "\n${YELLOW}正在重新构建镜像...${NC}"
    docker-compose up -d --build
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK] 服务已重新构建并启动${NC}"
        echo ""
        echo "前端界面: http://localhost:8000"
    fi
}

# 完全清理
clean() {
    echo -e "\n${YELLOW}[警告] 将删除所有容器、镜像和数据卷${NC}"
    read -p "确认清理? (y/n): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo ""
        docker-compose down -v
        docker rmi word2pdf 2>/dev/null
        echo -e "${GREEN}[OK] 清理完成${NC}"
    fi
}

# 查看状态
status() {
    echo ""
    docker ps -a --filter "name=word2pdf"
    echo ""
    docker-compose ps
}

# 显示菜单
show_menu() {
    echo ""
    echo "==================================="
    echo "Word转PDF服务 - Docker管理"
    echo "==================================="
    echo ""
    echo "1. 构建并启动服务"
    echo "2. 启动已构建的服务"
    echo "3. 停止服务"
    echo "4. 查看日志"
    echo "5. 重新构建并启动"
    echo "6. 完全清理"
    echo "7. 查看服务状态"
    echo "0. 退出"
    echo ""
    read -p "请输入选项 (0-7): " choice
    
    case $choice in
        1) check_docker && check_docker_running && build_start ;;
        2) check_docker && check_docker_running && start ;;
        3) stop ;;
        4) logs ;;
        5) check_docker && rebuild ;;
        6) clean ;;
        7) status ;;
        0) exit 0 ;;
        *) echo -e "${RED}[错误] 无效的选项${NC}" ;;
    esac
}

# 主程序
main() {
    check_docker
    check_docker_running
    
    while true; do
        show_menu
        echo ""
        read -p "按回车键继续..."
    done
}

main
