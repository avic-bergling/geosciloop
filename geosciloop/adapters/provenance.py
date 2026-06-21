from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SECRET_KEYS = {
    "api_key",
    "access_key",
    "access_token",
    "authorization",
    "client_secret",
    "credential",
    "credentials",
    "key",
    "password",
    "private_key",
    "secret",
    "service_account_key",
    "token",
}


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "<redacted>" if key.lower() in SECRET_KEYS else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


@dataclass
class DataSourceProvenance:
    provider: str
    dataset: str
    source_type: str
    query: dict[str, Any]
    assets: list[dict[str, Any]] = field(default_factory=list)
    temporal_extent: dict[str, Any] = field(default_factory=dict)
    spatial_extent: dict[str, Any] = field(default_factory=dict)
    credentials_required: bool = False
    access_method: str = "optional_adapter"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "dataset": self.dataset,
            "source_type": self.source_type,
            "query": _redact(self.query),
            "assets": _redact(self.assets),
            "temporal_extent": _redact(self.temporal_extent),
            "spatial_extent": _redact(self.spatial_extent),
            "credentials_required": self.credentials_required,
            "access_method": self.access_method,
            "notes": list(self.notes),
        }


def build_real_data_manifest(records: list[DataSourceProvenance], run_mode: str) -> dict[str, Any]:
    return {
        "run_mode": run_mode,
        "record_count": len(records),
        "records": [record.to_dict() for record in records],
        "offline_test_safe": False,
        "notes": [
            "Real-data adapters are optional and are not used by offline CI tests.",
            "Credentials and API keys must be supplied by the user environment and are redacted from manifests.",
        ],
    }
