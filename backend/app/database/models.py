import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import relationship

from app.database.connection import Base

class Research(Base):

    __tablename__ = "researches"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    topic = Column(
        String,
        nullable=False
    )

    objective = Column(
        Text,
        nullable=True
    )

    status = Column(
        String,
        default="initialized"
    )

    revision_count = Column(
        Integer,
        default=0
    )

    max_revisions = Column(
        Integer,
        default=2
    )

    errors = Column(
        JSON,
        default=list
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    sources = relationship(
        "Source",
        back_populates="research",
        cascade="all, delete-orphan"
    )

    evidence = relationship(
        "Evidence",
        back_populates="research",
        cascade="all, delete-orphan"
    )

    reports = relationship(
        "Report",
        back_populates="research",
        cascade="all, delete-orphan"
    )

    revisions = relationship(
        "Revision",
        back_populates="research",
        cascade="all, delete-orphan"
    )


class Source(Base):

    __tablename__ = "sources"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    research_id = Column(
        String,
        ForeignKey("researches.id"),
        nullable=False
    )

    title = Column(
        Text,
        nullable=True
    )

    url = Column(
        Text,
        nullable=False
    )

    source_type = Column(
        String,
        nullable=True
    )

    score = Column(
        Float,
        nullable=True
    )

    metadata_json = Column(
        JSON,
        default=dict
    )

    research = relationship(
        "Research",
        back_populates="sources"
    )


class Evidence(Base):

    __tablename__ = "evidence"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    research_id = Column(
        String,
        ForeignKey("researches.id"),
        nullable=False
    )

    claim = Column(
        Text,
        nullable=False
    )

    supporting_text = Column(
        Text,
        nullable=False
    )

    source_url = Column(
        Text,
        nullable=True
    )

    evidence_type = Column(
        String,
        nullable=True
    )

    confidence = Column(
        Float,
        nullable=True
    )

    limitations = Column(
        JSON,
        default=list
    )

    research = relationship(
        "Research",
        back_populates="evidence"
    )


class Report(Base):

    __tablename__ = "reports"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    research_id = Column(
        String,
        ForeignKey("researches.id"),
        nullable=False
    )

    title = Column(
        Text,
        nullable=False
    )

    report_data = Column(
        JSON,
        nullable=False
    )

    revision_count = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    research = relationship(
        "Research",
        back_populates="reports"
    )


class Revision(Base):

    __tablename__ = "revisions"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    research_id = Column(
        String,
        ForeignKey("researches.id"),
        nullable=False
    )

    revision_number = Column(
        Integer,
        nullable=False
    )

    score = Column(
        Float,
        nullable=True
    )

    passed = Column(
        Boolean,
        default=False
    )

    critic_data = Column(
        JSON,
        nullable=True
    )

    changes = Column(
        JSON,
        default=list
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    research = relationship(
        "Research",
        back_populates="revisions"
    )