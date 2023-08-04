def test_read_dishes(client, db_session, test_menu, test_submenu, test_dish):
    db_session.add(test_menu)
    db_session.add(test_submenu)
    db_session.commit()
    response = client.get(f'/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}/dishes')
    assert response.status_code == 200
    assert response.json() == []


def test_create_dish(client, db_session, test_menu, test_submenu):
    db_session.add(test_menu)
    db_session.add(test_submenu)
    db_session.commit()
    dish_data = {'title': 'New Dish', 'description': 'New Description', 'price': '10.00'}
    response = client.post(f'/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}/dishes', json=dish_data)
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == dish_data['title']
    assert data['description'] == dish_data['description']
    assert data['price'] == dish_data['price']


def test_update_dish(client, db_session, setup_dish):
    test_menu, test_submenu, test_dish = setup_dish
    updated_data = {'title': 'Updated Dish', 'description': 'Updated Description', 'price': '20.00'}
    response = client.patch(f'/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}/dishes/{test_dish.id}',
                            json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == updated_data['title']
    assert data['description'] == updated_data['description']
    assert data['price'] == updated_data['price']


def test_update_not_exist_dish(client, db_session, test_menu, test_submenu):
    db_session.add(test_menu)
    db_session.add(test_submenu)
    db_session.commit()
    updated_data = {'title': 'Updated Dish', 'description': 'Updated Description', 'price': '20.00'}
    response = client.patch(f'/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}/dishes/80000',
                            json=updated_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'dish not found'}


def test_delete_dish(client, db_session, setup_dish):
    test_menu, test_submenu, test_dish = setup_dish

    response = client.delete(f'/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}/dishes/{test_dish.id}')
    assert response.status_code == 200
    assert response.json() == {'detail': 'Dish deleted'}


def test_delete_not_exist_dish(client, db_session, test_menu, test_submenu):
    db_session.add(test_menu)
    db_session.add(test_submenu)
    db_session.commit()
    response = client.delete(f'/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}/dishes/80000000')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Dish not found'}
