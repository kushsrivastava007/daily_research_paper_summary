# src/paper_digest/notifications/email.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
import json
from paper_digest.auth.config import settings


def send_digest_email(
    recipient_email: str,
    papers: list,
    user_name: str = None
) -> bool:
    """Send email digest of papers to user."""

    if not settings.SENDGRID_API_KEY:
        print(f"Warning: SendGrid API key not configured. Skipping email to {recipient_email}")
        return False

    # Build email HTML
    papers_html = ""
    for paper in papers[:10]:  # Limit to top 10 papers
        score = paper.get("score", "N/A")
        title = paper.get("title", "")
        abstract = paper.get("abstract", "")[:200]
        url = paper.get("url", "")
        authors = paper.get("authors", [])
        authors_str = ", ".join(authors[:3]) + ("..." if len(authors) > 3 else "")

        papers_html += f"""
        <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #007bff; background-color: #f8f9fa;">
            <h3 style="margin-top: 0; color: #333;">
                <a href="{url}" style="color: #007bff; text-decoration: none;">
                    {title}
                </a>
            </h3>
            <p style="color: #666; margin: 5px 0;"><strong>Score:</strong> {score}/10</p>
            <p style="color: #666; margin: 5px 0;"><strong>Authors:</strong> {authors_str}</p>
            <p style="color: #555; margin: 5px 0;">{abstract}...</p>
            <a href="{url}" style="color: #007bff; text-decoration: none; font-size: 14px;">
                Read on arXiv →
            </a>
        </div>
        """

    greeting = f"Hi {user_name}," if user_name else "Hi,"

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #007bff; margin: 0;">📚 Paper Digest</h1>
                    <p style="color: #666; margin-top: 5px;">Your Daily AI Research Summary</p>
                </div>

                <p>{greeting}</p>
                <p>We found {len(papers)} highly relevant research papers for you today. Here are the top picks:</p>

                {papers_html}

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="color: #666; font-size: 12px; text-align: center;">
                    <a href="{settings.APP_URL}/settings" style="color: #007bff; text-decoration: none;">
                        Manage Preferences
                    </a> | 
                    <a href="{settings.APP_URL}" style="color: #007bff; text-decoration: none;">
                        View Dashboard
                    </a>
                </p>
                <p style="color: #999; font-size: 12px; text-align: center;">
                    © Paper Digest - AI Research Discovery
                </p>
            </div>
        </body>
    </html>
    """

    try:
        message = Mail(
            from_email=settings.SENDGRID_FROM_EMAIL,
            to_emails=recipient_email,
            subject="📚 Your Daily Paper Digest",
            html_content=html_content,
        )

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        print(f"Email sent to {recipient_email} (Status: {response.status_code})")
        return response.status_code in [200, 201, 202]

    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")
        return False


def send_welcome_email(recipient_email: str, user_name: str = None) -> bool:
    """Send welcome email to new user."""

    if not settings.SENDGRID_API_KEY:
        return False

    greeting = f"Hi {user_name}," if user_name else "Hi,"

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #007bff; margin: 0;">📚 Welcome to Paper Digest!</h1>
                </div>

                <p>{greeting}</p>
                <p>Thanks for joining Paper Digest! 🎉</p>

                <p>To get started, you'll need to:</p>
                <ol>
                    <li>Add your Groq API key to your account settings</li>
                    <li>Customize your research interests</li>
                    <li>Sit back and receive daily paper digests!</li>
                </ol>

                <p style="text-align: center; margin: 30px 0;">
                    <a href="{settings.APP_URL}/settings" 
                       style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Complete Setup
                    </a>
                </p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="color: #666; font-size: 12px; text-align: center;">
                    © Paper Digest - AI Research Discovery
                </p>
            </div>
        </body>
    </html>
    """

    try:
        message = Mail(
            from_email=settings.SENDGRID_FROM_EMAIL,
            to_emails=recipient_email,
            subject="Welcome to Paper Digest! 📚",
            html_content=html_content,
        )

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code in [200, 201, 202]

    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False
