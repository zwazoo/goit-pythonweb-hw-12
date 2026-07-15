import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("../.."))

load_dotenv(os.path.abspath("../../.env"))

project = "Contacts API"
copyright = "2026, Liudmyla"
author = "Liudmyla"
release = "1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False

autodoc_mock_imports = [
    "fastapi",
    "starlette",
    "sqlalchemy",
    "alembic",
    "redis",
    "cloudinary",
    "asyncpg",
    "fastapi_mail",
    "libgravatar",
    "pwdlib",
    "slowapi",
    "jose",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
