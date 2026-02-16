import asyncio
from collections.abc import Iterable
from telemetry import smart
from ..state.drive import update_drives_state


_POLLING_RUNNING = False
_DRIVES_TO_WATCH : set[smart.DriveHandle] = set()

def _watch_drives(drives: Iterable[smart.DriveHandle]):
    global _DRIVES_TO_WATCH
    _DRIVES_TO_WATCH = set(drives)


async def monitor_all_drives(interval: float = 10):
    global _POLLING_RUNNING

    if _POLLING_RUNNING:
        return

    _watch_drives(smart.query_all_drives())

    _POLLING_RUNNING = True
    while _POLLING_RUNNING:
        update_drives_state(_DRIVES_TO_WATCH)
        await asyncio.sleep(interval)

def stop_polling():
    global _POLLING_RUNNING
    _POLLING_RUNNING = False
