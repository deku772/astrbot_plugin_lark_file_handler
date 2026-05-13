# astrbot_plugin_lark_file_handler

> 飞书文件消息处理插件 for [AstrBot](https://github.com/AstrBotDevs/AstrBot)

## ✨ 功能

当用户通过飞书发送文件（docx、pdf、xlsx 等）时，自动下载并提取文本内容，让 LLM 能直接读取文件内容。

- 仅在收到文件消息时才触发，**不影响普通文本消息的效率**
- 支持 docx、pdf、xlsx、pptx、txt、md 等常见格式
- 自动将文件内容注入到 LLM 上下文中

## 📦 安装

将插件文件夹复制到 AstrBot 的 `plugins/` 目录下：

```bash
cp -r astrbot_plugin_lark_file_handler /path/to/astrbot/data/plugins/
```

重启 AstrBot 即可自动加载。

## 📋 支持的文件格式

| 格式 | 说明 |
|------|------|
| `.docx` | Microsoft Word 文档 |
| `.pdf` | PDF 文档 |
| `.xlsx` | Microsoft Excel 表格 |
| `.pptx` | Microsoft PowerPoint 演示文稿 |
| `.txt` | 纯文本文件 |
| `.md` | Markdown 文件 |
| `.csv` | CSV 数据文件 |
| `.json` | JSON 数据文件 |
| `.py` | Python 源码 |
| `.js` | JavaScript 源码 |
| `.ts` | TypeScript 源码 |
| `.yaml` / `.yml` | YAML 配置文件 |
| `.xml` | XML 文件 |
| `.html` | HTML 文件 |
| `.css` | CSS 样式文件 |
| `.sql` | SQL 脚本 |
| `.log` | 日志文件 |

## 🔧 依赖

插件运行需要以下 Python 库（按需安装）：

```bash
pip install python-docx pdfplumber openpyxl python-pptx
```

## 📖 使用方式

安装后无需额外配置，直接在飞书中发送文件给 Bot 即可。插件会自动拦截文件消息，提取文本内容后交给 LLM 处理。

示例：
- 用户发送一个 `.docx` 文件
- 插件自动提取文档内容
- LLM 可以基于文档内容回答用户问题

## 📄 许可证

MIT License
