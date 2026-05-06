"""APScheduler jobs."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.main_pipeline import run_pipeline
from backend.core.logger import logger

_scheduler = None


def get_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        # Daily at 16:30 Beijing (after A-share close 15:00 + buffer)
        _scheduler.add_job(
            run_pipeline,
            CronTrigger(hour=16, minute=30),
            id="daily_pipeline",
            replace_existing=True,
            kwargs={"use_llm": True},
        )
        logger.info("Scheduler initialized (daily 16:30 Asia/Shanghai)")
    return _scheduler


def start_scheduler():
    s = get_scheduler()
    if not s.running:
        s.start()
        logger.info("Scheduler started")
