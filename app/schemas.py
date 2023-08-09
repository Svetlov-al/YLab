from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class MenuBase(BaseModel):
    title: str
    description: str


class MenuCreate(MenuBase):
    pass


class MenuOutPut(MenuBase):
    id: UUID
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
    id: UUID
    menu_id: UUID

    class Config:
        from_attributes = True


class SubmenuOutPut(SubmenuBase):
    id: UUID
    menu_id: UUID
    dishes_count: int | None

    class Config:
        from_attributes = True


class Submenu(SubmenuBase):
    id: UUID
    dishes_count: int | None

    class Config:
        from_attributes = True


class DishBase(BaseModel):
    title: str
    description: str
    price: Decimal


class DishCreate(DishBase):
    pass


class DishCreated(DishBase):
    id: UUID


class DishOut(BaseModel):
    id: UUID
    title: str
    description: str
    price: str

    class Config:
        from_attributes = True


class Dish(DishBase):
    id: UUID

    class Config:
        from_attributes = True
