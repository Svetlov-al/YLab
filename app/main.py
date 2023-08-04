import aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.routers import dishes, menus, submenus

from . import models
from .database import engine

models.Base.metadata.create_all(bind=engine)

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
    redis = aioredis.from_url('redis://redis', decode_respones=True)
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-chache')


@app.get('/')
async def root():
    return {'message': 'Hello World'}
