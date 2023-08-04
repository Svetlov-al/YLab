from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

from app import schemas
from app.config import settings
from app.database import get_db
from app.database_repository import DishRepository, MenuRepository, SubmenuRepository
from app.menu_service import MenuService

router = APIRouter(
    prefix='/api/v1',
    tags=['Menu']
)

cache_expire_time = settings.cache_expire


@router.get('/menus', status_code=status.HTTP_200_OK)
@cache(expire=cache_expire_time)
def read_menus(db: Session = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    return menu_service.read_menus()


@router.get('/menus/{menu_id}', response_model=schemas.MenuOutPut, status_code=status.HTTP_200_OK)
@cache(expire=cache_expire_time)
def read_menu(menu_id: UUID, db: Session = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu = menu_service.read_menu(menu_id)
    return schemas.MenuOutPut.model_validate(menu)


@router.post('/menus', status_code=status.HTTP_201_CREATED, response_model=schemas.MenuOutPut)
def create_menu(menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu_created = menu_service.create_menu(menu)
    return schemas.MenuOutPut.model_validate(menu_created)


@router.patch('/menus/{menu_id}', response_model=schemas.MenuOutPut)
def update_menu(menu_id: UUID, menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu_updated = menu_service.update_menu(menu_id, menu)
    return schemas.MenuOutPut.model_validate(menu_updated)


@router.delete('/menus/{menu_id}')
def delete_menu(menu_id: UUID, db: Session = Depends(get_db)):
    menu_service = MenuService(MenuRepository(db), SubmenuRepository(db), DishRepository(db))
    menu_service.delete_menu(menu_id)
    return {'status': True, 'message': 'Menu deleted'}
