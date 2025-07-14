from typing import List
from fastapi import APIRouter, HTTPException, status
from takehome.models import (
    Project, ProjectCreate, Candidate, CandidateCreate,
    TeamFormationRequest, TeamFormationResponse
)
from takehome.database import db
from takehome.team_algorithm import TeamFormationAlgorithm
from takehome.external_api import external_api_service
from takehome import logger

router = APIRouter(prefix="/api", tags=["api"])


# Project endpoints
@router.post("/projects/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate):
    """创建新项目"""
    try:
        new_project = db.create_project(project)
        logger.info(f"Created project: {new_project.title} with ID: {new_project.id}")
        return new_project
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )


@router.get("/projects/", response_model=List[Project])
async def get_projects():
    """获取所有项目"""
    try:
        projects = db.get_all_projects()
        logger.info(f"Retrieved {len(projects)} projects")
        return projects
    except Exception as e:
        logger.error(f"Error retrieving projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )


@router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: int):
    """获取特定项目"""
    try:
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        logger.info(f"Retrieved project: {project.title}")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project"
        )


@router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: int, project: ProjectCreate):
    """更新项目"""
    try:
        updated_project = db.update_project(project_id, project)
        if not updated_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        logger.info(f"Updated project: {updated_project.title}")
        return updated_project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int):
    """删除项目"""
    try:
        success = db.delete_project(project_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        logger.info(f"Deleted project with ID: {project_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )


# Candidate endpoints
@router.post("/candidates/", response_model=Candidate, status_code=status.HTTP_201_CREATED)
async def create_candidate(candidate: CandidateCreate):
    """创建新候选人"""
    try:
        new_candidate = db.create_candidate(candidate)
        logger.info(f"Created candidate: {new_candidate.name} with ID: {new_candidate.id}")
        return new_candidate
    except Exception as e:
        logger.error(f"Error creating candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create candidate"
        )


@router.get("/candidates/", response_model=List[Candidate])
async def get_candidates():
    """获取所有候选人"""
    try:
        candidates = db.get_all_candidates()
        logger.info(f"Retrieved {len(candidates)} candidates")
        return candidates
    except Exception as e:
        logger.error(f"Error retrieving candidates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve candidates"
        )


@router.get("/candidates/{candidate_id}", response_model=Candidate)
async def get_candidate(candidate_id: int):
    """获取特定候选人"""
    try:
        candidate = db.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with ID {candidate_id} not found"
            )
        
        # 如果候选人没有评分，尝试获取评分
        if candidate.special_score is None:
            try:
                skills_data = [(skill.name, float(skill.expertise_level)) for skill in candidate.skills]
                score = await external_api_service.get_candidate_score(str(candidate_id), skills_data)
                if score is not None:
                    db.update_candidate_score(candidate_id, score)
                    candidate.special_score = score
                    logger.info(f"Updated candidate {candidate_id} with score: {score}")
            except Exception as e:
                logger.warning(f"Failed to get score for candidate {candidate_id}: {e}")
        
        logger.info(f"Retrieved candidate: {candidate.name}")
        return candidate
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving candidate {candidate_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve candidate"
        )


@router.put("/candidates/{candidate_id}", response_model=Candidate)
async def update_candidate(candidate_id: int, candidate: CandidateCreate):
    """更新候选人"""
    try:
        updated_candidate = db.update_candidate(candidate_id, candidate)
        if not updated_candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with ID {candidate_id} not found"
            )
        logger.info(f"Updated candidate: {updated_candidate.name}")
        return updated_candidate
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating candidate {candidate_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update candidate"
        )


@router.delete("/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(candidate_id: int):
    """删除候选人"""
    try:
        success = db.delete_candidate(candidate_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with ID {candidate_id} not found"
            )
        logger.info(f"Deleted candidate with ID: {candidate_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting candidate {candidate_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete candidate"
        )


# Team formation endpoint
@router.post("/form-team/", response_model=TeamFormationResponse)
async def form_team(request: TeamFormationRequest):
    """形成最优团队"""
    try:
        # 获取项目信息
        project = db.get_project(request.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {request.project_id} not found"
            )
        
        # 获取候选人信息
        candidates = db.get_candidates_by_ids(request.candidate_ids)
        if not candidates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid candidates found"
            )
        
        # 为没有评分的候选人获取评分
        candidates_to_update = []
        for candidate in candidates:
            if candidate.special_score is None:
                skills_data = [(skill.name, float(skill.expertise_level)) for skill in candidate.skills]
                candidates_to_update.append((str(candidate.id), skills_data))
        
        if candidates_to_update:
            try:
                scores = await external_api_service.get_candidate_scores_batch(candidates_to_update)
                for candidate_id_str, score in scores.items():
                    candidate_id = int(candidate_id_str)
                    db.update_candidate_score(candidate_id, score)
                    # 更新内存中的候选人对象
                    for candidate in candidates:
                        if candidate.id == candidate_id:
                            candidate.special_score = score
                            break
                logger.info(f"Updated scores for {len(scores)} candidates")
            except Exception as e:
                logger.warning(f"Failed to update some candidate scores: {e}")
        
        # 形成团队
        team_result = TeamFormationAlgorithm.form_optimal_team(
            project, candidates, request.team_size
        )
        
        logger.info(f"Formed team for project {request.project_id} with {len(team_result.team)} members")
        return team_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error forming team: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to form team"
        ) 