from dataclasses import dataclass
from typing import Optional
from model.models import MachinePartError

@dataclass
class MachinePartErrorDTO:
    id: Optional[int]
    part_id: int
    error_code: str
    description: Optional[str]

    @classmethod
    def from_orm(cls, orm_obj: MachinePartError) -> "MachinePartErrorDTO":
        return cls(
            id=orm_obj.id,
            part_id=orm_obj.part_id,
            error_code=orm_obj.error_code,
            description=orm_obj.description
        )

    def to_dict(self):
        return {
            "id": self.id,
            "part_id": self.part_id,
            "error_code": self.error_code,
            "description": self.description
        }

    def to_orm(self) -> MachinePartError:
        return MachinePartError(
            id=self.id,
            part_id=self.part_id,
            error_code=self.error_code,
            description=self.description
        )