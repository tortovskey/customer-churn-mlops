"""initial schema

Revision ID: 20260510_0001
Revises:
Create Date: 2026-05-10 20:40:00
"""
from alembic import op
import sqlalchemy as sa

revision = "20260510_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("tenure_months", sa.Integer(), nullable=False),
        sa.Column("monthly_payment", sa.Float(), nullable=False),
        sa.Column("support_requests", sa.Integer(), nullable=False),
        sa.Column("tariff_type", sa.String(length=50), nullable=False),
        sa.Column("last_month_activity", sa.Float(), nullable=False),
        sa.Column("has_debt", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clients_id"), "clients", ["id"], unique=False)
    op.create_index(op.f("ix_clients_full_name"), "clients", ["full_name"], unique=False)

    op.create_table(
        "model_registry",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("model_version", sa.String(length=120), nullable=False),
        sa.Column("model_path", sa.String(length=500), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_version"),
    )
    op.create_index(op.f("ix_model_registry_id"), "model_registry", ["id"], unique=False)
    op.create_index(op.f("ix_model_registry_model_name"), "model_registry", ["model_name"], unique=False)

    op.create_table(
        "ml_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ml_logs_id"), "ml_logs", ["id"], unique=False)
    op.create_index(op.f("ix_ml_logs_event_type"), "ml_logs", ["event_type"], unique=False)

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("model_version", sa.String(length=120), nullable=False),
        sa.Column("prediction_value", sa.Float(), nullable=False),
        sa.Column("prediction_label", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_predictions_id"), "predictions", ["id"], unique=False)
    op.create_index(op.f("ix_predictions_client_id"), "predictions", ["client_id"], unique=False)
    op.create_index(op.f("ix_predictions_model_version"), "predictions", ["model_version"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_predictions_model_version"), table_name="predictions")
    op.drop_index(op.f("ix_predictions_client_id"), table_name="predictions")
    op.drop_index(op.f("ix_predictions_id"), table_name="predictions")
    op.drop_table("predictions")

    op.drop_index(op.f("ix_ml_logs_event_type"), table_name="ml_logs")
    op.drop_index(op.f("ix_ml_logs_id"), table_name="ml_logs")
    op.drop_table("ml_logs")

    op.drop_index(op.f("ix_model_registry_model_name"), table_name="model_registry")
    op.drop_index(op.f("ix_model_registry_id"), table_name="model_registry")
    op.drop_table("model_registry")

    op.drop_index(op.f("ix_clients_full_name"), table_name="clients")
    op.drop_index(op.f("ix_clients_id"), table_name="clients")
    op.drop_table("clients")

