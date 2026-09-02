import os
import json
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Boolean, Text, select, UniqueConstraint

logger = logging.getLogger('safelane.platform')

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./safelane.db")

# Auto-normalize: Railway injects postgresql:// but SQLAlchemy needs postgresql+asyncpg://
# Without this, SQLAlchemy defaults to psycopg2 which is not installed.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    logger.info("Auto-converted DATABASE_URL: postgres:// → postgresql+asyncpg://")
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info("Auto-converted DATABASE_URL: postgresql:// → postgresql+asyncpg://")

engine_kwargs = {}
if DATABASE_URL.startswith("postgresql+asyncpg"):
    if os.environ.get("DB_SSL_INSECURE") == "true":
        logger.warning("DB_SSL_INSECURE is set to true. Bypassing SSL verification. DO NOT USE IN PRODUCTION.")
        import ssl
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        engine_kwargs["connect_args"] = {"ssl": ssl_ctx}
    else:
        # Proper SSL context
        import ssl
        ssl_ctx = ssl.create_default_context()
        engine_kwargs["connect_args"] = {"ssl": ssl_ctx}

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass


# ── User ──

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    github_username: Mapped[str] = mapped_column(String, nullable=False)
    github_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    encrypted_token: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Registration (connected repository) ──

class Registration(Base):
    __tablename__ = "registrations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    owner: Mapped[str] = mapped_column(String, nullable=False)
    repo: Mapped[str] = mapped_column(String, nullable=False)
    encrypted_token: Mapped[str] = mapped_column(String, nullable=False)
    orchestrator_url: Mapped[str] = mapped_column(String, nullable=True)
    azure_search_endpoint: Mapped[str] = mapped_column(String, nullable=True)
    azure_search_key: Mapped[str] = mapped_column(String, nullable=True)
    azure_tenant_id: Mapped[str] = mapped_column(String, nullable=True)
    azure_workspace_id: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    sync_error: Mapped[str] = mapped_column(String, nullable=True)
    rollback_strategy: Mapped[str] = mapped_column(String, nullable=False, default="branch")
    custom_holiday_dates: Mapped[str] = mapped_column(Text, nullable=True)
    deploy_window_start_utc: Mapped[int] = mapped_column(Integer, nullable=True)
    deploy_window_end_utc: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Analysis Record ──

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"
    __table_args__ = (
        UniqueConstraint('registration_id', 'pr_number', 'head_sha', name='uq_analysis_reg_pr_sha'),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    registration_id: Mapped[int] = mapped_column(Integer, nullable=True)
    pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    head_sha: Mapped[str] = mapped_column(String, nullable=True)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False)
    decision: Mapped[str] = mapped_column(String, nullable=False)
    risk_brief: Mapped[str] = mapped_column(Text, nullable=True)
    rollback_playbook: Mapped[str] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=True)
    security_findings_json: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ── Pull Request Record ──

class PullRequestRecord(Base):
    __tablename__ = "pull_request_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    registration_id: Mapped[int] = mapped_column(Integer, nullable=False)
    pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=True)
    state: Mapped[str] = mapped_column(String, nullable=True)
    head_sha: Mapped[str] = mapped_column(String, nullable=True)
    author: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Activity Event ──

class ActivityEvent(Base):
    __tablename__ = "activity_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    registration_id: Mapped[int] = mapped_column(Integer, nullable=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ── Database initialization ──

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── User CRUD ──

async def upsert_user(github_id: int, github_username: str, encrypted_token: str | None = None) -> User:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.github_id == github_id))
        user = result.scalars().first()
        if user:
            user.github_username = github_username
            if encrypted_token:
                user.encrypted_token = encrypted_token
            user.updated_at = datetime.utcnow()
        else:
            user = User(
                github_id=github_id,
                github_username=github_username,
                encrypted_token=encrypted_token,
            )
            session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def get_user_by_github_id(github_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.github_id == github_id))
        return result.scalars().first()


# ── Registration CRUD ──

async def get_registration(owner: str, repo: str) -> Registration | None:
    async with async_session() as session:
        result = await session.execute(
            select(Registration).where(
                Registration.owner == owner,
                Registration.repo == repo,
                Registration.is_active == True,
            )
        )
        return result.scalars().first()


