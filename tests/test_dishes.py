import uuid

import httpx
import pytest
from asgi_lifespan import LifespanManager

from app.main import app


@pytest.mark.asyncio
class TestDish:

    async def test_read_dishes(self, fixture_menu, fixture_submenu, fixture_dish):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = menu_response.json()['id']

                submenu_response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
                submenu_id = submenu_response.json()['id']

                dish_response = await client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
                                                  json=fixture_dish)
                assert dish_response.status_code == 201

                response = await client.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes')
                assert response.status_code == 200
                assert len(response.json()) == 1
                assert response.json()[0]['title'] == fixture_dish['title']
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_create_dish(self, fixture_menu, fixture_submenu, fixture_dish):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = menu_response.json()['id']

                submenu_response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
                submenu_id = submenu_response.json()['id']

                response = await client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=fixture_dish)
                assert response.status_code == 201
                data = response.json()
                assert data['title'] == fixture_dish['title']
                assert data['description'] == fixture_dish['description']
                assert data['price'] == str(fixture_dish['price'])
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_update_dish(self, fixture_menu, fixture_submenu, fixture_dish, fixture_dish_update):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = menu_response.json()['id']

                submenu_response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
                submenu_id = submenu_response.json()['id']

                dish_response = await client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
                                                  json=fixture_dish)
                dish_id = dish_response.json()['id']

                response = await client.patch(
                    f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', json=fixture_dish_update)
                assert response.status_code == 200
                data = response.json()
                assert data['title'] == fixture_dish_update['title']
                assert data['description'] == fixture_dish_update['description']
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_update_not_exist_dish(self, fixture_menu, fixture_submenu, fixture_dish_update):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = menu_response.json()['id']

                submenu_response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
                submenu_id = submenu_response.json()['id']

                random_uuid = uuid.uuid4()
                response = await client.patch(
                    f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{random_uuid}', json=fixture_dish_update)
                assert response.status_code == 404
                assert response.json() == {'detail': 'dish not found'}
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_delete_dish(self, fixture_menu, fixture_submenu, fixture_dish):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = menu_response.json()['id']

                submenu_response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
                submenu_id = submenu_response.json()['id']

                dish_response = await client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
                                                  json=fixture_dish)
                dish_id = dish_response.json()['id']

                response = await client.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
                assert response.status_code == 200
                assert response.json() == {'status': True, 'message': 'The dish has been deleted'}
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_delete_not_exist_dish(self, fixture_menu, fixture_submenu):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                menu_id = menu_response.json()['id']

                submenu_response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
                submenu_id = submenu_response.json()['id']

                random_uuid = uuid.uuid4()
                response = await client.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{random_uuid}')
                assert response.status_code == 404
                assert response.json() == {'detail': 'dish not found'}
                await client.delete(f'/api/v1/menus/{menu_id}')
