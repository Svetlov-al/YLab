import uuid

import httpx
import pytest
from asgi_lifespan import LifespanManager

from app.main import app


@pytest.mark.asyncio
class TestSubmenu:

    async def test_read_submenus(self, fixture_menu, fixture_submenu):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                assert menu_response.status_code == 201
                menu_id = menu_response.json()['id']

                await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)

                response = await client.get(f'/api/v1/menus/{menu_id}/submenus')
                assert response.status_code == 200
                assert len(response.json()) == 1
                assert response.json()[0]['title'] == fixture_submenu['title']
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_create_submenu(self, fixture_menu, fixture_submenu):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:
                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                assert menu_response.status_code == 201
                menu_id = menu_response.json()['id']

                response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
                assert response.status_code == 201
                data = response.json()
                assert data['title'] == fixture_submenu['title']
                assert data['description'] == fixture_submenu['description']
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_update_submenu(self, fixture_menu, fixture_submenu, fixture_submenu_update):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:

                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                assert menu_response.status_code == 201
                menu_id = menu_response.json()['id']

                submenu_response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
                submenu_id = submenu_response.json()['id']

                response = await client.patch(
                    f'/api/v1/menus/{menu_id}/submenus/{submenu_id}', json=fixture_submenu_update)
                assert response.status_code == 200
                data = response.json()
                assert data['title'] == fixture_submenu_update['title']
                assert data['description'] == fixture_submenu_update['description']
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_update_not_exist_submenu(self, fixture_menu, fixture_submenu_update):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:

                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                assert menu_response.status_code == 201
                menu_id = menu_response.json()['id']

                random_uuid = uuid.uuid4()
                response = await client.patch(f'/api/v1/menus/{menu_id}/submenus/{random_uuid}', json=fixture_submenu_update)
                assert response.status_code == 404
                assert response.json() == {'detail': 'submenu not found'}
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_delete_submenu(self, fixture_menu, fixture_submenu):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:

                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                assert menu_response.status_code == 201
                menu_id = menu_response.json()['id']

                submenu_response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=fixture_submenu)
                submenu_id = submenu_response.json()['id']

                response = await client.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
                assert response.status_code == 200
                assert response.json() == {'message': 'submenu deleted'}
                await client.delete(f'/api/v1/menus/{menu_id}')

    async def test_delete_not_exist_submenu(self, fixture_menu):
        async with LifespanManager(app):
            async with httpx.AsyncClient(app=app, base_url='http://test') as client:

                menu_response = await client.post('/api/v1/menus', json=fixture_menu)
                assert menu_response.status_code == 201
                menu_id = menu_response.json()['id']

                random_uuid = uuid.uuid4()
                response = await client.delete(f'/api/v1/menus/{menu_id}/submenus/{random_uuid}')
                assert response.status_code == 404
                assert response.json() == {'detail': 'submenu not found'}
                await client.delete(f'/api/v1/menus/{menu_id}')
