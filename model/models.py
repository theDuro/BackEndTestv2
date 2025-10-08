from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Boolean,
    DateTime, Float, JSON, func
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    login = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    machines = relationship("Machine", back_populates="company")


class Machine(Base):
    __tablename__ = 'machines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    name = Column(String, nullable=False)
    config = Column(JSONB, default=dict)

    company = relationship("Company", back_populates="machines")
    machine_data = relationship("MachineDataORM", back_populates="machine")
    errors = relationship("MachineError", back_populates="machine", cascade="all, delete-orphan")
    parts = relationship("MachinePart", back_populates="machine", cascade="all, delete-orphan")


class MachineDataORM(Base):
    __tablename__ = 'machine_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey('machines.id'), nullable=False)
    timestamp = Column(DateTime, default=func.now())
    is_running = Column(Boolean, nullable=False)
    has_error = Column(Boolean, nullable=False)
    cycle_completed = Column(Integer, nullable=False)
    tag1 = Column(Float)
    tag2 = Column(Float)
    tag3 = Column(Float)
    tag4 = Column(Float)

    machine = relationship("Machine", back_populates="machine_data")


class MachineError(Base):
    __tablename__ = 'errors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey('machines.id'), nullable=False)
    error_code = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=func.now())

    machine = relationship("Machine", back_populates="errors")


class MachinePart(Base):
    __tablename__ = 'machine_parts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey('machines.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    x = Column(Float, nullable=False, default=0.0)
    y = Column(Float, nullable=False, default=0.0)
    its_working = Column(Boolean, nullable=False, default=True)  # ✅ nowe pole logiczne

    # relacje
    machine = relationship("Machine", back_populates="parts")
    errors = relationship("MachinePartError", back_populates="part", cascade="all, delete-orphan")
    stats = relationship("MachinePartStat", back_populates="part", cascade="all, delete-orphan")  # ✅ relacja wiele–do–jednego

class MachinePartError(Base):
    __tablename__ = 'machine_part_errors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_id = Column(Integer, ForeignKey('machine_parts.id', ondelete='CASCADE'), nullable=False)
    error_code = Column(String(50))
    description = Column(String)
    part = relationship("MachinePart", back_populates="errors")
    occurrences = relationship("MachinePartErrorOccurrence", back_populates="error", cascade="all, delete-orphan")


class MachinePartErrorOccurrence(Base):
    __tablename__ = 'machine_part_error_occurrences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    error_id = Column(Integer, ForeignKey('machine_part_errors.id', ondelete='CASCADE'), nullable=False)
    part_id = Column(Integer, ForeignKey('machine_parts.id', ondelete='CASCADE'), nullable=False)
    occurred_at = Column(DateTime, default=func.now())
    error_code = Column(String, nullable=False)
    description = Column(String, nullable=True)
 
    error = relationship("MachinePartError", back_populates="occurrences")
    part = relationship("MachinePart")

class MachinePartStat(Base):
    __tablename__ = 'machine_part_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    counter = Column(Integer, nullable=False, default=0)
    is_empty = Column(Boolean, nullable=False, default=False)
    part_id = Column(Integer, ForeignKey('machine_parts.id', ondelete='CASCADE'), nullable=False)

    part = relationship("MachinePart", back_populates="stats")