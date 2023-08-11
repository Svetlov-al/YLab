from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import get_db, sync_engine
from app.database_repository import DishRepository, MenuRepository, SubmenuRepository
from app.menu_service import MenuService
from app.routers import dishes, menus, submenus
from app.tools import redis_client

models.Base.metadata.create_all(bind=sync_engine)


app = FastAPI(
    title='YLab_University'
)


app.include_router(menus.router)
app.include_router(submenus.router)
app.include_router(dishes.router)

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def startup_event():
    await redis_client.setup()


@app.get('/')
async def root(db: AsyncSession = Depends(get_db)):
    menu_repo = MenuRepository(db)
    submenu_repo = SubmenuRepository(db)
    dish_repo = DishRepository(db)

    menu_service = MenuService(menu_repo, submenu_repo, dish_repo)
    return await menu_service.get_full_menus()
