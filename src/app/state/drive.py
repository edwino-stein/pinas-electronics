from collections.abc import Iterable, Iterator
from pathlib import Path

from telemetry import smart
from ..model import DriveState

_DRIVES_STATE: set[DriveState] = set()

def _make_drive_state_from_drive_handle(dev_object: smart.DriveHandle) -> DriveState:
    drive_info = dev_object.info
    drive_attrs = dev_object.attributes
    return DriveState(device_path=Path(dev_object.os_reference),
                      family=drive_info.family,
                      model=drive_info.model,
                      serial_number=drive_info.serial_number,
                      interface=drive_info.interface,
                      type=drive_info.type,
                      health_status=dev_object.health_status,
                      temperature=next(map(lambda a: a.raw,
                                           filter(lambda a: a.field == smart.DriveSmartAttibuteField.TEMPERATURE_CELSIUS_194,
                                                  drive_attrs)), 0))

def update_drives_state(drive_objects: Iterable[smart.DriveHandle]):
    global _DRIVES_STATE
    _DRIVES_STATE = set(map(_make_drive_state_from_drive_handle, drive_objects))

def total_drives() -> int:
    return len(_DRIVES_STATE)

def iter_drives_state() -> Iterator[DriveState]:
    return iter(_DRIVES_STATE)
