from dataclasses import dataclass

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy import func

from db import Base, Session


@dataclass
class Article(Base):

    __tablename__ = "article"

    id: int = Column("id", Integer, primary_key=True)
    title: str = Column("title", String(300), nullable=False)
    link: str = Column("link", String(300), nullable=False)
    content: str = Column("content", String(1000), nullable=True)
    timestamp: str = Column("timestamp", DateTime, nullable=False)

    @staticmethod
    def get_first_timestamp():
        return Session.query(func.min(Article.timestamp)).scalar()

    @staticmethod
    def get_all_articles():
        return Session.query(Article).all()

    def to_mesage_format(self):
        return f"{self.title}({self.link})"
