"""
飞书文件消息处理插件

功能：当用户通过飞书发送文件（docx、pdf、xlsx 等）时，
      自动下载并提取文本内容，让 LLM 能直接读取文件内容。

特点：
- 仅在收到文件消息时才触发，不影响普通文本消息的效率
- 支持 docx、pdf、xlsx、pptx、txt、md 等常见格式
- 自动将文件内容注入到 LLM 上下文中
"""

import os
import json
import tempfile
from pathlib import Path

import astrbot.api.message_components as Comp
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star
from astrbot.core.star.filter.event_message_type import EventMessageType


class LarkFileHandler(Star):
    """飞书文件消息处理器"""

    def __init__(self, context: Context):
        super().__init__(context)
        self.temp_dir = Path(tempfile.gettempdir()) / "lark_files"
        self.temp_dir.mkdir(exist_ok=True)
        # 支持的文件格式
        self.supported_formats = {
            ".docx": "word",
            ".pdf": "pdf",
            ".xlsx": "excel",
            ".pptx": "ppt",
            ".txt": "text",
            ".md": "text",
            ".csv": "text",
            ".json": "text",
            ".py": "text",
            ".js": "text",
            ".ts": "text",
            ".yaml": "text",
            ".yml": "text",
            ".xml": "text",
            ".html": "text",
            ".css": "text",
            ".sql": "text",
            ".log": "text",
        }

    @filter.event_message_type(EventMessageType.ALL, priority=1)
    async def on_file_message(self, event: AstrMessageEvent):
        """拦截文件消息，自动下载并提取内容"""
        try:
            # 获取消息中的文件组件
            file_components = []
            for comp in event.message_obj.message:
                if isinstance(comp, Comp.File):
                    file_components.append(comp)
                elif isinstance(comp, Comp.Image):
                    # 图片文件也尝试处理
                    file_components.append(comp)

            if not file_components:
                # 没有文件组件，直接放行
                return

            logger.info(f"[LarkFile] 收到 {len(file_components)} 个文件，开始处理")

            # 处理每个文件
            file_contents = []
            for comp in file_components:
                content = await self._process_file(comp)
                if content:
                    file_contents.append(content)

            if file_contents:
                # 将文件内容注入到消息上下文中
                combined_content = "\n\n".join(file_contents)
                # 在原始消息后追加文件内容提示
                original_text = event.message_str or ""
                if original_text:
                    event.message_str = f"{original_text}\n\n[文件内容已自动提取，以下是文件内容]\n\n{combined_content}"
                else:
                    event.message_str = f"[文件内容已自动提取，以下是文件内容]\n\n{combined_content}"

                logger.info(f"[LarkFile] 文件内容已注入，总长度: {len(combined_content)}")

        except Exception as e:
            logger.error(f"[LarkFile] 处理文件消息失败: {e}")

    async def _process_file(self, comp) -> str | None:
        """处理单个文件组件，返回提取的文本内容"""
        try:
            file_path = None
            file_name = "unknown"

            if isinstance(comp, Comp.File):
                file_path = comp.file_
                file_name = comp.name or "unknown"
            elif isinstance(comp, Comp.Image):
                file_path = comp.file_
                file_name = "image"

            if not file_path:
                return None

            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.warning(f"[LarkFile] 文件不存在: {file_path}")
                return None

            # 获取文件扩展名
            ext = Path(file_path).suffix.lower()
            if ext not in self.supported_formats:
                logger.info(f"[LarkFile] 不支持的文件格式: {ext}")
                return None

            # 根据格式提取内容
            file_type = self.supported_formats[ext]
            content = None

            if file_type == "text":
                content = await self._read_text_file(file_path)
            elif file_type == "word":
                content = await self._read_docx(file_path)
            elif file_type == "pdf":
                content = await self._read_pdf(file_path)
            elif file_type == "excel":
                content = await self._read_excel(file_path)
            elif file_type == "ppt":
                content = await self._read_pptx(file_path)

            if content:
                return f"📄 **{file_name}** 的内容：\n\n{content}"
            else:
                return None

        except Exception as e:
            logger.error(f"[LarkFile] 处理文件失败: {e}")
            return None

    async def _read_text_file(self, file_path: str) -> str | None:
        """读取文本文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, "r", encoding="gbk") as f:
                return f.read()

    async def _read_docx(self, file_path: str) -> str | None:
        """读取 Word 文档"""
        try:
            from docx import Document
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            # 读取表格
            for table in doc.tables:
                for row in table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    paragraphs.append(" | ".join(cells))
            return "\n".join(paragraphs)
        except Exception as e:
            logger.error(f"[LarkFile] 读取 docx 失败: {e}")
            return None

    async def _read_pdf(self, file_path: str) -> str | None:
        """读取 PDF 文件"""
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"[LarkFile] 读取 pdf 失败: {e}")
            return None

    async def _read_excel(self, file_path: str) -> str | None:
        """读取 Excel 文件"""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            text_parts = []
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                text_parts.append(f"--- Sheet: {sheet_name} ---")
                for row in ws.iter_rows(values_only=True):
                    cells = [str(cell) if cell is not None else "" for cell in row]
                    text_parts.append(" | ".join(cells))
            wb.close()
            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"[LarkFile] 读取 xlsx 失败: {e}")
            return None

    async def _read_pptx(self, file_path: str) -> str | None:
        """读取 PPT 文件"""
        try:
            from pptx import Presentation
            prs = Presentation(file_path)
            text_parts = []
            for i, slide in enumerate(prs.slides, 1):
                text_parts.append(f"--- 第 {i} 页 ---")
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for para in shape.text_frame.paragraphs:
                            text = para.text.strip()
                            if text:
                                text_parts.append(text)
            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"[LarkFile] 读取 pptx 失败: {e}")
            return None


star_cls = LarkFileHandler
