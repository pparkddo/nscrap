from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from sqlalchemy_repr import RepresentableBase

import config


URI = config.DATABASE_URI
ECHO = config.SQLALCHEMY_ECHO


Base = declarative_base(cls=RepresentableBase)

engine = create_engine(URI, echo=ECHO)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
