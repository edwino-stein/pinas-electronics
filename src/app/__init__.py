import argparse
import asyncio
from pprint import pprint
import RPi.GPIO as GPIO
from .state import drive
from .service import drive_service
from pySMART import SMARTCTL


SMARTCTL.sudo = True
GPIO.setmode(GPIO.BCM)


async def log_task():
    while True:
        print('Drives:', end=' ')
        pprint(list(drive.iter_drives_state()))
        await asyncio.sleep(5)


async def _main(args: argparse.Namespace) -> int:

    await asyncio.gather(
        drive_service.monitor_all_drives(30),
        log_task()
    )

    return 0


def _parse_args(argv: list[str]) -> argparse.Namespace:
    return None


def main(argv: list[str]) -> int:
    try:
        print(asyncio.run(_main(_parse_args(argv))))
    except KeyboardInterrupt:
        drive_service.stop_polling()
