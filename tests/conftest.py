"""Global pytest safety configuration.

This module is imported before test modules, so application settings and the
SQLAlchemy engine can never resolve to the operational development database.
"""
import os


os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///./data/prahari_pytest_isolated.db"
)
