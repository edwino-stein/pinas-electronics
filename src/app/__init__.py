import argparse
import asyncio
import logging
import signal
import typing
import importlib
import configparser
import RPi.GPIO as GPIO
from pathlib import Path

from .state import app as app_state

_SERVICES = ['app.service.drive_monitoring', 'app.service.fan_control', 'app.service.temperature_control']

async def _start(args: argparse.Namespace) -> int:
    logger = logging.getLogger(__name__)

    logger.info('Starting application loop...')

    logger.debug('Main task renamed to "__main__".')
    typing.cast(asyncio.Task, asyncio.current_task()).set_name('__main__')

    logger.debug('Registering the signal INTerrupt event handler to the event loop.')
    asyncio.get_running_loop().add_signal_handler(signal.SIGINT, _on_sigint)

    logger.info('Loading services...')
    for s in map(importlib.import_module, _SERVICES):
        logger.info('Setting up service "%s"...', s.__name__)
        await s.setup()

    logger.info('Starting services...')
    async with asyncio.TaskGroup() as tg:
        for s in map(importlib.import_module, _SERVICES):
            logger.info('Staring up service "%s"...', s.__name__)
            tg.create_task(s.start())

        logger.info('Application running, CTRL+C to stop...')

    logger.info('Application stopped, bye!')
    return 0


async def _stop():
    logger = logging.getLogger(__name__)

    logger.info("Stopping services...")
    for s in map(importlib.import_module, _SERVICES):
        logger.info('Stopping service "%s"...', s.__name__)
        await s.stop()

    logger.info("Awaiting for service tasks....")
    for task in list(filter(lambda t: t.get_name() not in ['__main__', '__stop__'], asyncio.all_tasks())):
        task.cancel()
        await asyncio.sleep(0.1)


def _on_sigint():
    logger = logging.getLogger(__name__)
    logger.info("Signal INTerrupt captured! Stopping application...")
    asyncio.create_task(_stop(), name='__stop__')


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog='pinas-electronics', description='PINAS eletronics controller.')

    parser.add_argument('work_dir', type=Path, help='Work directory') 
    parser.add_argument('-f',
                        dest='config_file',
                        type=Path,
                        default=Path('config.ini'),
                        help='Configuration file, relative to given work directory.')
    
    parser.add_argument('-v', '--verbose', action="store_true", help='Enable detailed logging.')

    return parser.parse_args(argv)


def main(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s %(levelname)6s [%(name)-31s] %(message)s')
    logger = logging.getLogger(__name__)

    app_state._set_work_dir_and_config_file(args.work_dir, args.config_file)

    if not app_state.WORK_DIR.is_dir():
        logger.error('Invalid work directory: It is not a directory.')
        return 1

    if not app_state.CONFIG_FILE.is_file():
        logger.error('Invalid configuration file: File does not exist.')
        return 1

    logger.debug('Using work directory: %s', app_state.WORK_DIR)
    logger.debug('Parsing config file: %s', app_state.CONFIG_FILE)

    config = configparser.ConfigParser()
    config.read(app_state.CONFIG_FILE)
    app_state._set_config(config)

    logger.debug('GPIO set to BCM mode.')
    GPIO.setmode(GPIO.BCM)

    try:
        return asyncio.run(_start(args))
    except:
        logging.exception('Something bad happened:')
        return 1
