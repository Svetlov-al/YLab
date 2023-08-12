from __future__ import annotations

import uuid

from sqlalchemy import Column, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType  # type: ignore

from app.database import Base


class Menu(Base):
    __tablename__ = 'menus'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)  # type: ignore
    title = Column(String)
    description = Column(String)

    submenus = relationship('Submenu', cascade='all, delete-orphan', back_populates='menu')  # type: ignore


class Submenu(Base):
    __tablename__ = 'submenus'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)  # type: ignore
    title = Column(String)
    description = Column(String)

    menu_id = Column(UUIDType(binary=False), ForeignKey('menus.id', ondelete='CASCADE'))  # type: ignore
    menu = relationship('Menu', back_populates='submenus')  # type: ignore

    dishes = relationship('Dish', cascade='all, delete-orphan', back_populates='submenu')  # type: ignore


class Dish(Base):
    __tablename__ = 'dishes'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)  # type: ignore
    title = Column(String)
    description = Column(String)
    price = Column(Numeric(10, 2))

    submenu_id = Column(UUIDType(binary=False), ForeignKey('submenus.id', ondelete='CASCADE'))  # type: ignore
    submenu = relationship('Submenu', back_populates='dishes')  # type: ignore
