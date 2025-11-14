from __future__ import annotations
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.matching.simulator import BatchProcessor
from app.models.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


async def process_batch_assignment():
    """Runs every few minutes to assign pending orders."""
    db = SessionLocal()
    try:
        processor = BatchProcessor(db)
        result = await processor.process_batch()
        logger.info(
            f"Batch {result.get('batch_id')} => assigned {result.get('assigned_orders')}/{result.get('total_orders')} orders"
        )
    except Exception as e:
        logger.exception(f"Batch processing failed: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        process_batch_assignment,
        "interval",
        minutes=3,
        id="batch_assignment",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("WORK4FOOD batch scheduler started (3-minute intervals)")
    return scheduler


