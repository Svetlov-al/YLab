import uuid


def test_menu_has_correct_number_of_submenus_and_dishes(client, create_menu, create_submenu, create_dish):
    response = client.get(f'/api/v1/menus/{create_menu["id"]}')
    assert response.status_code == 200
    data = response.json()

    assert data['submenus_count'] == 1
    assert data['dishes_count'] == 1


def test_read_menus(client, fixture_menu):
    response = client.get('/api/v1/menus')
    assert response.status_code == 200
    assert response.json() == []
    client.post('/api/v1/menus', json=fixture_menu)
    response = client.get('/api/v1/menus')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['title'] == fixture_menu['title']


def test_read_menu(client, fixture_menu):
    response = client.post('/api/v1/menus', json=fixture_menu)
    response = client.get(f'/api/v1/menus/{response.json()["id"]}')
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == fixture_menu['title']
    assert data['description'] == fixture_menu['description']


def test_read_not_exist_menu(client):
    random_uuid = uuid.uuid4()
    response = client.get(f'/api/v1/menus/{random_uuid}')
    assert response.status_code == 404


def test_create_menu(client, fixture_menu):
    response = client.post('/api/v1/menus', json=fixture_menu)
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == fixture_menu['title']
    assert data['description'] == fixture_menu['description']


def test_update_menu(client, fixture_menu_update, fixture_menu):
    to_update_response = client.post('/api/v1/menus', json=fixture_menu)
    to_update_data = to_update_response.json()
    response = client.patch(f'/api/v1/menus/{to_update_data["id"]}', json=fixture_menu_update)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == fixture_menu_update['title']
    assert data['description'] == fixture_menu_update['description']


def test_update_not_exist_menu(client, fixture_menu_update):
    random_uuid = uuid.uuid4()
    response = client.patch(f'/api/v1/menus/{random_uuid}', json=fixture_menu_update)
    assert response.status_code == 404
    assert response.json() == {'detail': 'menu not found'}


def test_delete_menu(client, fixture_menu):
    # Создание меню
    create_response = client.post('/api/v1/menus', json=fixture_menu)
    assert create_response.status_code == 201  # или другой ожидаемый статус кода
    menu_data = create_response.json()
    menu_id = menu_data['id']

    # Удаление меню
    response = client.delete(f'/api/v1/menus/{menu_id}')
    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'Menu deleted'}
