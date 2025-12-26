"""
数据库模型定义
使用SQLAlchemy ORM定义所有数据表
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, BigInteger, Float, Boolean, Text,
    DateTime, ForeignKey, Index, CheckConstraint, ARRAY, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database.connection import Base


# ============================================
# 会话管理相关表
# ============================================

class Session(Base):
    """会话表"""
    __tablename__ = "sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    mode = Column(String(20), nullable=False, index=True)
    title = Column(Text, nullable=True)

    # 元数据
    grade_level = Column(String(20), nullable=True)  # 'primary', 'middle', 'high'
    subject = Column(String(50), nullable=True)

    # 状态
    status = Column(String(20), default='active', index=True)

    # 统计
    total_interactions = Column(Integer, default=0)
    total_ai_calls = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    editor_states = relationship("EditorState", back_populates="session", cascade="all, delete-orphan")
    literature_analyses = relationship("LiteratureAnalysis", back_populates="session", cascade="all, delete-orphan")
    error_annotations = relationship("ErrorAnnotation", back_populates="session", cascade="all, delete-orphan")
    document_structures = relationship("DocumentStructure", back_populates="session", cascade="all, delete-orphan")
    math_steps = relationship("MathStep", back_populates="session", cascade="all, delete-orphan")
    logic_tree_nodes = relationship("LogicTreeNode", back_populates="session", cascade="all, delete-orphan")
    debug_sessions = relationship("DebugSession", back_populates="session", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    user_actions = relationship("UserAction", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("mode IN ('literature', 'science')", name='check_mode'),
        CheckConstraint("status IN ('active', 'archived', 'deleted')", name='check_status'),
        Index('idx_user_mode', 'user_id', 'mode'),
        Index('idx_created_at_desc', 'created_at', postgresql_using='btree', postgresql_ops={'created_at': 'DESC'}),
    )


class EditorState(Base):
    """编辑器状态表"""
    __tablename__ = "editor_states"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)

    # 内容
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=True, index=True)
    word_count = Column(Integer, nullable=True)

    # 光标和选择
    cursor_position = Column(JSONB, nullable=True)
    selections = Column(ARRAY(JSONB), nullable=True)

    # 版本控制
    version = Column(Integer, nullable=False, default=1)
    parent_version = Column(Integer, nullable=True)

    # 变更信息
    change_type = Column(String(20), nullable=True)
    changed_range = Column(JSONB, nullable=True)

    # 时间戳
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    session = relationship("Session", back_populates="editor_states")

    __table_args__ = (
        Index('idx_session_version', 'session_id', 'version'),
    )


# ============================================
# 文科模式相关表
# ============================================

class LiteratureAnalysis(Base):
    """文章分析结果表"""
    __tablename__ = "literature_analysis"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)

    # 分析类型和版本
    analysis_type = Column(String(50), nullable=False)
    content_version = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=True, index=True)

    # 结果数据
    results = Column(JSONB, nullable=False)

    # 元信息
    processing_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String(50), nullable=True)

    # 缓存控制
    is_cached = Column(Boolean, default=False)
    cache_hit_count = Column(Integer, default=0)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    session = relationship("Session", back_populates="literature_analyses")

    __table_args__ = (
        Index('idx_session_analysis', 'session_id', 'analysis_type'),
        Index('idx_cache_key', 'session_id', 'analysis_type', 'content_hash', unique=True),
    )


class ErrorAnnotation(Base):
    """错误标注表"""
    __tablename__ = "error_annotations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)
    content_version = Column(Integer, nullable=False)

    # 错误信息
    error_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), default='medium')

    # 位置
    start_pos = Column(Integer, nullable=False)
    end_pos = Column(Integer, nullable=False)
    line_number = Column(Integer, nullable=True)

    # 内容
    original_text = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)

    # 置信度
    confidence = Column(Float, nullable=True)

    # 用户反馈
    status = Column(String(20), default='pending', index=True)
    user_action = Column(String(20), nullable=True)
    user_feedback = Column(Text, nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    session = relationship("Session", back_populates="error_annotations")

    __table_args__ = (
        CheckConstraint("severity IN ('low', 'medium', 'high')", name='check_severity'),
        CheckConstraint("status IN ('pending', 'accepted', 'rejected', 'ignored')", name='check_status'),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name='check_confidence'),
        Index('idx_session_version', 'session_id', 'content_version'),
    )


class DocumentStructure(Base):
    """文档结构树表"""
    __tablename__ = "document_structure"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)
    content_version = Column(Integer, nullable=False)

    # 节点信息
    node_type = Column(String(50), nullable=False)
    node_id = Column(String(100), nullable=True)

    # 层次关系
    parent_id = Column(BigInteger, ForeignKey('document_structure.id', ondelete='CASCADE'), nullable=True)
    level = Column(Integer, nullable=False)
    position_in_parent = Column(Integer, nullable=True)

    # 内容
    content_summary = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)

    # 位置映射
    start_pos = Column(Integer, nullable=False)
    end_pos = Column(Integer, nullable=False)

    # 分析结果
    analysis_data = Column(JSONB, nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    session = relationship("Session", back_populates="document_structures")
    children = relationship("DocumentStructure", backref="parent", remote_side=[id])

    __table_args__ = (
        Index('idx_session_structure', 'session_id', 'content_version'),
        Index('idx_hierarchy', 'parent_id', 'position_in_parent'),
        Index('idx_position', 'start_pos', 'end_pos'),
    )


# ============================================
# 理科模式相关表
# ============================================

class MathStep(Base):
    """数学步骤表"""
    __tablename__ = "math_steps"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)
    content_version = Column(Integer, nullable=False)

    # 步骤信息
    step_number = Column(Integer, nullable=False)
    step_order = Column(Integer, nullable=False)

    # 内容
    step_content = Column(Text, nullable=False)
    formula = Column(Text, nullable=True)
    formula_rendered = Column(Text, nullable=True)

    # 符号表示
    symbolic_form = Column(JSONB, nullable=True)

    # 变量状态
    variables_before = Column(JSONB, nullable=True)
    variables_after = Column(JSONB, nullable=True)
    variables_introduced = Column(ARRAY(Text), nullable=True)

    # 验证结果
    is_valid = Column(Boolean, nullable=True)
    validation_details = Column(JSONB, nullable=True)

    # 错误信息
    errors = Column(ARRAY(JSONB), nullable=True)
    warnings = Column(ARRAY(JSONB), nullable=True)

    # 关联
    parent_step_id = Column(BigInteger, ForeignKey('math_steps.id'), nullable=True)
    depends_on_steps = Column(ARRAY(Integer), nullable=True)

    # 提示
    next_step_hint = Column(Text, nullable=True)
    alternative_approaches = Column(ARRAY(JSONB), nullable=True)

    # 位置
    start_pos = Column(Integer, nullable=True)
    end_pos = Column(Integer, nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    session = relationship("Session", back_populates="math_steps")
    substeps = relationship("MathStep", backref="parent_step", remote_side=[id])

    __table_args__ = (
        Index('idx_session_steps', 'session_id', 'step_order'),
    )


class LogicTreeNode(Base):
    """逻辑树表"""
    __tablename__ = "logic_tree_nodes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)
    content_version = Column(Integer, nullable=False)

    # 节点信息
    node_id = Column(String(100), nullable=False)
    node_type = Column(String(50), nullable=False, index=True)

    # 内容
    content = Column(Text, nullable=False)
    symbolic_form = Column(JSONB, nullable=True)
    description = Column(Text, nullable=True)

    # 层次关系
    parent_id = Column(BigInteger, ForeignKey('logic_tree_nodes.id'), nullable=True)
    level = Column(Integer, nullable=False)
    position = Column(JSONB, nullable=True)

    # 依赖关系
    depends_on = Column(ARRAY(String(100)), nullable=True)
    required_by = Column(ARRAY(String(100)), nullable=True)

    # 状态
    status = Column(String(20), nullable=False)
    completion_percentage = Column(Float, nullable=True)

    # 推理信息
    reasoning = Column(Text, nullable=True)
    formula_used = Column(Text, nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    session = relationship("Session", back_populates="logic_tree_nodes")
    children = relationship("LogicTreeNode", backref="parent", remote_side=[id])

    __table_args__ = (
        CheckConstraint("status IN ('complete', 'incomplete', 'missing', 'invalid')", name='check_status'),
        Index('idx_session_tree', 'session_id', 'content_version'),
        Index('idx_node_id', 'session_id', 'node_id'),
        Index('idx_node_type_status', 'node_type', 'status'),
    )


class DebugSession(Base):
    """断点调试会话表"""
    __tablename__ = "debug_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)

    # 断点信息
    breakpoint_step_id = Column(BigInteger, ForeignKey('math_steps.id'), nullable=True)
    breakpoint_step_number = Column(Integer, nullable=True)

    # 执行追踪
    execution_trace = Column(JSONB, nullable=False)

    # 当前状态快照
    current_state = Column(JSONB, nullable=False)

    # 调试建议
    insights = Column(ARRAY(JSONB), nullable=True)
    warnings = Column(ARRAY(JSONB), nullable=True)
    next_actions = Column(ARRAY(JSONB), nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    session = relationship("Session", back_populates="debug_sessions")

    __table_args__ = (
        Index('idx_session_debug', 'session_id', 'created_at', postgresql_ops={'created_at': 'DESC'}),
    )


# ============================================
# 对话和交互相关表
# ============================================

class ChatMessage(Base):
    """聊天消息表"""
    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)

    # 消息内容
    role = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)

    # 上下文信息
    context = Column(JSONB, nullable=True)

    # 元信息
    message_type = Column(String(50), nullable=True)
    related_agent = Column(String(50), nullable=True)

    # Token使用
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String(50), nullable=True)

    # 引用关系
    reply_to_message_id = Column(BigInteger, ForeignKey('chat_messages.id'), nullable=True)
    related_analysis_id = Column(BigInteger, nullable=True)

    # 用户反馈
    user_rating = Column(Integer, nullable=True)
    user_feedback = Column(Text, nullable=True)
    is_helpful = Column(Boolean, nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    session = relationship("Session", back_populates="chat_messages")
    replies = relationship("ChatMessage", backref="reply_to", remote_side=[id])

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_role'),
        CheckConstraint("user_rating >= 1 AND user_rating <= 5", name='check_rating'),
        Index('idx_session_messages', 'session_id', 'created_at'),
    )


# ============================================
# 用户反馈和学习数据表
# ============================================

class UserAction(Base):
    """用户操作日志表"""
    __tablename__ = "user_actions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)

    # 操作信息
    action_type = Column(String(50), nullable=False, index=True)
    target_type = Column(String(50), nullable=True)
    target_id = Column(String(255), nullable=True)  # Changed from BigInteger to String to support error IDs like "err_001"

    # 操作详情
    action_data = Column(JSONB, nullable=True)

    # 上下文
    editor_state_id = Column(BigInteger, ForeignKey('editor_states.id'), nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    session = relationship("Session", back_populates="user_actions")

    __table_args__ = (
        Index('idx_session_actions', 'session_id', 'created_at'),
    )


class UserLearningProgress(Base):
    """学习进度表"""
    __tablename__ = "user_learning_progress"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)

    # 领域和技能
    subject = Column(String(50), nullable=False)
    skill_type = Column(String(100), nullable=False)

    # 统计
    total_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

    # 掌握度
    mastery_level = Column(Float, default=0.0)
    last_practice_at = Column(DateTime(timezone=True), nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("mastery_level >= 0 AND mastery_level <= 1", name='check_mastery'),
        Index('idx_user_skill', 'user_id', 'subject', 'skill_type', unique=True),
        Index('idx_mastery', 'user_id', 'mastery_level'),
    )
