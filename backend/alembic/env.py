import sys
import os
from logging.config import fileConfig
from alembic import context

# --- This is the key fix ---
# Add the parent directory of 'alembic' to the Python path
# This allows the script to find the 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# ---------------------------

from app.database import engine # Import your app's engine
from app.models import Base     # Import your models' Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Use your models' metadata ---
target_metadata = Base.metadata
# ---------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # This is the key change: we use the engine from our app
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