async def create_registration(**kwargs) -> Registration:
    async with async_session() as session:
        reg = Registration(**kwargs)
        session.add(reg)
        await session.commit()
        await session.refresh(reg)
        return reg


async def list_registrations(user_id: int) -> list[Registration]:
    async with async_session() as session:
        result = await session.execute(select(Registration).where(Registration.user_id == user_id))
        return list(result.scalars().all())


async def get_registration_by_id(reg_id: int) -> Registration | None:
    async with async_session() as session:
        result = await session.execute(select(Registration).where(Registration.id == reg_id))
        return result.scalars().first()


async def update_registration_sync(reg_id: int, error: str | None = None):
    async with async_session() as session:
        result = await session.execute(select(Registration).where(Registration.id == reg_id))
        reg = result.scalars().first()
        if reg:
            reg.last_synced_at = datetime.utcnow()
            reg.sync_error = error
            await session.commit()


async def set_registration_inactive(reg_id: int):
    """Mark a registration as inactive (e.g. when GitHub returns 404)."""
    async with async_session() as session:
        result = await session.execute(select(Registration).where(Registration.id == reg_id))
        reg = result.scalars().first()
        if reg:
            reg.is_active = False
            await session.commit()


# ── Analysis Record CRUD ──

async def save_analysis_record(
    registration_id: int | None,
    pr_number: int,
    head_sha: str | None,
    report,
) -> AnalysisRecord:
    async with async_session() as session:
        record = AnalysisRecord(
            registration_id=registration_id,
            pr_number=pr_number,
            head_sha=head_sha,
            confidence_score=report.confidence_score,
            decision=report.decision,
            risk_brief=report.risk_brief,
            rollback_playbook=report.rollback_playbook,
            evidence_json=json.dumps([er.model_dump() for er in report.evidence_results]),
            security_findings_json=json.dumps([sf.model_dump() for sf in report.security_findings]),
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record


async def get_analysis_records(registration_id: int, limit: int = 20) -> list[AnalysisRecord]:
    async with async_session() as session:
        result = await session.execute(
            select(AnalysisRecord)
            .where(AnalysisRecord.registration_id == registration_id)
            .order_by(AnalysisRecord.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


async def get_analysis_by_pr(registration_id: int, pr_number: int) -> AnalysisRecord | None:
    async with async_session() as session:
        result = await session.execute(
            select(AnalysisRecord)
            .where(
                AnalysisRecord.registration_id == registration_id,
                AnalysisRecord.pr_number == pr_number,
            )
            .order_by(AnalysisRecord.created_at.desc())
        )
        return result.scalars().first()


async def get_analysis_by_sha(registration_id: int, pr_number: int, head_sha: str) -> AnalysisRecord | None:
    """Check if an analysis already exists for this exact (registration, PR, SHA) triplet.
    Used to skip re-analysis of unchanged PRs/commits during sync."""
    if not head_sha:
        return None
    async with async_session() as session:
        result = await session.execute(
            select(AnalysisRecord)
            .where(
                AnalysisRecord.registration_id == registration_id,
                AnalysisRecord.pr_number == pr_number,
                AnalysisRecord.head_sha == head_sha,
            )
        )
        return result.scalars().first()


# ── Pull Request Record CRUD ──

async def save_pr_record(**kwargs) -> PullRequestRecord:
    async with async_session() as session:
        record = PullRequestRecord(**kwargs)
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record


async def get_pr_records(registration_id: int, limit: int = 20) -> list[PullRequestRecord]:
    async with async_session() as session:
        result = await session.execute(
            select(PullRequestRecord)
            .where(PullRequestRecord.registration_id == registration_id)
            .order_by(PullRequestRecord.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


# ── Activity Event CRUD ──

async def save_activity_event(registration_id: int | None, event_type: str, payload: dict | None = None) -> ActivityEvent:
    async with async_session() as session:
        event = ActivityEvent(
            registration_id=registration_id,
            event_type=event_type,
            payload_json=json.dumps(payload) if payload else None,
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event
