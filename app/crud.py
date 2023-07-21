from sqlalchemy.orm import Session
from app import models, schemas
from fastapi import HTTPException


# CRUD for Menu
def get_menu(db: Session, menu_id: int):
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if db_menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    return db_menu


def get_menus(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Menu).offset(skip).limit(limit).all()


def create_menu(db: Session, menu: schemas.MenuCreate):
    db_menu = models.Menu(title=menu.title, description=menu.description)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu


def update_menu(db: Session, menu: schemas.MenuCreate, menu_id: int):
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if db_menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    db_menu.title = menu.title
    db_menu.description = menu.description
    db.commit()
    db.refresh(db_menu)
    return db_menu


def delete_menu(db: Session, menu_id: int):
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    print(db_menu)
    if db_menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    db.delete(db_menu)
    db.commit()
    return {'status': True, 'message': 'Deleted'}


# CRUD for Submenu
def get_submenu(db: Session, submenu_id: int):
    db_submenu = db.query(models.Submenu).filter(models.Submenu.id == submenu_id).first()
    if db_submenu is None:
        raise HTTPException(status_code=404, detail="Submenu not found")
    return db_submenu


def get_submenus(db: Session, menu_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Submenu).filter(models.Submenu.menu_id == menu_id).offset(skip).limit(limit).all()


def create_submenu(db: Session, submenu: schemas.SubmenuCreate, menu_id: int):
    db_submenu = models.Submenu(**submenu.model_dump(), menu_id=menu_id)
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return db_submenu


def update_submenu(db: Session, submenu: schemas.SubmenuCreate, submenu_id: int):
    db_submenu = db.query(models.Submenu).filter(models.Submenu.id == submenu_id).first()
    if db_submenu is None:
        raise HTTPException(status_code=404, detail="Submenu not found")
    for key, value in submenu.model_dump().items():
        setattr(db_submenu, key, value)
    db.commit()
    db.refresh(db_submenu)
    return db_submenu


def delete_submenu(db: Session, submenu_id: int):
    db_submenu = db.query(models.Submenu).filter(models.Submenu.id == submenu_id).first()
    if db_submenu is None:
        raise HTTPException(status_code=404, detail="Submenu not found")
    db.delete(db_submenu)
    db.commit()
    return {'status': True, 'message': 'Deleted'}


# CRUD for Dish
def get_dish(db: Session, dish_id: int):
    db_dish = db.query(models.Dish).filter(models.Dish.id == dish_id).first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return db_dish


def get_dishes(db: Session, submenu_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Dish).filter(models.Dish.submenu_id == submenu_id).offset(skip).limit(limit).all()


def create_dish(db: Session, dish: schemas.DishCreate, submenu_id: int):
    db_dish = models.Dish(**dish.model_dump(), submenu_id=submenu_id)
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


def update_dish(db: Session, dish: schemas.DishCreate, dish_id: int):
    db_dish = db.query(models.Dish).filter(models.Dish.id == dish_id).first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    for key, value in dish.model_dump().items():
        setattr(db_dish, key, value)
    db.commit()
    db.refresh(db_dish)
    return db_dish


def delete_dish(db: Session, dish_id: int):
    db_dish = db.query(models.Dish).filter(models.Dish.id == dish_id).first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    db.delete(db_dish)
    db.commit()
    return {'status': True, 'message': 'Deleted'}
