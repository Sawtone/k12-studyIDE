"""
安全相关工具
包括JWT令牌、密码哈希等
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.core.exceptions import UnauthorizedException


# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码

    Returns:
        是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码哈希

    Args:
        password: 明文密码

    Returns:
        哈希密码
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建访问令牌

    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量

    Returns:
        JWT令牌
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    解码访问令牌

    Args:
        token: JWT令牌

    Returns:
        解码后的数据

    Raises:
        UnauthorizedException: 令牌无效或过期
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        raise UnauthorizedException(f"令牌无效: {str(e)}")


def generate_session_token(user_id: str, session_id: str) -> str:
    """
    生成会话令牌

    Args:
        user_id: 用户ID
        session_id: 会话ID

    Returns:
        会话令牌
    """
    data = {
        "user_id": user_id,
        "session_id": session_id,
        "type": "session"
    }
    return create_access_token(data)


def verify_session_token(token: str) -> tuple[str, str]:
    """
    验证会话令牌

    Args:
        token: 会话令牌

    Returns:
        (user_id, session_id)

    Raises:
        UnauthorizedException: 令牌无效
    """
    payload = decode_access_token(token)

    if payload.get("type") != "session":
        raise UnauthorizedException("令牌类型错误")

    user_id = payload.get("user_id")
    session_id = payload.get("session_id")

    if not user_id or not session_id:
        raise UnauthorizedException("令牌数据不完整")

    return user_id, session_id
