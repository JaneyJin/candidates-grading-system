import pytest
from fastapi.testclient import TestClient
from takehome.app import app
from takehome.database import db
from takehome.models import Skill

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """每个测试前重置数据库"""
    db.projects.clear()
    db.candidates.clear()
    db._project_id_counter = 1
    db._candidate_id_counter = 1


class TestProjects:
    """项目相关测试"""
    
    def test_create_project(self):
        """测试创建项目"""
        project_data = {
            "title": "Test Project",
            "skills": [
                {"name": "Python", "expertise_level": 7},
                {"name": "JavaScript", "expertise_level": 8}
            ]
        }
        
        response = client.post("/api/projects/", json=project_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Test Project"
        assert len(data["skills"]) == 2
        assert data["id"] == 1
    
    def test_get_project(self):
        """测试获取项目"""
        # 先创建项目
        project_data = {
            "title": "Test Project",
            "skills": [{"name": "Python", "expertise_level": 7}]
        }
        create_response = client.post("/api/projects/", json=project_data)
        project_id = create_response.json()["id"]
        
        # 获取项目
        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Project"
    
    def test_get_nonexistent_project(self):
        """测试获取不存在的项目"""
        response = client.get("/api/projects/999")
        assert response.status_code == 404
    
    def test_update_project(self):
        """测试更新项目"""
        # 先创建项目
        project_data = {
            "title": "Original Title",
            "skills": [{"name": "Python", "expertise_level": 7}]
        }
        create_response = client.post("/api/projects/", json=project_data)
        project_id = create_response.json()["id"]
        
        # 更新项目
        update_data = {
            "title": "Updated Title",
            "skills": [{"name": "JavaScript", "expertise_level": 8}]
        }
        response = client.put(f"/api/projects/{project_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["skills"][0]["name"] == "JavaScript"
    
    def test_delete_project(self):
        """测试删除项目"""
        # 先创建项目
        project_data = {
            "title": "Test Project",
            "skills": [{"name": "Python", "expertise_level": 7}]
        }
        create_response = client.post("/api/projects/", json=project_data)
        project_id = create_response.json()["id"]
        
        # 删除项目
        response = client.delete(f"/api/projects/{project_id}")
        assert response.status_code == 204
        
        # 验证项目已被删除
        get_response = client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 404


class TestCandidates:
    """候选人相关测试"""
    
    def test_create_candidate(self):
        """测试创建候选人"""
        candidate_data = {
            "name": "John Doe",
            "skills": [
                {"name": "Python", "expertise_level": 8},
                {"name": "JavaScript", "expertise_level": 6}
            ]
        }
        
        response = client.post("/api/candidates/", json=candidate_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "John Doe"
        assert len(data["skills"]) == 2
        assert data["id"] == 1
    
    def test_get_candidate(self):
        """测试获取候选人"""
        # 先创建候选人
        candidate_data = {
            "name": "John Doe",
            "skills": [{"name": "Python", "expertise_level": 8}]
        }
        create_response = client.post("/api/candidates/", json=candidate_data)
        candidate_id = create_response.json()["id"]
        
        # 获取候选人
        response = client.get(f"/api/candidates/{candidate_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "John Doe"
    
    def test_get_nonexistent_candidate(self):
        """测试获取不存在的候选人"""
        response = client.get("/api/candidates/999")
        assert response.status_code == 404
    
    def test_update_candidate(self):
        """测试更新候选人"""
        # 先创建候选人
        candidate_data = {
            "name": "Original Name",
            "skills": [{"name": "Python", "expertise_level": 7}]
        }
        create_response = client.post("/api/candidates/", json=candidate_data)
        candidate_id = create_response.json()["id"]
        
        # 更新候选人
        update_data = {
            "name": "Updated Name",
            "skills": [{"name": "JavaScript", "expertise_level": 8}]
        }
        response = client.put(f"/api/candidates/{candidate_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["skills"][0]["name"] == "JavaScript"
    
    def test_delete_candidate(self):
        """测试删除候选人"""
        # 先创建候选人
        candidate_data = {
            "name": "John Doe",
            "skills": [{"name": "Python", "expertise_level": 7}]
        }
        create_response = client.post("/api/candidates/", json=candidate_data)
        candidate_id = create_response.json()["id"]
        
        # 删除候选人
        response = client.delete(f"/api/candidates/{candidate_id}")
        assert response.status_code == 204
        
        # 验证候选人已被删除
        get_response = client.get(f"/api/candidates/{candidate_id}")
        assert get_response.status_code == 404


class TestTeamFormation:
    """团队匹配测试"""
    
    def test_form_team(self):
        """测试团队匹配"""
        # 创建项目
        project_data = {
            "title": "Full-stack Project",
            "skills": [
                {"name": "Python", "expertise_level": 7},
                {"name": "JavaScript", "expertise_level": 8},
                {"name": "React", "expertise_level": 6}
            ]
        }
        project_response = client.post("/api/projects/", json=project_data)
        project_id = project_response.json()["id"]
        
        # 创建候选人
        candidates_data = [
            {
                "name": "Alice",
                "skills": [
                    {"name": "Python", "expertise_level": 9},
                    {"name": "JavaScript", "expertise_level": 7}
                ]
            },
            {
                "name": "Bob",
                "skills": [
                    {"name": "JavaScript", "expertise_level": 9},
                    {"name": "React", "expertise_level": 8}
                ]
            }
        ]
        
        candidate_ids = []
        for candidate_data in candidates_data:
            response = client.post("/api/candidates/", json=candidate_data)
            candidate_ids.append(response.json()["id"])
        
        # 形成团队
        team_request = {
            "project_id": project_id,
            "candidate_ids": candidate_ids,
            "team_size": 2
        }
        
        response = client.post("/api/form-team/", json=team_request)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["team"]) == 2
        assert data["coverage"] == 1.0
        assert data["total_expertise"] > 0
    
    def test_form_team_with_nonexistent_project(self):
        """测试使用不存在的项目进行团队匹配"""
        team_request = {
            "project_id": 999,
            "candidate_ids": [1, 2],
            "team_size": 2
        }
        
        response = client.post("/api/form-team/", json=team_request)
        assert response.status_code == 404
    
    def test_form_team_with_nonexistent_candidates(self):
        """测试使用不存在的候选人进行团队匹配"""
        # 创建项目
        project_data = {
            "title": "Test Project",
            "skills": [{"name": "Python", "expertise_level": 7}]
        }
        project_response = client.post("/api/projects/", json=project_data)
        project_id = project_response.json()["id"]
        
        team_request = {
            "project_id": project_id,
            "candidate_ids": [999, 1000],
            "team_size": 2
        }
        
        response = client.post("/api/form-team/", json=team_request)
        assert response.status_code == 404


class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "Candidate Grading System" in data["message"] 