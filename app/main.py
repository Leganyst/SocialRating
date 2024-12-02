# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from app.core.database import engine, Base
from app.models import achievement, bonus, collective, user
from app.routers.auth import router as auth_router
from app.routers.crud_endpoint_achievement import router as achievement_router_crud
from app.routers.crud_endpoint_collective import router as collective_router
from app.routers.crud_endpoint_bonus import router as bonus_router_сrud
from app.routers.crud_endpoint_user import router as user_router_crud
from app.routers.clicker import router as clicker
from app.routers.bonus import router as bonus_router
from app.routers.achievement import router as achievement_router
from app.routers.all_bonus import router as all_bonus_router
from app.routers.user import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan, swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"}, debug=True)

# origins = [
#     "https://*.vercel.app",
#     "https://*.wormhole.vk-apps.com",
#     "https://*.pages.vk-apps.com",
#     "https://*.pages-ac.vk-apps.com",
#     "https://pages-ac.vk-apps.com"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
#     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
# )

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html_github():
    return get_swagger_ui_html(
    openapi_url=app.openapi_url,
    title=f"{app.title} - Swagger UI",
    # swagger_ui_dark.css raw url
    swagger_css_url="https://raw.githubusercontent.com/Itz-fork/Fastapi-Swagger-UI-Dark/main/assets/swagger_ui_dark.min.css"
)


app.include_router(auth_router)
app.include_router(user_router_crud)
app.include_router(bonus_router_сrud)
app.include_router(collective_router)
app.include_router(achievement_router_crud)
app.include_router(clicker)
app.include_router(bonus_router)
app.include_router(achievement_router)
app.include_router(all_bonus_router)
app.include_router(user_router)