from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Skill(BaseModel):
    name: str = Field(..., description="Skill name")
    expertise_level: int = Field(..., ge=1, le=10, description="Expertise level from 1-10")


class ProjectBase(BaseModel):
    title: str = Field(..., description="Project title")
    skills: List[Skill] = Field(..., description="Required skills for the project")


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateBase(BaseModel):
    name: str = Field(..., description="Candidate name")
    skills: List[Skill] = Field(..., description="Candidate skills")


class CandidateCreate(CandidateBase):
    pass


class Candidate(CandidateBase):
    id: int
    special_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamMember(BaseModel):
    candidate_id: int
    name: str
    assigned_skills: List[str]


class TeamFormationRequest(BaseModel):
    project_id: int
    candidate_ids: List[int] = Field(..., min_items=1, max_items=100)
    team_size: int = Field(..., ge=1, le=10)


class TeamFormationResponse(BaseModel):
    team: List[TeamMember]
    total_expertise: int
    coverage: float


class CandidateScoreRequest(BaseModel):
    candidate_id: str
    skills: List[tuple[str, float]]  # (skill_name, expertise_level)


class CandidateScoreResponse(BaseModel):
    latency_ms: int
    success: bool = True
    error_log: Optional[str] = None
    special_scores: List[float] = [] 