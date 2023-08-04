from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.database_repository import DishRepository, MenuRepository, SubmenuRepository
from app.dish_service import DishService

router = APIRouter(
    prefix='/api/v1',
    tags=['Dishes']
)


@router.get('/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=list[schemas.Dish])
def read_dishes(menu_id: UUID, submenu_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dish_service = DishService(DishRepository(db), SubmenuRepository(db), MenuRepository(db))
    return dish_service.read_dishes(submenu_id, skip, limit)


@router.get('/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=schemas.Dish)
def read_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: Session = Depends(get_db)):
    dish_service = DishService(DishRepository(db), SubmenuRepository(db), MenuRepository(db))
    dish = dish_service.read_dish(menu_id, submenu_id, dish_id)
    return dish


@router.post('/menus/{menu_id}/submenus/{submenu_id}/dishes', status_code=status.HTTP_201_CREATED,
             response_model=schemas.DishOut)
def create_dish(menu_id: UUID, submenu_id: UUID, dish: schemas.DishCreate, db: Session = Depends(get_db)):
    dish_service = DishService(DishRepository(db), SubmenuRepository(db), MenuRepository(db))
    return dish_service.create_dish(menu_id, submenu_id, dish)


@router.patch('/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=schemas.DishOut)
def update_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: schemas.DishCreate,
                db: Session = Depends(get_db)):
    dish_service = DishService(DishRepository(db), SubmenuRepository(db), MenuRepository(db))
    return dish_service.update_dish(menu_id, submenu_id, dish_id, dish)


@router.delete('/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: Session = Depends(get_db)):
    dish_service = DishService(DishRepository(db), SubmenuRepository(db), MenuRepository(db))
    return dish_service.delete_dish(menu_id, submenu_id, dish_id)
