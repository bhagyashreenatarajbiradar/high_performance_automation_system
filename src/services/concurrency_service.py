
import asyncio
import logging

logger = logging.getLogger(__name__)

MAX_CONCURRENT_TASKS = 5


async def execute_single_task(task_id: int):
    """
    Simulate asynchronous execution of one task.
    """
    logger.info("Task %s started", task_id)

    await asyncio.sleep(2)

    logger.info("Task %s completed", task_id)

    return {
        "task_id": task_id,
        "status": "Completed",
        "message": f"Task {task_id} executed successfully"
    }


async def execute_tasks_concurrently(task_ids: list[int]):
    """
    Execute multiple tasks concurrently with a concurrency limit.
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    async def limited_execution(task_id: int):
        async with semaphore:
            return await execute_single_task(task_id)

    results = await asyncio.gather(
        *(limited_execution(task_id) for task_id in task_ids)
    )

    return results
