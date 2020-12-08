from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from sqlalchemy_repr import RepresentableBase

from settings import read_settings


SETTINGS = read_settings()


URI = "sqlite+pysqlite:///nscrap.db"
ECHO = SETTINGS["sqlalchemy_echo"]


Base = declarative_base(cls=RepresentableBase)

engine = create_engine(URI, echo=ECHO)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
