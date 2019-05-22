#!/usr/bin/env python
import os
import gpustat
import time
import scipy as sp
import numpy as np

# Tuple of (Temp, Percent Fan)s, specifying a cooling curve
COOLING_CURVE = ((0, 5),  (30, 10), (50, 30), (70, 85), (80, 96), (85, 100))

# Fast Dead band in percent fan for fast dead band.
# Do not change fan speed if within interval since last change
# and change amount is less than 
FAST_DEAD_BAND = 7
# Fast Dead band interval in seconds
FAST_DEAD_BAND_INTERVAL = 5

# Dead Band Interval to set speed every time
SLOW_DEAD_BAND_INTERVAL = 600


def set_fan_speed(gpu, speed):
        speed = int(speed)
        display_fix = 'DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0'
        os.system('{display_fix} nvidia-settings -a "[gpu:{gpu}]/GPUFanControlState=1" -a "[fan:{gpu}]/GPUTargetFanSpeed={speed}" --ctrl-display=:0'.format(**locals()))

def get_gpus():
        gpus = gpustat.new_query()
        return [i for i in range(len(gpus))]

def get_temps():
        gpus = gpustat.new_query()
        return [gpus[gpu].temperature for gpu in range(len(gpus))]


if __name__ == "__main__":

        gpus = get_gpus()
        speeds = [-100] * len(get_gpus())
        last_slow_change = time.time()
        x, y = np.array(list(zip(*COOLING_CURVE)))
        while True:
                slow_changed = False
                temps = get_temps()
                for gpu in gpus:
                        new_speed = None
                        speed = speeds[gpu]
                        temp = temps[gpu]
                        target_speed = np.interp(temp, x, y)
                        print(abs(target_speed-speed))
                        if abs(target_speed-speed)>FAST_DEAD_BAND_INTERVAL:
                                new_speed = target_speed
                        elif (time.time()-last_slow_change)>SLOW_DEAD_BAND_INTERVAL:
                                print("slow change")
                                new_speed = target_speed
                                slow_changed = True
                        if new_speed != None:
                                speeds[gpu] = new_speed
                                set_fan_speed(gpu, new_speed)
                if slow_changed:
                        last_slow_change = time.time()
                time.sleep(FAST_DEAD_BAND_INTERVAL)
