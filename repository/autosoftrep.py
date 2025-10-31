from sqlalchemy import create_engine,func
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List

from model.models import (
    Base, Company, Machine, MachineDataORM,
    MachinePartStat, MachinePartErrorOccurrence,
    MachinePart, MachinePartError, MachineError
)

from dto.machine import MachineDTO
from dto.companydto import CompanyDTO
from dto.machine_data import MachineDataDTO
from dto.machine_part_stat import MachinePartStatDTO
from dto.machine_error import ErrorDTO
from dto.machine_part import MachinePartDTO
from dto.machine_part_error_occurrence import MachinePartErrorOccurrenceDTO
from dto.machine_part_error import MachinePartErrorDTO


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
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class AutoSoftRepository:

    # ------------------ COMPANY / MACHINE ------------------
    def create_company(self, name: str) -> Company:
        with get_db_session() as session:
            company = Company(name=name)
            session.add(company)
            session.flush()
            return company

    def create_machine(self, company_id: int, name: str, config: dict = None) -> Machine:
        with get_db_session() as session:
            machine = Machine(company_id=company_id, name=name, config=config or {})
            session.add(machine)
            session.flush()
            return machine

    def get_company_with_login(self, login: str) -> Optional[CompanyDTO]:
        with get_db_session() as session:
            orm_object = session.query(Company).filter_by(login=login).first()
            if orm_object:
                return CompanyDTO.from_orm(orm_object)
            return None

    # ------------------ MACHINE DATA ------------------
    def add_machine_data(self, machine_id: int, is_running: bool, has_error: bool,
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

    def get_all_machine_data_dto(self):
        with get_db_session() as session:
            orm_objects = session.query(MachineDataORM).all()
            return [MachineDataDTO.from_orm(obj) for obj in orm_objects]

    def get_machine_data_dto_by_id(self, machine_id: int):
        with get_db_session() as session:
            results = session.query(MachineDataORM).filter_by(machine_id=machine_id).all()
            return [MachineDataDTO.from_orm(obj) for obj in results]

    def get_machine_data_by_id_and_time_range(self, machine_id: int, start_time, end_time):
        with get_db_session() as session:
            results = (
                session.query(MachineDataORM)
                .filter(MachineDataORM.machine_id == machine_id)
                .filter(MachineDataORM.timestamp >= start_time)
                .filter(MachineDataORM.timestamp <= end_time)
                .all()
            )
            return [MachineDataDTO.from_orm(obj) for obj in results]

    def get_all_machine_data_by_company_id_dto(self, company_id: int):
        with get_db_session() as session:
            results = (
                session.query(MachineDataORM)
                .join(Machine)
                .filter(Machine.company_id == company_id)
                .all()
            )
            return [MachineDataDTO.from_orm(obj) for obj in results]

    # ------------------ MACHINE ------------------
    def get_machines(self):
        with get_db_session() as session:
            orm_objects = session.query(Machine).all()
            return [MachineDTO.from_orm(obj) for obj in orm_objects]

    def get_machines_dto_by_company_id(self, company_id: int):
        with get_db_session() as session:
            orm_objects = session.query(Machine).filter_by(company_id=company_id).all()
            return [MachineDTO.from_orm(obj) for obj in orm_objects]

    def get_machine_config(self, machine_id: int) -> dict:
        with get_db_session() as session:
            machine = session.query(Machine).get(machine_id)
            if not machine:
                raise ValueError(f"Machine with id {machine_id} not found")
            return machine.config or {}

    def update_machine_config(self, machine_id: int, new_config: dict) -> None:
        with get_db_session() as session:
            machine = session.query(Machine).get(machine_id)
            if not machine:
                raise ValueError(f"Machine with id {machine_id} not found")
            machine.config = new_config
            session.commit()

    # ------------------ ERRORS ------------------
    def get_all_errors_by_company_id(self, company_id: int):
        with get_db_session() as session:
            results = (
                session.query(MachineError)
                .join(Machine)
                .filter(Machine.company_id == company_id)
                .all()
            )
            return [ErrorDTO.from_orm(obj) for obj in results]

    def get_error_by_machine_id(self, machine_id: int):
        with get_db_session() as session:
            results = session.query(MachineError).filter(MachineError.machine_id == machine_id).all()
            return [ErrorDTO.from_orm(obj) for obj in results]

    # ------------------ MACHINE PARTS ------------------
    def get_machine_parts_by_machine_id(self, machine_id: int):
        with get_db_session() as session:
            results = session.query(MachinePart).filter_by(machine_id=machine_id).all()
            return [MachinePartDTO.from_orm(obj) for obj in results]

    def get_errors_for_part(self, part_id: int):
        with get_db_session() as session:
            results = session.query(MachinePartError).filter_by(part_id=part_id).all()
            return [MachinePartErrorDTO.from_orm(obj) for obj in results]

    def get_occurrences_by_machine_id(self, machine_id: int):
        with get_db_session() as session:
            results = (
                session.query(MachinePartErrorOccurrence)
                .join(MachinePart, MachinePart.id == MachinePartErrorOccurrence.part_id)
                .filter(MachinePart.machine_id == machine_id)
                .all()
            )
            return [MachinePartErrorOccurrenceDTO.from_orm(obj) for obj in results]

    def get_all_occurrences(self):
        with get_db_session() as session:
            results = session.query(MachinePartErrorOccurrence).all()
            return [MachinePartErrorOccurrenceDTO.from_orm(obj) for obj in results]

    def get_occurrences_by_part_id_and_date(self, part_id: int, date_from: datetime):
        with get_db_session() as session:
            results = (
                session.query(MachinePartErrorOccurrence)
                .filter(MachinePartErrorOccurrence.part_id == part_id)
                .filter(MachinePartErrorOccurrence.occurred_at >= date_from)
                .all()
            )
            return [MachinePartErrorOccurrenceDTO.from_orm(obj) for obj in results]

    def get_error_ids_for_part_in_date_range(self, part_id: int, date_from: datetime):
        with get_db_session() as session:
            results = (
                session.query(MachinePartErrorOccurrence.error_id)
                .filter(MachinePartErrorOccurrence.part_id == part_id)
                .filter(MachinePartErrorOccurrence.occurred_at >= date_from)
                .all()
            )
            return [row[0] for row in results]

   

    def get_stats_for_machine(self, machine_id: int):
        with get_db_session() as session:
            results = (
                session.query(MachinePartStat)
                .join(MachinePart)
                .filter(MachinePart.machine_id == machine_id)
                .all()
            )
            return [MachinePartStatDTO.from_orm(obj) for obj in results]
        
    def get_error_code_for_part_in_date_range(self, part_id: int, date_from: datetime):

        with get_db_session() as session:
            results = (
                session.query(MachinePartErrorOccurrence.error_code)
                .filter(MachinePartErrorOccurrence.part_id == part_id)
                .filter(MachinePartErrorOccurrence.occurred_at >= date_from)
                .distinct()
                .all()
            )
            return [row[0] for row in results]   

    def get_last_errors(self, machine_id: int):
        with get_db_session() as session:
            results = (
                session.query(MachinePartErrorOccurrence)
                .join(MachinePart)
                .filter(MachinePart.machine_id == machine_id)
                .order_by(MachinePartErrorOccurrence.id.desc())
                .limit(10)
                .all()
            )
            return [MachinePartErrorOccurrenceDTO.from_orm(obj) for obj in results]
        
    def get_error_code_for_machine_in_date_range(self,  machine_id: int, date_from: datetime):
        
        with get_db_session() as session:
            results = (
                session.query(MachinePartErrorOccurrence.error_code)
                .join(MachinePart)
                .filter(MachinePart.machine_id == machine_id)
                .filter(MachinePartErrorOccurrence.occurred_at >= date_from)
                .distinct()
                .all()
            )
            return [row[0] for row in results]   
        

        