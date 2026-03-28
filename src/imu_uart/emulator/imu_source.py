import random
import time
from imu_uart.protocol.models import IMUSample

def generate_sample() -> IMUSample:
    now = int(time.time() * 1_000_000)
    return IMUSample(
        accel_x=random.gauss(0, 5),
        accel_y=random.gauss(0, 5),
        accel_z=random.gauss(1000, 5),
        timestamp_accel=now,
        gyro_x=int(random.gauss(0, 100)),
        gyro_y=int(random.gauss(0, 100)),
        gyro_z=int(random.gauss(0, 100)),
        timestamp_gyro=now + 1,
        mag_x=random.gauss(200, 10),
        mag_y=random.gauss(50, 10),
        mag_z=random.gauss(400, 10),
        timestamp_mag=now + 2,
    )