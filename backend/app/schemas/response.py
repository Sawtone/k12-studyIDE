"""
Pydantic数据模型 - 响应模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.common import ModeEnum


# ============================================
# OCR响应模型
# ============================================

class OCRRegion(BaseModel):
    """OCR识别区域"""
    text: str = Field(..., description="识别的文本")
    bounding_box: List[int] = Field(..., description="边界框[x, y, width, height]")
    confidence: float = Field(..., description="置信度")


class OCRResponse(BaseModel):
    """OCR识别响应"""
    text: str = Field(..., description="识别出的文字内容")
    confidence: float = Field(..., description="整体置信度")
    regions: List[OCRRegion] = Field(default=[], description="文字区域信息")
    processing_time_ms: int = Field(..., description="处理时间（毫秒）")


# ============================================
# 调试响应模型
# ============================================

class DebugResponse(BaseModel):
    """断点调试响应"""
    execution_trace: List[Dict[str, Any]] = Field(..., description="执行追踪")
    current_state: Dict[str, Any] = Field(..., description="当前状态")
    insights: List[Dict[str, Any]] = Field(..., description="调试洞察")
    next_possible_actions: List[str] = Field(..., description="下一步可能的操作")
    validation: Dict[str, Any] = Field(..., description="验证结果")


# ============================================
# 步骤拆解响应模型
# ============================================

class DecomposedStep(BaseModel):
    """拆解的步骤"""
    step_number: int = Field(..., description="步骤号")
    content: str = Field(..., description="步骤内容")
    formulas: List[str] = Field(default=[], description="公式列表")
    reasoning: str = Field(..., description="推理说明")


class DecomposeStepsResponse(BaseModel):
    """步骤拆解响应"""
    steps: List[DecomposedStep] = Field(..., description="拆解的步骤列表")


# ============================================
# 编辑历史响应模型
# ============================================

class EditorHistoryItem(BaseModel):
    """编辑历史项"""
    version: int = Field(..., description="版本号")
    content: str = Field(..., description="内容")
    change_type: Optional[str] = Field(None, description="变更类型")
    changed_range: Optional[Dict[str, int]] = Field(None, description="变更范围")
    timestamp: str = Field(..., description="时间戳")


class EditorHistoryResponse(BaseModel):
    """编辑历史响应"""
    history: List[EditorHistoryItem] = Field(..., description="历史记录列表")


# ============================================
# 分页响应模型
# ============================================

class PaginationResponse(BaseModel):
    """分页信息响应"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")


# ============================================
# 会话相关响应模型
# ============================================

class SessionResponse(BaseModel):
    """会话响应"""
    session_id: str = Field(..., description="会话ID")
    mode: ModeEnum = Field(..., description="学习模式")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
    ws_url: str = Field(..., description="WebSocket连接地址")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "mode": "literature",
                "status": "active",
                "created_at": "2025-01-01T12:00:00Z",
                "ws_url": "ws://localhost:8000/ws/session/550e8400-e29b-41d4-a716-446655440000"
            }
        }


