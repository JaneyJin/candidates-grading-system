"""
候选人评分系统使用示例
演示如何创建项目、候选人和进行团队匹配
"""

import asyncio
import httpx
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000/api"


async def create_project(client: httpx.AsyncClient, title: str, skills: list) -> Dict[str, Any]:
    """创建项目"""
    project_data = {
        "title": title,
        "skills": skills
    }
    
    response = await client.post(f"{BASE_URL}/projects/", json=project_data)
    response.raise_for_status()
    return response.json()


async def create_candidate(client: httpx.AsyncClient, name: str, skills: list) -> Dict[str, Any]:
    """创建候选人"""
    candidate_data = {
        "name": name,
        "skills": skills
    }
    
    response = await client.post(f"{BASE_URL}/candidates/", json=candidate_data)
    response.raise_for_status()
    return response.json()


async def form_team(client: httpx.AsyncClient, project_id: int, candidate_ids: list, team_size: int) -> Dict[str, Any]:
    """形成团队"""
    team_request = {
        "project_id": project_id,
        "candidate_ids": candidate_ids,
        "team_size": team_size
    }
    
    response = await client.post(f"{BASE_URL}/form-team/", json=team_request)
    response.raise_for_status()
    return response.json()


async def main():
    """主函数 - 演示完整流程"""
    print("🚀 候选人评分系统演示")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. 创建项目
            print("\n📋 1. 创建项目...")
            project_skills = [
                {"name": "Python", "expertise_level": 7},
                {"name": "JavaScript", "expertise_level": 8},
                {"name": "React", "expertise_level": 6},
                {"name": "SQL", "expertise_level": 5}
            ]
            
            project = await create_project(client, "全栈开发项目", project_skills)
            print(f"✅ 项目创建成功: {project['title']} (ID: {project['id']})")
            
            # 2. 创建候选人
            print("\n👥 2. 创建候选人...")
            candidates_data = [
                {
                    "name": "Alice",
                    "skills": [
                        {"name": "Python", "expertise_level": 9},
                        {"name": "JavaScript", "expertise_level": 7},
                        {"name": "React", "expertise_level": 8}
                    ]
                },
                {
                    "name": "Bob",
                    "skills": [
                        {"name": "JavaScript", "expertise_level": 9},
                        {"name": "React", "expertise_level": 8},
                        {"name": "SQL", "expertise_level": 7}
                    ]
                },
                {
                    "name": "Charlie",
                    "skills": [
                        {"name": "Python", "expertise_level": 8},
                        {"name": "SQL", "expertise_level": 8},
                        {"name": "DevOps", "expertise_level": 7}
                    ]
                }
            ]
            
            candidate_ids = []
            for candidate_data in candidates_data:
                candidate = await create_candidate(client, candidate_data["name"], candidate_data["skills"])
                candidate_ids.append(candidate["id"])
                print(f"✅ 候选人创建成功: {candidate['name']} (ID: {candidate['id']})")
            
            # 3. 获取候选人详情（会自动获取评分）
            print("\n📊 3. 获取候选人详情...")
            for candidate_id in candidate_ids:
                response = await client.get(f"{BASE_URL}/candidates/{candidate_id}")
                candidate = response.json()
                score = candidate.get("special_score", "未获取")
                print(f"👤 {candidate['name']}: 评分 = {score}")
            
            # 4. 形成团队
            print("\n🤝 4. 形成最优团队...")
            team_result = await form_team(client, project["id"], candidate_ids, 2)
            
            print(f"✅ 团队匹配成功!")
            print(f"📈 技能覆盖率: {team_result['coverage']:.1%}")
            print(f"🎯 总专业度: {team_result['total_expertise']}")
            print("\n👥 团队成员:")
            
            for member in team_result["team"]:
                print(f"  • {member['name']} (ID: {member['candidate_id']})")
                print(f"    分配技能: {', '.join(member['assigned_skills'])}")
            
            # 5. 查看所有项目
            print("\n📋 5. 查看所有项目...")
            response = await client.get(f"{BASE_URL}/projects/")
            projects = response.json()
            print(f"📊 共有 {len(projects)} 个项目:")
            for p in projects:
                print(f"  • {p['title']} (ID: {p['id']})")
            
            # 6. 查看所有候选人
            print("\n👥 6. 查看所有候选人...")
            response = await client.get(f"{BASE_URL}/candidates/")
            candidates = response.json()
            print(f"📊 共有 {len(candidates)} 个候选人:")
            for c in candidates:
                print(f"  • {c['name']} (ID: {c['id']})")
            
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP错误: {e}")
            print(f"响应内容: {e.response.text}")
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    print("⚠️  请确保:")
    print("1. 主应用正在运行 (poetry run dev)")
    print("2. Mock API正在运行 (poetry run mock)")
    print("3. 两个服务都在默认端口 (8000 和 8001)")
    print()
    
    # 运行演示
    asyncio.run(main()) 