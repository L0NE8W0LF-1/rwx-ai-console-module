"""Scanner models: HardwareProfile, DeviceInfo, DiagnosticReport, FieldStatus
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime


class FieldStatus(str, Enum):
    DETECTED = "detected"
    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"
    DENIED = "denied"
    FAILED = "failed"


@dataclass
class FieldValue:
    value: Any
    status: FieldStatus = FieldStatus.UNKNOWN
    source: Optional[str] = None


@dataclass
class HardwareProfile:
    profile_name: str
    device_family: str
    platform: str
    model: str
    fields: Dict[str, FieldValue] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        d = {
            "profile_name": self.profile_name,
            "device_family": self.device_family,
            "platform": self.platform,
            "model": self.model,
            "fields": {k: {"value": v.value, "status": v.status.value, "source": v.source} for k, v in self.fields.items()},
            "provenance": self.provenance,
        }
        return d


@dataclass
class DeviceInfo:
    device_id: str
    name: str
    model: str
    state: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosticReport:
    device_id: str
    checks: Dict[str, str]
    passed: bool
    summary: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ScanResult:
    profile: Optional[HardwareProfile]
    devices: List[DeviceInfo]
    reports: List[DiagnosticReport]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
