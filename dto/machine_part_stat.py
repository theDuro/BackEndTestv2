from dataclasses import dataclass
from typing import Optional
from model.models import MachinePartStat

@dataclass
class MachinePartStatDTO:
    id: Optional[int]
    name: str
    counter: int
    is_empty: bool
    part_id: int

    @classmethod
    def from_orm(cls, orm_obj: MachinePartStat) -> "MachinePartStatDTO":
        return cls(
            id=orm_obj.id,
            name=orm_obj.name,
            counter=orm_obj.counter,
            is_empty=orm_obj.is_empty,
            part_id=orm_obj.part_id
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "counter": self.counter,
            "is_empty": self.is_empty,
            "part_id": self.part_id
        }

    def to_orm(self) -> MachinePartStat:
        return MachinePartStat(
            id=self.id,
            name=self.name,
            counter=self.counter,
            is_empty=self.is_empty,
            part_id=self.part_id
        )