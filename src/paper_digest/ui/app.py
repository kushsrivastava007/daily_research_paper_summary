# src/paper_digest/ui/app.py
import json
from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from typing import Optional, Annotated

from paper_digest.storage.database import (
    init_db,
    get_all_papers,
    get_paper,
    get_user,
    get_user_by_email,
    update_user_preferences,
    update_user_api_key,
)
from paper_digest.graph.pipeline import run_pipeline
from paper_digest.auth.oauth import oauth, handle_oauth_callback, get_current_user_id, create_access_token
from paper_digest.auth.config import settings
from paper_digest.notifications.email import send_welcome_email
from pydantic import BaseModel

app = FastAPI(title="Paper Digest")

# Add session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Mount static files
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

init_db()


# ── Helper Functions ──────────────────────────────────────────

def get_user_from_token(authorization: Annotated[Optional[str], Header()] = None) -> dict:
    """Extract user from Bearer token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        user_id = get_current_user_id(token)
        if user_id:
            user = get_user(user_id)
            if user:
                return user
            raise HTTPException(status_code=401, detail="User not found")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    raise HTTPException(status_code=401, detail="Not authenticated")


# ── Pydantic Models ───────────────────────────────────────────

class UserPreferencesUpdate(BaseModel):
    receive_emails: bool = True
    categories: list[str] = ["cs.AI", "cs.LG", "cs.CL"]
    send_time: str = "09:00"  # UTC time


class APIKeyUpdate(BaseModel):
    groq_api_key: str


# ── Public Routes ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with paper list."""
    papers = get_all_papers()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"papers": papers}
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """User dashboard - redirects to index with auth."""
    papers = get_all_papers()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"papers": papers}
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """User settings page."""
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={}
    )


@app.get("/paper/{paper_id}", response_class=HTMLResponse)
async def paper_detail(request: Request, paper_id: str):
    """Paper detail view."""
    paper = get_paper(paper_id)
    if not paper:
        return HTMLResponse("Paper not found", status_code=404)

    notes = json.loads(paper.notes) if paper.notes else {}
    quiz = json.loads(paper.quiz) if paper.quiz else {}

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "papers": get_all_papers(),
            "selected": paper,
            "notes": notes,
            "quiz": quiz,
        }
    )


# ── OAuth Routes ──────────────────────────────────────────────

@app.get("/auth/login/{provider}")
async def login(provider: str, request: Request):
    """Redirect to OAuth provider."""
    if provider not in ["google", "github"]:
        return JSONResponse({"error": "Invalid provider"}, status_code=400)

    redirect_uri = request.url_for("auth_callback", provider=provider)
    return await oauth.create_client(provider).authorize_redirect(
        request,
        redirect_uri,
    )


@app.get("/auth/callback/{provider}")
async def auth_callback(provider: str, request: Request):
    """Handle OAuth callback."""
    if provider not in ["google", "github"]:
        return JSONResponse({"error": "Invalid provider"}, status_code=400)

    result = await handle_oauth_callback(request, provider)

    if "error" in result:
        return JSONResponse(result, status_code=400)

    # Send welcome email
    user_email = result.get("email")
    send_welcome_email(user_email)

    # Redirect to dashboard with token in URL (can be stored in cookie/localStorage)
    token = result.get("access_token")
    return RedirectResponse(
        url=f"{settings.APP_URL}/dashboard?token={token}",
        status_code=302,
    )


@app.get("/auth/logout")
async def logout():
    """Logout user."""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("authorization")
    return response


# ── User Profile Routes ───────────────────────────────────────

@app.get("/api/user/me", response_class=JSONResponse)
async def get_current_user_endpoint(user: dict = Depends(get_user_from_token)):
    """Get current user profile."""
    return user.to_dict()


@app.put("/api/user/preferences", response_class=JSONResponse)
async def update_preferences(
    body: UserPreferencesUpdate,
    user: dict = Depends(get_user_from_token),
):
    """Update user preferences."""
    prefs = {
        "receive_emails": body.receive_emails,
        "categories": body.categories,
        "send_time": body.send_time,
    }

    updated = update_user_preferences(user.id, prefs)
    return {"status": "success", "preferences": json.loads(updated.preferences)}


@app.put("/api/user/api-key", response_class=JSONResponse)
async def set_api_key(
    body: APIKeyUpdate,
    user: dict = Depends(get_user_from_token),
):
    """Set user's Groq API key."""
    # TODO: Encrypt the API key before storing
    updated = update_user_api_key(user.id, body.groq_api_key)
    return {"status": "success", "message": "API key updated"}


@app.post("/api/run")
async def trigger_pipeline(user: dict = Depends(get_user_from_token)):
    """Trigger paper pipeline."""
    if not user.groq_api_key:
        raise HTTPException(
            status_code=400,
            detail="Groq API key not configured. Please add it in settings."
        )

    try:
        state = run_pipeline()
        return {
            "status": "success",
            "papers": len(state.get("enriched_papers", [])),
            "errors": state.get("errors", []),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}