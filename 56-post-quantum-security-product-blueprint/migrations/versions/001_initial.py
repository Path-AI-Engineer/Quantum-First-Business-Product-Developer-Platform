"""Initial tenant-keyed synthetic metadata store.

Revision ID: 001_initial
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evidence",
        sa.Column("id", sa.String(120), primary_key=True),
        sa.Column("tenant_id", sa.String(32), nullable=False),
        sa.Column("asset_id", sa.String(120), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_evidence_tenant_id", "evidence", ["tenant_id"])
    op.create_index("ix_evidence_asset_id", "evidence", ["asset_id"])
    for name, width in (("decisions", 120), ("waves", 120), ("reports", 150)):
        op.create_table(
            name,
            sa.Column("id", sa.String(width), primary_key=True),
            sa.Column("tenant_id", sa.String(32), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=False),
        )
        op.create_index(f"ix_{name}_tenant_id", name, ["tenant_id"])
    op.create_table(
        "audit_events",
        sa.Column("sequence", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.String(32), nullable=False),
        sa.Column("actor", sa.String(120), nullable=False),
        sa.Column("operation", sa.String(80), nullable=False),
        sa.Column("object_id", sa.String(150), nullable=False),
        sa.Column("previous_hash", sa.String(64), nullable=False),
        sa.Column("hash", sa.String(64), nullable=False),
    )
    op.create_index("ix_audit_events_tenant_id", "audit_events", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_events_tenant_id", table_name="audit_events")
    op.drop_table("audit_events")
    for name in ("reports", "waves", "decisions"):
        op.drop_index(f"ix_{name}_tenant_id", table_name=name)
        op.drop_table(name)
    op.drop_index("ix_evidence_asset_id", table_name="evidence")
    op.drop_index("ix_evidence_tenant_id", table_name="evidence")
    op.drop_table("evidence")
