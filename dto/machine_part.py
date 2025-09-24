from dataclasses import dataclass
from typing import Optional
from model.models import MachinePart

@dataclass
class MachinePartDTO:
    id: Optional[int]
    machine_id: int
    name: str
    x: float
    y: float

    @classmethod
    def from_orm(cls, orm_obj: MachinePart) -> "MachinePartDTO":
        return cls(
            id=orm_obj.id,
            machine_id=orm_obj.machine_id,
            name=orm_obj.name,
            x=orm_obj.x,
            y=orm_obj.y
        )

    def to_dict(self):
        return {
            "id": self.id,
            "machine_id": self.machine_id,
            "name": self.name,
            "x": self.x,
            "y": self.y
        }

    def to_orm(self) -> MachinePart:
        return MachinePart(
            id=self.id,
            machine_id=self.machine_id,
            name=self.name,
            x=self.x,
            y=self.y
        )