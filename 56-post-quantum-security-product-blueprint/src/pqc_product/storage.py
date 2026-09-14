"""Tenant-keyed persistence for metadata only; raw uploads are discarded."""

from dataclasses import asdict
from typing import Any

from sqlalchemy import JSON, Column, Engine, Integer, MetaData, String, Table, create_engine, insert, select, update
from sqlalchemy.pool import StaticPool

from pqc_product.domain import Evidence

metadata = MetaData()

evidence_table = Table(
    "evidence",
    metadata,
    Column("id", String(120), primary_key=True),
    Column("tenant_id", String(32), nullable=False, index=True),
    Column("asset_id", String(120), nullable=False, index=True),
    Column("payload", JSON, nullable=False),
)
decision_table = Table(
    "decisions",
    metadata,
    Column("id", String(120), primary_key=True),
    Column("tenant_id", String(32), nullable=False, index=True),
    Column("payload", JSON, nullable=False),
)
wave_table = Table(
    "waves",
    metadata,
    Column("id", String(120), primary_key=True),
    Column("tenant_id", String(32), nullable=False, index=True),
    Column("payload", JSON, nullable=False),
)
report_table = Table(
    "reports",
    metadata,
    Column("id", String(150), primary_key=True),
    Column("tenant_id", String(32), nullable=False, index=True),
    Column("payload", JSON, nullable=False),
)
audit_table = Table(
    "audit_events",
    metadata,
    Column("sequence", Integer, primary_key=True, autoincrement=True),
    Column("tenant_id", String(32), nullable=False, index=True),
    Column("actor", String(120), nullable=False),
    Column("operation", String(80), nullable=False),
    Column("object_id", String(150), nullable=False),
    Column("previous_hash", String(64), nullable=False),
    Column("hash", String(64), nullable=False),
)


class DatabaseStore:
    """Small SQLAlchemy repository. Tests use SQLite; Compose uses PostgreSQL."""

    def __init__(self, url: str, *, initialize: bool = False) -> None:
        if url.startswith("sqlite:///:memory:"):
            self.engine: Engine = create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
        else:
            self.engine = create_engine(url, pool_pre_ping=True)
        if initialize:
            metadata.create_all(self.engine)

    def load_evidence(self) -> list[Evidence]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(evidence_table.c.payload).order_by(evidence_table.c.id)).scalars().all()
        return [Evidence(**row) for row in rows]

    def save_evidence(self, items: tuple[Evidence, ...]) -> tuple[Evidence, ...]:
        accepted: list[Evidence] = []
        with self.engine.begin() as conn:
            for item in items:
                existing = conn.execute(
                    select(evidence_table.c.tenant_id).where(evidence_table.c.id == item.id)
                ).scalar_one_or_none()
                if existing is None:
                    conn.execute(
                        insert(evidence_table).values(
                            id=item.id, tenant_id=item.tenant_id, asset_id=item.asset_id, payload=asdict(item)
                        )
                    )
                    accepted.append(item)
                elif existing != item.tenant_id:
                    raise ValueError("cross-tenant evidence ID collision")
        return tuple(accepted)

    def load_documents(self, table: Table) -> dict[str, dict[str, Any]]:
        if table not in (decision_table, wave_table, report_table):
            raise ValueError("unsupported document table")
        with self.engine.connect() as conn:
            rows = conn.execute(select(table.c.id, table.c.payload)).mappings().all()
        return {str(row["id"]): dict(row["payload"]) for row in rows}

    def save_document(self, table: Table, object_id: str, tenant_id: str, payload: dict[str, Any]) -> None:
        if table not in (decision_table, wave_table, report_table):
            raise ValueError("unsupported document table")
        with self.engine.begin() as conn:
            existing_tenant = conn.execute(
                select(table.c.tenant_id).where(table.c.id == object_id)
            ).scalar_one_or_none()
            if existing_tenant is None:
                conn.execute(insert(table).values(id=object_id, tenant_id=tenant_id, payload=payload))
            else:
                if existing_tenant != tenant_id:
                    raise ValueError("cross-tenant document ID collision")
                conn.execute(
                    update(table).where(table.c.id == object_id, table.c.tenant_id == tenant_id).values(payload=payload)
                )

    def load_audit(self) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(audit_table).order_by(audit_table.c.sequence)).mappings().all()
        return [dict(row) for row in rows]

    def save_audit(self, event: dict[str, Any]) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                insert(audit_table).values(
                    tenant_id=event["tenant_id"],
                    actor=event["actor"],
                    operation=event["operation"],
                    object_id=event["object_id"],
                    previous_hash=event["previous_hash"],
                    hash=event["hash"],
                )
            )
