import uuid


def test_read_submenus(client, db_session, test_menu, test_submenu):
    db_session.add(test_menu)
    db_session.commit()
    response = client.get(f'/api/v1/menus/{test_menu.id}/submenus')
    assert response.status_code == 200
    assert response.json() == []


def test_create_submenu(client, db_session, test_menu):
    db_session.add(test_menu)
    db_session.commit()
    submenu_data = {'title': 'New Submenu', 'description': 'New Description'}
    response = client.post(f'/api/v1/menus/{test_menu.id}/submenus', json=submenu_data)
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == submenu_data['title']
    assert data['description'] == submenu_data['description']


def test_update_submenu(client, db_session, test_create_submenu):
    test_menu, test_submenu = test_create_submenu
    updated_data = {'title': 'Updated Submenu', 'description': 'Updated Description'}
    response = client.patch(f'/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}', json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == updated_data['title']
    assert data['description'] == updated_data['description']


def test_update_not_exist_submenu(client, db_session, test_menu):
    db_session.add(test_menu)
    db_session.commit()
    random_uuid = uuid.uuid4()
    updated_data = {'title': 'Updated Submenu', 'description': 'Updated Description'}
    response = client.patch(f'/api/v1/menus/{test_menu.id}/submenus/{random_uuid}', json=updated_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'submenu not found'}


def test_delete_submenu(client, db_session, test_create_submenu):
    test_menu, test_submenu = test_create_submenu
    response = client.delete(f'/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}')
    assert response.status_code == 200
    assert response.json() == {'message': 'submenu deleted'}


def test_delete_not_exist_submenu(client, db_session, test_menu, test_submenu):
    db_session.add(test_menu)
    db_session.commit()
    random_uuid = uuid.uuid4()
    response = client.delete(f'/api/v1/menus/{test_menu.id}/submenus/{random_uuid}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'submenu not found'}
