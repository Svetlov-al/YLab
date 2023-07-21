from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix='/api/v1',
    tags=['Submenus']
)


@router.get("/menus/{menu_id}/submenus")
def read_submenus(menu_id: int, db: Session = Depends(get_db)):
    submenus = db.query(models.Submenu).filter(models.Submenu.menu_id == menu_id).all()
    return submenus


@router.get("/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.SubmenuOutPut,
            status_code=status.HTTP_200_OK)
def read_submenu(menu_id: int, submenu_id: int, db: Session = Depends(get_db)):
    submenu = db.query(models.Submenu).filter(models.Submenu.id == submenu_id, models.Submenu.menu_id == menu_id).first()
    if not submenu:
        raise HTTPException(status_code=404, detail="submenu not found")

    # Convert the submenu object to a dictionary
    submenu_dict = {**submenu.__dict__}
    submenu_dict.pop("_sa_instance_state", None)

    # Query to get the dish count
    dishes_count = db.query(models.Dish).filter(models.Dish.submenu_id == submenu_id).count()

    # Add the additional fields
    submenu_dict.update({
        "dishes_count": dishes_count
    })

    # Convert the dictionary back to a Submenu object
    submenu_dict['id'] = str(submenu_dict['id'])
    return schemas.SubmenuOutPut.model_validate(submenu_dict)


@router.post("/menus/{menu_id}/submenus", response_model=schemas.SubmenuOut, status_code=status.HTTP_201_CREATED)
def create_submenu(menu_id: int, submenu: schemas.SubmenuCreate, db: Session = Depends(get_db)):
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if db_menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    new_sub_menu = models.Submenu(menu_id=menu_id, **submenu.model_dump())
    db.add(new_sub_menu)
    db.commit()
    db.refresh(new_sub_menu)
    # Convert the SQLAlchemy model to a dictionary
    submenu_dict = {**new_sub_menu.__dict__}
    submenu_dict.pop("_sa_instance_state", None)
    # Convert the dictionary back to a Pydantic model
    submenu_dict['id'] = str(submenu_dict['id'])
    return schemas.SubmenuOut(**submenu_dict)


@router.patch("/menus/{menu_id}/submenus/{submenu_id}")
def update_submenu(menu_id: int, submenu_id: int, submenu: schemas.SubmenuCreate, db: Session = Depends(get_db)):
    db_submenu = db.query(models.Submenu).filter(models.Submenu.id == submenu_id).first()
    if not db_submenu:
        raise HTTPException(status_code=404, detail="Submenu not found")

    db_submenu.title = submenu.title
    db_submenu.description = submenu.description
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)

    return db_submenu


@router.delete("/menus/{menu_id}/submenus/{submenu_id}")
def delete_submenu(menu_id: int, submenu_id: int, db: Session = Depends(get_db)):
    submenu = db.query(models.Submenu).filter(models.Submenu.id == submenu_id).first()
    if not submenu:
        raise HTTPException(status_code=404, detail="Submenu not found")
    db.delete(submenu)
    db.commit()
    return {"message": "Submenu deleted"}