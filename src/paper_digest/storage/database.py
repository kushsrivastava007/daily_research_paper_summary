# src/paper_digest/storage/database.py
import json
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Text,
    DateTime,
    Boolean,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from paper_digest.storage.crypto import encrypt_value, decrypt_value

# SQLite file lives in data/ folder at project root
DATABASE_URL = "sqlite:///data/papers.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


# ── ORM Model ────────────────────────────────────────────────

class PaperRecord(Base):
    """One row per paper ever seen by the pipeline."""
    __tablename__ = "papers"

    id          = Column(String, primary_key=True)   # arXiv ID
    title       = Column(String, nullable=False)
    abstract    = Column(Text,   nullable=False)
    authors     = Column(Text,   nullable=False)     # JSON string
    published   = Column(String, nullable=False)
    url         = Column(String, nullable=False)
    score       = Column(Float,  nullable=True)
    notes       = Column(Text,   nullable=True)      # JSON string
    quiz        = Column(Text,   nullable=True)      # JSON string
    seen        = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """User account for paper digest service."""
    __tablename__ = "users"

    id              = Column(String, primary_key=True)      # unique user ID
    email           = Column(String, unique=True, nullable=False)
    oauth_provider  = Column(String, nullable=False)        # 'google' or 'github'
    oauth_id        = Column(String, nullable=False)        # provider's user ID
    groq_api_key    = Column(Text, nullable=True)           # encrypted
    preferences     = Column(Text, nullable=True)           # JSON with user settings
    created_at      = Column(DateTime, default=datetime.utcnow)
    last_login      = Column(DateTime, nullable=True)
    is_active       = Column(Boolean, default=True)

    def to_dict(self):
        prefs = json.loads(self.preferences) if self.preferences else {}
        return {
            "id": self.id,
            "email": self.email,
            "oauth_provider": self.oauth_provider,
            "preferences": prefs,
        }


class TokenBlacklist(Base):
    """Tracks revoked/blacklisted tokens on logout."""
    __tablename__ = "token_blacklist"

    id              = Column(String, primary_key=True)      # unique ID
    token_hash      = Column(String, unique=True, nullable=False)  # hash of token
    user_id         = Column(String, nullable=False)        # user who logged out
    blacklisted_at  = Column(DateTime, default=datetime.utcnow)
    expires_at      = Column(DateTime, nullable=False)      # when token naturally expires


# ── Setup ─────────────────────────────────────────────────────

def init_db():
    """Create tables if they don't exist."""
    import os
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(engine)


# ── Write operations ──────────────────────────────────────────

def save_paper(paper) -> None:
    """Save or update a paper in the database."""
    with SessionLocal() as session:
        record = session.get(PaperRecord, paper.id)

        if record:
            # update existing record
            record.score = paper.score
            record.notes = paper.notes
            record.quiz  = paper.quiz
        else:
            # insert new record
            record = PaperRecord(
                id        = paper.id,
                title     = paper.title,
                abstract  = paper.abstract,
                authors   = json.dumps(paper.authors),
                published = paper.published,
                url       = paper.url,
                score     = paper.score,
                notes     = paper.notes,
                quiz      = paper.quiz,
            )
            session.add(record)

        session.commit()


def save_papers(papers: list) -> None:
    """Save multiple papers."""
    for paper in papers:
        save_paper(paper)


def mark_as_seen(paper_ids: list[str]) -> None:
    """Mark papers as seen so curator skips them tomorrow."""
    with SessionLocal() as session:
        for pid in paper_ids:
            record = session.get(PaperRecord, pid)
            if record:
                record.seen = True
        session.commit()


# ── Read operations ───────────────────────────────────────────

def get_seen_ids() -> set[str]:
    """Return all paper IDs already seen — curator uses this."""
    with SessionLocal() as session:
        records = session.query(PaperRecord.id).filter_by(seen=True).all()
        return {r.id for r in records}


def get_all_papers() -> list[PaperRecord]:
    """Return all papers — UI uses this."""
    with SessionLocal() as session:
        return session.query(PaperRecord).order_by(
            PaperRecord.created_at.desc()
        ).all()


def get_paper(paper_id: str) -> PaperRecord | None:
    """Return a single paper by ID — UI uses this."""
    with SessionLocal() as session:
        return session.get(PaperRecord, paper_id)


# ── User Management ──────────────────────────────────────────

def create_or_update_user(
    email: str,
    oauth_provider: str,
    oauth_id: str,
    groq_api_key: str = None,
) -> User:
    """Create new user or update existing one with OAuth info."""
    encrypted_key = encrypt_value(groq_api_key) if groq_api_key else groq_api_key
    with SessionLocal() as session:
        user = session.query(User).filter_by(email=email).first()

        if user:
            user.last_login = datetime.utcnow()
            if encrypted_key:
                user.groq_api_key = encrypted_key
        else:
            import uuid
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                oauth_provider=oauth_provider,
                oauth_id=oauth_id,
                groq_api_key=encrypted_key,
                preferences=json.dumps({
                    "receive_emails": True,
                    "categories": ["cs.AI", "cs.LG", "cs.CL"],
                }),
            )
            session.add(user)

        session.commit()
        return user


def get_user(user_id: str) -> User | None:
    """Retrieve user by ID."""
    with SessionLocal() as session:
        return session.get(User, user_id)


def get_user_by_email(email: str) -> User | None:
    """Retrieve user by email."""
    with SessionLocal() as session:
        return session.query(User).filter_by(email=email).first()


def update_user_preferences(user_id: str, preferences: dict) -> User:
    """Update user preferences (categories, receive_emails, etc.)."""
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user:
            user.preferences = json.dumps(preferences)
            session.commit()
        return user


def update_user_api_key(user_id: str, groq_api_key: str) -> User:
    """Update user's Groq API key (stored encrypted)."""
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user:
            user.groq_api_key = encrypt_value(groq_api_key)
            session.commit()
        return user


def get_user_groq_api_key(user_id: str) -> str | None:
    """Retrieve a user's Groq API key, decrypted."""
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user and user.groq_api_key:
            return decrypt_value(user.groq_api_key)
        return None


def get_all_active_users() -> list[User]:
    """Get all active users for sending notifications."""
    with SessionLocal() as session:
        return session.query(User).filter_by(is_active=True).all()


# ── Token Blacklist Management ───────────────────────────

def add_token_to_blacklist(token_hash: str, user_id: str, expires_at: datetime) -> None:
    """Add a token to the blacklist on logout."""
    import uuid
    with SessionLocal() as session:
        blacklist_entry = TokenBlacklist(
            id=str(uuid.uuid4()),
            token_hash=token_hash,
            user_id=user_id,
            expires_at=expires_at,
        )
        session.add(blacklist_entry)
        session.commit()


def is_token_blacklisted(token_hash: str) -> bool:
    """Check if a token has been blacklisted."""
    with SessionLocal() as session:
        # Also clean up expired entries
        session.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at < datetime.utcnow()
        ).delete()
        session.commit()
        
        entry = session.query(TokenBlacklist).filter_by(
            token_hash=token_hash
        ).first()
        return entry is not None
