from uuid import UUID

from fastapi import HTTPException

from app import schemas
from app.database_repository import DishRepository, MenuRepository, SubmenuRepository


class DishService:
    def __init__(self, dish_repository: DishRepository, submenu_repository: SubmenuRepository, menu_repository: MenuRepository):
        self.dish_repository = dish_repository
        self.submenu_repository = submenu_repository
        self.menu_repository = menu_repository

    async def read_dishes(self, submenu_id: UUID, skip: int = 0, limit: int = 100):
        dishes = await self.dish_repository.get_dishes(submenu_id, skip, limit)
        return dishes

    async def read_dish(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID):
        menu = await self.menu_repository.get_menu(menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail='menu not found')

        submenu = await self.submenu_repository.get_submenu(menu_id, submenu_id)
        if not submenu:
            raise HTTPException(status_code=404, detail='submenu not found')

        dish = await self.dish_repository.get_dish(submenu_id, dish_id)
        if not dish:
            raise HTTPException(status_code=404, detail='dish not found')

        return schemas.Dish(
            id=dish.id,
            title=dish.title,
            description=dish.description,
            price=dish.price
        )

    async def create_dish(self, menu_id: UUID, submenu_id: UUID, dish_data: schemas.DishCreate):
        menu = await self.menu_repository.get_menu(menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail='menu not found')

        submenu = await self.submenu_repository.get_submenu(menu_id, submenu_id)
        if not submenu:
            raise HTTPException(status_code=404, detail='submenu not found')
        dish = await self.dish_repository.create_dish(submenu_id, dish_data)

        return schemas.DishOut(
            id=dish.id,
            title=dish.title,
            description=dish.description,
            price=str(dish.price),
        )

    async def update_dish(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_data: schemas.DishCreate):
        menu = await self.menu_repository.get_menu(menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail='menu not found')

        dish = await self.dish_repository.update_dish(submenu_id, dish_id, dish_data)
        if not dish:
            raise HTTPException(status_code=404, detail='dish not found')
        return schemas.DishOut(
            id=dish.id,
            title=dish.title,
            description=dish.description,
            price=str(dish.price),
        )

    async def delete_dish(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID):
        menu = await self.menu_repository.get_menu(menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail='menu not found')

        dish = await self.dish_repository.delete_dish(submenu_id, dish_id)
        if dish is None:
            raise HTTPException(status_code=404, detail='dish not found')
        return {'status': True, 'message': 'The dish has been deleted'}
