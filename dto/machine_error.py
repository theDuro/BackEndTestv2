from typing import Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ErrorDTO:
    id: int
    machine_id: int
    error_code: str
    description: Optional[str]
    created_at: datetime

    @classmethod
    def from_orm(cls, orm_obj) -> "ErrorDTO":
        return cls(
            id=orm_obj.id,
            machine_id=orm_obj.machine_id,
            error_code=orm_obj.error_code,
            description=orm_obj.description,
            created_at=orm_obj.created_at
        )

    def to_dict(self):
        return {
            "id": self.id,
            "machine_id": self.machine_id,
            "error_code": self.error_code,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }