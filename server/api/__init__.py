from flask import Blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

from server.api.routes import register_routes 