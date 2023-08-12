import json
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

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


def recursive_dictify(obj) -> dict | list:
    if isinstance(obj, list):
        return [recursive_dictify(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        obj_dict = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):  # Исключаем служебные атрибуты
                obj_dict[key] = recursive_dictify(value)
        return obj_dict
    else:
        return obj


@router.get('/', status_code=status.HTTP_200_OK)
async def root(db: AsyncSession = Depends(get_db)):
    menu_repo = MenuRepository(db)
    submenu_repo = SubmenuRepository(db)
    dish_repo = DishRepository(db)

    menu_service = MenuService(menu_repo, submenu_repo, dish_repo)
    menus = await menu_service.get_full_menus()
    return recursive_dictify(menus)


@router.get('/menus', status_code=status.HTTP_200_OK)
async def read_menus(db: AsyncSession = Depends(get_db)):
    cached_menus = await redis_client.get_list('menus')
    if cached_menus:
        return json.loads(cached_menus[0])
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menus = await menu_service.read_menus()
    # Сериализация списка меню в строку JSON и добавление в кеш
    serialized_menus = json.dumps([{'id': str(menu.id), **menu.dict(exclude={'id'})} for menu in menus])
    await redis_client.add_to_list('menus', serialized_menus, expire_time=cache_expire_time)
    return menus


@router.get('/menus/{menu_id}', response_model=schemas.MenuOutPut, status_code=status.HTTP_200_OK)
async def read_menu(menu_id: UUID, db: AsyncSession = Depends(get_db)):

    cache_key = f'MenuData_{menu_id}'
    # Попробуем получить меню из кеша
    cached_menu = await redis_client.get_key(cache_key)
    if cached_menu:
        return json.loads(cached_menu)

    # Если меню нет в кеше, получим его из базы данных
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu = await menu_service.read_menu(menu_id)

    # Сериализуем меню в строку JSON и добавим в кеш
    serialized_menu = json.dumps({'id': str(menu.id), **menu.dict(exclude={'id'})})
    await redis_client.set_key(cache_key, serialized_menu, expire_time=cache_expire_time)

    return schemas.MenuOutPut.model_validate(menu)


@router.post('/menus', status_code=status.HTTP_201_CREATED, response_model=schemas.MenuOutPut)
async def create_menu(menu: schemas.MenuCreate, db: AsyncSession = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu_created = await menu_service.create_menu(menu)

    # Инвалидация кеша
    await redis_client.delete_key('menus')

    return schemas.MenuOutPut.model_validate(menu_created)


@router.patch('/menus/{menu_id}', response_model=schemas.MenuOutPut)
async def update_menu(menu_id: UUID, menu: schemas.MenuBase, db: AsyncSession = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu_updated = await menu_service.update_menu(menu_id, menu)

    # Инвалидация кеша
    await redis_client.delete_key('menus')
    await redis_client.delete_key(f'MenuData_{menu_id}')

    return schemas.MenuOutPut.model_validate(menu_updated)


@router.delete('/menus/{menu_id}')
async def delete_menu(menu_id: UUID, db: AsyncSession = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    await menu_service.delete_menu(menu_id)

    # Инвалидация кеша
    await redis_client.delete_key('menus')
    await redis_client.delete_key(f'MenuData_{menu_id}')

    return {'status': True, 'message': 'Menu deleted'}
