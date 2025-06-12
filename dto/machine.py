from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class MachineDTO:
    id: int
    company_id: int
    name: str
    config: Dict

    @classmethod
    def from_orm(cls, orm_obj) -> "MachineDTO":
        return cls(
            id=orm_obj.id,
            company_id=orm_obj.company_id,
            name=orm_obj.name,
            config=orm_obj.config or {}
        )

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "name": self.name,
            "config": self.config
        }
