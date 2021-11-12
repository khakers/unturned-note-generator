from dataclasses import field
from marshmallow_dataclass import dataclass
from marshmallow import Schema
from typing import ClassVar, Type



from typing import List, Optional

@dataclass
class Language:
    language: str
    text: List[str] = field(default_factory=list)

@dataclass
class Note:
    name: str
    id: Optional[int]
    guid: Optional[str]
    text: List[Language] = field(default_factory=list)

@dataclass
class Map:
    name: Optional[str]
    notes: List[Note]
    Schema: ClassVar[Type[Schema]] = Schema




