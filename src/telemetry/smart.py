from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum, Enum
from pySMART import DeviceList, Device, Attribute

class DriveSmartStatus(StrEnum):

    PASS = 'PASS'
    FAIL = 'FAIL'
    UNKNOWN = 'UNKNOWN'

    @classmethod
    def make_from_pysmart_device(cls, dev_object: Device):
        return cls(dev_object.assessment) if dev_object.assessment in cls else cls.UNKNOWN


class DriveInterface(StrEnum):

    SATA = 'sat'
    UNKNOWN = 'unknown'

    @classmethod
    def make_from_pysmart_device(cls, dev_object: Device):
        return cls(dev_object.interface) if dev_object.interface in cls else cls.UNKNOWN


class DriveType(StrEnum):

    HDD = 'hdd'
    SSD = 'ssd'
    UNKNOWN = 'unknown'

    @classmethod
    def make_from_pysmart_device(cls, dev_object: Device):
        return cls.SSD if dev_object.is_ssd else cls.HDD


class DriveSmartAttibuteField(Enum):
    RAW_READ_ERROR_RATE_1 = 1
    SPIN_UP_TIME_3 = 3
    START_STOP_COUNT_4 = 4
    REALLOCATED_SECTOR_CT_5 = 5
    SEEK_ERROR_RATE_7 = 7
    POWER_ON_HOURS_9 = 9
    SPIN_RETRY_COUNI_10 = 10
    CALIBRATION_RETRY_COUNT = 11
    POWER_CYCLE_COUNT_12 = 12
    POWER_OOFF_RETRACT_COUNT_192 = 192
    LOAD_CYCLE_COUNT_193 = 193
    TEMPERATURE_CELSIUS_194 = 194
    REALLOCATED_EVENT_COUNT_196 = 196
    CURRENT_PENDING_SECTOR_197 = 197
    OFFLINE_UNCORRECTABLE_198 = 198
    UDMA_CRC_ERROR_COUNT_199 = 199
    MULTI_ZONE_ERROR_RATE_200 = 200

    UNKNOWN_0 = 0

    @property
    def field_name(self) -> str:
        return self.name[0:self.name.rfind('_')].lower()

    @classmethod
    def make_from_pysmart_attribute(cls, attr_object: Attribute):
        return cls(attr_object.num) if attr_object.num in cls else cls.UNKNOWN_0


@dataclass(frozen=True)
class DriveInfo:

    vendor: str
    family: str
    model: str
    serial_number: str
    interface: DriveInterface
    type: DriveType
    size: int
    rotation_rate: int

    @classmethod
    def make_from_pysmart_device(cls, dev_object: Device):
        return cls(vendor=dev_object.vendor,
                   family=dev_object.family,
                   model=dev_object.model,
                   serial_number=dev_object.serial,
                   interface=DriveInterface.make_from_pysmart_device(dev_object),
                   type=DriveType.make_from_pysmart_device(dev_object),
                   size=dev_object.size,
                   rotation_rate=dev_object.rotation_rate)


@dataclass(frozen=True)
class DriveSmartAttibute:

    field: DriveSmartAttibuteField
    value: str
    worst: int
    threshold: int | None
    type: str
    updated: str
    when_failed: str
    raw: int | str

    @classmethod
    def make_from_pysmart_attribute(cls, attr_object: Attribute):
        return cls(field=DriveSmartAttibuteField.make_from_pysmart_attribute(attr_object),
                   value=attr_object.value,
                   worst=attr_object.worst,
                   threshold=attr_object.thresh,
                   type=attr_object.type,
                   updated=attr_object.updated,
                   when_failed=attr_object.when_failed,
                   raw=attr_object.raw_int if attr_object.raw_int is not None else attr_object.raw)


class DriveHandle:

    def __init__(self, os_reference: str):
        self._os_reference = os_reference

    @property
    def os_reference(self) -> str:
        return self._os_reference

    def __eq__(self, value):
            if isinstance(value, self.__class__):
                return self.os_reference == value.os_reference

            if isinstance(value, Device):
                return self.os_reference == value.dev_reference

            if type(value) is str:
                return self.os_reference == value

            return False

    def __hash__(self):
        return hash(self.os_reference)

    @property
    def info(self) -> DriveInfo:
        return DriveInfo.make_from_pysmart_device(Device(self.os_reference))

    @property
    def attributes(self) -> set[DriveSmartAttibute]:
        return set(self.iter_attributes())

    @property
    def health_status(self) -> DriveSmartStatus:
        return DriveSmartStatus.make_from_pysmart_device(Device(self.os_reference))

    def iter_attributes(self) -> Iterator[DriveSmartAttibute]:
        attributes = filter(lambda a: a is not None, Device(self.os_reference).attributes)
        return map(DriveSmartAttibute.make_from_pysmart_attribute, attributes)

    def __repr__(self):
        return f'<DriveHandle "{self.os_reference}">'

    @classmethod
    def make_from_pysmart_device(cls, dev_object: Device):
        return cls(dev_object.dev_reference)


def _scan_pysmart_devices() -> Iterator[Device]:
    return filter(lambda d: d.smart_capable and d.smart_enabled, DeviceList().devices)

def query_all_drives() -> Iterator[DriveHandle]:
    return map(DriveHandle.make_from_pysmart_device, _scan_pysmart_devices())

def query_drive_by_serial_number(serial_number: str) -> Iterator[DriveHandle]:
    return map(DriveHandle.make_from_pysmart_device, filter(lambda d: d.serial == serial_number, _scan_pysmart_devices()))

def query_drive_by_os_reference(os_reference: str) -> Iterator[DriveHandle]:
    return map(DriveHandle.make_from_pysmart_device, filter(lambda d: d.dev_reference == os_reference, _scan_pysmart_devices()))

def query_drive_by_interface(interface: DriveInterface) -> Iterator[DriveHandle]:
    devices = filter(lambda d: DriveInterface.make_from_pysmart_device(d) == interface, _scan_pysmart_devices())
    return map(DriveHandle.make_from_pysmart_device, devices)

def query_drive_by_type(drive_type: DriveType) -> Iterator[DriveInfo]:
    devices = filter(lambda d: DriveType.make_from_pysmart_device(d) == drive_type, _scan_pysmart_devices())
    return map(DriveHandle.make_from_pysmart_device, devices)
