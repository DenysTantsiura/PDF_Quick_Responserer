# from datetime import datetime
# import traceback

from fastapi import HTTPException, status
# import redis
# import redis.asyncio as aredis
# from redis.exceptions import AuthenticationError
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.conf.config import settings
from src.conf.messages import MSC500_DATABASE_CONFIG, MSC500_DATABASE_CONNECT


URI = settings.sqlalchemy_database_url


engine = create_engine(URI, echo=True)
DBSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = DBSession()
    try:
        yield db

    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    finally:
        db.close()
