import os
from fastapi.openapi.utils import get_openapi
from .main import app
import yaml


with open(os.path.join(os.path.dirname(__file__), "..", "schema.yml"), "w+") as f:
    yaml.dump(
        get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        ),
        f,
    )
