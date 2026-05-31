# Word 转 PDF 服务测试指南

## 📁 测试文件

我们已在 `test_data/` 目录下生成了测试文件：
- `test_file_1.docx` - 第一个测试文件
- `test_file_2.docx` - 第二个测试文件  
- `test_file_3.docx` - 第三个测试文件

## 🚀 快速开始

### 1. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

### 2. 访问网页界面

打开浏览器访问：`http://localhost:8000`

### 3. 访问 API 文档

打开浏览器访问：`http://localhost:8000/docs`

## 🧪 测试方法

### 方法一：使用网页界面（推荐）

1. 打开 `http://localhost:8000`
2. 选择「单个文件」或「批量转换」
3. 上传 `test_data/` 目录下的测试文件
4. 点击「开始转换」
5. 下载转换结果

### 方法二：使用测试脚本

```bash
# 确保服务正在运行，然后执行：
python test_api.py
```

### 方法三：使用 curl

测试单个文件转换：
```bash
curl -X POST "http://localhost:8000/convert/single" \
  -F "file=@test_data/test_file_1.docx" \
  --output test_output.pdf
```

测试批量转换：
```bash
curl -X POST "http://localhost:8000/convert/batch" \
  -F "files=@test_data/test_file_1.docx" \
  -F "files=@test_data/test_file_2.docx" \
  -F "files=@test_data/test_file_3.docx" \
  --output test_output.zip
```

## 📋 测试清单

- [ ] 服务正常启动
- [ ] 网页界面可以访问
- [ ] 单个文件可以上传和转换
- [ ] 批量文件可以上传和转换
- [ ] 转换结果可以正常下载
- [ ] API 文档可以访问

## 🐛 常见问题

### Windows 下转换失败
确保已安装 Microsoft Word 或 LibreOffice

### Linux 下转换失败
确保已安装 LibreOffice：
```bash
sudo apt-get install libreoffice
```

### 依赖安装失败
```bash
pip install -r requirements.txt
```
