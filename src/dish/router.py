from typing import Literal

from fastapi import APIRouter, Depends, Path, Query, status
from loguru import logger

from src.dish.service import DishService
from src.dish.repository import DishRepository
from src.dish.schema import DishCreate, DishUpdate, DishResponse
from src.core.database import get_db
from src.auth.user_manager import get_current_user, current_superuser


router = APIRouter(
    prefix="/dishes", tags=["Dishes"],
    dependencies=[Depends(get_current_user)] # 添加用户依赖，登录用户才能访问
)


# 注入仓库层和服务层，可以扩展其他依赖，比如redis缓存
async def get_dish_service(session=Depends(get_db)) -> DishService:
    repository = DishRepository(session)
    return DishService(repository)


# 链式依赖：create_dish -> get_dish_service -> get_db
# 路由层 -> 服务层 -> 仓库层
@router.post("/", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
async def create_dish(
    dish_data: DishCreate, service: DishService = Depends(get_dish_service)
):
    """创建新菜品"""
    new_dish = await service.create_dish(dish_data)
    return new_dish


@router.get("/{dish_id}", response_model=DishResponse)
async def get_dish(
    dish_id: int = Path(..., description="菜品ID"),     # Path 为路径参数声明相同类型的校验
    service: DishService = Depends(get_dish_service),
):
    """获取单个菜品"""

    logger.debug(f"正在获取菜品 ID: {dish_id}")
    try:
        dish = await service.get_dish_by_id(dish_id)
        logger.info(f"获取到菜品, ID: {dish_id}")
        return dish
    except Exception as e:
        logger.error(f"获取 ID 为 {dish_id} 的菜品时出错: {str(e)}")
        raise   # 直接将服务层异常抛出


@router.get("/", response_model=list[DishResponse])
async def list_dishes(
    search: str | None = Query(None, description="搜索关键词"),  # Query 为查询参数声明更多的校验
    order_by: Literal["id", "name", "created_at"] = Query("id", description="排序字段"),
    direction: Literal["asc", "desc"] = Query("asc", description="排序方向"),
    limit: int = Query(10, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: DishService = Depends(get_dish_service),
):
    """查询所有菜品"""
    dishes = await service.list_dishes(
        search=search,
        order_by=order_by,
        direction=direction,
        limit=limit,
        offset=offset,
    )
    return dishes


@router.patch("/{dish_id}", response_model=DishResponse)
async def update_dish(
    dish_data: DishUpdate,
    dish_id: int = Path(..., description="菜品ID"),
    service: DishService = Depends(get_dish_service),
):
    """更新菜品"""
    dish = await service.update_dish(dish_id, dish_data)
    return dish


@router.delete(
    "/{dish_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(current_superuser)] # 仅超级用户可删除
)
async def delete_dish(
    dish_id: int = Path(..., description="菜品ID"),
    service: DishService = Depends(get_dish_service),
):
    """删除菜品"""

    await service.delete_dish(dish_id)