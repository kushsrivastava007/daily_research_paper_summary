# 📚 Paper Digest

An LLM-powered research paper discovery and learning platform. Get daily personalized summaries of the latest AI/ML/NLP research papers delivered to your inbox.

## ✨ Features

- 🔐 **OAuth Authentication** - Sign in with Google or GitHub
- 📧 **Daily Email Digests** - Automatic summaries of relevant papers
- 🤖 **AI-Powered Ranking** - Papers scored for relevance using Groq LLMs
- 📝 **Learning Notes** - Auto-generated summaries and learning guides
- 🎓 **Quiz Generation** - Test yourself with AI-generated quizzes
- ⚙️ **Customizable Settings** - Choose research categories, email times, preferences
- 🚀 **Production Ready** - Easy deployment to Railway, Render, or self-hosted

## 🎯 How It Works

```
1. Fetch    → Retrieves latest papers from arXiv (AI/ML/NLP categories)
2. Rank     → Scores papers 1-10 for relevance to AI engineering
3. Curate   → Selects top papers, skips duplicates from previous runs
4. Enrich   → Generates learning notes and quizzes using LLMs
5. Store    → Saves everything to SQLite
6. Notify   → Sends daily email digest to subscribed users
```

## 🚀 Quick Start

### Local Development (Docker)

```bash
# Clone and navigate
git clone <your-repo>
cd paper-digest

# Setup environment
cp .env.example .env
# Edit .env with your OAuth credentials and API keys

# Run with Docker
docker-compose up
```

Visit `http://localhost:8000`

### Local Development (Python)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env

# Run
uvicorn src.paper_digest.ui.app:app --reload
```

## 📋 Requirements

### API Keys (All Required)

1. **Groq API Key** - LLM for ranking and summarizing papers
   - Sign up: https://console.groq.com
   - Free tier available

2. **OAuth Credentials** (choose one or both):
   - **Google OAuth**: https://console.cloud.google.com
   - **GitHub OAuth**: https://github.com/settings/developers

3. **SendGrid API Key** - Email notifications
   - Sign up: https://sendgrid.com
   - Free tier available

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed setup instructions.

## 🌐 Deployment

### 🚄 Railway (Recommended - 5 minutes)

1. Push code to GitHub
2. Go to railway.app → Create project from GitHub
3. Add environment variables (from `.env.example`)
4. Deploy automatically on push

### 🎨 Render

Similar to Railway - connect GitHub, add env vars, deploy.

### 🏗️ Self-Hosted

Use provided `Dockerfile`:

```bash
docker build -t paper-digest .
docker run -d -p 8000:8000 \
  -e GOOGLE_CLIENT_ID=... \
  -e SENDGRID_API_KEY=... \
  -v /data:/app/data \
  paper-digest
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive guide.

## 📚 Architecture

### Technology Stack

- **Framework**: FastAPI + Uvicorn
- **LLM**: Groq API + LiteLLM + LangGraph
- **Data**: SQLAlchemy + SQLite (or PostgreSQL)
- **Auth**: OAuth2 (Authlib)
- **Email**: SendGrid
- **Scheduling**: APScheduler
- **Frontend**: HTML5 + Vanilla JS

### Database Schema

```
Users
├── id (UUID)
├── email
├── oauth_provider (google|github)
├── oauth_id
├── groq_api_key (encrypted)
├── preferences (JSON)
└── created_at

Papers
├── id (arXiv ID)
├── title
├── abstract
├── authors (JSON)
├── url
├── score (1-10)
├── notes (JSON)
├── quiz (JSON)
└── created_at
```

### API Endpoints

**Public:**
- `GET /` - Home page
- `GET /auth/login/{provider}` - OAuth login
- `GET /auth/callback/{provider}` - OAuth callback
- `GET /auth/logout` - Logout

**Authenticated:**
- `GET /api/user/me` - Get user profile
- `PUT /api/user/preferences` - Update preferences
- `PUT /api/user/api-key` - Set Groq API key
- `POST /api/run` - Trigger paper pipeline

## 🔧 Configuration

### Environment Variables

```bash
# OAuth - Google
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# OAuth - GitHub  
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# SendGrid
SENDGRID_API_KEY=...
SENDGRID_FROM_EMAIL=noreply@paperdigest.ai

# App
SECRET_KEY=... # Change in production!
APP_URL=http://localhost:8000
GROQ_API_KEY=... # Default for global runs
```

### Email Digest Timing

Emails sent daily at **9:00 AM UTC** by default.

Edit `src/paper_digest/scheduler/tasks.py` to customize.

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Check code style
ruff check src/

# Format code
ruff format src/
```

## 📖 User Guide

### 1. Sign Up
- Click "Login with Google/GitHub"
- Authorize the app

### 2. Configure Settings
- Go to Settings (⚙️)
- Add your Groq API key
- Choose research categories
- Enable email notifications

### 3. View Papers
- Dashboard shows latest papers
- Papers ranked by relevance (1-10)
- View learning notes and quizzes

### 4. Receive Emails
- Daily digest emails at scheduled time
- Top 10 papers with summaries
- Manage email frequency in settings

## 🐛 Troubleshooting

**OAuth not working?**
- Verify redirect URIs match exactly
- Check Client ID/Secret are correct

**Emails not sending?**
- Verify SendGrid API key
- Check sender email is authenticated in SendGrid
- Ensure `receive_emails` is enabled in user preferences

**Database locked?**
- Switch to PostgreSQL for production
- Or increase SQLite timeout in DATABASE_URL

See [DEPLOYMENT.md](DEPLOYMENT.md) for more troubleshooting.

## 📝 Project Structure

```
paper-digest/
├── src/paper_digest/
│   ├── ui/              # FastAPI app & templates
│   ├── graph/           # LangGraph pipeline
│   ├── agents/          # LLM agents (ranker, curator, etc)
│   ├── tools/           # External tools (arXiv fetcher)
│   ├── storage/         # Database layer
│   ├── auth/            # OAuth & authentication
│   ├── notifications/   # Email notifications
│   └── scheduler/       # Background tasks
├── tests/               # Unit & integration tests
├── Dockerfile           # Container config
├── docker-compose.yml   # Local dev setup
├── railway.toml         # Railway deployment config
└── DEPLOYMENT.md        # Deployment guide
```

## 🚀 Next Steps

- [ ] Encryption for stored API keys
- [ ] User roles & admin dashboard
- [ ] Paper recommendations based on history
- [ ] Slack/Discord notifications
- [ ] API rate limiting
- [ ] Analytics & usage tracking
- [ ] Multi-tenant support

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! See issues for ideas.

## ❓ FAQ

**Q: Is my API key safe?**  
A: Currently stored as plaintext in database. Production version should use encryption.

**Q: Can I use my own LLM?**  
A: Yes! Modify `src/paper_digest/llm.py` to use any provider.

**Q: How many emails will I receive?**  
A: One daily digest per day at your scheduled time.

**Q: What if I don't have a Groq key?**  
A: You can provide your own API key in settings, or deploy with a default key.

## 📞 Support

- Issues: GitHub Issues
- Email: support@paperdigest.ai (if deployed)

---

**Made with ❤️ for AI engineers who love research papers**
