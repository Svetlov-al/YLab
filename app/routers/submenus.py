import json
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas
from app.config import settings
from app.database import get_db
from app.database_repository import MenuRepository, SubmenuRepository
from app.submenu_service import SubmenuService
from app.tools import redis_client

router = APIRouter(
    prefix='/api/v1',
    tags=['Submenus']
)

cache_expire_time = settings.cache_expire


@router.get('/menus/{menu_id}/submenus', response_model=list[schemas.SubmenuOut])
async def read_submenus(menu_id: UUID, db: Session = Depends(get_db)):
    cache_key = f'Submenus_{menu_id}'

    # Попробуем получить подменю из кеша
    cached_submenus = await redis_client.get_key(cache_key)
    if cached_submenus:
        return json.loads(cached_submenus)

    # Если подменю нет в кеше, получим их из базы данных
    submenu_service = SubmenuService(MenuRepository(db), SubmenuRepository(db))
    submenus = await submenu_service.read_submenus(menu_id)

    # Преобразуем каждый объект Submenu в экземпляр Pydantic модели
    pydantic_submenus = [schemas.SubmenuOut(**submenu.__dict__) for submenu in submenus]

    # Сериализуем подменю в строку JSON и добавим в кеш
    serialized_submenus = json.dumps([{'id': str(submenu.id), 'menu_id': str(submenu.menu_id),
                                       **submenu.model_dump(exclude={'id', 'menu_id'})} for submenu in pydantic_submenus])
    await redis_client.set_key(cache_key, serialized_submenus, expire_time=cache_expire_time)

    return submenus


@router.get('/menus/{menu_id}/submenus/{submenu_id}', response_model=schemas.SubmenuOutPut,
            status_code=status.HTTP_200_OK)
async def read_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    cache_key = f'Submenu_{menu_id}'

    # Попробуем получить подменю из кеша
    cached_submenus = await redis_client.get_key(cache_key)
    if cached_submenus:
        return json.loads(cached_submenus)

    submenu_service = SubmenuService(MenuRepository(db), SubmenuRepository(db))
    submenu = await submenu_service.read_submenu(menu_id, submenu_id)

    # Сериализуем подменю в строку JSON и добавим в кеш
    serialized_submenu = json.dumps(
        {
            'id': str(submenu.id),
            'menu_id': str(submenu.menu_id),
            **submenu.dict(exclude={'id', 'menu_id'})
        })
    await redis_client.set_key(cache_key, serialized_submenu, expire_time=cache_expire_time)

    return submenu


@router.post('/menus/{menu_id}/submenus', response_model=schemas.SubmenuOutPut, status_code=status.HTTP_201_CREATED)
async def create_submenu(menu_id: UUID, submenu: schemas.SubmenuCreate, db: Session = Depends(get_db)):
    submenu_service = SubmenuService(MenuRepository(db), SubmenuRepository(db))
    submenu_created = await submenu_service.create_submenu(menu_id, submenu)

    # Удаление кеша связанного с этим меню
    await redis_client.delete_key('menus')
    await redis_client.delete_key(f'MenuData_{menu_id}')
    await redis_client.delete_key(f'Submenus_{menu_id}')
    await redis_client.delete_key(f'Submenu_{menu_id}')

    return submenu_created


@router.patch('/menus/{menu_id}/submenus/{submenu_id}', response_model=schemas.SubmenuOutPut)
async def update_submenu(menu_id: UUID, submenu_id: UUID, submenu: schemas.SubmenuCreate, db: Session = Depends(get_db)):
    submenu_service = SubmenuService(MenuRepository(db), SubmenuRepository(db))
    submenu_updated = await submenu_service.update_submenu(menu_id, submenu_id, submenu)

    # Удаление кеша связанного с этим меню
    await redis_client.delete_key('menus')
    await redis_client.delete_key(f'MenuData_{menu_id}')
    await redis_client.delete_key(f'Submenus_{menu_id}')
    await redis_client.delete_key(f'Submenu_{menu_id}')

    return submenu_updated


@router.delete('/menus/{menu_id}/submenus/{submenu_id}')
async def delete_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    submenu_service = SubmenuService(MenuRepository(db), SubmenuRepository(db))
    await submenu_service.delete_submenu(menu_id, submenu_id)

    # Удаление кеша связанного с этим меню
    await redis_client.delete_key('menus')
    await redis_client.delete_key(f'MenuData_{menu_id}')
    await redis_client.delete_key(f'Submenus_{menu_id}')
    await redis_client.delete_key(f'Submenu_{menu_id}')

    return {'message': 'submenu deleted'}