class SessionDetailResponse(BaseModel):
    """会话详情响应"""
    session_id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")
    mode: ModeEnum = Field(..., description="学习模式")
    title: Optional[str] = Field(None, description="标题")
    grade_level: Optional[str] = Field(None, description="年级水平")
    status: str = Field(..., description="状态")
    statistics: Dict[str, Any] = Field(..., description="统计信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class SessionListResponse(BaseModel):
    """会话列表响应"""
    sessions: List[Dict[str, Any]] = Field(..., description="会话列表")
    pagination: PaginationResponse = Field(..., description="分页信息")


class EditorSyncResponse(BaseModel):
    """编辑器同步响应"""
    version: int = Field(..., description="版本号")
    saved: bool = Field(..., description="是否保存成功")
    content_hash: str = Field(..., description="内容哈希")
    word_count: int = Field(..., description="字数")


# ============================================
# 文科模式响应模型
# ============================================

class ErrorAnnotation(BaseModel):
    """错误标注"""
    id: str = Field(..., description="错误ID")
    type: str = Field(..., description="错误类型")
    severity: str = Field(..., description="严重程度")
    start_pos: int = Field(..., description="起始位置")
    end_pos: int = Field(..., description="结束位置")
    line_number: Optional[int] = Field(None, description="行号")
    original_text: str = Field(..., description="原文本")
    suggestion: Optional[str] = Field(None, description="建议修改")
    explanation: str = Field(..., description="错误说明")
    confidence: float = Field(..., description="置信度")


class GrammarCheckResponse(BaseModel):
    """语法检查响应"""
    errors: List[ErrorAnnotation] = Field(..., description="错误列表")
    processing_time_ms: int = Field(..., description="处理时间(毫秒)")
    from_cache: bool = Field(..., description="是否来自缓存")


class PolishVersion(BaseModel):
    """润色版本"""
    version: int = Field(..., description="版本号")
    polished_text: str = Field(..., description="润色后的文本")
    style: str = Field(..., description="风格标签")
    changes: List[str] = Field(..., description="变更说明")
    reasoning: str = Field(..., description="润色理由")


class PolishResponse(BaseModel):
    """文本润色响应"""
    versions: List[PolishVersion] = Field(..., description="润色版本列表")
    recommended: int = Field(..., description="推荐版本号")
    recommendation_reason: str = Field(..., description="推荐理由")


class StructureNode(BaseModel):
    """结构节点"""
    id: str = Field(..., description="节点ID")
    type: str = Field(..., description="节点类型")
    title: str = Field(..., description="标题")
    summary: Optional[str] = Field(None, description="摘要")
    start_pos: int = Field(..., description="起始位置")
    end_pos: int = Field(..., description="结束位置")
    children: List['StructureNode'] = Field(default=[], description="子节点")


class StructureAnalyzeResponse(BaseModel):
    """结构分析响应"""
    structure_type: str = Field(..., description="结构类型")
    overall_pattern: str = Field(..., description="整体模式")
    tree: StructureNode = Field(..., description="结构树")
    relationships: List[Dict[str, str]] = Field(..., description="关系列表")


class DimensionScore(BaseModel):
    """维度评分"""
    score: float = Field(..., description="分数")
    reasoning: str = Field(..., description="评分理由")
    issues: List[str] = Field(..., description="问题列表")
    suggestions: List[str] = Field(..., description="建议列表")


class HealthScoreResponse(BaseModel):
    """健康度评分响应"""
    overall_score: float = Field(..., description="总分")
    grade: str = Field(..., description="等级")
    dimensions: Dict[str, DimensionScore] = Field(..., description="各维度评分")
    top_priorities: List[str] = Field(..., description="优先改进项")
    strengths: List[str] = Field(..., description="优势")


# ============================================
# 理科模式响应模型
# ============================================

class StepValidation(BaseModel):
    """步骤验证结果"""
    step_number: int = Field(..., description="步骤号")
    is_valid: bool = Field(..., description="是否有效")
    symbolic_form: str = Field(..., description="符号化形式")
    variables_state: Dict[str, Any] = Field(..., description="变量状态")
    errors: List[Dict[str, str]] = Field(..., description="错误列表")
    next_step_hint: Optional[str] = Field(None, description="下一步提示")


class ValidateStepsResponse(BaseModel):
    """验证步骤响应"""
    validation_results: List[StepValidation] = Field(..., description="验证结果")
    overall_assessment: Dict[str, Any] = Field(..., description="整体评估")


class LogicTreeResponse(BaseModel):
    """逻辑树响应"""
    problem_analysis: Dict[str, Any] = Field(..., description="问题分析")
    logic_tree: Dict[str, Any] = Field(..., description="逻辑树")
    derivation_paths: List[Dict[str, Any]] = Field(..., description="推导路径")
    suggestions: List[str] = Field(..., description="建议")


# ============================================
# 对话相关响应模型
# ============================================

class ChatMessageResponse(BaseModel):
    """聊天消息响应"""
    message_id: int = Field(..., description="消息ID")
    role: str = Field(..., description="角色")
    content: str = Field(..., description="内容")
    message_type: Optional[str] = Field(None, description="消息类型")
    action_items: List[str] = Field(default=[], description="可操作建议")
    created_at: datetime = Field(..., description="创建时间")


class ChatHistoryResponse(BaseModel):
    """聊天历史响应"""
    messages: List[ChatMessageResponse] = Field(..., description="消息列表")
    has_more: bool = Field(..., description="是否有更多")


# ============================================
# OCR相关响应模型
# ============================================

class OCRResponse(BaseModel):
    """OCR识别响应"""
    text: str = Field(..., description="识别出的文字")
    confidence: float = Field(..., description="置信度")
    processing_time_ms: int = Field(..., description="处理时间(毫秒)")


# ============================================
# 系统相关响应模型
# ============================================

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="状态")
    version: str = Field(..., description="版本")
    services: Dict[str, str] = Field(..., description="服务状态")


class CapabilitiesResponse(BaseModel):
    """系统能力响应"""
    modes: List[str] = Field(..., description="支持的模式")
    literature_capabilities: List[Dict[str, Any]] = Field(..., description="文科能力")
    science_capabilities: List[Dict[str, Any]] = Field(..., description="理科能力")
    limits: Dict[str, Any] = Field(..., description="限制")
