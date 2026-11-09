
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Body,
    BackgroundTasks,
    Query
)

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db

from src.models.task import Task
from src.models.execution_history import ExecutionHistory
from src.models.task_schema import (
    TaskCreate,
    TaskUpdate,
    TaskResponse
)

from src.services.task_service import (
    create_task,
    get_task,
    update_task,
    delete_task
)

from src.services.concurrency_service import (
    execute_tasks_concurrently
)

from src.services.background_service import (
    process_background_tasks
)


router = APIRouter(
    prefix="/api",
    tags=["Automation Tasks"]
)


# ---------------------------------------
# CREATE TASK
# ---------------------------------------

@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_task(db, task_data)


# ---------------------------------------
# GET ALL TASKS WITH PAGINATION
# ---------------------------------------

@router.get("/tasks")
async def get_tasks(
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Task)

    if status:
        query = query.where(Task.status == status)

    count_query = select(func.count()).select_from(
        query.subquery()
    )

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = (
        query
        .order_by(Task.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    tasks = result.scalars().all()

    return {
        "total_records": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (
            (total + page_size - 1) // page_size
        ),
        "tasks": tasks
    }


# ---------------------------------------
# CONCURRENT TASK EXECUTION
# ---------------------------------------

@router.post("/tasks/execute-concurrently")
async def execute_concurrent_tasks(
    task_ids: list[int] = Body(..., embed=True)
):
    if not task_ids:
        return {
            "message": "Please provide at least one task ID",
            "results": []
        }

    results = await execute_tasks_concurrently(task_ids)

    return {
        "message": "Concurrent task execution completed",
        "total_tasks": len(results),
        "results": results
    }


# ---------------------------------------
# BACKGROUND TASK EXECUTION
# ---------------------------------------

@router.post(
    "/tasks/execute-background",
    status_code=status.HTTP_202_ACCEPTED
)
async def execute_tasks_in_background(
    background_tasks: BackgroundTasks,
    task_ids: list[int] = Body(..., embed=True)
):
    if not task_ids:
        return {
            "message": "Please provide at least one task ID"
        }

    background_tasks.add_task(
        process_background_tasks,
        task_ids
    )

    return {
        "message": "Tasks submitted for background execution",
        "total_tasks": len(task_ids),
        "task_ids": task_ids,
        "status": "Accepted"
    }


# ---------------------------------------
# EXECUTION HISTORY WITH PAGINATION
# ---------------------------------------

@router.get("/tasks/execution-history")
async def get_execution_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    count_query = select(func.count()).select_from(
        ExecutionHistory
    )

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = (
        select(ExecutionHistory)
        .order_by(ExecutionHistory.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    records = result.scalars().all()

    return {
        "total_records": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (
            (total + page_size - 1) // page_size
        ),
        "history": [
            {
                "id": record.id,
                "task_id": record.task_id,
                "status": record.status,
                "result": record.result,
                "started_at": record.started_at,
                "completed_at": record.completed_at
            }
            for record in records
        ]
    }


# ---------------------------------------
# GET SINGLE TASK
# ---------------------------------------

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def task_details(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    task = await get_task(db, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# ---------------------------------------
# UPDATE TASK
# ---------------------------------------

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def edit_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    task = await update_task(db, task_id, task_data)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# ---------------------------------------
# DELETE TASK
# ---------------------------------------

@router.delete("/tasks/{task_id}")
async def remove_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await delete_task(db, task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "message": "Task deleted successfully"
    }
