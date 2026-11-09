
import logging
from datetime import datetime

from src.database.database import AsyncSessionLocal
from src.models.execution_history import ExecutionHistory
from src.services.concurrency_service import (
    execute_tasks_concurrently
)

logger = logging.getLogger(__name__)


async def process_background_tasks(task_ids: list[int]):

    history_ids = []

    async with AsyncSessionLocal() as db:
        try:
            # Create execution history records
            for task_id in task_ids:
                record = ExecutionHistory(
                    task_id=task_id,
                    status="Running"
                )

                db.add(record)

            await db.commit()

            # Retrieve records created for this batch
            from sqlalchemy import select

            result = await db.execute(
                select(ExecutionHistory)
                .where(
                    ExecutionHistory.task_id.in_(task_ids),
                    ExecutionHistory.status == "Running"
                )
                .order_by(ExecutionHistory.id.desc())
            )

            records = result.scalars().all()

            # Match the records to this batch
            records = records[:len(task_ids)]
            records.reverse()

            history_ids = [record.id for record in records]

            # Execute tasks concurrently
            execution_results = await execute_tasks_concurrently(
                task_ids
            )

            # Save results
            for record, execution_result in zip(
                records, execution_results
            ):
                record.status = execution_result["status"]
                record.result = execution_result["message"]
                record.completed_at = datetime.utcnow()

            await db.commit()

            logger.info("Execution history saved successfully")

        except Exception:
            await db.rollback()
            logger.exception("Background execution failed")

