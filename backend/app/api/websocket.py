"""
WebSocket连接处理
提供实时双向通信功能
"""

import json
import uuid
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.cache.redis_client import redis_cache
from app.database.connection import get_session_factory

logger = get_logger(__name__)


class ConnectionManager:
    """
    WebSocket连接管理器

    职责：
    1. 管理WebSocket连接
    2. 消息广播
    3. 连接状态维护
    """

    def __init__(self) -> None:
        """初始化连接管理器"""
        # 存储活跃连接: {session_id: {connection_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        logger.info("WebSocket连接管理器已初始化")

    async def connect(self, websocket: WebSocket, session_id: str, connection_id: str) -> None:
        """
        建立WebSocket连接

        Args:
            websocket: WebSocket对象
            session_id: 会话ID
            connection_id: 连接ID
        """
        await websocket.accept()

        # 添加到连接池
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}

        self.active_connections[session_id][connection_id] = websocket

        # 更新Redis中的连接集合
        await redis_cache.sadd(f"ws:session:{session_id}", connection_id)

        logger.info(f"WebSocket连接已建立: session={session_id}, connection={connection_id}")

        # 发送欢迎消息
        await self.send_personal_message(
            {
                "type": "system_notification",
                "data": {
                    "level": "info",
                    "message": "连接成功，开始学习吧！"
                }
            },
            websocket
        )

    async def disconnect(self, session_id: str, connection_id: str) -> None:
        """
        断开WebSocket连接

        Args:
            session_id: 会话ID
            connection_id: 连接ID
        """
        if session_id in self.active_connections:
            if connection_id in self.active_connections[session_id]:
                del self.active_connections[session_id][connection_id]

            # 如果会话没有连接了，删除会话
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

        # 从Redis中移除
        await redis_cache.srem(f"ws:session:{session_id}", connection_id)

        logger.info(f"WebSocket连接已断开: session={session_id}, connection={connection_id}")

    async def send_personal_message(self, message: Dict, websocket: WebSocket) -> None:
        """
        发送个人消息

        Args:
            message: 消息内容
            websocket: WebSocket对象
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送个人消息失败: {str(e)}")

    async def broadcast_to_session(self, message: Dict, session_id: str) -> None:
        """
        向会话的所有连接广播消息

        Args:
            message: 消息内容
            session_id: 会话ID
        """
        if session_id not in self.active_connections:
            logger.warning(f"会话 {session_id} 没有活跃连接")
            return

        # 向所有连接发送消息
        disconnected = []
        for connection_id, websocket in self.active_connections[session_id].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"广播消息失败: connection={connection_id}, error={str(e)}")
                disconnected.append(connection_id)

        # 清理断开的连接
        for connection_id in disconnected:
            await self.disconnect(session_id, connection_id)

    async def handle_message(
        self,
        message: Dict,
        session_id: str,
        websocket: WebSocket
    ) -> None:
        """
        处理客户端消息

        Args:
            message: 消息内容
            session_id: 会话ID
            websocket: WebSocket对象
        """
        message_type = message.get("type")
        data = message.get("data", {})

        logger.debug(f"收到WebSocket消息: type={message_type}, session={session_id}")

        try:
            if message_type == "heartbeat":
                # 心跳消息
                await self.send_personal_message(
                    {"type": "heartbeat_ack", "data": {}},
                    websocket
                )

            elif message_type == "editor_update":
                # 编辑器更新 - 实际调用SessionManager同步编辑器状态
                try:
                    from app.services.orchestrator.session_manager import SessionManager

                    # 获取数据库会话
                    session_factory = get_session_factory()
                    async with session_factory() as db:
                        manager = SessionManager(db)

                        # 同步编辑器状态
                        editor_state = await manager.sync_editor_state(
                            session_id=session_id,
                            content=data.get("content", ""),
                            cursor_position=data.get("cursor_position"),
                            selections=data.get("selections"),
                            version=data.get("version")
                        )

                        # 发送确认消息
                        await self.send_personal_message(
                            {
                                "type": "editor_update_ack",
                                "data": {
                                    "version": editor_state.version,
                                    "saved": True,
                                    "content_hash": editor_state.content_hash,
                                    "word_count": editor_state.word_count
                                }
                            },
                            websocket
                        )

                        logger.info(f"编辑器状态已同步: session={session_id}, version={editor_state.version}")

                except Exception as e:
                    logger.error(f"编辑器状态同步失败: {str(e)}")
                    await self.send_personal_message(
                        {
                            "type": "error",
                            "data": {
                                "code": "EDITOR_SYNC_ERROR",
                                "message": f"编辑器状态同步失败: {str(e)}",
                                "recoverable": True
                            }
                        },
                        websocket
                    )

            elif message_type == "request_analysis":
                # 请求分析 - 实际调用AgentCoordinator执行分析
                try:
                    from app.services.orchestrator.agent_coordinator import agent_coordinator
                    from app.services.orchestrator.session_manager import SessionManager

                    analysis_type = data.get("analysis_type")
                    priority = data.get("priority", "normal")

                    # 发送分析开始通知
                    await self.send_personal_message(
                        {
                            "type": "analysis_started",
                            "data": {
                                "analysis_type": analysis_type,
                                "priority": priority
                            }
                        },
                        websocket
                    )

                    # 获取数据库会话
                    session_factory = get_session_factory()
                    async with session_factory() as db:
                        manager = SessionManager(db)
                        session = await manager.get_session(session_id)

                        # 从缓存获取内容
                        from app.cache.cache_strategies import session_cache
                        cached_content = await session_cache.get_content(session_id)
                        content = cached_content.get("content", "") if cached_content else ""

                        # 根据分析类型选择Agent
                        agent_type_map = {
                            "grammar": "grammar_checker",
                            "structure": "structure_analyzer",
                            "health": "health_scorer",
                            "polish": "polish"
                        }

                        agent_type = agent_type_map.get(analysis_type)
                        if not agent_type:
                            raise ValueError(f"未知的分析类型: {analysis_type}")

                        # 执行Agent
                        result = await agent_coordinator.execute_agent(
                            agent_type=agent_type,
                            session_id=session_id,
                            request_id=str(uuid.uuid4()),
                            agent_kwargs={
                                "grade_level": session.grade_level or "middle"
                            },
                            content=content
                        )

                        # 发送分析结果
                        if result.success:
                            await self.send_personal_message(
                                {
                                    "type": "analysis_result",
                                    "data": {
                                        "analysis_type": analysis_type,
                                        "results": result.data,
                                        "metadata": result.metadata
                                    }
                                },
                                websocket
                            )
                            logger.info(f"分析完成: session={session_id}, type={analysis_type}")
                        else:
                            raise Exception(result.error)

                except Exception as e:
                    logger.error(f"分析执行失败: {str(e)}")
                    await self.send_personal_message(
                        {
                            "type": "error",
                            "data": {
                                "code": "ANALYSIS_ERROR",
                                "message": f"分析执行失败: {str(e)}",
                                "recoverable": True
                            }
                        },
                        websocket
                    )

            elif message_type == "chat_message":
                # 聊天消息 - 实际调用ChatAgent处理消息
                try:
                    from app.services.orchestrator.agent_coordinator import agent_coordinator
                    from app.services.orchestrator.session_manager import SessionManager
                    from app.repositories.chat_history_repo import ChatHistoryRepository

                    user_message = data.get("message", "")
                    context = data.get("context", {})

                    # 获取数据库会话
                    session_factory = get_session_factory()
                    async with session_factory() as db:
                        manager = SessionManager(db)
                        session = await manager.get_session(session_id)

                        # 获取聊天历史
                        chat_repo = ChatHistoryRepository(db)
                        chat_history = await chat_repo.get_recent_context(
                            session_id=session_id,
                            limit=10
                        )

                        # 保存用户消息
                        user_msg = await chat_repo.save_message(
                            session_id=session_id,
                            role="user",
                            content=user_message,
                            context=context
                        )

                        # 执行Chat Agent
                        result = await agent_coordinator.execute_agent(
                            agent_type="chat",
                            session_id=session_id,
                            request_id=str(uuid.uuid4()),
                            agent_kwargs={
                                "grade_level": session.grade_level or "middle",
                                "mode": session.mode,
                                "subject": session.subject or ""
                            },
                            message=user_message,
                            context=context,
                            chat_history=chat_history
                        )

                        if result.success:
                            # 保存助手回复
                            assistant_msg = await chat_repo.save_message(
                                session_id=session_id,
                                role="assistant",
                                content=result.data.get("content", ""),
                                message_type=result.data.get("message_type"),
                                related_agent="chat_agent",
                                tokens_used=result.metadata.get("tokens_used"),
                                model_used=result.metadata.get("model"),
                                reply_to_message_id=user_msg.id
                            )

                            # 发送聊天响应
                            await self.send_personal_message(
                                {
                                    "type": "chat_response",
                                    "data": {
                                        "message_id": str(assistant_msg.id),
                                        "content": result.data.get("content", ""),
                                        "message_type": result.data.get("message_type"),
                                        "action_items": result.data.get("action_items", []),
                                        "created_at": assistant_msg.created_at.isoformat()
                                    }
                                },
                                websocket
                            )

                            logger.info(f"聊天消息已处理: session={session_id}, message_id={assistant_msg.id}")
                        else:
                            raise Exception(result.error)

                except Exception as e:
                    logger.error(f"聊天消息处理失败: {str(e)}")
                    await self.send_personal_message(
                        {
                            "type": "error",
                            "data": {
                                "code": "CHAT_ERROR",
                                "message": f"聊天消息处理失败: {str(e)}",
                                "recoverable": True
                            }
                        },
                        websocket
                    )

            else:
                logger.warning(f"未知的消息类型: {message_type}")
                await self.send_personal_message(
                    {
                        "type": "error",
                        "data": {
                            "code": "UNKNOWN_MESSAGE_TYPE",
                            "message": f"未知的消息类型: {message_type}",
                            "recoverable": True
                        }
                    },
                    websocket
                )

        except Exception as e:
            logger.error(f"处理消息失败: {str(e)}")
            await self.send_personal_message(
                {
                    "type": "error",
                    "data": {
                        "code": "MESSAGE_PROCESSING_ERROR",
                        "message": f"处理消息失败: {str(e)}",
                        "recoverable": True
                    }
                },
                websocket
            )

    def get_connection_count(self, session_id: str) -> int:
        """
        获取会话的连接数

        Args:
            session_id: 会话ID

        Returns:
            连接数
        """
        if session_id not in self.active_connections:
            return 0
        return len(self.active_connections[session_id])


# 创建全局连接管理器实例
connection_manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
    """
    WebSocket端点处理函数

    Args:
        websocket: WebSocket对象
        session_id: 会话ID
    """
    import uuid
    connection_id = str(uuid.uuid4())

    try:
        # 建立连接
        await connection_manager.connect(websocket, session_id, connection_id)

        # 消息循环
        while True:
            # 接收消息
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await connection_manager.handle_message(message, session_id, websocket)
            except json.JSONDecodeError:
                logger.error(f"无效的JSON消息: {data}")
                await connection_manager.send_personal_message(
                    {
                        "type": "error",
                        "data": {
                            "code": "INVALID_JSON",
                            "message": "无效的JSON格式",
                            "recoverable": True
                        }
                    },
                    websocket
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket客户端断开连接: session={session_id}")
        await connection_manager.disconnect(session_id, connection_id)

    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")
        await connection_manager.disconnect(session_id, connection_id)
