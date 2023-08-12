from app.tools import redis_client


async def invalidate_cache():
    """
    Функция для инвалидации (очистки) всего кэша в Redis.
    """
    await redis_client.clear_all()
    print('Cache invalidated!')


def recursive_dictify(obj) -> dict | list:
    if isinstance(obj, list):
        return [recursive_dictify(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        obj_dict = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):  # Исключаем служебные атрибуты
                obj_dict[key] = recursive_dictify(value)
        return obj_dict
    else:
        return obj
