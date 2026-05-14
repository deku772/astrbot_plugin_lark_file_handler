# Changelog

All notable changes to this project will be documented in this file.

---

## v3.1.0 - 2026-05-14

### Fixed
- 修复内容注入机制：使用 `event.set_extra/get_extra` 传递文件内容，替代实例变量缓存，避免 session_id 不匹配
- 修复 README 不被 AstrBot 识别的问题（确保文件在仓库根目录）

### Added
- 增加详细的 INFO 级别日志输出，方便远程排查 handler 是否被触发
- 增加 `CHANGELOG.md` 和 `LICENSE` 文件
- 支持 Reply 消息中嵌套的文件组件提取
- 空消息时自动追加"请总结文件内容"提示

### Changed
- 文件路径获取改为三级 fallback：`get_file()` → `file_` → `url`
- 简化 `on_llm_request` 注入逻辑，从 event extra 读取而非实例缓存

---

## v2.0.0 - 2026-05-14

### Added
- 双路径注入：同时修改 `event.message_str` 和通过 `on_llm_request` 钩子注入
- 飞书平台过滤：`@filter.platform_adapter_type(PlatformAdapterType.LARK)`
- ARM 平台兼容：PDF 提取 pdfplumber → PyPDF2 fallback
- 文件大小限制（10MB）+ 内容长度截断（50K 字符）
- `requirements.txt` 声明依赖

---

## v1.0.0 - 2026-05-14

### Added
- 初始版本：基本的飞书文件消息处理功能
- 支持 docx, pdf, xlsx, pptx, txt, md 等格式
- 通过修改 `event.message_str` 注入文件内容

---

> This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
