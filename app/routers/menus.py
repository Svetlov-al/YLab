from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix='/api/v1',
    tags=['Menu']
)


@router.get("/menus", status_code=status.HTTP_200_OK)
def read_menus(db: Session = Depends(get_db)):
    menus = db.query(models.Menu).all()

    results = []
    for menu in menus:
        submenus_subquery = db.query(models.Submenu.menu_id, func.count('*').label('submenus_count')).group_by(models.Submenu.menu_id).subquery()
        dishes_subquery = db.query(models.Submenu.menu_id, func.count(models.Dish.id).label('dishes_count')).join(models.Dish).group_by(models.Submenu.menu_id).subquery()
        menu_details = db.query(models.Menu, submenus_subquery.c.submenus_count, dishes_subquery.c.dishes_count).outerjoin(submenus_subquery, models.Menu.id == submenus_subquery.c.menu_id).outerjoin(dishes_subquery, models.Menu.id == dishes_subquery.c.menu_id).filter(models.Menu.id == menu.id).first()
        menu, submenus_count, dishes_count = menu_details
        results.append({
            "id": menu.id,
            "title": menu.title,
            "description": menu.description,
            "submenus_count": submenus_count or 0,
            "dishes_count": dishes_count or 0,
        })
    return results


@router.get("/menus/{menu_id}", response_model=schemas.MenuOutPut, status_code=status.HTTP_200_OK)
def read_menu(menu_id: int, db: Session = Depends(get_db)):
    menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="menu not found")
    # Convert the menu object to a dictionary
    menu_dict = {**menu.__dict__}
    menu_dict.pop("_sa_instance_state", None)

    # Query to get the submenu count and dish count
    submenus_count = db.query(models.Submenu).filter(models.Submenu.menu_id == menu.id).count()
    dishes_count = db.query(models.Dish).join(models.Submenu).filter(models.Submenu.menu_id == menu.id).count()

    # Add the additional fields
    menu_dict.update({
        "submenus_count": submenus_count,
        "dishes_count": dishes_count
    })

    # Convert the dictionary back to a Menu object
    menu_dict['id'] = str(menu_dict['id'])
    return schemas.MenuOutPut.model_validate(menu_dict)


@router.post("/menus", status_code=status.HTTP_201_CREATED, response_model=schemas.MenuCreated)
def create_menu(menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    db_menu = models.Menu(**menu.model_dump())
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)

    # Convert the db_menu object to a dictionary
    menu_dict = {**db_menu.__dict__}
    menu_dict.pop("_sa_instance_state", None)

    # Add the additional fields
    menu_dict.update({
        "submenus_count": 0,
        "dishes_count": 0
    })

    # Convert the dictionary back to a Menu object
    menu_dict['id'] = str(menu_dict['id'])
    return schemas.MenuCreated.model_validate(menu_dict)


@router.patch("/menus/{menu_id}", response_model=schemas.MenuOutPut)
def update_menu(menu_id: int, menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()

    if not db_menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    db_menu.title = menu.title
    db_menu.description = menu.description

    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)

    # Convert the db_menu object to a dictionary
    menu_dict = {**db_menu.__dict__}
    menu_dict.pop("_sa_instance_state", None)

    # Query to get the submenu count and dish count
    submenus_count = db.query(models.Submenu).filter(models.Submenu.menu_id == db_menu.id).count()
    dishes_count = db.query(models.Dish).join(models.Submenu).filter(models.Submenu.menu_id == db_menu.id).count()

    # Add the additional fields
    menu_dict.update({
        "submenus_count": submenus_count,
        "dishes_count": dishes_count
    })

    # Convert the dictionary back to a Menu object
    menu_dict['id'] = str(menu_dict['id'])
    return schemas.MenuOutPut.model_validate(menu_dict)


@router.delete("/menus/{menu_id}")
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()

    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    db.delete(menu)
    db.commit()

    return {"status": True, "message": "Menu deleted"}