from uuid import UUID

from fastapi import HTTPException

from app import schemas
from app.database_repository import DishRepository, MenuRepository, SubmenuRepository


class MenuService:
    def __init__(self, menu_repository: MenuRepository, submenu_repository: SubmenuRepository,
                 dish_repository: DishRepository):
        self.menu_repository = menu_repository
        self.submenu_repository = submenu_repository
        self.dish_repository = dish_repository

    async def read_menus(self):
        menus = await self.menu_repository.get_menus()
        results = []
        for menu_row in menus:
            menu = menu_row[0]  # Получаем объект модели из строки результата
            submenus_count = await self.menu_repository.get_submenus_count(menu.id)
            dishes_count = await self.menu_repository.get_dishes_count(menu.id)
            results.append(schemas.MenuOutPut(
                id=str(menu.id),
                title=menu.title,
                description=menu.description,
                submenus_count=submenus_count,
                dishes_count=dishes_count,
            ))
        return results

    async def read_menu(self, menu_id: UUID):
        menu = await self.menu_repository.get_menu(menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail='menu not found')

        submenus_count = await self.menu_repository.get_submenus_count(menu.id)
        dishes_count = await self.menu_repository.get_dishes_count(menu.id)

        return schemas.MenuOutPut(
            id=menu.id,
            title=menu.title,
            description=menu.description,
            submenus_count=submenus_count,
            dishes_count=dishes_count,
        )

    async def create_menu(self, menu: schemas.MenuCreate):
        db_menu = await self.menu_repository.create_menu(menu)

        return schemas.MenuOutPut(
            id=db_menu.id,
            title=db_menu.title,
            description=db_menu.description,
            submenus_count=0,
            dishes_count=0,
        )

    async def update_menu(self, menu_id: UUID, menu: schemas.MenuCreate):
        db_menu = await self.menu_repository.update_menu(menu_id, menu)

        if not db_menu:
            raise HTTPException(status_code=404, detail='menu not found')

        submenus_count = await self.menu_repository.get_submenus_count(db_menu.id)
        dishes_count = await self.menu_repository.get_dishes_count(db_menu.id)

        return schemas.MenuOutPut(
            id=db_menu.id,
            title=db_menu.title,
            description=db_menu.description,
            submenus_count=submenus_count,
            dishes_count=dishes_count,
        )

    async def delete_menu(self, menu_id: UUID):
        menu = await self.menu_repository.get_menu(menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail='menu not found')
        await self.menu_repository.delete_menu(menu_id)
        return {'status': True, 'message': 'Menu deleted'}
