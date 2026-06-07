# 🚀 Paper Digest - Quick Start Guide

Get Paper Digest running in 5 minutes!

## Option 1: Railway (Recommended - Easiest)

### Prerequisites
- GitHub account
- Groq API key (get from https://console.groq.com - free)
- SendGrid API key (get from https://sendgrid.com - free)
- OAuth credentials (Google or GitHub)

### Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Railway Account**
   - Go to https://railway.app
   - Sign in with GitHub
   - Create new project from GitHub repo

3. **Add Environment Variables** (in Railway dashboard)
   ```
   GOOGLE_CLIENT_ID=your-google-id
   GOOGLE_CLIENT_SECRET=your-google-secret
   GOOGLE_REDIRECT_URI=https://your-app.railway.app/auth/callback/google
   
   GITHUB_CLIENT_ID=your-github-id
   GITHUB_CLIENT_SECRET=your-github-secret
   GITHUB_REDIRECT_URI=https://your-app.railway.app/auth/callback/github
   
   SENDGRID_API_KEY=SG.xxxxx
   SENDGRID_FROM_EMAIL=noreply@your-domain.com
   
   SECRET_KEY=<run: openssl rand -hex 32>
   APP_URL=https://your-app.railway.app
   ```

4. **Deploy**
   - Click Deploy button
   - Wait 2-3 minutes
   - Your app is live!

## Option 2: Local Docker

```bash
# Clone repo
git clone <your-repo>
cd paper-digest

# Setup
cp .env.example .env
# Edit .env with your keys

# Run
docker-compose up

# Visit http://localhost:8000
```

## OAuth Setup (5 minutes)

### Google OAuth
1. Go to https://console.cloud.google.com
2. Create new project
3. Enable "Google+ API"
4. Create OAuth 2.0 credentials (type: Web)
5. Add authorized redirect URLs:
   - Local: `http://localhost:8000/auth/callback/google`
   - Production: `https://your-app.com/auth/callback/google`
6. Copy Client ID and Secret to `.env`

### GitHub OAuth
1. Go to https://github.com/settings/developers
2. New OAuth App
3. Application name: "Paper Digest"
4. Homepage URL: `http://localhost:8000` (or your domain)
5. Authorization callback: `http://localhost:8000/auth/callback/github`
6. Copy Client ID and Secret to `.env`

## User Flow

1. **User signs up** → OAuth with Google/GitHub
2. **Welcome email sent** → User receives welcome notification
3. **User goes to Settings** → Adds Groq API key
4. **Scheduler runs daily** → Fetches papers, generates notes, sends email
5. **User receives digest** → Top papers in inbox at 9 AM UTC

## Next Steps

- [ ] Configure OAuth credentials
- [ ] Get SendGrid API key
- [ ] Deploy to Railway/Render
- [ ] Test by manually triggering `/api/run` endpoint
- [ ] Verify email delivery

## Troubleshooting

**OAuth not working?**
```
Check:
- Redirect URLs match exactly (including http/https)
- Client ID/Secret are correct
- APP_URL environment variable is set
```

**Emails not sending?**
```
Check:
- SENDGRID_API_KEY is valid
- Sender email is authenticated in SendGrid
- User has receive_emails = true in preferences
```

**Database issues?**
```
Delete data/papers.db and let it recreate:
rm data/papers.db
```

## Need Help?

- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
- Check [README.md](README.md) for full documentation
- Review logs in your deployment platform

## Architecture at a Glance

```
User → OAuth Login → Database
                   → Settings (API key, categories)
                   → Scheduler (9 AM UTC daily)
                   → Fetch Papers → Rank → Curate → Enrich
                   → Send Email → Inbox ✓
```

## Features

✅ OAuth authentication (Google/GitHub)  
✅ User-provided API keys  
✅ Daily automated email digests  
✅ Paper ranking & analysis  
✅ Learning notes generation  
✅ Quiz generation  
✅ Production-ready deployment  
✅ Multi-user support  

## Deployment Checklist

- [ ] GitHub repo ready
- [ ] OAuth credentials obtained
- [ ] SendGrid API key obtained
- [ ] Railway/Render account created
- [ ] Environment variables configured
- [ ] Domain/custom URL configured (optional)
- [ ] SSL certificate configured (auto on Railway/Render)
- [ ] First user signup test completed
- [ ] Email delivery test completed
- [ ] Scheduled job test completed

---

**You're all set! Deploy and start discovering papers 🚀**
