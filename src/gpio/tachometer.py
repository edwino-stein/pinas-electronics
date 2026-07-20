import time
import RPi.GPIO as GPIO # type: ignore

class Tachometer:

    def __init__(self, dinput_pin: int, pulses_per_rev: int = 1):
        GPIO.setup(dinput_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self._pin = dinput_pin
        self._pulses_per_rev = pulses_per_rev
        self._pulse_counter: int = 0
        self._timer: float = 0.0

    @property
    def rotation_rate(self) -> float:
        frequency = (self._pulse_counter / self._pulses_per_rev) / (time.time() - self._timer)
        self._timer = time.time()
        self._pulse_counter: int = 0
        return frequency * 60

    def _on_pin_fell(self, *args):
        self._pulse_counter += 1

    def start(self):
        GPIO.add_event_detect(self._pin, GPIO.FALLING, self._on_pin_fell)

    def stop(self):
        GPIO.remove_event_detect(self._pin)


def setup(dinput_pin: int, pulses_per_rev: int = 1) -> Tachometer:
    return Tachometer(dinput_pin, pulses_per_rev)
