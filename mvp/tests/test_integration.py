import pytest
from request_manager import RequestManager, Request, RequestPriority
from gemini_service import GeminiService
from monitoring import MonitoringDashboard
import asyncio
import time

@pytest.fixture
def monitoring():
    return MonitoringDashboard()

@pytest.mark.asyncio
async def test_cache_key_collisions(monitoring):
    # Test that similar requests don't collide
    req1 = Request(payload={"method": "categorize_gtd_level", "task_content": "Task A"}, priority=RequestPriority.HIGH)
    req2 = Request(payload={"method": "categorize_gtd_level", "task_content": "Task B"}, priority=RequestPriority.HIGH)
    
    manager = RequestManager(batch_processor=lambda x: [None]*len(x.requests))
    key1 = manager.cache._generate_cache_key(req1)
    key2 = manager.cache._generate_cache_key(req2)
    assert key1 != key2, "Different content should generate different cache keys"

@pytest.mark.asyncio
async def test_mixed_priority_batching():
    # Test batch prioritization
    manager = RequestManager(batch_processor=lambda x: [None]*len(x.requests))
    
    # Submit mixed priority requests
    await manager.submit_request(Request(payload={}, priority=RequestPriority.LOW))
    await manager.submit_request(Request(payload={}, priority=RequestPriority.HIGH))
    
    # Verify high priority processed first
    batch = await manager._collect_batch(manager.queues[RequestPriority.HIGH])
    assert len(batch.requests) == 1, "High priority should be processed separately"

@pytest.mark.asyncio
async def test_high_volume_processing():
    """Test concurrency scaling with simulated load"""
    manager = RequestManager(batch_processor=lambda x: [None]*len(x.requests))
    tasks = [Request(payload={}, priority=RequestPriority.MEDIUM) for _ in range(200)]
    
    start = time.monotonic()
    await asyncio.gather(*[manager.submit_request(t) for t in tasks])
    duration = time.monotonic() - start
    
    assert duration < 10, "200 requests should process in under 10 seconds" 