import json
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas
from app.config import settings
from app.database import get_db
from app.database_repository import DishRepository, MenuRepository, SubmenuRepository
from app.menu_service import MenuService
from app.tools import redis_client

router = APIRouter(
    prefix='/api/v1',
    tags=['Menu']
)

cache_expire_time = settings.cache_expire


@router.get('/menus', status_code=status.HTTP_200_OK)
async def read_menus(db: Session = Depends(get_db)):
    cached_menus = await redis_client.get_list('menus')
    if cached_menus:
        return json.loads(cached_menus[0])
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menus = menu_service.read_menus()
    # Сериализация списка меню в строку JSON и добавление в кеш
    serialized_menus = json.dumps([{'id': str(menu.id), **menu.dict(exclude={'id'})} for menu in menus])
    await redis_client.add_to_list('menus', serialized_menus, expire_time=cache_expire_time)
    return menus


@router.get('/menus/{menu_id}', response_model=schemas.MenuOutPut, status_code=status.HTTP_200_OK)
async def read_menu(menu_id: UUID, db: Session = Depends(get_db)):

    cache_key = f'MenuData_{menu_id}'
    # Попробуем получить меню из кеша
    cached_menu = await redis_client.get_key(cache_key)
    if cached_menu:
        return json.loads(cached_menu)

    # Если меню нет в кеше, получим его из базы данных
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu = menu_service.read_menu(menu_id)

    # Сериализуем меню в строку JSON и добавим в кеш
    serialized_menu = json.dumps({'id': str(menu.id), **menu.dict(exclude={'id'})})
    await redis_client.set_key(cache_key, serialized_menu, expire_time=cache_expire_time)

    return schemas.MenuOutPut.model_validate(menu)


@router.post('/menus', status_code=status.HTTP_201_CREATED, response_model=schemas.MenuOutPut)
async def create_menu(menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu_created = menu_service.create_menu(menu)

    # Инвалидация кеша
    await redis_client.delete_key('menus')

    return schemas.MenuOutPut.model_validate(menu_created)


@router.patch('/menus/{menu_id}', response_model=schemas.MenuOutPut)
async def update_menu(menu_id: UUID, menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu_updated = menu_service.update_menu(menu_id, menu)

    # Инвалидация кеша
    await redis_client.delete_key('menus')
    await redis_client.delete_key(f'MenuData_{menu_id}')

    return schemas.MenuOutPut.model_validate(menu_updated)


@router.delete('/menus/{menu_id}')
async def delete_menu(menu_id: UUID, db: Session = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu_service.delete_menu(menu_id)

    # Инвалидация кеша
    await redis_client.delete_key('menus')
    await redis_client.delete_key(f'MenuData_{menu_id}')

    return {'status': True, 'message': 'Menu deleted'}
