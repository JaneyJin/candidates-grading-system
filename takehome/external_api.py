import asyncio
import httpx
from typing import List, Optional
from takehome.models import CandidateScoreRequest, CandidateScoreResponse
from takehome import logger

MOCK_FLAKY_ENDPOINT = "http://localhost:8001/generate_score"


class ExternalAPIService:
    """
    外部API服务，处理flaky的评分API
    """
    
    def __init__(self, max_retries: int = 5, timeout: float = 30.0):
        self.max_retries = max_retries
        self.timeout = timeout
        self._cache: dict[str, float] = {}  # 简单的内存缓存
    
    async def get_candidate_score(
        self, 
        candidate_id: str, 
        skills: List[tuple[str, float]]
    ) -> Optional[float]:
        """
        获取候选人评分，带重试机制和缓存
        
        Args:
            candidate_id: 候选人ID
            skills: 技能列表 [(skill_name, expertise_level), ...]
            
        Returns:
            评分或None（如果失败）
        """
        # 检查缓存
        cache_key = f"{candidate_id}_{hash(tuple(skills))}"
        if cache_key in self._cache:
            logger.info(f"Cache hit for candidate {candidate_id}")
            return self._cache[cache_key]
        
        # 重试机制
        for attempt in range(self.max_retries):
            try:
                score = await self._call_score_api(candidate_id, skills)
                if score is not None:
                    # 缓存结果
                    self._cache[cache_key] = score
                    logger.info(f"Successfully got score for candidate {candidate_id} on attempt {attempt + 1}")
                    return score
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for candidate {candidate_id}: {e}")
            
            # 指数退避
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time}s before retry for candidate {candidate_id}")
                await asyncio.sleep(wait_time)
        
        logger.error(f"Failed to get score for candidate {candidate_id} after {self.max_retries} attempts")
        return None
    
    async def _call_score_api(
        self, 
        candidate_id: str, 
        skills: List[tuple[str, float]]
    ) -> Optional[float]:
        """
        调用评分API
        
        Args:
            candidate_id: 候选人ID
            skills: 技能列表
            
        Returns:
            评分或None
        """
        request_data = CandidateScoreRequest(
            candidate_id=candidate_id,
            skills=skills
        )
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    MOCK_FLAKY_ENDPOINT,
                    json=request_data.model_dump()
                )
                response.raise_for_status()
                
                result = CandidateScoreResponse(**response.json())
                
                if not result.success:
                    logger.warning(f"API returned error for candidate {candidate_id}: {result.error_log}")
                    return None
                
                # 计算平均评分
                if result.special_scores:
                    return sum(result.special_scores) / len(result.special_scores)
                else:
                    return None
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error for candidate {candidate_id}: {e}")
                return None
            except httpx.RequestError as e:
                logger.error(f"Request error for candidate {candidate_id}: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error for candidate {candidate_id}: {e}")
                return None
    
    async def get_candidate_scores_batch(
        self, 
        candidates_data: List[tuple[str, List[tuple[str, float]]]]
    ) -> dict[str, float]:
        """
        批量获取候选人评分
        
        Args:
            candidates_data: [(candidate_id, skills), ...]
            
        Returns:
            {candidate_id: score, ...}
        """
        tasks = []
        for candidate_id, skills in candidates_data:
            task = self.get_candidate_score(candidate_id, skills)
            tasks.append((candidate_id, task))
        
        results = {}
        for candidate_id, task in tasks:
            score = await task
            if score is not None:
                results[candidate_id] = score
        
        return results


# 全局实例
external_api_service = ExternalAPIService() 