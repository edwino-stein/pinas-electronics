from RPi import GPIO

def _rpi_pwn_value(value: float) -> float:
    return min(100, max(0, value) * 100)

class Fan:

    def __init__(self, pwn_pin: int, pwm_frequency: float):
        GPIO.setup(pwn_pin, GPIO.OUT)

        self._pwn_pin = pwn_pin
        self._pwm_obj = GPIO.PWM(pwn_pin, pwm_frequency)

    @property
    def speed(self) -> float:
        return self._pwm_obj._dc / 100 if self._pwm_obj._dc is not None else -1

    @speed.setter
    def speed(self, speed: float):
        self._pwm_obj.ChangeDutyCycle(_rpi_pwn_value(speed))

    def start(self, speed: float = 0.0):
        self._pwm_obj.start(_rpi_pwn_value(speed))
    
    def stop(self):
        self._pwm_obj.stop()


def setup(pwn_pin: int, pwm_frequency: float = 25.0):
    return Fan(pwn_pin, pwm_frequency)
