from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal
TaskOrigin = Literal['conversation','plan','workflow','skill-gap']
AssigneeType = Literal['user','role','queue','unassigned']
ScheduleMode = Literal['cron','interval','event']
ScheduleAction = Literal['workflow','report','condition']
@dataclass(slots=True)
class TaskRecord:
    task_id:str; title:str; origin:TaskOrigin; source_ref:str
    dependencies:list[str]=field(default_factory=list)
    acceptance_criteria:list[str]=field(default_factory=list)
    assignee_type:AssigneeType='unassigned'; assignee:str|None=None
@dataclass(slots=True)
class ScheduleRecord:
    schedule_id:str; mode:ScheduleMode; action_type:ScheduleAction; action_target:str
    approval_required:bool=False; approval_policy_ref:str|None=None
