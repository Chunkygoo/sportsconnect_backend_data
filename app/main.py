import nest_asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_csrf_protect.exceptions import CsrfProtectError
from mangum import Mangum
from supertokens_python import (
    InputAppInfo,
    SupertokensConfig,
    get_all_cors_headers,
    init,
)
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe import (
    emailverification,
    session,
    thirdpartyemailpassword,
)
from supertokens_python.recipe.thirdpartyemailpassword import Google

from .admin.routers import universities as admin_universities
from .admin.routers import user as admin_user
from .config import settings
from .routers import auth, education, email, experience, universities, user

if settings.environment == "PROD":
    app = FastAPI(openapi_url=None, redoc_url=None)
    nest_asyncio.apply()  # lambda supertokens_python fix
    mode = "wsgi"
    recipe_list = [
        session.init(
            cookie_secure=settings.cookie_secure,
            cookie_same_site=settings.cookie_same_site,
        ),
    ]
else:
    app = FastAPI()
    mode = "asgi"
    recipe_list = [
        session.init(
            cookie_secure=settings.cookie_secure,
            cookie_domain=settings.cookie_domain,
            cookie_same_site=settings.cookie_same_site,
        ),
    ]

recipe_list += [
    emailverification.init(mode=settings.email_verification),
    thirdpartyemailpassword.init(
        providers=[
            Google(
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret,
            ),
        ],
    ),
]

init(
    app_info=InputAppInfo(
        app_name="SportsConnect",
        api_domain=settings.api_auth_url,
        website_domain=settings.app_url,
        api_base_path="/auth",
        website_base_path="/auth",
    ),
    #
    supertokens_config=SupertokensConfig(
        # connection_uri="http://localhost:3567", # Self-hosted core.
        connection_uri=settings.connection_uri,
        api_key=settings.api_key,
    ),
    framework="fastapi",
    recipe_list=recipe_list,
    mode=mode,
)


@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=403, content={"detail": exc.message}
    )  # use 403 and not exc.status_code because supertokens_python sends refresh request if status code is 401


app.add_middleware(get_middleware())


@app.get("/healthdata")
def check_health():
    return {"health": "healthy (data)"}


app.include_router(user.router)
app.include_router(auth.router)
app.include_router(email.router)
app.include_router(experience.router)
app.include_router(education.router)
app.include_router(universities.router)

# admin routes
app.include_router(admin_user.router)
app.include_router(admin_universities.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.origin_0, "*"],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Range"]
    + ["fdi-version", "rid", "anti-csrf"]
    + get_all_cors_headers(),
)

handler = Mangum(app)
