from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas


class MenuRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_submenus_count(self, menu_id):
        result = await self.db.execute(
            select(func.count(models.Submenu.id)).where(models.Submenu.menu_id == menu_id)
        )
        return result.scalar()

    async def get_dishes_count(self, menu_id):
        result = await self.db.execute(
            select(func.count(models.Dish.id))
            .join(models.Submenu)
            .where(models.Submenu.menu_id == menu_id)
        )
        return result.scalar()

    async def get_menus(self):
        result = await self.db.execute(select(models.Menu))
        return result.fetchall()

    async def get_menu(self, menu_id):
        result = await self.db.execute(
            select(models.Menu).where(models.Menu.id == menu_id)
        )
        fetch_result = result.fetchone()
        if fetch_result is None:
            raise HTTPException(status_code=404, detail='menu not found')
        db_menu = fetch_result[0]
        return db_menu

    async def create_menu(self, menu_data: schemas.MenuCreate):
        db_menu = models.Menu(**menu_data.model_dump())
        self.db.add(db_menu)
        await self.db.commit()
        await self.db.refresh(db_menu)
        return db_menu

    async def update_menu(self, menu_id, menu: schemas.MenuCreate):
        db_menu = await self.get_menu(menu_id)
        db_menu.title = menu.title
        db_menu.description = menu.description
        self.db.add(db_menu)
        await self.db.commit()
        await self.db.refresh(db_menu)
        return db_menu

    async def delete_menu(self, menu_id):
        menu = await self.get_menu(menu_id)
        await self.db.delete(menu)
        await self.db.commit()
        return menu


class SubmenuRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_submenus(self, menu_id):
        result = await self.db.execute(select(models.Submenu).where(models.Submenu.menu_id == menu_id))
        return result.scalars().all()

    async def get_submenu(self, menu_id, submenu_id):
        query = (
            select(models.Submenu)
            .where(
                (models.Submenu.menu_id == menu_id) & (models.Submenu.id == submenu_id)))
        result = await self.db.execute(query)
        submenu = result.scalar()
        if not submenu:
            raise HTTPException(status_code=404, detail='submenu not found')
        return submenu

    async def create_submenu(self, menu_id, submenu_data: schemas.SubmenuCreate):
        db_submenu = models.Submenu(menu_id=menu_id, **submenu_data.model_dump())
        self.db.add(db_submenu)
        await self.db.commit()
        await self.db.refresh(db_submenu)
        return db_submenu

    async def update_submenu(self, menu_id, submenu_id, submenu_data: schemas.SubmenuCreate):
        db_submenu = await self.get_submenu(menu_id, submenu_id)
        for key, value in submenu_data.model_dump().items():
            setattr(db_submenu, key, value)
        await self.db.commit()
        await self.db.refresh(db_submenu)
        return db_submenu

    async def delete_submenu(self, menu_id, submenu_id):
        submenu = await self.get_submenu(menu_id, submenu_id)
        await self.db.delete(submenu)
        await self.db.commit()
        return submenu


class DishRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dishes(self, submenu_id, skip, limit):
        result = await self.db.execute(
            select(models.Dish).filter(models.Dish.submenu_id == submenu_id).offset(skip).limit(limit))
        dishes = result.fetchall()
        return [dish[0] for dish in dishes]

    async def get_dish(self, submenu_id, dish_id):
        result = await self.db.execute(
            select(models.Dish).where(models.Dish.submenu_id == submenu_id, models.Dish.id == dish_id))
        dish = result.fetchone()
        if dish is None:
            raise HTTPException(status_code=404, detail='dish not found')
        return dish[0]

    async def create_dish(self, submenu_id, dish: schemas.DishCreate):
        db_dish = models.Dish(submenu_id=submenu_id, **dish.model_dump())
        self.db.add(db_dish)
        await self.db.commit()
        await self.db.refresh(db_dish)
        return db_dish

    async def update_dish(self, submenu_id, dish_id, dish_data: schemas.DishCreate):
        db_dish = await self.get_dish(submenu_id, dish_id)
        for key, value in dish_data.model_dump().items():
            setattr(db_dish, key, value)
        await self.db.commit()
        await self.db.refresh(db_dish)
        return db_dish

    async def delete_dish(self, submenu_id, dish_id):
        db_dish = await self.get_dish(submenu_id, dish_id)
        await self.db.delete(db_dish)
        await self.db.commit()
        return db_dish
