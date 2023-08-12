from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import sync_engine
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
