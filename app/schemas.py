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
        from_attributes = True


class MenuCreated(MenuBase):
    id: str
    submenus_count: int
    dishes_count: int

    class Config:
        from_attributes = True


class SubmenuBase(BaseModel):
    title: str
    description: str


class SubmenuCreate(SubmenuBase):
    pass


class SubmenuOut(SubmenuBase):
    id: str
    menu_id: int

    class Config:
        from_attributes = True


class SubmenuOutPut(SubmenuBase):
    id: str
    menu_id: int
    dishes_count: int

    class Config:
        from_attributes = True


class Submenu(SubmenuBase):
    id: int
    dishes_count: int

    class Config:
        from_attributes = True


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
        from_attributes = True


class Dish(DishBase):
    id: int

    class Config:
        from_attributes = True
