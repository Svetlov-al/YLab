import uuid

import httpx
import pytest
from asgi_lifespan import LifespanManager

from app.main import app


@pytest.mark.asyncio
class TestMenu:

    async def test_menu_has_correct_number_of_submenus_and_dishes(self, fixture_menu, fixture_submenu,
                                                                  fixture_dish):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                # Создание меню
                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = menu_response.json()['id']

                # Создание подменю
                submenu_response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
                submenu_id = submenu_response.json()['id']
                # Создание блюда в подменю
                await client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
                                  json=fixture_dish)

                # Проверка количества подменю и блюд в меню
                response = await client.get(f'/api/v1/menus/{menu_id}')
                assert response.status_code == 200
                data = response.json()

                assert data['submenus_count'] == 1
                assert data['dishes_count'] == 1
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_read_menus(self, fixture_menu):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                response = await client.get('/api/v1/menus')
                assert response.status_code == 200

                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = menu_response.json()['id']
                response = await client.get('/api/v1/menus')
                assert response.status_code == 200
                assert len(response.json()) == 1
                assert response.json()[0]['title'] == fixture_menu['title']
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_read_menu(self, fixture_menu):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = menu_response.json()['id']
                response = await client.get(f'/api/v1/menus/{menu_id}')
                assert response.status_code == 200
                data = response.json()
                assert data['title'] == fixture_menu['title']
                assert data['description'] == fixture_menu['description']
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_read_not_exist_menu(self):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                random_uuid = uuid.uuid4()
                response = await client.get(f'/api/v1/menus/{random_uuid}')
                assert response.status_code == 404

    async def test_create_menu(self, fixture_menu):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = menu_response.json()['id']
                assert menu_response.status_code == 201
                data = menu_response.json()
                assert data['title'] == fixture_menu['title']
                assert data['description'] == fixture_menu['description']
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_update_menu(self, fixture_menu_update, fixture_menu):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                to_update_response = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = to_update_response.json()['id']
                to_update_data = to_update_response.json()
                response = await client.patch(f'/api/v1/menus/{to_update_data["id"]}', json=fixture_menu_update)
                assert response.status_code == 200
                data = response.json()
                assert data['title'] == fixture_menu_update['title']
                assert data['description'] == fixture_menu_update['description']
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_update_not_exist_menu(self, fixture_menu_update):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                random_uuid = uuid.uuid4()
                response = await client.patch(f'/api/v1/menus/{random_uuid}', json=fixture_menu_update)
                assert response.status_code == 404
                assert response.json() == {'detail': 'menu not found'}

    async def test_delete_menu(self, fixture_menu):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                # Создание меню
                create_response = await client.post('/api/v1/menus', json=fixture_menu)
                assert create_response.status_code == 201  # или другой ожидаемый статус кода
                menu_data = create_response.json()
                menu_id = menu_data['id']

                # Удаление меню
                response = await client.delete(f'/api/v1/menus/{menu_id}')
                assert response.status_code == 200
                assert response.json() == {'status': True, 'message': 'Menu deleted'}

    async def test_matreshka(self, fixture_menu, fixture_submenu, fixture_dish):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                # Создание меню
                create_menu = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = create_menu.json()['id']

                # Создание подменю
                submenu_response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
                submenu_id = submenu_response.json()['id']

                # Создание блюда в подменю
                await client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=fixture_dish)

                # Проверка количества подменю и блюд в меню
                response = await client.get('/api/v1/')
                assert response.status_code == 200
                data = response.json()
                # Проверка структуры и содержимого меню
                assert 'id' in data[0]
                assert 'title' in data[0]
                assert 'description' in data[0]
                assert 'submenus' in data[0]
                # assert isinstance(data["submenus"], list)

                # Проверка структуры и содержимого подменю
                submenu = data[0]['submenus'][0]
                assert 'id' in submenu
                assert 'title' in submenu
                assert 'description' in submenu
                assert 'dishes' in submenu
                # assert isinstance(submenu["dishes"], list)

                # Проверка структуры и содержимого блюда
                dish = submenu['dishes'][0]
                assert 'id' in dish
                assert 'title' in dish
                assert 'description' in dish
                assert 'price' in dish

                await client.delete(f'/api/v1/menus/{menu_id}')
