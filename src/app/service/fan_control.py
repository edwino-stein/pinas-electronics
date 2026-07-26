import asyncio
import typing
import logging
from gpio import tachometer, fan
from ..state import fan as fan_state, app

logger = logging.getLogger(__name__)

_TACHOMETER: tachometer.Tachometer = typing.cast(tachometer.Tachometer, None)
_FAN: fan.Fan = typing.cast(fan.Fan, None)
_LOOP: bool = False
_POLLING_INTERVAL: float = 1

async def setup():
    global _TACHOMETER, _FAN

    logger.debug('Parsing the configuration section "fan control"...')

    if 'fan control' not in app.CONFIG.sections():
        logger.error('Missing config section "fan control".')
        raise RuntimeError('Missing config section "fan control".')

    if 'fan_pin' not in app.CONFIG['fan control'].keys():
        logger.error('Missing config option "fan_pin" in section "fan control".')
        raise RuntimeError('Missing config option "fan_pin" in section "fan control".')

    fan_pin = app.CONFIG['fan control'].getint('fan_pin')
    if type(fan_pin) is not int or fan_pin not in range(1, 41):
        logger.error('The config option "fan_pin" in section "fan control" must be an integer number between 1 and 40.')
        raise RuntimeError('The config option "fan_pin" in section "fan control" must be an integer number between 1 and 40.')

    if 'fan_pwm_freq' not in app.CONFIG['fan control'].keys():
        logger.warning('Missing config option "fan_pwm_freq" in section "fan control".')

    fan_pwm_freq = app.CONFIG['fan control'].getfloat('fan_pwm_freq')
    if type(fan_pwm_freq) is not float or fan_pwm_freq <= 0:
        logger.warning ('Invalid config option "fan_pwm_freq" in section "fan control".')
        logger.warning('Using "fan_pwm_freq" default value: 25.0')
        fan_pwm_freq = 25.0

    tachometer_pin = app.CONFIG['fan control'].getint('tachometer_pin')
    if type(tachometer_pin) is not int or tachometer_pin not in range(1, 41):
        logger.error('The config option "tachometer_pin" in section "fan control" must be an integer number between 1 and 40.')
        raise RuntimeError('The config option "tachometer_pin" in section "fan control" must be an integer number between 1 and 40.')

    if 'tachometer_pulses_per_rev' not in app.CONFIG['fan control'].keys():
        logger.warning('Missing config option "tachometer_pulses_per_rev" in section "fan control".')

    tachometer_pulses_per_rev = app.CONFIG['fan control'].getint('tachometer_pulses_per_rev')
    if type(tachometer_pulses_per_rev) is not int or tachometer_pulses_per_rev <= 0:
        logger.warning ('Invalid config option "tachometer_pulses_per_rev" in section "fan control".')
        logger.warning('Using "tachometer_pulses_per_rev" default value: 2')
        tachometer_pulses_per_rev = 2

    logger.info('Fan set to PWM pin #%d, at %.2fhz', fan_pin, fan_pwm_freq)
    _FAN = fan.setup(fan_pin, fan_pwm_freq)

    logger.info('Fan tachometer set to DIN pin #%d, at %d pulses per revolution', tachometer_pin, tachometer_pulses_per_rev)
    _TACHOMETER = tachometer.setup(tachometer_pin, tachometer_pulses_per_rev)


async def start():
    global _LOOP

    if _TACHOMETER is None or _FAN is None:
        logger.error('Module wasn\'t initilized.')
        raise RuntimeError('Module wasn\'t initilized.')

    logger.info('Starting tachometer...')
    for i in range(0, 10):
        try:
            _TACHOMETER.start()
            break
        except:
            logger.warning('Fail to start tachometer! Trying again (%d/10)...', i+1)
            await asyncio.sleep(0.5)

    logger.info('Starting fan...')
    _FAN.start(0.0)

    logger.info('Starting fan stat polling...')
    _LOOP = True
    while _LOOP:
        logger.debug('Checking fan stat...')
        await asyncio.to_thread(lambda: fan_state._update_chassis_power(_FAN.speed))
        await asyncio.to_thread(lambda: fan_state._update_chassis_rpm(_TACHOMETER.rotation_rate))
        logger.debug('Fan stat: %.2f%% / %.2f RPM', fan_state.CHASSIS.power * 100, fan_state.CHASSIS.rpm)

        logger.debug('Sleeping for %.2f seconds', _POLLING_INTERVAL)
        await asyncio.sleep(_POLLING_INTERVAL)
        logger.debug('Wake up!')


async def stop():
    global _LOOP

    logger.info('Stopping fan stat polling...')
    _LOOP = False

    if _TACHOMETER is not None:
        logger.info('Stopping tachometer...')
        _TACHOMETER.stop()

    if _FAN is not None:
        logger.info('Stopping fan...')
        _FAN.stop()


def set_fan_power(fan_power: float):
    logger.info('Fan power set to %.2f%%', fan_power * 100)
    if _FAN is not None: _FAN.speed = fan_power
