import json
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.background_work import recursive_dictify
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


@router.post('/invalidate/')
async def trigger_invalidation(background_tasks: BackgroundTasks):
    background_tasks.add_task(redis_client.clear_all)
    return {'message': 'Cache invalidation has been triggered in the background'}


@router.get('/', status_code=status.HTTP_200_OK)
async def root(db: AsyncSession = Depends(get_db)):
    menu_repo = MenuRepository(db)
    submenu_repo = SubmenuRepository(db)
    dish_repo = DishRepository(db)

    menu_service = MenuService(menu_repo, submenu_repo, dish_repo)
    menus = await menu_service.get_full_menus()
    return recursive_dictify(menus)


@router.get('/menus', status_code=status.HTTP_200_OK)
async def read_menus(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    cached_menus = await redis_client.get_list('menus')
    if cached_menus:
        return json.loads(cached_menus[0])

    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menus = await menu_service.read_menus()

    serialized_menus = json.dumps([{'id': str(menu.id), **menu.dict(exclude={'id'})} for menu in menus])
    background_tasks.add_task(redis_client.add_to_list, 'menus', serialized_menus, cache_expire_time)

    return menus


@router.get('/menus/{menu_id}', response_model=schemas.MenuOutPut, status_code=status.HTTP_200_OK)
async def read_menu(menu_id: UUID, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    cache_key = f'MenuData_{menu_id}'
    cached_menu = await redis_client.get_key(cache_key)
    if cached_menu:
        return json.loads(cached_menu)

    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu = await menu_service.read_menu(menu_id)

    serialized_menu = json.dumps({'id': str(menu.id), **menu.dict(exclude={'id'})})
    background_tasks.add_task(redis_client.set_key, cache_key, serialized_menu, cache_expire_time)

    return schemas.MenuOutPut.dict(menu)


@router.post('/menus', status_code=status.HTTP_201_CREATED, response_model=schemas.MenuOutPut)
async def create_menu(menu: schemas.MenuCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu_created = await menu_service.create_menu(menu)

    background_tasks.add_task(redis_client.delete_key, 'menus')

    return schemas.MenuOutPut.dict(menu_created)


@router.patch('/menus/{menu_id}', response_model=schemas.MenuOutPut)
async def update_menu(menu_id: UUID, menu: schemas.MenuBase, background_tasks: BackgroundTasks,
                      db: AsyncSession = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu_updated = await menu_service.update_menu(menu_id, menu)

    background_tasks.add_task(redis_client.delete_key, 'menus')
    background_tasks.add_task(redis_client.delete_key, f'MenuData_{menu_id}')

    return schemas.MenuOutPut.dict(menu_updated)


@router.delete('/menus/{menu_id}')
async def delete_menu(menu_id: UUID, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    await menu_service.delete_menu(menu_id)

    background_tasks.add_task(redis_client.delete_key, 'menus')
    background_tasks.add_task(redis_client.delete_key, f'MenuData_{menu_id}')

    return {'status': True, 'message': 'Menu deleted'}
