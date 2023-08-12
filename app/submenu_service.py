from uuid import UUID

from fastapi import HTTPException

from app import schemas
from app.database_repository import MenuRepository, SubmenuRepository


class SubmenuService:
    def __init__(self, menu_repository: MenuRepository, submenu_repository: SubmenuRepository):
        self.submenu_repository = submenu_repository
        self.menu_repository = menu_repository

    async def read_submenus(self, menu_id: UUID):
        submenus = await self.submenu_repository.get_submenus(menu_id)
        return submenus

    async def read_submenu(self, menu_id: UUID, submenu_id: UUID):
        submenu = await self.submenu_repository.get_submenu(menu_id, submenu_id)
        if not submenu:
            raise HTTPException(status_code=404, detail='submenu not found')

        dishes_count = await self.menu_repository.get_dishes_count(menu_id)
        return schemas.SubmenuOutPut(
            id=submenu.id,
            title=submenu.title,
            description=submenu.description,
            menu_id=submenu.menu_id,
            dishes_count=dishes_count,
        )

    async def create_submenu(self, menu_id: UUID, submenu_data: schemas.SubmenuCreate):
        menu = await self.menu_repository.get_menu(menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail='menu not found')
        submenu = await self.submenu_repository.create_submenu(menu_id, submenu_data)

        return schemas.SubmenuOutPut(
            id=submenu.id,
            title=submenu.title,
            description=submenu.description,
            menu_id=submenu.menu_id,
            dishes_count=0,
        )

    async def update_submenu(self, menu_id: UUID, submenu_id: UUID, submenu_data: schemas.SubmenuBase):
        submenu = await self.submenu_repository.update_submenu(menu_id, submenu_id, submenu_data)

        if not submenu:
            raise HTTPException(status_code=404, detail='submenu not found')

        dishes_count = await self.menu_repository.get_dishes_count(menu_id)
        return schemas.SubmenuOutPut(
            id=submenu.id,
            title=submenu.title,
            description=submenu.description,
            menu_id=submenu.menu_id,
            dishes_count=dishes_count,
        )

    async def delete_submenu(self, menu_id: UUID, submenu_id: UUID):
        submenu = await self.submenu_repository.get_submenu(menu_id, submenu_id)
        if submenu is None:
            raise HTTPException(status_code=404, detail='submenu not found')
        await self.submenu_repository.delete_submenu(menu_id, submenu_id)
        return {'status': True, 'message': 'submenu deleted'}
