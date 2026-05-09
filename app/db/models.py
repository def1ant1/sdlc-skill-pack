"""
app/db/models.py — SQLAlchemy ORM models for Apotheon.

Covers: workflow runs/steps, approvals, audit logs, connectors,
users, organizations, policies, and token usage.

Compatible with both SQLite (dev) and Postgres (prod).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, JSON, Enum as SAEnum,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Organization / User / Workspace
# ---------------------------------------------------------------------------

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    plan_tier = Column(String(50), default="free")       # free | pro | enterprise
    max_concurrent_workflows = Column(Integer, default=3)
    max_workflows_per_hour = Column(Integer, default=60)
    max_memory_gb = Column(Float, default=1.0)
    max_connector_count = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    users = relationship("User", back_populates="org", cascade="all, delete-orphan")
    workflow_runs = relationship("WorkflowRun", back_populates="org")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255))
    role = Column(String(50), default="developer")       # admin | operator | developer | viewer
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    org = relationship("Organization", back_populates="users")


class ApiToken(Base):
    __tablename__ = "api_tokens"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    last_used_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=_utcnow)


# ---------------------------------------------------------------------------
# Workflow Runs & Steps
# ---------------------------------------------------------------------------

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(String(36), primary_key=True)            # matches run_id (RUN-xxx)
    org_id = Column(String(36), ForeignKey("organizations.id"))
    plan_id = Column(String(100))
    objective = Column(Text, nullable=False)
    mode = Column(String(20), default="local")           # local | temporal | dry_run
    status = Column(String(30), default="queued")        # queued | running | completed | failed | paused_for_hitl | dry_run | cancelled
    total_steps = Column(Integer, default=0)
    completed_steps = Column(Integer, default=0)
    paused_at_step = Column(Integer)
    failed_at_step = Column(Integer)
    context_packet = Column(JSON)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    org = relationship("Organization", back_populates="workflow_runs")
    steps = relationship("WorkflowStep", back_populates="run", cascade="all, delete-orphan", order_by="WorkflowStep.step_number")
    approvals = relationship("Approval", back_populates="run")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(String(36), primary_key=True, default=_uuid)
    run_id = Column(String(36), ForeignKey("workflow_runs.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    skill_name = Column(String(100), nullable=False)
    phase = Column(String(100))
    status = Column(String(30), default="pending")       # pending | running | completed | failed | error | dry_run | pending_hitl
    output_preview = Column(Text)                        # first 500 chars
    error = Column(Text)
    duration_ms = Column(Integer, default=0)
    hitl_required = Column(Boolean, default=False)
    hitl_reason = Column(Text)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    run = relationship("WorkflowRun", back_populates="steps")


# ---------------------------------------------------------------------------
# HITL Approvals
# ---------------------------------------------------------------------------

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=_uuid)
    run_id = Column(String(36), ForeignKey("workflow_runs.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    skill_name = Column(String(100), nullable=False)
    risk_level = Column(String(10), default="L3")        # L1 | L2 | L3
    risk_score = Column(Integer, default=0)              # 0-100
    hitl_reason = Column(Text)
    status = Column(String(20), default="pending")       # pending | approved | rejected | escalated | expired
    decided_by = Column(String(36), ForeignKey("users.id"))
    decision_reason = Column(Text)
    requested_at = Column(DateTime(timezone=True), default=_utcnow)
    decided_at = Column(DateTime(timezone=True))
    sla_deadline = Column(DateTime(timezone=True))

    run = relationship("WorkflowRun", back_populates="approvals")


# ---------------------------------------------------------------------------
# Audit Log (append-only)
# ---------------------------------------------------------------------------

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=_uuid)
    org_id = Column(String(36))
    run_id = Column(String(36))
    actor = Column(String(200), nullable=False)           # "system:<skill>" | "human:<user_id>"
    action = Column(String(50), nullable=False)           # executed | approved | rejected | accessed | modified
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    outcome = Column(String(20))                          # success | failure | pending
    risk_level = Column(String(10))
    entry_metadata = Column(JSON)
    prev_hash = Column(String(64))
    entry_hash = Column(String(64))
    occurred_at = Column(DateTime(timezone=True), default=_utcnow)


# ---------------------------------------------------------------------------
# Connectors
# ---------------------------------------------------------------------------

class ConnectorRegistration(Base):
    __tablename__ = "connector_registrations"

    id = Column(String(36), primary_key=True, default=_uuid)
    org_id = Column(String(36))
    connector_name = Column(String(100), nullable=False)
    connector_class = Column(String(200), nullable=False)
    version = Column(String(20), default="0.1.0")
    status = Column(String(20), default="registered")    # registered | validated | active | degraded | inactive | retired
    is_current = Column(Boolean, default=True)
    config = Column(JSON)
    last_health_check_at = Column(DateTime(timezone=True))
    last_health_status = Column(String(20))
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(String(36), primary_key=True, default=_uuid)
    connector_id = Column(String(36), ForeignKey("connector_registrations.id"), nullable=False)
    org_id = Column(String(36))
    access_token_hash = Column(String(255))              # never store plaintext
    token_type = Column(String(50), default="Bearer")
    scope = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    refresh_token_hash = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


# ---------------------------------------------------------------------------
# Governance — Policies & Risk Events
# ---------------------------------------------------------------------------

class Policy(Base):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=_uuid)
    org_id = Column(String(36))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    rule_expression = Column(Text, nullable=False)       # Python predicate string
    action = Column(String(30), nullable=False)          # BLOCK | WARN | REQUIRE_APPROVAL
    scope_pattern = Column(String(200), default="*")     # skill glob pattern
    is_active = Column(Boolean, default=True)
    is_immutable = Column(Boolean, default=False)        # hardcoded invariants
    created_by = Column(String(36))
    approved_by = Column(String(36))
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class PolicyEvaluation(Base):
    __tablename__ = "policy_evaluations"

    id = Column(String(36), primary_key=True, default=_uuid)
    policy_id = Column(String(36), ForeignKey("policies.id"), nullable=False)
    run_id = Column(String(36))
    skill_name = Column(String(100))
    result = Column(String(20))                          # allow | block | warn | require_approval
    reason = Column(Text)
    evaluated_at = Column(DateTime(timezone=True), default=_utcnow)


# ---------------------------------------------------------------------------
# Observability — Token Usage & Benchmarks
# ---------------------------------------------------------------------------

class TokenUsage(Base):
    __tablename__ = "token_usage"

    id = Column(String(36), primary_key=True, default=_uuid)
    org_id = Column(String(36))
    run_id = Column(String(36))
    step_id = Column(String(36))
    skill_name = Column(String(100))
    model = Column(String(100))
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    recorded_at = Column(DateTime(timezone=True), default=_utcnow)


class BenchmarkBaseline(Base):
    __tablename__ = "benchmark_baselines"

    id = Column(String(36), primary_key=True, default=_uuid)
    skill_name = Column(String(100), nullable=False, index=True)
    window_runs = Column(Integer, default=30)
    p50_latency_ms = Column(Float)
    p95_latency_ms = Column(Float)
    p99_latency_ms = Column(Float)
    avg_input_tokens = Column(Float)
    avg_output_tokens = Column(Float)
    success_rate = Column(Float)
    computed_at = Column(DateTime(timezone=True), default=_utcnow)