import argparse
import asyncio
import logging
import signal
import typing
import importlib
import RPi.GPIO as GPIO

_SERVICES = []

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
    return argparse.Namespace()


def main(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)6s [%(name)-15s] %(message)s')
    logger = logging.getLogger(__name__)

    logger.debug('GPIO set to BCM mode.')
    GPIO.setmode(GPIO.BCM)

    try:
        return asyncio.run(_start(args))
    except:
        logging.exception('Something bad happened:')
        return 1
