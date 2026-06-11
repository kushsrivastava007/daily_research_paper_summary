# src/paper_digest/scheduler/tasks.py
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from paper_digest.storage.database import (
    get_all_papers,
    get_all_active_users,
)
from paper_digest.notifications.email import send_digest_email
from paper_digest.graph.pipeline import run_pipeline


def run_pipeline_and_send_digest():
    """Run the paper-fetching pipeline, then send the daily digest email."""
    print(f"[{datetime.utcnow().isoformat()}] Running pipeline before digest...")
    try:
        run_pipeline()
    except Exception as e:
        print(f"Error running pipeline: {e}")

    send_daily_digest()


def send_daily_digest():
    """Send paper digest email to all active users."""
    print(f"[{datetime.utcnow().isoformat()}] Starting daily digest send...")

    try:
        users = get_all_active_users()
        papers = get_all_papers()

        # Convert papers to dicts for JSON serialization
        papers_data = []
        for paper in papers[:20]:  # Limit to last 20 papers
            papers_data.append({
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": json.loads(paper.authors) if isinstance(paper.authors, str) else paper.authors,
                "url": paper.url,
                "score": paper.score,
                "published": paper.published,
            })

        for user in users:
            if not user.preferences:
                continue

            prefs = json.loads(user.preferences)

            # Check if user wants to receive emails
            if not prefs.get("receive_emails", True):
                continue

            # Filter papers by categories (optional)
            # For now, send all papers
            success = send_digest_email(
                recipient_email=user.email,
                papers=papers_data,
                user_name=user.email.split("@")[0],
            )

            if success:
                print(f"✓ Sent digest to {user.email}")
            else:
                print(f"✗ Failed to send digest to {user.email}")

        print(f"[{datetime.utcnow().isoformat()}] Daily digest send completed")

    except Exception as e:
        print(f"Error in send_daily_digest: {e}")


def start_scheduler(scheduler_config: dict = None):
    """Start background scheduler for recurring tasks."""

    # Default config: send digest every day at 9 AM UTC
    if scheduler_config is None:
        scheduler_config = {
            "hour": 9,
            "minute": 0,
            "timezone": "UTC",
        }

    scheduler = BackgroundScheduler()

    # Schedule daily digest
    scheduler.add_job(
        run_pipeline_and_send_digest,
        "cron",
        hour=scheduler_config.get("hour", 9),
        minute=scheduler_config.get("minute", 0),
        timezone=scheduler_config.get("timezone", "UTC"),
        id="daily_digest",
        name="Run pipeline and send daily paper digest",
    )

    scheduler.start()
    print("✓ Scheduler started - Daily digest at {}:{}".format(
        scheduler_config.get("hour", 9),
        str(scheduler_config.get("minute", 0)).zfill(2),
    ))

    return scheduler
