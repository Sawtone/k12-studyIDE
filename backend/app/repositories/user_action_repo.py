"""
UserAction Repository
用户操作日志数据访问层
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.database.models import UserAction
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserActionRepository:
    """
    用户操作Repository

    职责：
    1. 记录用户操作日志
    2. 查询操作历史
    3. 统计用户行为
    4. 支持AI改进
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_action(
        self,
        session_id: str,
        action_type: str,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        action_data: Optional[Dict[str, Any]] = None,
        editor_state_id: Optional[int] = None
    ) -> UserAction:
        """
        记录用户操作

        Args:
            session_id: 会话ID
            action_type: 操作类型（accept_suggestion, reject, modify, ignore等）
            target_type: 目标类型（error, suggestion, analysis）
            target_id: 目标ID
            action_data: 操作数据（JSON）
            editor_state_id: 编辑器状态ID

        Returns:
            UserAction对象
        """
        try:
            action = UserAction(
                session_id=session_id,
                action_type=action_type,
                target_type=target_type,
                target_id=target_id,
                action_data=action_data,
                editor_state_id=editor_state_id
            )

            self.db.add(action)
            await self.db.flush()
            await self.db.refresh(action)

            logger.info(f"记录用户操作: session={session_id}, type={action_type}, target={target_type}")

            return action

        except Exception as e:
            logger.error(f"记录用户操作失败: {str(e)}")
            raise

    async def get_actions_by_session(
        self,
        session_id: str,
        action_type: Optional[str] = None,
        limit: int = 100
    ) -> List[UserAction]:
        """
        获取会话的操作历史

        Args:
            session_id: 会话ID
            action_type: 操作类型过滤（可选）
            limit: 返回数量限制

        Returns:
            UserAction列表
        """
        try:
            query = select(UserAction).where(
                UserAction.session_id == session_id
            )

            if action_type:
                query = query.where(UserAction.action_type == action_type)

            query = query.order_by(UserAction.created_at.desc()).limit(limit)

            result = await self.db.execute(query)
            actions = result.scalars().all()

            return list(actions)

        except Exception as e:
            logger.error(f"获取操作历史失败: {str(e)}")
            raise

    async def get_action_statistics(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        获取操作统计信息

        Args:
            session_id: 会话ID

        Returns:
            统计信息字典
        """
        try:
            # 按操作类型统计
            type_query = select(
                UserAction.action_type,
                func.count(UserAction.id).label('count')
            ).where(
                UserAction.session_id == session_id
            ).group_by(UserAction.action_type)

            type_result = await self.db.execute(type_query)
            type_stats = {row.action_type: row.count for row in type_result}

            # 总操作数
            total_query = select(func.count(UserAction.id)).where(
                UserAction.session_id == session_id
            )
            total_result = await self.db.execute(total_query)
            total = total_result.scalar()

            # 接受率（如果有相关操作）
            accept_count = type_stats.get('accept_suggestion', 0)
            reject_count = type_stats.get('reject_suggestion', 0)
            total_feedback = accept_count + reject_count
            acceptance_rate = accept_count / total_feedback if total_feedback > 0 else 0

            return {
                'total_actions': total,
                'by_type': type_stats,
                'acceptance_rate': acceptance_rate,
                'accepted': accept_count,
                'rejected': reject_count
            }

        except Exception as e:
            logger.error(f"获取操作统计失败: {str(e)}")
            raise

    async def get_recent_actions(
        self,
        session_id: str,
        hours: int = 24,
        limit: int = 50
    ) -> List[UserAction]:
        """
        获取最近的操作

        Args:
            session_id: 会话ID
            hours: 时间范围（小时）
            limit: 返回数量限制

        Returns:
            UserAction列表
        """
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            query = select(UserAction).where(
                UserAction.session_id == session_id,
                UserAction.created_at >= since
            ).order_by(UserAction.created_at.desc()).limit(limit)

            result = await self.db.execute(query)
            actions = result.scalars().all()

            return list(actions)

        except Exception as e:
            logger.error(f"获取最近操作失败: {str(e)}")
            raise

    async def get_actions_by_target(
        self,
        session_id: str,
        target_type: str,
        target_id: str
    ) -> List[UserAction]:
        """
        获取针对特定目标的操作

        Args:
            session_id: 会话ID
            target_type: 目标类型
            target_id: 目标ID

        Returns:
            UserAction列表
        """
        try:
            query = select(UserAction).where(
                UserAction.session_id == session_id,
                UserAction.target_type == target_type,
                UserAction.target_id == target_id
            ).order_by(UserAction.created_at)

            result = await self.db.execute(query)
            actions = result.scalars().all()

            return list(actions)

        except Exception as e:
            logger.error(f"获取目标操作失败: {str(e)}")
            raise

    async def get_user_behavior_pattern(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        分析用户行为模式

        Args:
            session_id: 会话ID

        Returns:
            行为模式分析结果
        """
        try:
            actions = await self.get_actions_by_session(session_id, limit=1000)

            if not actions:
                return {
                    'total_actions': 0,
                    'patterns': {}
                }

            # 分析操作序列
            action_sequence = [a.action_type for a in actions]

            # 统计常见模式
            patterns = {}

            # 接受/拒绝模式
            accept_reject_pattern = {
                'quick_accept': 0,  # 快速接受（少于5秒）
                'careful_accept': 0,  # 仔细考虑后接受
                'quick_reject': 0,
                'careful_reject': 0
            }

            # 修改模式
            modification_pattern = {
                'direct_apply': 0,  # 直接应用
                'modify_then_apply': 0,  # 修改后应用
                'ignore': 0  # 忽略
            }

            # 简单统计（实际可以更复杂）
            for action in actions:
                if action.action_type == 'accept_suggestion':
                    accept_reject_pattern['quick_accept'] += 1
                elif action.action_type == 'reject_suggestion':
                    accept_reject_pattern['quick_reject'] += 1
                elif action.action_type == 'modify':
                    modification_pattern['modify_then_apply'] += 1
                elif action.action_type == 'ignore':
                    modification_pattern['ignore'] += 1

            patterns['accept_reject'] = accept_reject_pattern
            patterns['modification'] = modification_pattern

            return {
                'total_actions': len(actions),
                'patterns': patterns,
                'action_sequence': action_sequence[-20:]  # 最近20个操作
            }

        except Exception as e:
            logger.error(f"分析用户行为模式失败: {str(e)}")
            raise

    async def cleanup_old_actions(
        self,
        days: int = 90
    ) -> int:
        """
        清理旧的操作日志

        Args:
            days: 保留天数

        Returns:
            删除的数量
        """
        try:
            from sqlalchemy import delete

            cutoff_date = datetime.utcnow() - timedelta(days=days)

            stmt = delete(UserAction).where(
                UserAction.created_at < cutoff_date
            )

            result = await self.db.execute(stmt)
            deleted_count = result.rowcount

            logger.info(f"清理旧操作日志: deleted={deleted_count}, before={cutoff_date}")

            return deleted_count

        except Exception as e:
            logger.error(f"清理旧操作日志失败: {str(e)}")
            raise
