import math

from imu_uart.protocol.models import IMUSample

# complementary filter weight: 98% gyro, 2% accelerometer
ALPHA = 0.98

class OrientationEstimator:

    def __init__(self):
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self._last_timestamp: int | None = None

    def update(self, sample: IMUSample) -> list[float]:
        dt = self._compute_dt(sample.timestamp_gyro)

        # accel-based pitch and roll (gravity reference)
        accel_roll = math.atan2(sample.accel_y, sample.accel_z)
        accel_pitch = math.atan2(
            -sample.accel_x, 
            math.sqrt(sample.accel_y ** 2 + sample.accel_z ** 2)
        )

        # gyro rates: convert from mDeg/s to rad/s
        gx = math.radians(sample.gyro_x / 1000.0)
        gy = math.radians(sample.gyro_y / 1000.0)
        gz = math.radians(sample.gyro_z / 1000.0)

        # complementary filter: trust gyro short-term, accel long-term
        self.roll = ALPHA * (self.roll + gx * dt) + (1 - ALPHA) * accel_roll
        self.pitch = ALPHA * (self.pitch + gy * dt) + (1 - ALPHA) * accel_pitch

        # yaw from gyro only (no accel reference for yaw)
        self.yaw += gz * dt
        return self._to_quaternion()

    def _compute_dt(self, timestamp: int) -> float:
        if self._last_timestamp is None:
            self._last_timestamp = timestamp
            return 0.0
        dt = (timestamp - self._last_timestamp) / 1_000_000.0
        self._last_timestamp = timestamp
        return dt

    def _to_quaternion(self) -> list[float]:
        # euler to quaternion conversion (avoids gimbal lock in storage)
        cr = math.cos(self.roll / 2)
        sr = math.sin(self.roll / 2)
        cp = math.cos(self.pitch / 2)
        sp = math.sin(self.pitch / 2)
        cy = math.cos(self.yaw / 2)
        sy = math.sin(self.yaw / 2)
        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy
        return [w, x, y, z]