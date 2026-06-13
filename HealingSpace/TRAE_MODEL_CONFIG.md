# Trae 模型配置指南

## DeepSeek API Key 配置

您的 DeepSeek API Key: `从环境变量 DEEPSEEK_API_KEY 获取`

## 在 Trae IDE 中配置 DeepSeek-V4 模型

### 第一步：打开设置
1. 点击 Trae IDE 左下角的头像
2. 选择"设置"（Settings）

### 第二步：添加模型
1. 在设置页面中，点击左侧菜单的"模型"（Models）
2. 点击"添加模型"（Add Model）按钮

### 第三步：选择模型服务商
1. 在弹窗中选择"模型服务商"（Model Provider）
2. 从下拉列表中选择"DeepSeek"

### 第四步：填写 API Key
1. 在"API 密钥"（API Key）输入框中填入您的 DeepSeek API Key
   ```
   请从环境变量 DEEPSEEK_API_KEY 获取您的 API Key
   ```

### 第五步：选择模型
1. 展开"高级配置"（Advanced Settings）
2. 在"模型系列"（Model Series）中选择"DeepSeek-V4"
3. 或选择"deepseek-chat"作为通用对话模型

### 第六步：保存配置
1. 点击"保存"或"确认"按钮
2. 等待模型配置完成

## 验证配置

配置完成后，您可以通过以下方式验证：
1. 在 Trae IDE 中打开 AI 对话功能
2. 选择刚配置的 DeepSeek 模型
3. 发送一条测试消息确认连接正常

## 常见问题

### Q: 没有看到"模型"选项？
A: 确保使用的是最新版本的 Trae IDE，如果没有可以检查更新。

### Q: API Key 格式错误？
A: 确保复制的 API Key 完整，没有多余的空格或换行。

### Q: 连接失败？
A: 检查网络连接是否正常，或者 API Key 是否过期。

## 项目中使用

配置完成后，在项目中：
1. 设置环境变量：`export DEEPSEEK_API_KEY=您的API密钥`
2. 重启开发服务器：`npm run dev`
3. 访问 http://localhost:5173/
4. 点击右下角"开始倾诉"按钮测试 AI 对话功能

## 技术支持

如果配置过程中遇到问题，请参考 Trae 官方文档或联系技术支持。
