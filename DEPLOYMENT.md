# Deployment Guide - Paper Digest

This guide explains how to deploy Paper Digest to production.

## Architecture Overview

Paper Digest is a FastAPI application that:
- Uses OAuth for user authentication (Google/GitHub)
- Stores papers and user data in SQLite (local) or PostgreSQL (production)
- Sends daily email digests via SendGrid
- Runs scheduled tasks using APScheduler

## Prerequisites

1. **OAuth Credentials** (choose at least one):
   - Google OAuth: [Get credentials](https://console.cloud.google.com)
   - GitHub OAuth: [Get credentials](https://github.com/settings/developers)

2. **SendGrid API Key**:
   - Sign up at [SendGrid](https://sendgrid.com)
   - Get your API key from account settings

3. **Groq API Key** (for users):
   - Each user provides their own Groq API key
   - Sign up at [Groq](https://console.groq.com)

## Local Development

### Option 1: Docker Compose (Recommended)

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env

# Start the app
docker-compose up
```

App will be available at `http://localhost:8000`

### Option 2: Direct Python

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with credentials
cp .env.example .env
nano .env

# Run the app
uvicorn src.paper_digest.ui.app:app --reload
```

## Production Deployment

### Option 1: Railway (Recommended - Easiest)

1. **Connect GitHub**:
   - Go to [Railway.app](https://railway.app)
   - Create new project from GitHub repository

2. **Configure Environment Variables**:
   - In Railway dashboard, go to Variables
   - Add all variables from `.env.example`:
     ```
     GOOGLE_CLIENT_ID
     GOOGLE_CLIENT_SECRET
     GITHUB_CLIENT_ID
     GITHUB_CLIENT_SECRET
     SENDGRID_API_KEY
     SECRET_KEY
     APP_URL=https://your-domain.railway.app
     ```

3. **Deploy**:
   - Railway will automatically detect Dockerfile
   - Push to main branch to trigger deployment

### Option 2: Render

1. **Connect GitHub**:
   - Go to [Render.com](https://render.com)
   - Create new Web Service from GitHub

2. **Configure**:
   - Runtime: Docker
   - Add environment variables (same as Railway)

3. **Deploy**:
   - Click Deploy

### Option 3: AWS/DigitalOcean/Self-Hosted

**Docker Deployment**:

```bash
# Build image
docker build -t paper-digest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_CLIENT_ID=... \
  -e GOOGLE_CLIENT_SECRET=... \
  -e SENDGRID_API_KEY=... \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  -v /data:/app/data \
  paper-digest
```

**Nginx Reverse Proxy** (optional):

```nginx
server {
    listen 80;
    server_name paperdigest.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## OAuth Setup

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project
3. Enable "Google+ API"
4. Create OAuth 2.0 credentials (Web Application)
5. Add authorized redirect URIs:
   - For local: `http://localhost:8000/auth/callback/google`
   - For production: `https://your-domain.com/auth/callback/google`
6. Copy Client ID and Client Secret to `.env`

### GitHub OAuth

1. Go to GitHub Settings → [Developer settings](https://github.com/settings/developers)
2. Create new OAuth App
3. Set Authorization callback URL:
   - For local: `http://localhost:8000/auth/callback/github`
   - For production: `https://your-domain.com/auth/callback/github`
4. Copy Client ID and Client Secret to `.env`

## Email Configuration

### SendGrid Setup

1. Create account at [SendGrid](https://sendgrid.com)
2. Verify sender email in Settings → Sender Authentication
3. Get API key from Settings → API Keys
4. Set `SENDGRID_FROM_EMAIL` to your verified sender email
5. Add `SENDGRID_API_KEY` to `.env`

## Database

### SQLite (Default - Local/Development)

- Automatically created at `data/papers.db`
- Works on all platforms
- Limited for high concurrency

### PostgreSQL (Recommended for Production)

Update `DATABASE_URL` in `src/paper_digest/storage/database.py`:

```python
DATABASE_URL = "postgresql://user:password@localhost/paper_digest"
```

Install PostgreSQL driver:

```bash
pip install psycopg2-binary
```

## Scheduled Email Sending

**Daily digest emails are sent at 9:00 AM UTC** by default.

To customize the send time, modify `src/paper_digest/scheduler/tasks.py`:

```python
scheduler_config = {
    "hour": 14,      # 2 PM UTC
    "minute": 30,    # 30 minutes
    "timezone": "UTC",
}
```

## Monitoring & Logging

- Check logs in deployment platform dashboard
- For local Docker: `docker-compose logs -f`
- For local Python: Logs appear in terminal

## Troubleshooting

### OAuth not working

- Verify redirect URIs match exactly
- Check CLIENT_ID and CLIENT_SECRET are correct
- Ensure `APP_URL` environment variable is set correctly

### Emails not sending

- Check SENDGRID_API_KEY is valid
- Verify sender email is authenticated in SendGrid
- Check user preferences (receive_emails = true)

### Database locked error (SQLite)

- Switch to PostgreSQL for production
- Increase timeout: `sqlite:///data/papers.db?timeout=20`

## Backup Strategy

### SQLite Backup

```bash
# Regular backups
cp data/papers.db data/papers.db.backup
```

### PostgreSQL Backup

```bash
pg_dump paper_digest > backup.sql
```

## Security Checklist

- [ ] Change `SECRET_KEY` to a random value in production
- [ ] Use HTTPS (automatic with Railway/Render)
- [ ] Enable OAuth only for trusted providers
- [ ] Encrypt API keys in database (TODO)
- [ ] Set up CORS properly if frontend is separate
- [ ] Regular backups of database

## Update & Maintenance

```bash
# Update dependencies
pip install -U -r requirements.txt

# Run tests
pytest tests/

# Format code
ruff format src/

# Check for issues
ruff check src/
```
