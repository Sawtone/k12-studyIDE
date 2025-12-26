"""
DocumentStructure Repository
文档结构数据访问层
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import DocumentStructure
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentStructureRepository:
    """
    文档结构Repository

    职责：
    1. 保存文章结构树
    2. 查询结构节点
    3. 构建层次关系
    4. 支持结构分析
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_structure_tree(
        self,
        session_id: str,
        content_version: int,
        nodes: List[Dict[str, Any]]
    ) -> List[DocumentStructure]:
        """
        保存文档结构树

        Args:
            session_id: 会话ID
            content_version: 内容版本号
            nodes: 节点列表（包含层次关系）

        Returns:
            DocumentStructure对象列表
        """
        try:
            # 先删除旧的结构
            await self.delete_structure_by_version(session_id, content_version)

            saved_nodes = []
            node_id_map = {}  # node_id -> db_id 映射

            # 第一遍：创建所有节点（不设置parent_id）
            for node_data in nodes:
                node = DocumentStructure(
                    session_id=session_id,
                    content_version=content_version,
                    node_type=node_data['node_type'],
                    node_id=node_data['node_id'],
                    level=node_data['level'],
                    position_in_parent=node_data.get('position_in_parent'),
                    content_summary=node_data.get('content_summary'),
                    full_text=node_data.get('full_text'),
                    start_pos=node_data['start_pos'],
                    end_pos=node_data['end_pos'],
                    analysis_data=node_data.get('analysis_data')
                )
                self.db.add(node)
                saved_nodes.append(node)

            # 刷新以获取数据库ID
            await self.db.flush()

            # 建立映射
            for node in saved_nodes:
                node_id_map[node.node_id] = node.id

            # 第二遍：设置parent_id
            for i, node_data in enumerate(nodes):
                if 'parent_node_id' in node_data and node_data['parent_node_id']:
                    parent_db_id = node_id_map.get(node_data['parent_node_id'])
                    if parent_db_id:
                        saved_nodes[i].parent_id = parent_db_id

            await self.db.flush()

            logger.info(f"保存文档结构树: session={session_id}, version={content_version}, nodes={len(nodes)}")

            return saved_nodes

        except Exception as e:
            logger.error(f"保存文档结构树失败: {str(e)}")
            raise

    async def get_structure_by_version(
        self,
        session_id: str,
        content_version: int
    ) -> List[DocumentStructure]:
        """
        获取指定版本的文档结构

        Args:
            session_id: 会话ID
            content_version: 内容版本号

        Returns:
            DocumentStructure列表
        """
        try:
            query = select(DocumentStructure).where(
                DocumentStructure.session_id == session_id,
                DocumentStructure.content_version == content_version
            ).order_by(DocumentStructure.level, DocumentStructure.position_in_parent)

            result = await self.db.execute(query)
            nodes = result.scalars().all()

            return list(nodes)

        except Exception as e:
            logger.error(f"获取文档结构失败: {str(e)}")
            raise

    async def get_structure_tree(
        self,
        session_id: str,
        content_version: int
    ) -> Dict[str, Any]:
        """
        获取文档结构树（层次化）

        Args:
            session_id: 会话ID
            content_version: 内容版本号

        Returns:
            树形结构字典
        """
        try:
            nodes = await self.get_structure_by_version(session_id, content_version)

            if not nodes:
                return {}

            # 构建节点字典
            node_dict = {}
            for node in nodes:
                node_dict[node.id] = {
                    'id': node.node_id,
                    'type': node.node_type,
                    'level': node.level,
                    'title': node.content_summary or '',
                    'summary': node.content_summary,
                    'start_pos': node.start_pos,
                    'end_pos': node.end_pos,
                    'analysis_data': node.analysis_data,
                    'children': []
                }

            # 构建树形结构
            root = None
            for node in nodes:
                node_obj = node_dict[node.id]
                if node.parent_id is None:
                    root = node_obj
                else:
                    if node.parent_id in node_dict:
                        node_dict[node.parent_id]['children'].append(node_obj)

            return root or {}

        except Exception as e:
            logger.error(f"获取文档结构树失败: {str(e)}")
            raise

    async def get_node_by_position(
        self,
        session_id: str,
        content_version: int,
        position: int
    ) -> Optional[DocumentStructure]:
        """
        根据位置获取节点

        Args:
            session_id: 会话ID
            content_version: 内容版本号
            position: 文本位置

        Returns:
            DocumentStructure对象或None
        """
        try:
            query = select(DocumentStructure).where(
                DocumentStructure.session_id == session_id,
                DocumentStructure.content_version == content_version,
                DocumentStructure.start_pos <= position,
                DocumentStructure.end_pos >= position
            ).order_by(DocumentStructure.level.desc())  # 最深层的节点

            result = await self.db.execute(query)
            return result.scalars().first()

        except Exception as e:
            logger.error(f"根据位置获取节点失败: {str(e)}")
            raise

    async def get_children(
        self,
        parent_id: int
    ) -> List[DocumentStructure]:
        """
        获取子节点

        Args:
            parent_id: 父节点ID

        Returns:
            DocumentStructure列表
        """
        try:
            query = select(DocumentStructure).where(
                DocumentStructure.parent_id == parent_id
            ).order_by(DocumentStructure.position_in_parent)

            result = await self.db.execute(query)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"获取子节点失败: {str(e)}")
            raise

    async def delete_structure_by_version(
        self,
        session_id: str,
        content_version: int
    ) -> int:
        """
        删除指定版本的文档结构

        Args:
            session_id: 会话ID
            content_version: 内容版本号

        Returns:
            删除的数量
        """
        try:
            stmt = delete(DocumentStructure).where(
                DocumentStructure.session_id == session_id,
                DocumentStructure.content_version == content_version
            )

            result = await self.db.execute(stmt)
            deleted_count = result.rowcount

            logger.info(f"删除文档结构: session={session_id}, version={content_version}, count={deleted_count}")

            return deleted_count

        except Exception as e:
            logger.error(f"删除文档结构失败: {str(e)}")
            raise

    async def get_structure_summary(
        self,
        session_id: str,
        content_version: int
    ) -> Dict[str, Any]:
        """
        获取结构摘要信息

        Args:
            session_id: 会话ID
            content_version: 内容版本号

        Returns:
            摘要信息字典
        """
        try:
            from sqlalchemy import func

            # 统计各类型节点数量
            type_query = select(
                DocumentStructure.node_type,
                func.count(DocumentStructure.id).label('count')
            ).where(
                DocumentStructure.session_id == session_id,
                DocumentStructure.content_version == content_version
            ).group_by(DocumentStructure.node_type)

            type_result = await self.db.execute(type_query)
            type_stats = {row.node_type: row.count for row in type_result}

            # 统计层级深度
            depth_query = select(
                func.max(DocumentStructure.level).label('max_depth')
            ).where(
                DocumentStructure.session_id == session_id,
                DocumentStructure.content_version == content_version
            )

            depth_result = await self.db.execute(depth_query)
            max_depth = depth_result.scalar() or 0

            return {
                'node_count_by_type': type_stats,
                'max_depth': max_depth,
                'total_nodes': sum(type_stats.values())
            }

        except Exception as e:
            logger.error(f"获取结构摘要失败: {str(e)}")
            raise
