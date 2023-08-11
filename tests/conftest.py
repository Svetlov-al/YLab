import asyncio

import pytest

from app.tools import redis_client


@pytest.fixture(autouse=True)
async def clear_cache_after_test():
    yield  # здесь выполняется тест
    await redis_client.clear_all()


@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


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
