from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from dto.machine import MachineDTO
from dto.companydto import CompanyDTO
from typing import Optional

from dto.machine_data import MachineDataDTO
from model.models import Base, Company, Machine, MachineDataORM
DATABASE_URL = "postgresql://autosoft:Test1234%21@autosoft.postgres.database.azure.com:5432/postgres?sslmode=require"

engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)
SessionLocal = scoped_session(sessionmaker(bind=engine))
@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
def create_company(name: str) -> Company:
    with get_db_session() as session:
        company = Company(name=name)
        session.add(company)
        session.flush()  
        return company

def create_machine(company_id: int, name: str, config: dict = None) -> Machine:
    with get_db_session() as session:
        machine = Machine(company_id=company_id, name=name, config=config or {})
        session.add(machine)
        session.flush()
        return machine

def add_machine_data(machine_id: int, is_running: bool, has_error: bool,
                     cycle_completed: int, tag1=None, tag2=None, tag3=None, tag4=None) -> MachineDataORM:
    with get_db_session() as session:
        data = MachineDataORM(
            machine_id=machine_id,
            is_running=is_running,
            has_error=has_error,
            cycle_completed=cycle_completed,
            tag1=tag1,
            tag2=tag2,
            tag3=tag3,
            tag4=tag4
        )
        session.add(data)
        session.flush()
        return data

def get_company_with_machines(company_id: int) -> Company:
    with get_db_session() as session:
        return session.query(Company).filter(Company.id == company_id).first()

def get_company_with_login(login: str) -> Optional[CompanyDTO]:
    with get_db_session() as session:
        orm_object = session.query(Company).filter_by(login=login).first()
        if orm_object:
            return CompanyDTO.from_orm(orm_object)
        return None

def get_all_machine_data_dto():
    with get_db_session() as session:
        orm_objects = session.query(MachineDataORM).all()
        dtos = [MachineDataDTO.from_orm(obj) for obj in orm_objects]
        return dtos

def get_all_machine_data_dicts():
    with get_db_session() as session:
        orm_objects = session.query(MachineDataORM).all()
        dtos = [MachineDataDTO.from_orm(obj) for obj in orm_objects]
        dicts = [dto.__dict__ for dto in dtos]
        return dicts

def get_machine_data_dto_by_id(machine_id: int):
     with get_db_session() as session:
           results = session.query(MachineDataORM).filter_by(machine_id=machine_id).all()
           dtos = [MachineDataDTO.from_orm(obj) for obj in results]
           return dtos

def get_machines_dto_by_company_id(company_id: int):
    with get_db_session() as session:
        orm_objects = session.query(Machine).filter_by(company_id=company_id).all()
        dtos = [MachineDTO.from_orm(obj) for obj in orm_objects]
        return dtos

def get_machines():
    with get_db_session() as session:
        orm_objects = session.query(Machine).all()
        dtos = [MachineDTO.from_orm(obj) for obj in orm_objects]
        return dtos

def get_machine_data_by_id_and_time_range(machine_id: int, start_time, end_time):
    with get_db_session() as session:
        results = session.query(MachineDataORM)\
            .filter(MachineDataORM.machine_id == machine_id)\
            .filter(MachineDataORM.timestamp >= start_time)\
            .filter(MachineDataORM.timestamp <= end_time)\
            .all()

        dtos = [MachineDataDTO.from_orm(obj) for obj in results]
        return dtos

def get_all_machine_data_by_company_id_dto(company_id: int):
    with get_db_session() as session:
        results = (
            session.query(MachineDataORM)
            .join(Machine)
            .filter(Machine.company_id == company_id)
            .all()
        )
        return [MachineDataDTO.from_orm(obj) for obj in results]