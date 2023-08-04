from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get('/')
async def root():
    return {'message': 'Hello World'}
