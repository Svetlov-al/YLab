from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .database import Base


class Menu(Base):
    __tablename__ = 'menus'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)

    submenus = relationship("Submenu", cascade="all, delete-orphan", back_populates="menu")


class Submenu(Base):
    __tablename__ = 'submenus'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)

    menu_id = Column(Integer, ForeignKey('menus.id', ondelete="CASCADE"))
    menu = relationship("Menu", back_populates="submenus")

    dishes = relationship("Dish", cascade="all, delete-orphan", back_populates="submenu")


class Dish(Base):
    __tablename__ = 'dishes'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    price = Column(Numeric(10, 2))

    submenu_id = Column(Integer, ForeignKey('submenus.id', ondelete="CASCADE"))
    submenu = relationship("Submenu", back_populates="dishes")