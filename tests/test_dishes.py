import uuid


def test_read_dishes(client, create_menu, create_submenu, create_dish, fixture_dish):
    response = client.get(f'/api/v1/menus/{create_menu["id"]}/submenus/{create_submenu["id"]}/dishes')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['title'] == fixture_dish['title']


def test_create_dish(client, create_menu, create_submenu, fixture_dish):
    response = client.post(
        f'/api/v1/menus/{create_menu["id"]}/submenus/{create_submenu["id"]}/dishes', json=fixture_dish)
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == fixture_dish['title']
    assert data['description'] == fixture_dish['description']
    assert data['price'] == str(fixture_dish['price'])


def test_update_dish(client, create_menu, create_submenu, create_dish, fixture_dish_update):
    response = client.patch(
        f'/api/v1/menus/{create_menu["id"]}/submenus/{create_submenu["id"]}/dishes/{create_dish["id"]}', json=fixture_dish_update)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == fixture_dish_update['title']
    assert data['description'] == fixture_dish_update['description']
    assert data['price'] == str(fixture_dish_update['price'])


def test_update_not_exist_dish(client, create_menu, create_submenu, fixture_dish_update):
    random_uuid = uuid.uuid4()
    response = client.patch(
        f'/api/v1/menus/{create_menu["id"]}/submenus/{create_submenu["id"]}/dishes/{random_uuid}', json=fixture_dish_update)
    assert response.status_code == 404
    assert response.json() == {'detail': 'dish not found'}


def test_delete_dish(client, create_menu, create_submenu, create_dish):
    response = client.delete(
        f'/api/v1/menus/{create_menu["id"]}/submenus/{create_submenu["id"]}/dishes/{create_dish["id"]}')
    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'The dish has been deleted'}


def test_delete_not_exist_dish(client, create_menu, create_submenu):
    random_uuid = uuid.uuid4()
    response = client.delete(f'/api/v1/menus/{create_menu["id"]}/submenus/{create_submenu["id"]}/dishes/{random_uuid}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'dish not found'}
