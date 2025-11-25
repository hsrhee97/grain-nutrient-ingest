"""SQLAlchemy ORM 모델 정의."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class NutrientType(str, enum.Enum):
    """영양소 타입 열거형."""

    GOOD = "good"
    BAD = "bad"


class SurveyOption(Base):
    """설문 옵션 테이블."""

    __tablename__ = "survey_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String(100), nullable=False)
    question_label = Column(String(200), nullable=False)
    option_id = Column(String(100), unique=True, nullable=False, index=True)
    option_label = Column(String(200), nullable=False)

    # 관계
    papers = relationship("Paper", back_populates="option", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SurveyOption(option_id='{self.option_id}', option_label='{self.option_label}')>"


class Paper(Base):
    """논문 테이블."""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    option_id = Column(String(100), ForeignKey("survey_options.option_id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=True)
    source = Column(String(100), nullable=False)  # "semantic_scholar", "crossref", "manual"
    doi = Column(String(200), nullable=True, unique=True, index=True)
    abstract = Column(Text, nullable=True)
    raw_metadata = Column(JSON, nullable=True)

    # 관계
    option = relationship("SurveyOption", back_populates="papers")
    nutrients = relationship("Nutrient", back_populates="paper", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Paper(id={self.id}, title='{self.title[:50]}...')>"


class Nutrient(Base):
    """영양소 테이블."""

    __tablename__ = "nutrients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(20), nullable=False)  # "good" or "bad"
    extra_info = Column(JSON, nullable=True)

    # 관계
    paper = relationship("Paper", back_populates="nutrients")

    def __repr__(self) -> str:
        return f"<Nutrient(id={self.id}, name='{self.name}', type='{self.type}')>"

