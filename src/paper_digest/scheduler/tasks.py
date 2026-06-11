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
        # Collect all unique categories from active users
        users = get_all_active_users()
        all_categories = set()
        for user in users:
            if user.preferences:
                prefs = json.loads(user.preferences)
                cats = prefs.get("categories", [])
                all_categories.update(cats)

        categories = list(all_categories) if all_categories else None
        run_pipeline(categories=categories)
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
            paper_cats = []
            if paper.paper_categories:
                try:
                    paper_cats = json.loads(paper.paper_categories)
                except (json.JSONDecodeError, TypeError):
                    paper_cats = []
            papers_data.append({
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": json.loads(paper.authors) if isinstance(paper.authors, str) else paper.authors,
                "url": paper.url,
                "score": paper.score,
                "published": paper.published,
                "paper_categories": paper_cats,
            })

        for user in users:
            if not user.preferences:
                continue

            prefs = json.loads(user.preferences)

            # Check if user wants to receive emails
            if not prefs.get("receive_emails", True):
                continue

            # Filter papers to only those matching user's selected categories
            user_cats = set(prefs.get("categories", []))
            if user_cats:
                user_papers = [
                    p for p in papers_data
                    if user_cats & set(p.get("paper_categories", []))
                ]
            else:
                user_papers = papers_data  # no preference = send all

            if not user_papers:
                print(f"⏭ No matching papers for {user.email}, skipping")
                continue

            success = send_digest_email(
                recipient_email=user.email,
                papers=user_papers,
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

    # Default config: send digest every day at 00:05 AM IST (for testing)
    if scheduler_config is None:
        scheduler_config = {
            "hour": 0,
            "minute": 5,
            "timezone": "Asia/Kolkata",
        }

    scheduler = BackgroundScheduler()

    # Schedule daily digest
    scheduler.add_job(
        run_pipeline_and_send_digest,
        "cron",
        hour=scheduler_config.get("hour", 0),
        minute=scheduler_config.get("minute", 5),
        timezone=scheduler_config.get("timezone", "Asia/Kolkata"),
        id="daily_digest",
        name="Run pipeline and send daily paper digest",
    )

    scheduler.start()
    print("✓ Scheduler started - Daily digest at {}:{} {}".format(
        scheduler_config.get("hour", 0),
        str(scheduler_config.get("minute", 5)).zfill(2),
        scheduler_config.get("timezone", "Asia/Kolkata"),
    ))

    return scheduler
