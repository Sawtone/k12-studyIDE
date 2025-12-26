"""
OCR识别Agent
使用Qwen视觉模型进行图片文字识别
"""

from typing import Any, Dict
import base64

from app.services.agents.base import BaseAgent, AgentConfig, AgentResult
from app.services.llm.model_router import TaskType


class OCRAgent(BaseAgent):
    """
    OCR识别Agent

    功能：
    1. 图片文字识别
    2. 手写识别
    3. 支持中英文
    4. 返回识别结果和置信度
    """

    def __init__(self, language: str = "zh", recognize_handwriting: bool = False, **kwargs) -> None:
        """
        初始化OCR Agent

        Args:
            language: 识别语言 (zh/en/auto)
            recognize_handwriting: 是否识别手写
        """
        config = AgentConfig(
            name="ocr_agent",
            task_type=TaskType.OCR,
            temperature=0.1,  # OCR需要精确
            enable_cache=True
        )
        super().__init__(config)
        self.language = language
        self.recognize_handwriting = recognize_handwriting

    @property
    def system_prompt(self) -> str:
        """系统提示词"""
        return """你是一个专业的OCR识别助手，擅长识别图片中的文字内容。

## 你的能力
- 识别印刷体文字
- 识别手写文字
- 支持中文和英文
- 保持原文的格式和结构

## 识别原则
1. 准确识别每个字符
2. 保持原文的段落结构
3. 标注不确定的字符
4. 给出整体置信度

## 输出格式
请直接返回识别出的文字内容，保持原文的格式。
如果有不确定的字符，用[?]标注。
"""

    @staticmethod
    def build_user_prompt(**kwargs: Any) -> str:
        """
        构建用户提示词

        Args:
            language: 语言 (zh/en/auto)
            recognize_handwriting: 是否识别手写

        Returns:
            用户提示词
        """
        language = kwargs.get("language", "auto")
        recognize_handwriting = kwargs.get("recognize_handwriting", False)

        language_map = {
            "zh": "中文",
            "en": "英文",
            "auto": "自动检测语言"
        }

        prompt = f"""请识别图片中的文字内容。

## 识别要求
- 语言：{language_map.get(language, language)}
- 手写识别：{'是' if recognize_handwriting else '否'}

## 注意事项
1. 准确识别每个字符
2. 保持原文的段落和格式
3. 对于不确定的字符，用[?]标注
4. 如果是手写文字，尽量识别潦草的字迹

请开始识别。
"""
        return prompt

    async def run(self, **kwargs: Any) -> AgentResult:
        """
        执行OCR识别

        Args:
            image_url: 图片URL或base64编码（可选）
            image_data: 图片二进制数据（可选）
            image_filename: 图片文件名（可选）
            language: 语言
            recognize_handwriting: 是否识别手写

        Returns:
            AgentResult对象
        """
        import time
        import base64

        start_time = time.time()

        try:
            # 验证输入
            self.validate_inputs(**kwargs)

            # 处理图片数据
            image_url = kwargs.get("image_url", "")
            image_data = kwargs.get("image_data")

            # 如果提供了image_data，转换为base64 data URL
            if image_data and not image_url:
                # 检测图片类型
                image_filename = kwargs.get("image_filename", "image.jpg")
                if image_filename.lower().endswith('.png'):
                    mime_type = "image/png"
                elif image_filename.lower().endswith('.jpg') or image_filename.lower().endswith('.jpeg'):
                    mime_type = "image/jpeg"
                elif image_filename.lower().endswith('.gif'):
                    mime_type = "image/gif"
                elif image_filename.lower().endswith('.webp'):
                    mime_type = "image/webp"
                else:
                    mime_type = "image/jpeg"  # 默认

                # 转换为base64
                base64_data = base64.b64encode(image_data).decode('utf-8')
                image_url = f"data:{mime_type};base64,{base64_data}"

            language = kwargs.get("language", "auto")

            # 构建提示词
            user_prompt = self.build_user_prompt(**kwargs)

            # 使用Qwen视觉模型进行OCR
            result_text = await self.llm.analyze_image(
                image_url=image_url,
                prompt=user_prompt,
                model=self.llm.ocr_model
            )

            # 计算置信度（简单估算）
            confidence = self._estimate_confidence(result_text)

            execution_time_ms = (time.time() - start_time) * 1000

            return AgentResult(
                success=True,
                data={
                    "text": result_text,
                    "confidence": confidence,
                    "language": language
                },
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "agent": self.config.name
                }
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"OCR识别失败: {str(e)}")

            return AgentResult(
                success=False,
                data=None,
                error=str(e),
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "agent": self.config.name
                }
            )

    @staticmethod
    def _estimate_confidence(text: str) -> float:
        """
        估算识别置信度

        Args:
            text: 识别结果文本

        Returns:
            置信度 (0-1)
        """
        if not text:
            return 0.0

        # 统计不确定字符的数量
        uncertain_count = text.count("[?]")
        total_chars = len(text)

        if total_chars == 0:
            return 0.0

        # 简单估算：不确定字符越少，置信度越高
        confidence = 1.0 - (uncertain_count / total_chars)
        return max(0.0, min(1.0, confidence))

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析AI响应

        Args:
            response: AI响应文本

        Returns:
            解析后的结构化数据
        """
        # OCR直接返回文本，不需要JSON解析
        return {
            "text": response.strip(),
            "confidence": self._estimate_confidence(response)
        }

    @staticmethod
    def validate_inputs(**kwargs: Any) -> None:
        """验证输入参数"""
        image_url = kwargs.get("image_url")
        image_data = kwargs.get("image_data")

        # 必须提供image_url或image_data之一
        if not image_url and not image_data:
            raise ValueError("必须提供image_url或image_data参数")

        # 如果提供了image_url，验证格式
        if image_url:
            if not isinstance(image_url, str):
                raise ValueError("image_url必须是字符串类型")

            # 验证是否为有效的URL或base64
            if not (image_url.startswith("http://") or
                    image_url.startswith("https://") or
                    image_url.startswith("data:image/")):
                raise ValueError("image_url必须是有效的URL或base64编码")

        # 如果提供了image_data，验证类型
        if image_data:
            if not isinstance(image_data, bytes):
                raise ValueError("image_data必须是bytes类型")
