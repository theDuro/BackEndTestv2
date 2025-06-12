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

    