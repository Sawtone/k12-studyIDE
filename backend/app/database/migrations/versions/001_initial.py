"""
初始数据库迁移
创建所有表结构

Revision ID: 001_initial
Revises:
Create Date: 2025-01-20 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建所有表"""

    # ============================================
    # 会话管理相关表
    # ============================================

    # 会话表
    op.create_table(
        'sessions',
        sa.Column('session_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('mode', sa.String(20), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('grade_level', sa.String(20), nullable=True),
        sa.Column('subject', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('total_interactions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_ai_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("mode IN ('literature', 'science')", name='sessions_mode_check'),
        sa.CheckConstraint("status IN ('active', 'archived', 'deleted')", name='sessions_status_check')
    )

    # 创建索引
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('idx_sessions_mode', 'sessions', ['mode'])
    op.create_index('idx_sessions_status', 'sessions', ['status'])
    op.create_index('idx_sessions_created_at', 'sessions', ['created_at'], postgresql_ops={'created_at': 'DESC'})

    # 编辑器状态表
    op.create_table(
        'editor_states',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('cursor_position', postgresql.JSONB(), nullable=True),
        sa.Column('selections', postgresql.ARRAY(postgresql.JSONB()), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('parent_version', sa.Integer(), nullable=True),
        sa.Column('change_type', sa.String(20), nullable=True),
        sa.Column('changed_range', postgresql.JSONB(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE')
    )

    # 创建索引
    op.create_index('idx_editor_states_session_id', 'editor_states', ['session_id'])
    op.create_index('idx_editor_states_version', 'editor_states', ['session_id', 'version'])
    op.create_index('idx_editor_states_content_hash', 'editor_states', ['content_hash'])

    # ============================================
    # 文科模式相关表
    # ============================================

    # 文章分析结果表
    op.create_table(
        'literature_analysis',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_type', sa.String(50), nullable=False),
        sa.Column('content_version', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=True),
        sa.Column('results', postgresql.JSONB(), nullable=False),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('model_used', sa.String(50), nullable=True),
        sa.Column('is_cached', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('cache_hit_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE')
    )

    # 创建索引
    op.create_index('idx_literature_analysis_session', 'literature_analysis', ['session_id', 'analysis_type'])
    op.create_index('idx_literature_analysis_content_hash', 'literature_analysis', ['content_hash'])
    op.create_index('idx_literature_analysis_cache_key', 'literature_analysis', ['session_id', 'analysis_type', 'content_hash'], unique=True)

    # 错误标注表
    op.create_table(
        'error_annotations',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_version', sa.Integer(), nullable=False),
        sa.Column('error_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('start_pos', sa.Integer(), nullable=False),
        sa.Column('end_pos', sa.Integer(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=True),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('suggestion', sa.Text(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('user_action', sa.String(20), nullable=True),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name='error_annotations_confidence_check')
    )

    # 创建索引
    op.create_index('idx_error_annotations_session_version', 'error_annotations', ['session_id', 'content_version'])
    op.create_index('idx_error_annotations_status', 'error_annotations', ['status'])
    op.create_index('idx_error_annotations_error_type', 'error_annotations', ['error_type'])

    # 文档结构树表
    op.create_table(
        'document_structure',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_version', sa.Integer(), nullable=False),
        sa.Column('node_type', sa.String(50), nullable=False),
        sa.Column('node_id', sa.String(100), nullable=True),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('position_in_parent', sa.Integer(), nullable=True),
        sa.Column('content_summary', sa.Text(), nullable=True),
        sa.Column('full_text', sa.Text(), nullable=True),
        sa.Column('start_pos', sa.Integer(), nullable=False),
        sa.Column('end_pos', sa.Integer(), nullable=False),
        sa.Column('analysis_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['document_structure.id'], ondelete='CASCADE')
    )

    # 创建索引
    op.create_index('idx_document_structure_session', 'document_structure', ['session_id', 'content_version'])
    op.create_index('idx_document_structure_hierarchy', 'document_structure', ['parent_id', 'position_in_parent'])
    op.create_index('idx_document_structure_position', 'document_structure', ['start_pos', 'end_pos'])

    # ============================================
    # 理科模式相关表
    # ============================================

    # 数学步骤表
    op.create_table(
        'math_steps',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_version', sa.Integer(), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('step_content', sa.Text(), nullable=False),
        sa.Column('formula', sa.Text(), nullable=True),
        sa.Column('formula_rendered', sa.Text(), nullable=True),
        sa.Column('symbolic_form', postgresql.JSONB(), nullable=True),
        sa.Column('variables_before', postgresql.JSONB(), nullable=True),
        sa.Column('variables_after', postgresql.JSONB(), nullable=True),
        sa.Column('variables_introduced', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=True),
        sa.Column('validation_details', postgresql.JSONB(), nullable=True),
        sa.Column('errors', postgresql.ARRAY(postgresql.JSONB()), nullable=True),
        sa.Column('warnings', postgresql.ARRAY(postgresql.JSONB()), nullable=True),
        sa.Column('parent_step_id', sa.BigInteger(), nullable=True),
        sa.Column('depends_on_steps', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('next_step_hint', sa.Text(), nullable=True),
        sa.Column('alternative_approaches', postgresql.ARRAY(postgresql.JSONB()), nullable=True),
        sa.Column('start_pos', sa.Integer(), nullable=True),
        sa.Column('end_pos', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_step_id'], ['math_steps.id'])
    )

    # 创建索引
    op.create_index('idx_math_steps_session', 'math_steps', ['session_id', 'step_order'])
    op.create_index('idx_math_steps_parent', 'math_steps', ['parent_step_id'])

    # 逻辑树表
    op.create_table(
        'logic_tree_nodes',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_version', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.String(100), nullable=False),
        sa.Column('node_type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('symbolic_form', postgresql.JSONB(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('position', postgresql.JSONB(), nullable=True),
        sa.Column('depends_on', postgresql.ARRAY(sa.String(100)), nullable=True),
        sa.Column('required_by', postgresql.ARRAY(sa.String(100)), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('completion_percentage', sa.Float(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('formula_used', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['logic_tree_nodes.id'])
    )

    # 创建索引
    op.create_index('idx_logic_tree_nodes_session', 'logic_tree_nodes', ['session_id', 'content_version'])
    op.create_index('idx_logic_tree_nodes_node_id', 'logic_tree_nodes', ['session_id', 'node_id'])
    op.create_index('idx_logic_tree_nodes_type_status', 'logic_tree_nodes', ['node_type', 'status'])

    # 断点调试会话表
    op.create_table(
        'debug_sessions',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('breakpoint_step_id', sa.BigInteger(), nullable=True),
        sa.Column('breakpoint_step_number', sa.Integer(), nullable=True),
        sa.Column('execution_trace', postgresql.JSONB(), nullable=False),
        sa.Column('current_state', postgresql.JSONB(), nullable=False),
        sa.Column('insights', postgresql.ARRAY(postgresql.JSONB()), nullable=True),
        sa.Column('warnings', postgresql.ARRAY(postgresql.JSONB()), nullable=True),
        sa.Column('next_actions', postgresql.ARRAY(postgresql.JSONB()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['breakpoint_step_id'], ['math_steps.id'])
    )

    # 创建索引
    op.create_index('idx_debug_sessions_session', 'debug_sessions', ['session_id', 'created_at'], postgresql_ops={'created_at': 'DESC'})

    # ============================================
    # 对话和交互相关表
    # ============================================

    # 聊天消息表
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('context', postgresql.JSONB(), nullable=True),
        sa.Column('message_type', sa.String(50), nullable=True),
        sa.Column('related_agent', sa.String(50), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('model_used', sa.String(50), nullable=True),
        sa.Column('reply_to_message_id', sa.BigInteger(), nullable=True),
        sa.Column('related_analysis_id', sa.BigInteger(), nullable=True),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('is_helpful', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reply_to_message_id'], ['chat_messages.id']),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='chat_messages_role_check'),
        sa.CheckConstraint("user_rating >= 1 AND user_rating <= 5", name='chat_messages_rating_check')
    )

    # 创建索引
    op.create_index('idx_chat_messages_session', 'chat_messages', ['session_id', 'created_at'])
    op.create_index('idx_chat_messages_role', 'chat_messages', ['role'])
    op.create_index('idx_chat_messages_reply_chain', 'chat_messages', ['reply_to_message_id'])

    # ============================================
    # 用户反馈和学习数据表
    # ============================================

    # 用户操作日志表
    op.create_table(
        'user_actions',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('target_type', sa.String(50), nullable=True),
        sa.Column('target_id', sa.BigInteger(), nullable=True),
        sa.Column('action_data', postgresql.JSONB(), nullable=True),
        sa.Column('editor_state_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['editor_state_id'], ['editor_states.id'])
    )

    # 创建索引
    op.create_index('idx_user_actions_session', 'user_actions', ['session_id', 'created_at'])
    op.create_index('idx_user_actions_action_type', 'user_actions', ['action_type'])

    # 学习进度表
    op.create_table(
        'user_learning_progress',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(50), nullable=False),
        sa.Column('skill_type', sa.String(100), nullable=False),
        sa.Column('total_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('successful_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mastery_level', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('last_practice_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # 创建索引
    op.create_index('idx_user_learning_progress_user_skill', 'user_learning_progress', ['user_id', 'subject', 'skill_type'], unique=True)
    op.create_index('idx_user_learning_progress_mastery', 'user_learning_progress', ['user_id', 'mastery_level'])


def downgrade() -> None:
    """删除所有表"""
    op.drop_table('user_learning_progress')
    op.drop_table('user_actions')
    op.drop_table('chat_messages')
    op.drop_table('debug_sessions')
    op.drop_table('logic_tree_nodes')
    op.drop_table('math_steps')
    op.drop_table('document_structure')
    op.drop_table('error_annotations')
    op.drop_table('literature_analysis')
    op.drop_table('editor_states')
    op.drop_table('sessions')
