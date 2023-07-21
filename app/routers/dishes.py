from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix='/api/v1',
    tags=['Dishes']
)


@router.get("/menus/{menu_id}/submenus/{submenu_id}/dishes")
def read_dishes(menu_id: int, submenu_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dishes = db.query(models.Dish).filter(models.Dish.submenu_id == submenu_id).offset(skip).limit(limit).all()
    return [schemas.Dish(**dish.__dict__) for dish in dishes]


@router.get("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=schemas.DishOut)
def read_dish(menu_id: int, submenu_id: int, dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(models.Dish).filter(models.Dish.id == dish_id, models.Dish.submenu_id == submenu_id).first()
    if dish is None:
        raise HTTPException(status_code=404, detail="dish not found")

    # Convert the SQLAlchemy model to a dictionary
    dishes_dict = {**dish.__dict__}
    dishes_dict.pop("_sa_instance_state", None)
    # Convert the dictionary back to a Pydantic model
    dishes_dict['id'] = str(dishes_dict['id'])
    dishes_dict['price'] = str(dishes_dict['price'])
    return schemas.DishOut(**dishes_dict)


@router.post("/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=schemas.DishCreated,
             status_code=status.HTTP_201_CREATED)
def create_dish(menu_id: int, submenu_id: int, dish: schemas.DishCreate, db: Session = Depends(get_db)):
    db_submenu = db.query(models.Submenu).filter(models.Submenu.id == submenu_id).first()
    if db_submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    db_dish = models.Dish(**dish.model_dump(), submenu_id=submenu_id)
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    # Convert the SQLAlchemy model to a dictionary
    dishes_dict = {**db_dish.__dict__}
    dishes_dict.pop("_sa_instance_state", None)
    # Convert the dictionary back to a Pydantic model
    dishes_dict['id'] = str(dishes_dict['id'])
    return schemas.DishCreated(**dishes_dict)


@router.patch("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=schemas.DishOut)
def update_dish(menu_id: int, submenu_id: int, dish_id: int, dish: schemas.DishCreate, db: Session = Depends(get_db)):
    db_dish = db.query(models.Dish).filter(models.Dish.id == dish_id, models.Dish.submenu_id == submenu_id).first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    for key, value in dish.model_dump().items():
        setattr(db_dish, key, value)
    db.commit()
    db.refresh(db_dish)
    # Convert the SQLAlchemy model to a dictionary
    dishes_dict = {**db_dish.__dict__}
    dishes_dict.pop("_sa_instance_state", None)
    # Convert the dictionary back to a Pydantic model
    dishes_dict['id'] = str(dishes_dict['id'])
    dishes_dict['price'] = str(dishes_dict['price'])
    return schemas.DishOut(**dishes_dict)


@router.delete("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
def delete_dish(menu_id: int, submenu_id: int, dish_id: int, db: Session = Depends(get_db)):
    db_dish = db.query(models.Dish).filter(models.Dish.id == dish_id, models.Dish.submenu_id == submenu_id).first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    db.delete(db_dish)
    db.commit()
    return {"detail": "Dish deleted"}
