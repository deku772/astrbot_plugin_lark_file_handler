# 飞书文件消息处理插件 v3 for [AstrBot](https://github.com/AstrBotDevs/AstrBot)

当用户通过飞书发送文件（docx、pdf、xlsx 等）时，自动下载并提取文本内容，让 LLM 能直接读取文件内容。

## v3 改进

- **修复内容注入机制**：使用 `event.set_extra/get_extra` 传递文件内容，替代实例变量缓存，避免 session_id 不匹配问题
- **增强远程调试能力**：大幅增加日志输出，handler 触发、文件发现、提取结果每一步都有日志
- **处理 Reply 嵌套文件**：支持引用消息中包含的文件组件
- **更健壮的文件路径获取**：`get_file()` → `file_` → `url` 三级 fallback
- **空 prompt 自动补充提示**：当用户只发文件不附文字时，自动追加"请总结文件内容"
- **简化 on_llm_request 注入**：从 event extra 读取，无需跨 handler 缓存

## v2 改进（仍保留）

- **双路径注入**：同时修改 `event.message_str` 和通过 `on_llm_request` 钩子注入
- **飞书平台过滤**：仅拦截飞书平台消息，不影响其他平台
- **ARM 平台兼容**：PDF 提取优先 pdfplumber，不可用时回退到 PyPDF2
- **文件大小/长度限制**：超过 10MB 跳过，单文件 50K 字符截断

## 安装

将插件文件夹复制到 AstrBot 的 plugins/ 目录下：

```bash
cp -r astrbot_plugin_lark_file_handler /path/to/astrbot/data/plugins/
```

安装依赖：

```bash
pip install -r requirements.txt
```

重启 AstrBot 即可自动加载。

## 故障排查

插件没有反应？检查以下步骤：

1. **确认日志中有 `[LarkFile] 插件已初始化`** — 如果没有，说明插件没被加载
2. **发送文件后查看日志** — 如果没有 `[LarkFile] on_file_message 被触发`，说明 handler 没被调度
3. **handler 不触发可能原因**：
   - 群聊中需要 @机器人 才能触发（取决于 `friend_message_needs_wake_prefix` 配置）
   - 私聊通常自动触发
4. **如果触发但无文件内容** — 检查 `[LarkFile] 发现 X 个文件组件` 日志，确认飞书适配器成功下载了文件

## 支持的文件格式

| 格式 | 说明 |
|------|------|
| .docx | Microsoft Word 文档 |
| .pdf | PDF 文档（pdfplumber 优先，回退 PyPDF2） |
| .xlsx | Microsoft Excel 表格 |
| .pptx | Microsoft PowerPoint 演示文稿 |
| .txt | 纯文本文件 |
| .md | Markdown 文件 |
| .csv | CSV 数据文件 |
| .json | JSON 数据文件 |
| .py / .js / .ts | 源码文件 |
| .yaml / .yml | YAML 配置文件 |
| .xml / .html / .css | 标记/样式文件 |
| .sql | SQL 脚本 |
| .log | 日志文件 |
| .toml / .ini / .conf / .env | 配置文件 |

## 依赖

### 自动安装（AstrBot 加载插件时自动处理）

纯 Python 包，无需编译，所有平台直接安装：

```
python-docx>=0.8.11
PyPDF2>=3.0.0
openpyxl>=3.1.0
python-pptx>=0.6.21
```

### 可选安装（提升 PDF 提取质量）

```bash
pip install pdfplumber>=0.9.0
```

> `pdfplumber` 的 PDF 提取质量优于 PyPDF2，但它依赖 `cryptography`（需要 C 编译工具链）。
> 在 ARM / Alpine 等平台上如果安装失败，**不影响使用**——插件会自动回退到 PyPDF2。
>
> ARM 平台如需安装 pdfplumber，先装系统依赖：
> ```bash
> sudo apt install build-essential libffi-dev python3-dev
> pip install pdfplumber
> ```

## 技术细节

### 内容注入方式

插件采用双路径注入确保内容到达 LLM：

1. **message_str 修改**：在事件处理阶段修改 `event.message_str`，兼容不走 LLM 的场景
2. **on_llm_request 钩子**：通过 `event.set_extra` 传递内容，在 LLM 请求前注入到 `ProviderRequest.prompt`

### 平台过滤

通过 `@filter.platform_adapter_type(PlatformAdapterType.LARK)` 装饰器，确保只在飞书平台触发。

## License

MIT License
