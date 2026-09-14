"""Local synthetic identity model; explicitly unsuitable for production auth."""

from dataclasses import dataclass
from typing import Literal

Role = Literal["owner", "architect", "app_owner", "reviewer"]


@dataclass(frozen=True)
class Identity:
    id: str
    tenant_id: str
    role: Role
    asset_prefix: str | None = None


ROLES: tuple[Role, ...] = ("owner", "architect", "app_owner", "reviewer")
IDENTITIES: dict[str, Identity] = {
    f"demo-{tenant}-{role}": Identity(
        id=f"demo-{tenant}-{role}",
        tenant_id=tenant,
        role=role,
        asset_prefix=f"{tenant}-asset-00" if role == "app_owner" else None,
    )
    for tenant in ("northstar", "aster", "harbor")
    for role in ROLES
}


def allowed(identity: Identity | None, tenant_id: str, action: str, asset_id: str | None = None) -> bool:
    if identity is None or identity.tenant_id != tenant_id:
        return False
    if identity.asset_prefix and asset_id and not asset_id.startswith(identity.asset_prefix):
        return False
    if action in {"read", "export"}:
        return True
    if action == "import":
        return identity.role in {"owner", "architect"}
    if action in {"decide", "wave"}:
        return identity.role in {"owner", "architect"}
    return False
