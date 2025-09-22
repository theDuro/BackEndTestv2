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

    @classmethod
    def from_orm(cls, orm_obj: MachinePartErrorOccurrence) -> "MachinePartErrorOccurrenceDTO":
        return cls(
            id=orm_obj.id,
            error_id=orm_obj.error_id,
            part_id=orm_obj.part_id,
            occurred_at=orm_obj.occurred_at
        )

    def to_dict(self):
        return {
            "id": self.id,
            "error_id": self.error_id,
            "part_id": self.part_id,
            "occurred_at": self.occurred_at.isoformat()
        }

    def to_orm(self) -> MachinePartErrorOccurrence:
        return MachinePartErrorOccurrence(
            id=self.id,
            error_id=self.error_id,
            part_id=self.part_id,
            occurred_at=self.occurred_at
        )