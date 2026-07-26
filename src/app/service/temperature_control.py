import asyncio
import math
import logging
import itertools
from collections import namedtuple
from collections.abc import Iterator
from ..state import app, drive, fan
from . import fan_control

logger = logging.getLogger(__name__)

TempRange = namedtuple('TempRange', ('min', 'max'))

_TEMPERATURE_CHECK_INTERVAL: float = 1.0
_FAN_SPEED_CURVE: dict[float, TempRange]
_LOOP: bool = False


def _decode_fan_power_curve(curve_point: str) -> tuple[float, float]:
    values = curve_point.split(':')
    if len(values) < 2:
        raise ValueError('Invalid fan curve point: Requires pattern "<FAN_POWER>:<TEMP_POINT>".')

    return (float(values[0].strip()), float(values[1].strip()))


def _iter_decode_fan_power_curve(input_str: str) -> Iterator[tuple[float, float]]:
    for p in map(_decode_fan_power_curve, input_str.split(',')):
        yield p


def _parse_fan_power_curve(input_str: str) -> dict[float, TempRange]:
  
    fan_power_curve = dict()
    prev = (0.0, -math.inf)

    for point in itertools.chain(_iter_decode_fan_power_curve(input_str), [(100, math.inf)]):
        if prev[0] > point[0]:
            raise RuntimeError(f'Invalid fan power point curve: Previous point is bigger than next ({prev[0]} > {point[0]}).')
        
        if prev[1] > point[1]:
            raise RuntimeError(f'Invalid temperature point curve: Previous point is bigger than next ({prev[1]} > {point[1]}).')

        fan_power_curve[prev[0]] = TempRange(min=prev[1], max=point[1])
        prev = point

    return fan_power_curve

def _in_temp_range(temp: float, temp_range: TempRange) -> bool:
    return temp_range.min <= temp and temp < temp_range.max

def calc_drives_temperature_avg() -> float:
    total_drives = drive.total_drives()
    return sum(map(lambda ds: ds.temperature, drive.iter_drives_state()))/total_drives if total_drives > 0 else math.inf


def get_target_fan_power(temp: float) -> float:
    return next(map(lambda i: i[0], filter(lambda i: _in_temp_range(temp, i[1]), _FAN_SPEED_CURVE.items())), 100.0)/100


async def on_temperature_change(temp: float):
    target_fan_power = get_target_fan_power(temp)
    if target_fan_power != fan.CHASSIS.power:
        fan_control.set_fan_power(target_fan_power)


async def setup():
    global _FAN_SPEED_CURVE, _TEMPERATURE_CHECK_INTERVAL

    logger.debug('Parsing the configuration section "temperature control"...')

    if 'temperature control' not in app.CONFIG.sections():
            logger.error('Missing config section "temperature control".')
            raise RuntimeError('Missing config section "temperature control".')

    if 'fan_power_curve' not in app.CONFIG['temperature control'].keys():
            logger.error('Missing config option "fan_power_curve" in section "temperature control".')
            raise RuntimeError('Missing config option "fan_power_curve" in section "temperature control".')

    fan_power_curve = _parse_fan_power_curve(app.CONFIG['temperature control'].get('fan_power_curve', '100:0'))

    if 'temp_check_interval' not in app.CONFIG['temperature control'].keys():
        logger.warning('Missing config option "temp_check_interval" in section "temperature control".')

    temp_check_interval = app.CONFIG['temperature control'].getfloat('temp_check_interval')
    if type(temp_check_interval) is not float or temp_check_interval <= 0:
        logger.warning ('Invalid config option "temp_check_interval" in section "temperature control".')
        logger.warning('Using "temp_check_interval" default value: %.2f', _TEMPERATURE_CHECK_INTERVAL)
        temp_check_interval = _TEMPERATURE_CHECK_INTERVAL

    logger.info('Fan power control curve points: %s',
                '; '.join(map(lambda p: f'{p[0]}% -> [{p[1].min} C, {p[1].max} C)', fan_power_curve.items())))
    _FAN_SPEED_CURVE = fan_power_curve

    logger.info('Temperature checking every: %.2f seconds', temp_check_interval)
    _TEMPERATURE_CHECK_INTERVAL = temp_check_interval


async def start():
    global _LOOP

    if _FAN_SPEED_CURVE is None or _TEMPERATURE_CHECK_INTERVAL is None:
            logger.error('Module wasn\'t initilized.')
            raise RuntimeError('Module wasn\'t initilized.')

    logger.info('Starting fan temperature monitoring...')
    _LOOP = True
    last_temp = 0.0

    while _LOOP:
        avg_temp = calc_drives_temperature_avg()
        if avg_temp != last_temp:
            logger.info('Avarange temperature changed! Before = %.2f C; Now = %.2f C.', last_temp, avg_temp)
            await on_temperature_change(avg_temp)

        last_temp = avg_temp
        logger.debug('Sleeping for %.2f seconds', _TEMPERATURE_CHECK_INTERVAL)
        await asyncio.sleep(_TEMPERATURE_CHECK_INTERVAL)
        logger.debug('Wake up!')


async def stop():
    global _LOOP

    logger.info('Stopping temperature monitoring...')
    _LOOP = False
