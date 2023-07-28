## YLab Project

Это пример приложения меню, написанного на Python и развернутого в Docker.

### Возможности
CRUD операции для меню, подменю и блюд
Вложенная структура меню, которая позволяет иметь подменю, а подменю иметь блюда.
Детали меню и подменю включают количество связанных подменю и блюд.
REST API со всеми endpoint для CRUD операций.
Документация Swagger/OpenAPI.
Docker контейнер для простого развертывания.
Конечные точки API.

## API имеет следующие конечные точки:

### Меню

`GET /menus` - получить список всех меню
`GET /menus/{id}` - получить конкретное меню
`POST /menus` - создать новое меню
`PATCH /menus/{id}` - обновить существующее меню
`DELETE /menus/{id}` - удалить меню

### Подменю

`GET /menus/{menu_id}/submenus` - получить список всех подменю для меню
`GET /menus/{menu_id}/submenus/{id}` - получить конкретное подменю
`POST /menus/{menu_id}/submenus` - создать новое подменю для меню
`PATCH /menus/{menu_id}/submenus/{id}` - обновить существующее подменю
`DELETE /menus/{menu_id}/submenus/{id}` - удалить подменю

## Блюда

`GET /menus/{menu_id}/submenus/{submenu_id}/dishes` - получить список всех блюд для подменю
`GET /menus/{menu_id}/submenus/{submenu_id}/dishes/{id}` - получить конкретное блюдо
`POST /menus/{menu_id}/submenus/{submenu_id}/dishes` - создать новое блюдо для подменю
`PATCH /menus/{menu_id}/submenus/{submenu_id}/dishes/{id}` - обновить существующее блюдо
`DELETE /menus/{menu_id}/submenus/{submenu_id}/dishes/{id}` - удалить блюдо

### Запуск приложения
Приложение запускается в Docker контейнере для простого развертывания.

### Для сборки:
Убедитесь, что у вас установлены Docker и Docker Compose. Вы можете установить Docker Desktop, который включает в себя Docker Compose, с официального сайта Docker.

Откройте терминал (или командную строку в Windows) и перейдите в каталог, где находится файл `docker-compose.yml`

### Для запуска: Введите следующую команду:

`docker-compose up -d`

### Для остановки:

`docker-compose down`

### Для запуска тестов в контейнере создан отдельный docker-compose-test.yml файл.
Запустить тесты можно командой:
`docker-compose -f docker-compose-tests.yml run api-tests`

Для остановки тестового контейнера:
`docker-compose -f docker-compose-tests.yml down`


### API будет доступен по адресу http://localhost:8000

### Документация OpenAPI/Swagger доступна по адресу http://localhost:8000/docs
