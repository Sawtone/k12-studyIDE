"""
Pydantic数据模型 - 通用模型
"""

from typing import Optional, Any, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ModeEnum(str, Enum):
    """学习模式枚举"""
    literature = "literature"
    science = "science"


class GradeLevelEnum(str, Enum):
    """年级水平枚举"""
    primary = "primary"
    middle = "middle"
    high = "high"


class StatusEnum(str, Enum):
    """状态枚举"""
    active = "active"
    archived = "archived"
    deleted = "deleted"


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: Dict[str, Any] = Field(..., description="错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "参数验证失败",
                    "details": {"field": "content", "reason": "不能为空"}
                }
            }
        }


class PaginationResponse(BaseModel):
    """分页响应模型"""
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    total: int = Field(..., description="总数")
    total_pages: int = Field(..., description="总页数")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "limit": 20,
                "total": 45,
                "total_pages": 3
            }
        }


class CursorPosition(BaseModel):
    """光标位置模型"""
    line: int = Field(..., description="行号")
    column: int = Field(..., description="列号")
    offset: Optional[int] = Field(None, description="偏移量")

    class Config:
        json_schema_extra = {
            "example": {
                "line": 10,
                "column": 5,
                "offset": 245
            }
        }


class Selection(BaseModel):
    """选择区域模型"""
    start: CursorPosition = Field(..., description="起始位置")
    end: CursorPosition = Field(..., description="结束位置")
    text: str = Field(..., description="选中的文本")

    class Config:
        json_schema_extra = {
            "example": {
                "start": {"line": 5, "column": 0},
                "end": {"line": 5, "column": 20},
                "text": "selected text"
            }
        }
