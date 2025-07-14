from typing import List, Dict, Tuple, Set
from itertools import combinations
from takehome.models import Project, Candidate, TeamMember, TeamFormationResponse


class TeamFormationAlgorithm:
    """
    团队匹配算法实现
    使用贪心算法 + 回溯搜索来找到最优团队
    """
    
    @staticmethod
    def form_optimal_team(
        project: Project, 
        candidates: List[Candidate], 
        team_size: int
    ) -> TeamFormationResponse:
        """
        形成最优团队
        
        Args:
            project: 项目信息
            candidates: 候选人列表
            team_size: 团队大小
            
        Returns:
            TeamFormationResponse: 团队信息
        """
        if not candidates or team_size <= 0:
            return TeamFormationResponse(team=[], total_expertise=0, coverage=0.0)
        
        # 获取项目所需技能
        required_skills = {skill.name: skill.expertise_level for skill in project.skills}
        
        # 如果团队大小大于候选人数量，调整团队大小
        team_size = min(team_size, len(candidates))
        
        # 生成所有可能的团队组合
        best_team = None
        best_score = -1
        best_coverage = 0.0
        
        for team_candidates in combinations(candidates, team_size):
            team_result = TeamFormationAlgorithm._evaluate_team(
                team_candidates, required_skills
            )
            
            if team_result is None:
                continue
                
            team_members, total_expertise, coverage = team_result
            
            # 优先选择覆盖率高的团队
            if coverage > best_coverage or (coverage == best_coverage and total_expertise > best_score):
                best_team = team_members
                best_score = total_expertise
                best_coverage = coverage
        
        if best_team is None:
            return TeamFormationResponse(team=[], total_expertise=0, coverage=0.0)
        
        return TeamFormationResponse(
            team=best_team,
            total_expertise=best_score,
            coverage=best_coverage
        )
    
    @staticmethod
    def _evaluate_team(
        team_candidates: Tuple[Candidate, ...], 
        required_skills: Dict[str, int]
    ) -> Tuple[List[TeamMember], int, float]:
        """
        评估团队的质量
        
        Args:
            team_candidates: 团队成员
            required_skills: 项目所需技能
            
        Returns:
            (团队成员, 总专业度, 覆盖率) 或 None
        """
        # 为每个技能找到最佳候选人
        skill_assignments: Dict[str, Tuple[int, str, int]] = {}  # skill -> (candidate_id, name, expertise)
        
        for candidate in team_candidates:
            for skill in candidate.skills:
                if skill.name in required_skills:
                    current_best = skill_assignments.get(skill.name, (0, "", 0))
                    if skill.expertise_level > current_best[2]:
                        skill_assignments[skill.name] = (
                            candidate.id, 
                            candidate.name, 
                            skill.expertise_level
                        )
        
        # 计算覆盖率
        covered_skills = len(skill_assignments)
        total_skills = len(required_skills)
        coverage = covered_skills / total_skills if total_skills > 0 else 0.0
        
        # 计算总专业度
        total_expertise = sum(assignment[2] for assignment in skill_assignments.values())
        
        # 构建团队成员信息
        team_members: Dict[int, TeamMember] = {}
        
        for skill_name, (candidate_id, candidate_name, expertise) in skill_assignments.items():
            if candidate_id not in team_members:
                # 找到候选人的完整信息
                candidate = next(c for c in team_candidates if c.id == candidate_id)
                team_members[candidate_id] = TeamMember(
                    candidate_id=candidate_id,
                    name=candidate_name,
                    assigned_skills=[]
                )
            team_members[candidate_id].assigned_skills.append(skill_name)
        
        return list(team_members.values()), total_expertise, coverage 