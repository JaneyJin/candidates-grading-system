from typing import Dict, List, Optional
from datetime import datetime
from takehome.models import Project, Candidate, ProjectCreate, CandidateCreate


class Database:
    def __init__(self):
        self.projects: Dict[int, Project] = {}
        self.candidates: Dict[int, Candidate] = {}
        self._project_id_counter = 1
        self._candidate_id_counter = 1

    def create_project(self, project: ProjectCreate) -> Project:
        project_id = self._project_id_counter
        self._project_id_counter += 1
        
        new_project = Project(
            id=project_id,
            title=project.title,
            skills=project.skills,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.projects[project_id] = new_project
        return new_project

    def get_project(self, project_id: int) -> Optional[Project]:
        return self.projects.get(project_id)

    def get_all_projects(self) -> List[Project]:
        return list(self.projects.values())

    def update_project(self, project_id: int, project: ProjectCreate) -> Optional[Project]:
        if project_id not in self.projects:
            return None
        
        updated_project = Project(
            id=project_id,
            title=project.title,
            skills=project.skills,
            created_at=self.projects[project_id].created_at,
            updated_at=datetime.now()
        )
        self.projects[project_id] = updated_project
        return updated_project

    def delete_project(self, project_id: int) -> bool:
        if project_id in self.projects:
            del self.projects[project_id]
            return True
        return False

    def create_candidate(self, candidate: CandidateCreate) -> Candidate:
        candidate_id = self._candidate_id_counter
        self._candidate_id_counter += 1
        
        new_candidate = Candidate(
            id=candidate_id,
            name=candidate.name,
            skills=candidate.skills,
            special_score=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.candidates[candidate_id] = new_candidate
        return new_candidate

    def get_candidate(self, candidate_id: int) -> Optional[Candidate]:
        return self.candidates.get(candidate_id)

    def get_all_candidates(self) -> List[Candidate]:
        return list(self.candidates.values())

    def get_candidates_by_ids(self, candidate_ids: List[int]) -> List[Candidate]:
        return [self.candidates.get(cid) for cid in candidate_ids if cid in self.candidates]

    def update_candidate(self, candidate_id: int, candidate: CandidateCreate) -> Optional[Candidate]:
        if candidate_id not in self.candidates:
            return None
        
        updated_candidate = Candidate(
            id=candidate_id,
            name=candidate.name,
            skills=candidate.skills,
            special_score=self.candidates[candidate_id].special_score,
            created_at=self.candidates[candidate_id].created_at,
            updated_at=datetime.now()
        )
        self.candidates[candidate_id] = updated_candidate
        return updated_candidate

    def update_candidate_score(self, candidate_id: int, special_score: float) -> Optional[Candidate]:
        if candidate_id not in self.candidates:
            return None
        
        self.candidates[candidate_id].special_score = special_score
        self.candidates[candidate_id].updated_at = datetime.now()
        return self.candidates[candidate_id]

    def delete_candidate(self, candidate_id: int) -> bool:
        if candidate_id in self.candidates:
            del self.candidates[candidate_id]
            return True
        return False


# Global database instance
db = Database() 