"""Initial schema — all Apotheon tables

Revision ID: 0001
Revises:
Create Date: 2026-05-09
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("slug", sa.String, nullable=False, unique=True),
        sa.Column("plan_tier", sa.String, nullable=False, server_default="starter"),
        sa.Column("max_concurrent_workflows", sa.Integer, nullable=False, server_default="3"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("org_id", sa.String, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column("role", sa.String, nullable=False, server_default="developer"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_users_org_id", "users", ["org_id"])

    # api_tokens
    op.create_table(
        "api_tokens",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("user_id", sa.String, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("token_hash", sa.String, nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # workflow_runs
    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("org_id", sa.String, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("plan_id", sa.String, nullable=True),
        sa.Column("objective", sa.Text, nullable=False),
        sa.Column("mode", sa.String, nullable=False, server_default="local"),
        sa.Column("status", sa.String, nullable=False, server_default="pending"),
        sa.Column("total_steps", sa.Integer, nullable=False, server_default="0"),
        sa.Column("completed_steps", sa.Integer, nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("created_by", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_workflow_runs_org_id", "workflow_runs", ["org_id"])
    op.create_index("ix_workflow_runs_status", "workflow_runs", ["status"])

    # workflow_steps
    op.create_table(
        "workflow_steps",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("run_id", sa.String, sa.ForeignKey("workflow_runs.id"), nullable=False),
        sa.Column("step_number", sa.Integer, nullable=False),
        sa.Column("skill_name", sa.String, nullable=False),
        sa.Column("status", sa.String, nullable=False, server_default="pending"),
        sa.Column("input_tokens", sa.Integer, nullable=True),
        sa.Column("output_tokens", sa.Integer, nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("hitl_required", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("output_text", sa.Text, nullable=True),
        sa.Column("error_detail", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("run_id", "step_number", name="uq_step_run_step"),
    )
    op.create_index("ix_workflow_steps_run_id", "workflow_steps", ["run_id"])

    # approvals
    op.create_table(
        "approvals",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("run_id", sa.String, sa.ForeignKey("workflow_runs.id"), nullable=False),
        sa.Column("step_number", sa.Integer, nullable=False),
        sa.Column("skill_name", sa.String, nullable=False),
        sa.Column("risk_level", sa.String, nullable=False, server_default="MEDIUM"),
        sa.Column("risk_score", sa.Float, nullable=True),
        sa.Column("status", sa.String, nullable=False, server_default="pending"),
        sa.Column("decided_by", sa.String, nullable=True),
        sa.Column("decision_comment", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("decided_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_approvals_run_id", "approvals", ["run_id"])
    op.create_index("ix_approvals_status", "approvals", ["status"])

    # audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("org_id", sa.String, nullable=False),
        sa.Column("run_id", sa.String, nullable=True),
        sa.Column("actor", sa.String, nullable=False),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("resource_type", sa.String, nullable=True),
        sa.Column("resource_id", sa.String, nullable=True),
        sa.Column("detail", sa.JSON, nullable=True),
        sa.Column("prev_hash", sa.String, nullable=True),
        sa.Column("entry_hash", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_log_org_id", "audit_log", ["org_id"])
    op.create_index("ix_audit_log_run_id", "audit_log", ["run_id"])

    # connector_registrations
    op.create_table(
        "connector_registrations",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("connector_name", sa.String, nullable=False, unique=True),
        sa.Column("connector_class", sa.String, nullable=False),
        sa.Column("version", sa.String, nullable=False),
        sa.Column("status", sa.String, nullable=False, server_default="registered"),
        sa.Column("config_encrypted", sa.Text, nullable=True),
        sa.Column("registered_at", sa.DateTime, server_default=sa.func.now()),
    )

    # oauth_tokens
    op.create_table(
        "oauth_tokens",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("connector_id", sa.String, sa.ForeignKey("connector_registrations.id"), nullable=False),
        sa.Column("access_token_hash", sa.String, nullable=False),
        sa.Column("refresh_token_hash", sa.String, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # policies
    op.create_table(
        "policies",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("org_id", sa.String, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("rule_expression", sa.Text, nullable=False),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("scope_pattern", sa.String, nullable=False, server_default="*"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("is_immutable", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("created_by", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_policies_org_id", "policies", ["org_id"])

    # policy_evaluations
    op.create_table(
        "policy_evaluations",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("policy_id", sa.String, sa.ForeignKey("policies.id"), nullable=False),
        sa.Column("run_id", sa.String, nullable=True),
        sa.Column("skill_name", sa.String, nullable=False),
        sa.Column("result", sa.String, nullable=False),
        sa.Column("detail", sa.JSON, nullable=True),
        sa.Column("evaluated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # token_usage
    op.create_table(
        "token_usage",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("org_id", sa.String, nullable=False),
        sa.Column("run_id", sa.String, nullable=True),
        sa.Column("skill_name", sa.String, nullable=False),
        sa.Column("model", sa.String, nullable=False),
        sa.Column("input_tokens", sa.Integer, nullable=False),
        sa.Column("output_tokens", sa.Integer, nullable=False),
        sa.Column("cost_usd", sa.Float, nullable=True),
        sa.Column("recorded_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_token_usage_org_id", "token_usage", ["org_id"])
    op.create_index("ix_token_usage_run_id", "token_usage", ["run_id"])

    # benchmark_baselines
    op.create_table(
        "benchmark_baselines",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("skill_name", sa.String, nullable=False),
        sa.Column("window_runs", sa.Integer, nullable=False),
        sa.Column("p50_latency_ms", sa.Float, nullable=True),
        sa.Column("p95_latency_ms", sa.Float, nullable=True),
        sa.Column("p99_latency_ms", sa.Float, nullable=True),
        sa.Column("avg_input_tokens", sa.Float, nullable=True),
        sa.Column("avg_output_tokens", sa.Float, nullable=True),
        sa.Column("success_rate", sa.Float, nullable=True),
        sa.Column("computed_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_benchmark_baselines_skill", "benchmark_baselines", ["skill_name"])


def downgrade() -> None:
    for table in [
        "benchmark_baselines", "token_usage", "policy_evaluations", "policies",
        "oauth_tokens", "connector_registrations", "audit_log", "approvals",
        "workflow_steps", "workflow_runs", "api_tokens", "users", "organizations",
    ]:
        op.drop_table(table)