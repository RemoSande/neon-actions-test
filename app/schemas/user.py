from pydantic import BaseModel, Field
from typing import Optional, Dict
 
class User(BaseModel):
    """Our Pokemon trainers (users) table"""
    name: str = Field(..., description="User name")
    trainer_name: Optional[str] = Field(default=None, description="Pokemon trainer name for user, if any")
    age: int 