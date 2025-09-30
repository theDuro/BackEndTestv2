from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from model.models import MachinePartErrorOccurrence

@dataclass
class MachinePartErrorOccurrenceDTO:
    id: Optional[int]
    error_id: int
    part_id: int
    occurred_at: datetime = field(default_factory=datetime.now)
    error_code: str = ""
    description: Optional[str] = None

    @classmethod
    def from_orm(cls, orm_obj: MachinePartErrorOccurrence) -> "MachinePartErrorOccurrenceDTO":
        return cls(
            id=orm_obj.id,
            error_id=orm_obj.error_id,
            part_id=orm_obj.part_id,
            occurred_at=orm_obj.occurred_at,
            error_code=orm_obj.error_code,
            description=orm_obj.description
        )

    def to_dict(self):
        return {
            "id": self.id,
            "error_id": self.error_id,
            "part_id": self.part_id,
            "occurred_at": self.occurred_at.isoformat(),
            "error_code": self.error_code,
            "description": self.description
        }

    def to_orm(self) -> MachinePartErrorOccurrence:
        return MachinePartErrorOccurrence(
            id=self.id,
            error_id=self.error_id,
            part_id=self.part_id,
            occurred_at=self.occurred_at,
            error_code=self.error_code,
            description=self.description
        )