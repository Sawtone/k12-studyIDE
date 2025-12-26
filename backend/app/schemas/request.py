"""
Pydantic数据模型 - 请求模型
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.common import ModeEnum, GradeLevelEnum, CursorPosition, Selection


# ============================================
# 会话相关请求模型
# ============================================

class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    user_id: str = Field(..., description="用户ID", example="user_12345")
    mode: Optional[ModeEnum] = Field(None, description="学习模式")
    title: Optional[str] = Field(None, description="会话标题", max_length=200)
    grade_level: Optional[GradeLevelEnum] = Field(None, description="年级水平")
    subject: Optional[str] = Field(None, description="学科", example="数学")


class UpdateSessionRequest(BaseModel):
    """更新会话请求"""
    title: Optional[str] = Field(None, description="会话标题", max_length=200)
    status: Optional[str] = Field(None, description="状态")
    mode: Optional[ModeEnum] = Field(None, description="学习模式")


class SyncEditorRequest(BaseModel):
    """同步编辑器状态请求"""
    content: str = Field(..., description="内容文本")
    cursor_position: Optional[CursorPosition] = Field(None, description="光标位置")
    selections: Optional[List[Selection]] = Field(None, description="选择区域")
    version: Optional[int] = Field(None, description="版本号")


# ============================================
# 文科模式请求模型
# ============================================

class GrammarCheckRequest(BaseModel):
    """语法检查请求"""
    session_id: str = Field(..., description="会话ID")
    content: Optional[str] = Field(None, description="要检查的内容")
    language: str = Field(default="zh", description="语言", example="zh")
    check_types: List[str] = Field(
        default=["typo", "grammar", "style"],
        description="检查类型"
    )
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


class PolishRequest(BaseModel):
    """文本润色请求"""
    session_id: str = Field(..., description="会话ID")
    text: str = Field(..., description="要润色的文本")
    polish_direction: str = Field(
        default="enhance_fluency",
        description="润色方向"
    )
    target_style: str = Field(default="formal", description="目标风格")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文")


class StructureAnalyzeRequest(BaseModel):
    """结构分析请求"""
    session_id: str = Field(..., description="会话ID")
    content: Optional[str] = Field(None, description="文章内容")


class HealthScoreRequest(BaseModel):
    """健康度评分请求"""
    session_id: str = Field(..., description="会话ID")
    content: Optional[str] = Field(None, description="文章内容")


# ============================================
# 理科模式请求模型
# ============================================

class MathStep(BaseModel):
    """数学步骤"""
    step_number: int = Field(..., description="步骤号")
    content: str = Field(..., description="步骤内容")
    formula: Optional[str] = Field(None, description="公式")


class ValidateStepsRequest(BaseModel):
    """验证数学步骤请求"""
    session_id: str = Field(..., description="会话ID")
    problem_statement: str = Field(..., description="问题描述")
    steps: List[MathStep] = Field(..., description="解题步骤")


class BuildLogicTreeRequest(BaseModel):
    """构建逻辑树请求"""
    session_id: str = Field(..., description="会话ID")
    problem_statement: str = Field(..., description="问题描述")
    existing_steps: Optional[List[str]] = Field(None, description="已有的推导")


# ============================================
# 对话相关请求模型
# ============================================

class ChatMessageRequest(BaseModel):
    """发送聊天消息请求"""
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="消息内容", max_length=2000)
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


class ChatFeedbackRequest(BaseModel):
    """聊天反馈请求"""
    message_id: int = Field(..., description="消息ID")
    is_helpful: Optional[bool] = Field(None, description="是否有帮助")
    rating: Optional[int] = Field(None, description="评分(1-5)", ge=1, le=5)
    feedback: Optional[str] = Field(None, description="反馈内容")


# ============================================
# OCR相关请求模型
# ============================================

class OCRRequest(BaseModel):
    """OCR识别请求"""
    session_id: Optional[str] = Field(None, description="会话ID")
    image_url: str = Field(..., description="图片URL或base64")
    language: str = Field(default="auto", description="语言")
    recognize_handwriting: bool = Field(default=False, description="是否识别手写")


# ============================================
# 反馈相关请求模型
# ============================================

class AcceptFeedbackRequest(BaseModel):
    """接受AI建议请求"""
    session_id: str = Field(..., description="会话ID")
    target_type: str = Field(..., description="目标类型", example="error")
    target_id: str = Field(..., description="目标ID", example="err_001")
    action: str = Field(..., description="操作类型", example="applied")
    modified_content: Optional[str] = Field(None, description="修改后的内容")


class RejectFeedbackRequest(BaseModel):
    """拒绝AI建议请求"""
    session_id: str = Field(..., description="会话ID")
    target_type: str = Field(..., description="目标类型", example="error")
    target_id: str = Field(..., description="目标ID", example="err_001")
    reason: str = Field(..., description="拒绝原因")
    comment: Optional[str] = Field(None, description="备注")


class ReportIssueRequest(BaseModel):
    """报告问题请求"""
    session_id: str = Field(..., description="会话ID")
    issue_type: str = Field(..., description="问题类型", example="incorrect_analysis")
    description: str = Field(..., description="问题描述")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


# ============================================
# 会话操作请求模型
# ============================================

class RestoreSessionRequest(BaseModel):
    """恢复会话到指定版本请求"""
    version: int = Field(..., description="目标版本号", ge=1)


class DecomposeStepsRequest(BaseModel):
    """题目拆解为步骤请求"""
    session_id: str = Field(..., description="会话ID")
    problem_text: str = Field(..., description="题目文本")


class DebugRequest(BaseModel):
    """断点调试请求"""
    session_id: str = Field(..., description="会话ID")
    breakpoint_step_number: int = Field(..., description="断点步骤号", ge=1)
    problem_statement: str = Field(..., description="问题描述")
    steps: List[MathStep] = Field(..., description="解题步骤")
