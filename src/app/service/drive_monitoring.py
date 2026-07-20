import asyncio
import logging
from telemetry import smart
from ..state import drive, app

logger = logging.getLogger(__name__)

_POLLING_RUNNING: bool = False
_POLLING_INTERVAL: float = 0.0
_DRIVES_TO_WATCH: set[str] = set()
_WATCH_TASKS: set[asyncio.Task] = set()

def _get_drive_temperature(drive_attrs: set[smart.DriveSmartAttibute]) -> int:
    temp_attr = filter(lambda a: a.field == smart.DriveSmartAttibuteField.TEMPERATURE_CELSIUS_194, drive_attrs)
    return next(map(lambda a: int(a.raw), temp_attr), 0)

async def setup():
    global _POLLING_INTERVAL, _DRIVES_TO_WATCH

    logger.debug('Parsing the configuration section "monitoring drives"...')

    if 'monitoring drives' not in app.CONFIG.sections():
        logger.error('Missing config section "monitoring drives".')
        raise RuntimeError('Missing config section "monitoring drives".')

    if 'drives' not in app.CONFIG['monitoring drives'].keys():
        logger.error('Missing config option "drives" in section "monitoring drives".')
        raise RuntimeError('Missing config option "drives" in section "monitoring drives".')

    drives = app.CONFIG['monitoring drives'].get('drives')
    if type(drives) is not str:
        logger.error('The config option "drives" in section "monitoring drives" must be a list of strings.')
        raise RuntimeError('The config option "drives" in section "monitoring drives" must be a list of strings.')

    if 'polling_interval' not in app.CONFIG['monitoring drives'].keys():
        logger.warning('Missing config option "polling_interval" in section "monitoring drives".')
        logger.warning('Using "polling_interval" default value: 20')

    polling_interval = app.CONFIG['monitoring drives'].getfloat('polling_interval')
    if type(polling_interval) is not float or polling_interval <= 0:
        logger.warning ('Invalid config option "polling_interval" in section "monitoring drives"..')
        logger.warning('Using "polling_interval" default value: 20')
        polling_interval = 20

    _POLLING_INTERVAL = polling_interval
    _DRIVES_TO_WATCH = set(map(lambda i: '/dev/' + i.strip().lower(), drives.split(',')))
    logger.info('Monitoring drives: %s', ', '.join(_DRIVES_TO_WATCH))
    logger.info('Polling interval: %.2f seconds', _POLLING_INTERVAL)

    logger.debug('Initializing SMART library.')
    smart.init()


async def start():
    global _POLLING_RUNNING, _WATCH_TASKS
    _POLLING_RUNNING = True
    
    logger.info('Starting monitoring polling...')
    while _POLLING_RUNNING:
        logger.debug('Scanning drives...')
        for drv in filter(lambda d: d.dev_reference in _DRIVES_TO_WATCH, await asyncio.to_thread(smart._scan_pysmart_devices)):
            drive_info = smart.DriveInfo.make_from_pysmart_device(drv)
            drive_smart_status = smart.DriveSmartStatus.make_from_pysmart_device(drv)
            drive_attrs = set(map(smart.DriveSmartAttibute.make_from_pysmart_attribute,
                                  filter(lambda a: a is not None, drv.attributes)))

            logger.debug('Drive "%s" stats: %s', drv.dev_reference, drive_info)

            drive.update_drive_state(drv.dev_reference,
                                     drive_info.family,
                                     drive_info.model,
                                     drive_info.serial_number,
                                     drive_info.interface,
                                     drive_info.type,
                                     drive_smart_status,
                                     _get_drive_temperature(drive_attrs))

        logger.debug('Sleeping for %.2f seconds', _POLLING_INTERVAL)
        await asyncio.sleep(_POLLING_INTERVAL)
        logger.debug('Wake up!')


async def stop():
    logger.info('Stopping monitoring polling...')
    global _POLLING_RUNNING
    _POLLING_RUNNING = False
