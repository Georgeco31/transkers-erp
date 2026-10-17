"""Add updated_at to client payments.

Revision ID: 20261017_0002
Revises: 20260811_0001
"""
from alembic import op
import sqlalchemy as sa


revision = "20261017_0002"
down_revision = "20260811_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("client_payments") as batch_op:
        batch_op.add_column(
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )
    op.execute("UPDATE client_payments SET updated_at = created_at WHERE updated_at IS NULL")
    with op.batch_alter_table("client_payments") as batch_op:
        batch_op.alter_column("updated_at", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("client_payments") as batch_op:
        batch_op.drop_column("updated_at")
