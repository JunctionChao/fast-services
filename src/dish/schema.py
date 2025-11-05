# pydantic 模型，用来校验数据和序列化输出
from typing import Annotated, Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# dish公共字段基类
class DishBase(BaseModel):
    """
    ...是python的内置常量Ellipsi，这里起占位符作用，表示必填字段
    Annotated 用于为类型添加额外的元数据 __metadata__, 不改变其基本类型语义。
    它在运行时可以被框架或库用来提取附加信息，比如用于数据验证、序列化、依赖注入
    """
    name: Annotated[str, Field(..., description="菜品名称")]
    description: Annotated[str | None, Field(None, description="菜品描述")]


# 创建dish的模型
class DishCreate(DishBase):
    pass


# 更新dish的模型
class DishUpdate(BaseModel):
    name: Annotated[str | None, Field(None, description="菜品名称")]
    description: Annotated[str | None, Field(None, description="菜品描述")]


# 响应模型（含时间戳）
class DishResponse(DishBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True} # 用于验证 DishResponse.model_validate(dish_db)
    # model_config = ConfigDict(from_attributes=True)


# https://fastapi.tiangolo.com/zh/tutorial/query-param-models/
# 查询参数模型
class DishQueryParams(BaseModel):
    """菜品列表查询参数"""

    search: Annotated[
        str | None, Field(description="搜索关键词，可根据名称或描述进行模糊匹配")
    ] = None

    order_by: Annotated[
        Literal["id", "name", "created_at"],
        Field(description="排序字段，可选：id、name、created_at"),
    ] = "id"

    direction: Annotated[
        Literal["asc", "desc"],
        Field(description="排序方向，可选：asc（升序）、desc（降序）"),
    ] = "asc"

    limit: Annotated[
        int, Field(ge=1, le=500, description="每页返回的最大条数（1-500）")
    ] = 10

    offset: Annotated[int, Field(ge=0, description="查询偏移量，用于分页")] = 0