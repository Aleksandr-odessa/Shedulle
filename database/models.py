from datetime import time, date
from typing import Dict

from sqlmodel import SQLModel,Field

class PlanBase(SQLModel):
    day: str
    start_time: str
    names:str
    duration:str| None

class Plan(PlanBase, table=True):
    id: int | None = Field(primary_key=True, index=True)
    finish_time: str

class EditTimeDay(SQLModel):
    times: Dict[str, str]
    days: Dict[str, str]

class DeleteLessonRequest(SQLModel):
    name: str
    day: str

