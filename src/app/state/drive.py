from pathlib import Path
from collections.abc import Iterator
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

_DRIVES_STATE: dict[str, DriveState] = dict()


def update_drive_state(device_path: str,
                       family: str,
                       model: str,
                       serial_number: str,
                       interface: DriveInterface,
                       type: DriveType,
                       health_status: DriveSmartStatus,
                       temperature: int):
    global _DRIVES_STATE
    _DRIVES_STATE[device_path] = DriveState(device_path=Path(device_path),
                                            family=family,
                                            model=model,
                                            serial_number=serial_number,
                                            interface=interface,
                                            type=type,
                                            health_status=health_status,
                                            temperature=temperature)

def drive(device_path: str) -> DriveState:
    return _DRIVES_STATE[device_path]

def total_drives() -> int:
    return len(_DRIVES_STATE)

def iter_drives_state() -> Iterator[DriveState]:
    return iter(_DRIVES_STATE.values())
