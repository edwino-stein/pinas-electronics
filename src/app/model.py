from pathlib import Path
from dataclasses import dataclass
from telemetry.smart import DriveInterface, DriveType, DriveSmartStatus

@dataclass(frozen=True)
class DriveState:
    device_path: Path
    family: str
    model: str
    serial_number: str
    interface: DriveInterface
    type: DriveType
    health_status: DriveSmartStatus
    temperature: int
