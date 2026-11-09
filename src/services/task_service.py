
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task
from src.models.task_schema import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, task_data: TaskCreate):
    new_task = Task(**task_data.model_dump())

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task


async def get_all_tasks(db: AsyncSession):
    result = await db.execute(
        select(Task).order_by(Task.id.desc())
    )

    return result.scalars().all()


async def get_task(db: AsyncSession, task_id: int):
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )

    return result.scalar_one_or_none()


async def update_task(
    db: AsyncSession,
    task_id: int,
    task_data: TaskUpdate
):
    task = await get_task(db, task_id)

    if task is None:
        return None

    update_data = task_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)

    return task


async def delete_task(db: AsyncSession, task_id: int):
    task = await get_task(db, task_id)

    if task is None:
        return False

    await db.delete(task)
    await db.commit()

    return True
