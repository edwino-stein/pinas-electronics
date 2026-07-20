from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class FanState:
    power: float
    rpm: float

CHASSIS: FanState = FanState(power=0.0, rpm=0.0)

def _update_chassis_rpm(rpm: float):
    global CHASSIS
    CHASSIS = FanState(power=CHASSIS.power, rpm=rpm)

def _update_chassis_power(power: float):
    global CHASSIS
    CHASSIS = FanState(power=power, rpm=CHASSIS.rpm)
