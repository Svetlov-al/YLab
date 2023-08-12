import asyncio
import os
from datetime import timedelta

import httpx
import openpyxl
from celery import Celery

# Получаем текущую директорию скрипта
current_directory = os.path.dirname(__file__)

# Строим путь к файлу относительно текущей директории
file_path = os.path.join(current_directory, '..', 'admin', 'Menu.xlsx')

celery_app = Celery('ylab')

# Настройки брокера и другие
celery_app.conf.broker_url = 'amqp://guest:guest@rabbitmq:5672//'
celery_app.conf.result_backend = 'rpc://'
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.broker_connection_retry_on_startup = True

# Настройки Celery Beat
celery_app.conf.beat_schedule = {
    'database_synchronization': {
        'task': 'app.celery_task.database_synchronization',
        'schedule': timedelta(seconds=15),
    },
}


def read_excel(file_path):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active

    menus = []
    submenus = []
    dishes = []

    row = 1
    while row <= sheet.max_row:
        if sheet.cell(row=row, column=1).value and isinstance(sheet.cell(row=row, column=1).value, str):  # Новое меню
            menu = {
                'uuid': sheet.cell(row=row, column=1).value,
                'title': sheet.cell(row=row, column=2).value,
                'description': sheet.cell(row=row, column=3).value
            }
            menus.append(menu)
            row += 1

            while row <= sheet.max_row and not isinstance(sheet.cell(row=row, column=1).value, str):  # Подменю
                if sheet.cell(row=row, column=2).value and isinstance(sheet.cell(row=row, column=2).value, str):
                    submenu = {
                        'uuid': sheet.cell(row=row, column=2).value,
                        'title': sheet.cell(row=row, column=3).value,
                        'description': sheet.cell(row=row, column=4).value,
                        'menu_uuid': menu['uuid']
                    }
                    submenus.append(submenu)
                    row += 1

                    while row <= sheet.max_row and not isinstance(sheet.cell(row=row, column=1).value,
                                                                  str) and not isinstance(
                            sheet.cell(row=row, column=2).value, str):  # Блюдо
                        price_value = sheet.cell(row=row, column=6).value
                        if isinstance(price_value, str):
                            price_value = price_value.replace(',', '.')
                        dish = {
                            'uuid': sheet.cell(row=row, column=3).value,
                            'title': sheet.cell(row=row, column=4).value,
                            'description': sheet.cell(row=row, column=5).value,
                            'price': float(price_value or 0),
                            'submenu_uuid': submenu['uuid'],
                            'menu_uuid': menu['uuid']  # Добавляем информацию о меню
                        }
                        dishes.append(dish)
                        row += 1
                else:
                    row += 1
        else:
            row += 1

    return menus, submenus, dishes


@celery_app.task
def database_synchronization():
    # Используем созданный событийный цикл для выполнения асинхронной функции
    loop = asyncio.get_event_loop()
    menus_data, submenus_data, dishes_data = read_excel(file_path)
    loop.run_until_complete(async_database_operations(menus_data, submenus_data, dishes_data))


BASE_URL = 'http://api:8000/api/v1'


async def async_database_operations(menus_data, submenus_data, dishes_data):
    async with httpx.AsyncClient() as client:
        # Обработка меню
        for menu_data in menus_data:
            menu_id = menu_data['uuid']
            response = await client.get(f'{BASE_URL}/menus/{menu_id}')

            if response.status_code == 200:  # Если меню с таким UUID найдено
                # Удаляем uuid из данных, так как при обновлении мы передаем только title и description
                del menu_data['uuid']
                await client.patch(f'{BASE_URL}/menus/{menu_id}', json=menu_data)
            elif response.status_code == 404:  # Если меню с таким UUID не найдено
                # Переименовываем ключ "uuid" в "id" для создания нового меню
                menu_data['id'] = menu_data.pop('uuid')
                await client.post(f'{BASE_URL}/menus', json=menu_data)

        # Обработка подменю
        for submenu_data in submenus_data:
            submenu_uuid = submenu_data['uuid']
            menu_uuid = submenu_data['menu_uuid']
            response = await client.get(f'{BASE_URL}/menus/{menu_uuid}/submenus/{submenu_uuid}')

            if response.status_code == 200:  # Если подменю с таким UUID найдено
                del submenu_data['uuid']
                del submenu_data['menu_uuid']
                await client.patch(f'{BASE_URL}/menus/{menu_uuid}/submenus/{submenu_uuid}', json=submenu_data)
            elif response.status_code == 404:  # Если подменю с таким UUID не найдено
                submenu_data['id'] = submenu_data.pop('uuid')
                del submenu_data['menu_uuid']
                await client.post(f'{BASE_URL}/menus/{menu_uuid}/submenus', json=submenu_data)

        # Обработка блюд
        for dish_data in dishes_data:
            dish_uuid = dish_data['uuid']
            menu_uuid = dish_data['menu_uuid']
            submenu_uuid = dish_data['submenu_uuid']
            response = await client.get(f'{BASE_URL}/menus/{menu_uuid}/submenus/{submenu_uuid}/dishes/{dish_uuid}')

            if response.status_code == 200:  # Если блюдо с таким UUID найдено
                del dish_data['uuid']
                del dish_data['menu_uuid']
                del dish_data['submenu_uuid']
                await client.patch(f'{BASE_URL}/menus/{menu_uuid}/submenus/{submenu_uuid}/dishes/{dish_uuid}', json=dish_data)
            elif response.status_code == 404:  # Если блюдо с таким UUID не найдено
                dish_data['id'] = dish_data.pop('uuid')
                del dish_data['menu_uuid']
                del dish_data['submenu_uuid']
                await client.post(f'{BASE_URL}/menus/{menu_uuid}/submenus/{submenu_uuid}/dishes', json=dish_data)
