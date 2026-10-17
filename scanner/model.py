from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class FieldStatus(str, Enum):
    DETECTED = "detected"
    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"
    DENIED = "denied"
    FAILED = "failed"
    USER_DECLARED = "user-declared"


@dataclass
class FieldValue:
    value: Any
    status: FieldStatus = FieldStatus.UNKNOWN
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "status": self.status.value,
            "source": self.source,
        }

    @staticmethod
    def redact(value: Any, key: Optional[str] = None) -> Any:
        text = str(value)
        key_lower = (key or "").lower()
        if isinstance(value, str):
            if any(marker in key_lower for marker in ("serial", "mac", "hostname", "host")):
                return "<REDACTED>"
            if any(token in text for token in ("serial", "mac", "hostname", "host")):
                return "<REDACTED>"
            return value
        return value


@dataclass
class HardwareProfile:
    profile_name: str
    device_family: str
    platform: str
    model: str
    fields: Dict[str, FieldValue] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"
    scan_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "scan_id": self.scan_id,
            "profile_name": self.profile_name,
            "device_family": self.device_family,
            "platform": self.platform,
            "model": self.model,
            "fields": {k: v.to_dict() for k, v in self.fields.items()},
            "provenance": self.provenance,
        }

    def redact_for_save(self) -> "HardwareProfile":
        redacted = HardwareProfile(
            profile_name=self.profile_name,
            device_family=self.device_family,
            platform=self.platform,
            model=self.model,
            fields={},
            provenance={
                **self.provenance,
                "redactions": [
                    "serials",
                    "MAC addresses",
                    "hostnames",
                ],
            },
            schema_version=self.schema_version,
            scan_id=self.scan_id,
        )
        for key, field in self.fields.items():
            redacted.fields[key] = FieldValue(
                value=FieldValue.redact(field.value, key),
                status=field.status,
                source=field.source,
            )
        return redacted


@dataclass
class DeviceInfo:
    device_id: str
    name: str
    model: str
    state: str
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "model": self.model,
            "state": self.state,
            "meta": self.meta,
        }


@dataclass
class DiagnosticReport:
    device_id: str
    checks: Dict[str, str]
    passed: bool
    summary: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ScanResult:
    profile: Optional[HardwareProfile]
    devices: List[DeviceInfo]
    reports: List[DiagnosticReport]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
