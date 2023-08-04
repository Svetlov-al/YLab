from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

from app import schemas
from app.config import settings
from app.database import get_db
from app.database_repository import MenuRepository, SubmenuRepository
from app.submenu_service import SubmenuService

router = APIRouter(
    prefix='/api/v1',
    tags=['Submenus']
)

cache_expire_time = settings.cache_expire


@router.get('/menus/{menu_id}/submenus', response_model=list[schemas.SubmenuOut])
@cache(expire=cache_expire_time)
def read_submenus(menu_id: UUID, db: Session = Depends(get_db)):
    submenu_service = SubmenuService(MenuRepository(db), SubmenuRepository(db))
    return submenu_service.read_submenus(menu_id)


@router.get('/menus/{menu_id}/submenus/{submenu_id}', response_model=schemas.SubmenuOutPut,
            status_code=status.HTTP_200_OK)
@cache(expire=cache_expire_time)
def read_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    submenu_service = SubmenuService(MenuRepository(db), SubmenuRepository(db))
    submenu = submenu_service.read_submenu(menu_id, submenu_id)
    return submenu


@router.post('/menus/{menu_id}/submenus', response_model=schemas.SubmenuOutPut, status_code=status.HTTP_201_CREATED)
def create_submenu(menu_id: UUID, submenu: schemas.SubmenuCreate, db: Session = Depends(get_db)):
    submenu_service = SubmenuService(MenuRepository(db), SubmenuRepository(db))
    submenu_created = submenu_service.create_submenu(menu_id, submenu)
    return submenu_created


@router.patch('/menus/{menu_id}/submenus/{submenu_id}', response_model=schemas.SubmenuOutPut)
def update_submenu(menu_id: UUID, submenu_id: UUID, submenu: schemas.SubmenuCreate, db: Session = Depends(get_db)):
    submenu_service = SubmenuService(MenuRepository(db), SubmenuRepository(db))
    submenu_updated = submenu_service.update_submenu(menu_id, submenu_id, submenu)
    return submenu_updated


@router.delete('/menus/{menu_id}/submenus/{submenu_id}')
def delete_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    submenu_service = SubmenuService(MenuRepository(db), SubmenuRepository(db))
    submenu_service.delete_submenu(menu_id, submenu_id)
    return {'message': 'Submenu deleted'}
