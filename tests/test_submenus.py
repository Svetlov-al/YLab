import uuid


def test_read_submenus(client, create_menu, create_submenu, fixture_submenu):
    response = client.get(f'/api/v1/menus/{create_menu["id"]}/submenus')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['title'] == fixture_submenu['title']


def test_create_submenu(client, create_menu, fixture_submenu):
    response = client.post(f'/api/v1/menus/{create_menu["id"]}/submenus', json=fixture_submenu)
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == fixture_submenu['title']
    assert data['description'] == fixture_submenu['description']


def test_update_submenu(client, create_menu, create_submenu, fixture_submenu_update):
    response = client.patch(
        f'/api/v1/menus/{create_menu["id"]}/submenus/{create_submenu["id"]}', json=fixture_submenu_update)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == fixture_submenu_update['title']
    assert data['description'] == fixture_submenu_update['description']


def test_update_not_exist_submenu(client, create_menu, fixture_submenu_update):
    random_uuid = uuid.uuid4()
    response = client.patch(f'/api/v1/menus/{create_menu["id"]}/submenus/{random_uuid}', json=fixture_submenu_update)
    assert response.status_code == 404
    assert response.json() == {'detail': 'submenu not found'}


def test_delete_submenu(client, create_menu, create_submenu):
    response = client.delete(f'/api/v1/menus/{create_menu["id"]}/submenus/{create_submenu["id"]}')
    assert response.status_code == 200
    assert response.json() == {'message': 'submenu deleted'}


def test_delete_not_exist_submenu(client, create_menu):
    random_uuid = uuid.uuid4()
    response = client.delete(f'/api/v1/menus/{create_menu["id"]}/submenus/{random_uuid}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'submenu not found'}
