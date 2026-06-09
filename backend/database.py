# ==================================
# SQLAlchemy Imports
# create_engine -> Creates DB connection
# sessionmaker -> Creates DB sessions
# declarative_base -> Base class for models
# ==================================

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)


# ==================================
# DATABASE CONFIGURATION
#
# Reads DATABASE_URL from environment.
# Defaults to local SQLite for development.
#
# For production (e.g. Render), set:
#   DATABASE_URL=postgresql://user:pass@host/db
# ==================================

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./coding_contest.db"
)

# Render provides postgres:// but SQLAlchemy
# requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )


# ==================================
# CREATE DATABASE ENGINE
#
# check_same_thread is only needed
# for SQLite connections
# ==================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine_kwargs = {
    "connect_args": connect_args,
}

# Detect stale connections on cloud PostgreSQL
if not DATABASE_URL.startswith("sqlite"):
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs
)


# ==================================
# CREATE DATABASE SESSION FACTORY
#
# autocommit=False:
# Changes save only after commit()
#
# autoflush=False:
# Avoids automatic updates before commit
#
# bind=engine:
# Connect session to database engine
# ==================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==================================
# BASE CLASS FOR MODELS
#
# Every SQLAlchemy model inherits
# from this Base class
#
# Example:
#
# class User(Base):
#     __tablename__="users"
# ==================================

Base = declarative_base()


# ==================================
# DATABASE DEPENDENCY
#
# Creates DB session for request
# Opens session at start
# Closes session automatically
#
# Used in FastAPI:
#
# db: Session = Depends(get_db)
# ==================================

def get_db():

    db = SessionLocal()

    try:

        # Give database session
        yield db

    finally:

        # Close session after use
        db.close()