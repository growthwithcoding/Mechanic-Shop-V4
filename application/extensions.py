from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# Create a base class for our models
class Base(DeclarativeBase):
    pass

# Initialize extensions (without binding to app yet)
db = SQLAlchemy(model_class=Base)
ma = Marshmallow()

# Initialize Flask-Limiter with key function to identify clients
limiter = Limiter(key_func=get_remote_address)

# Initialize Flask-Caching with SimpleCache (in-memory)
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

# Initialize JWT Manager for token-based authentication
jwt = JWTManager()

# Initialize Flask-Migrate for database migrations
migrate = Migrate()
