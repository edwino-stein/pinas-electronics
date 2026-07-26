; =====================================
; Template file for a config .INI file
; =====================================

;
; The "monitoring drives" section is related to the service "drive_monitoring", where it uses SMART protocol to gethering status
; info from drives, including temperature.
;
[monitoring drives]

; Comma-separated list (",") containing all device names that will be used to query SMART data. The device name is the same as the
; "/dev" directory, for example, given the device "/dev/XXX, only the final part is needed, the "XXX".
; This entry is required!
drives = sda, sdb, sdc, sdd

; Time interval in seconds which the "drive_monitoring" will use to query SMART data. Since the SMART query is performed via a
; system call, it is not recommended to set short intervals due overhead.
; This entry is optional! The default value is 20.0
polling_interval = 20


;
; The "fan control" section is related to the service "fan_control", where it controls and reports the chassis fan stats.
; It expects pin numbers in Broadcom pin numbering (BCM). See https://pinout.xyz for more details.
;
[fan control]

; Pin to control the fan power/speed. It requires to supports a hardware PWM, so take a look in https://pinout.xyz/pinout/pwm to
; check the hardware PWM pin availables.
; This entry is required!
fan_pin = 13

; PWM frequency in Hertz to determine the duty cycle. It depends of fan specification, however, most modern standard PC fans
; uses 25Hz.
; This entry is optional! The default value is 25.0
fan_pwm_freq = 25

; Pin to fan tachometer for measuring the fan rotation speed (RPM). It requires to support digital input in pull-up mode.
; This entry is required!
tachometer_pin = 17

; Number of pulses required to count as one complete fan rotation. most modern standard PC fans uses 1 or 2.
; This entry is optional! The default value is 2
tachometer_pulses_per_rev = 2


;
; The "temperature control" section is related to the service "temperature_control", where it constantly monitors the drives
; temperatures and sets the fan power based on a defined temperature versus fan power curve. The hard drive temperature is
; basically a simple arithmetic average of all reported temperatures from all hard drives whose SMART data was consulted.
;
; NOTE: It is recommended to try to keep the Hard Drives between 35 and 45 degrees celsius for longer longevity. However, it is
; also not recommended to keep the fan completely off all the time, even when no hard drive is running, to ensure fresh air
; circulation to all other electronic components. So keep it in mind to choose the right fan power curve.
;
[temperature control]

; Comma-separated list (",") containing all points of the temperature versus fan power curve in the format:
;
; <MAX_TEMPERATURE>:<FAN_POWER>, ...
;
; Where:
; - <MAX_TEMPERATURE>: The maximum temperature in degrees celsius for a given fan power setting.
; - <FAN_POWER>: The fan power in percentage (between 0% and 100%).
;
; The temperature versus fan power curve should be continuous and linear, so that the fan power is valid between the previous
; temperature point and the next temperature point (half-open interval). For instance, given the following points:
; 
; fan_power_curve = 10:0, 30:40, 80:50
; 
; The fan power will be defined by given intervals:
; 10% if: -INFITINE <= TEMP < 0
; 30% if: 0 <= TEMP < 40
; 80% if: 40 <= TEMP < 50
; 100% if: 50 <= TEMP < INFITINE
;
; NOTE: Some fans can not spin well in power setting bellow 20%, and can not even spin in values below 5%. Additionally, in some
; cases, the fan may spin intermittently, as if it were pulsing at low power settings.
;
; This entry is required!
fan_power_curve = 10:0, 30:40, 80:50

; Time interval in seconds which the "temperature_control" will use calculate the average temperature and update the fan power
; if needed.
; This entry is optional! The default value is 1
temp_check_interval = 1
