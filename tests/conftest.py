import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base
from app.main import app

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Testing_SessionLocal = sessionmaker(
    autocommit=False, autoflush=True, bind=engine)


@pytest.fixture(scope='function', autouse=True)
def db_session():
    Base.metadata.create_all(bind=engine)
    db = Testing_SessionLocal()
    transaction = db.begin()
    try:
        yield db
    finally:
        transaction.rollback()
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def client():
    with TestClient(app=app) as client:
        yield client


@pytest.fixture()
def fixture_menu():
    menu = {'title': 'New menu', 'description': 'New description'}
    return menu


@pytest.fixture()
def fixture_menu_update():
    menu = {'title': 'Updated menu', 'description': 'Updated description'}
    return menu


@pytest.fixture()
def fixture_submenu():
    submenus = {'title': 'New submenu', 'description': 'New description'}
    return submenus


@pytest.fixture()
def fixture_submenu_update():
    submenus = {'title': 'Updated submenu', 'description': 'Updated description'}
    return submenus


@pytest.fixture()
def fixture_dish():
    dish = {'title': 'New dish', 'description': 'New description', 'price': 1111.01}
    return dish


@pytest.fixture()
def fixture_dish_update():
    dish = {'title': 'Updated dish', 'description': 'Updated description', 'price': 2222.01}
    return dish


@pytest.fixture()
def create_menu(client, fixture_menu):
    response = client.post('/api/v1/menus', json=fixture_menu)
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def create_submenu(client, create_menu, fixture_submenu):
    menu_id = create_menu['id']
    response = client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def create_dish(client, create_submenu, fixture_dish):
    menu_id = create_submenu['menu_id']
    submenu_id = create_submenu['id']
    response = client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=fixture_dish)
    assert response.status_code == 201
    return response.json()
