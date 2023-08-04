from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas


class MenuRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_submenus_count(self, menu_id):
        return self.db.query(func.count(models.Submenu.id)).filter(models.Submenu.menu_id == menu_id).scalar()

    def get_dishes_count(self, menu_id):
        return self.db.query(func.count(models.Dish.id)).join(models.Submenu).filter(models.Submenu.menu_id == menu_id).scalar()

    def get_menus(self):
        return self.db.query(models.Menu).all()

    def get_menu(self, menu_id):
        return self.db.query(models.Menu).filter(models.Menu.id == menu_id).first()

    def create_menu(self, menu_data: schemas.MenuCreate):
        db_menu = models.Menu(**menu_data.model_dump())
        self.db.add(db_menu)
        self.db.commit()
        self.db.refresh(db_menu)
        return db_menu

    def update_menu(self, menu_id, menu: schemas.MenuCreate):
        db_menu = self.get_menu(menu_id)
        db_menu.title = menu.title
        db_menu.description = menu.description
        self.db.add(db_menu)
        self.db.commit()
        self.db.refresh(db_menu)
        return db_menu

    def delete_menu(self, menu_id):
        menu = self.get_menu(menu_id)
        self.db.delete(menu)
        self.db.commit()
        return menu


class SubmenuRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_submenus(self, menu_id):
        return self.db.query(models.Submenu).filter(models.Submenu.menu_id == menu_id).all()

    def get_submenu(self, menu_id, submenu_id):
        return self.db.query(models.Submenu).filter(models.Submenu.menu_id == menu_id,
                                                    models.Submenu.id == submenu_id).first()

    def create_submenu(self, menu_id, submenu_data: schemas.SubmenuCreate):
        db_submenu = models.Submenu(menu_id=menu_id, **submenu_data.model_dump())
        self.db.add(db_submenu)
        self.db.commit()
        self.db.refresh(db_submenu)
        return db_submenu

    def update_submenu(self, menu_id, submenu_id, submenu_data: schemas.SubmenuCreate):
        db_submenu = self.get_submenu(menu_id, submenu_id)
        for key, value in submenu_data.model_dump().items():
            setattr(db_submenu, key, value)
        self.db.commit()
        self.db.refresh(db_submenu)
        return db_submenu

    def delete_submenu(self, menu_id, submenu_id):
        submenu = self.get_submenu(menu_id, submenu_id)
        self.db.delete(submenu)
        self.db.commit()
        return submenu


class DishRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_dishes(self, submenu_id, skip, limit):
        return self.db.query(models.Dish).filter(models.Dish.submenu_id == submenu_id).offset(skip).limit(limit).all()

    def get_dish(self, submenu_id, dish_id):
        return self.db.query(models.Dish).filter(models.Dish.submenu_id == submenu_id,
                                                 models.Dish.id == dish_id).first()

    def create_dish(self, submenu_id, dish: schemas.DishCreate):
        dish = models.Dish(submenu_id=submenu_id, **dish.model_dump())
        self.db.add(dish)
        self.db.commit()
        self.db.refresh(dish)
        return dish

    def update_dish(self, submenu_id, dish_id, dish_data: schemas.DishCreate):
        db_dish = self.get_dish(submenu_id, dish_id)
        for key, value in dish_data.model_dump().items():
            setattr(db_dish, key, value)
        self.db.commit()
        self.db.refresh(db_dish)
        return db_dish

    def delete_dish(self, submenu_id, dish_id):
        dish = self.get_dish(submenu_id, dish_id)
        self.db.delete(dish)
        self.db.commit()
        return dish
