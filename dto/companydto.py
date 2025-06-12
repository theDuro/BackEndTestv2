from dataclasses import dataclass, field
from typing import List, Optional
from model.models import Company  # Zak³adam, ¿e to jest ORM z SQLAlchemy

@dataclass
class CompanyDTO:
    id: Optional[int]
    name: str
    login: str
    password: str  #

    @classmethod
    def from_orm(cls, orm_obj: Company) -> "CompanyDTO":
        return cls(
            id=orm_obj.id,
            name=orm_obj.name,
            login=orm_obj.login,
            password=orm_obj.password
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "login": self.login,
            "password": self.password,
        }

    def to_orm(self) -> Company:
        return Company(
            id=self.id,
            name=self.name,
            login=self.login,
            password=self.password
        )
