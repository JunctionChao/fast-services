# 仓库层（数据库操作）
from typing import Mapping, Any

from sqlalchemy import select, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.dish.model import Dish


class DishRepository:
    """数据库表仓库层"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, dish_data: Mapping[str, Any]) -> Dish:
        """创建菜品"""
        dish = Dish(**dish_data)
        self.session.add(dish)
        try:
            await self.session.commit()
        except IntegrityError: # 数据库完整性约束被违反 主键冲突、唯一索引重复、外键找不到、检查约束失败、非空字段缺值等
            await self.session.rollback()
            raise
        await self.session.refresh(dish)
        return dish

    async def get_by_id(self, dish_id: int) -> Dish | None:
        """根据ID获取菜品"""
        # result = await self.session.get(
        #     select(Dish).where(Dish.id == dish_id)
        # )
        # return result.scalars().first()
        dish = await self.session.get(Dish, dish_id)
        if not dish:
            return None
        return dish
    
    async def get_all(
        self,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Dish]:
        """获取所有菜品"""
        query = select(Dish)

        # 1. 搜索
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Dish.name.ilike(pattern),
                    Dish.description.ilike(pattern),
                )
            )
        # 2. 排序
        allowed_sort = {"id", "name", "description"}
        if order_by not in allowed_sort:
            order_by = "id"
        order_column = getattr(Dish, order_by, Dish.id)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )
        
        # 3. 分页
        limit = min(limit, 500)
        offset = max(offset, 0)
        paginated_query = query.offset(offset).limit(limit)
        items = await self.session.execute(paginated_query)

        return items.scalars().all()
    
    async def update(self, dish_data: Mapping[str, Any], dish_id: int) -> Dish | None:
        """更新菜品"""
        dish = await self.session.get(Dish, dish_id)
        if not dish:
            return None
        for key, value in dish_data.items():
            setattr(dish, key, value)
        await self.session.commit()
        await self.session.refresh(dish)
        return dish

    async def delete(self, dish_id: int) -> bool:
        """删除菜品"""
        dish = await self.session.get(Dish, dish_id)
        if not dish:
            return False
        await self.session.delete(dish)
        await self.session.commit()

        return True

    