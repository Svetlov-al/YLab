from pydantic import BaseModel
from decimal import Decimal


class MenuBase(BaseModel):
    title: str
    description: str


class MenuCreate(MenuBase):
    pass


class MenuOutPut(MenuBase):
    id: str
    submenus_count: int
    dishes_count: int

    class Config:
        orm_mode = True


class MenuCreated(MenuBase):
    id: str
    submenus_count: int
    dishes_count: int

    class Config:
        orm_mode = True


class SubmenuBase(BaseModel):
    title: str
    description: str


class SubmenuCreate(SubmenuBase):
    pass


class SubmenuOut(SubmenuBase):
    id: str
    menu_id: int

    class Config:
        orm_mode = True


class SubmenuOutPut(SubmenuBase):
    id: str
    menu_id: int
    dishes_count: int

    class Config:
        orm_mode = True


class Submenu(SubmenuBase):
    id: int
    dishes_count: int

    class Config:
        orm_mode = True


class DishBase(BaseModel):
    title: str
    description: str
    price: Decimal


class DishCreate(DishBase):
    pass


class DishCreated(DishBase):
    id: str


class DishOut(BaseModel):
    id: str
    title: str
    description: str
    price: str

    class Config:
        orm_mode = True


class Dish(DishBase):
    id: int

    class Config:
        orm_mode = True
