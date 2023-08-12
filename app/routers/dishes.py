import json
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.config import settings
from app.database import get_db
from app.database_repository import DishRepository, MenuRepository, SubmenuRepository
from app.dish_service import DishService
from app.tools import redis_client

router = APIRouter(
    prefix='/api/v1',
    tags=['Dishes']
)

cache_expire_time = settings.cache_expire


@router.get('/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=list[schemas.Dish])
async def read_dishes(menu_id: UUID, submenu_id: UUID, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    cache_key = f'Dishes_{submenu_id}'

    cached_dishes = await redis_client.get_key(cache_key)
    if cached_dishes:
        return json.loads(cached_dishes)

    dish_service = DishService(DishRepository(db), SubmenuRepository(db), MenuRepository(db))
    dishes = await dish_service.read_dishes(submenu_id, skip, limit)

    # Преобразуем каждый объект Dish в экземпляр Pydantic модели
    pydantic_dishes = [schemas.Dish(**dish.__dict__) for dish in dishes]

    # Сериализуем каждое блюдо в строку JSON и добавим в кеш
    serialized_dishes = json.dumps([{
        'id': str(dish.id),
        'menu_id': str(menu_id),
        'submenu_id': str(submenu_id),
        'price': str(dish.price),
        **dish.model_dump(exclude={'id', 'price'})
    } for dish in pydantic_dishes])
    await redis_client.set_key(cache_key, serialized_dishes, expire_time=cache_expire_time)

    return dishes


@router.get('/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=schemas.Dish)
async def read_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: AsyncSession = Depends(get_db)):

    cache_key = f'Dish_{submenu_id}'
    # Попробуем получить подменю из кеша
    cached_dish = await redis_client.get_key(cache_key)
    if cached_dish:
        return json.loads(cached_dish)

    dish_service = DishService(DishRepository(db), SubmenuRepository(db), MenuRepository(db))
    dish = await dish_service.read_dish(menu_id, submenu_id, dish_id)

    # Сериализуем подменю в строку JSON и добавим в кеш
    serialized_dish = json.dumps(
        {
            'id': str(dish.id),
            'menu_id': str(menu_id),
            'submenu_id': str(submenu_id),
            'price': str(dish.price),
            **dish.dict(exclude={'id', 'price'})
        })
    print(serialized_dish)
    await redis_client.set_key(cache_key, serialized_dish, expire_time=cache_expire_time)

    return dish


@router.post('/menus/{menu_id}/submenus/{submenu_id}/dishes', status_code=status.HTTP_201_CREATED,
             response_model=schemas.DishOut)
async def create_dish(menu_id: UUID, submenu_id: UUID, dish: schemas.DishCreate, db: AsyncSession = Depends(get_db)):
    dish_service = DishService(DishRepository(db), SubmenuRepository(db), MenuRepository(db))

    # Удаление кеша связанного с этим меню
    await redis_client.delete_key('menus')
    await redis_client.delete_key(f'MenuData_{menu_id}')
    await redis_client.delete_key(f'Submenus_{menu_id}')
    await redis_client.delete_key(f'Submenu_{menu_id}')
    await redis_client.delete_key(f'Dishes_{submenu_id}')
    await redis_client.delete_key(f'Dish_{submenu_id}')

    dish = await dish_service.create_dish(menu_id, submenu_id, dish)
    return dish


@router.patch('/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=schemas.DishOut)
async def update_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: schemas.DishBase,
                      db: AsyncSession = Depends(get_db)):
    dish_service = DishService(DishRepository(db), SubmenuRepository(db), MenuRepository(db))

    # Удаление кеша связанного с этим меню
    await redis_client.delete_key('menus')
    await redis_client.delete_key(f'MenuData_{menu_id}')
    await redis_client.delete_key(f'Submenus_{menu_id}')
    await redis_client.delete_key(f'Submenu_{menu_id}')
    await redis_client.delete_key(f'Dishes_{submenu_id}')
    await redis_client.delete_key(f'Dish_{submenu_id}')

    dish = await dish_service.update_dish(menu_id, submenu_id, dish_id, dish)
    return dish


@router.delete('/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: AsyncSession = Depends(get_db)):
    dish_service = DishService(DishRepository(db), SubmenuRepository(db), MenuRepository(db))

    # Удаление кеша связанного с этим меню
    await redis_client.delete_key('menus')
    await redis_client.delete_key(f'MenuData_{menu_id}')
    await redis_client.delete_key(f'Submenus_{menu_id}')
    await redis_client.delete_key(f'Submenu_{menu_id}')
    await redis_client.delete_key(f'Dishes_{submenu_id}')
    await redis_client.delete_key(f'Dish_{submenu_id}')

    dish = await dish_service.delete_dish(menu_id, submenu_id, dish_id)
    return dish
