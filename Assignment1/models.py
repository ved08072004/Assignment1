from pydantic import BaseModel
from typing import Optional, List

class User(BaseModel):
    name: str
    age: int
    role: Optional[str] = "AI Engineer"
    percentage: str
    cgpa: float
    skills: List[str] = []
    is_active: bool = True
