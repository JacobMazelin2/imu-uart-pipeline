from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class IMUSample:
    accel_x : float
    accel_y : float
    accel_z : float
    timestamp_accel : int
    gyro_x : int
    gyro_y : int
    gyro_z : int
    timestamp_gyro : int
    mag_x : float
    mag_y : float
    mag_z : float
    timestamp_mag : int

    def to_fields(self) -> list[str]:
        return [
            str(self.accel_x), str(self.accel_y), str(self.accel_z),
            str(self.timestamp_accel),
            str(self.gyro_x), str(self.gyro_y), str(self.gyro_z),
            str(self.timestamp_gyro),
            str(self.mag_x), str(self.mag_y), str(self.mag_z),
            str(self.timestamp_mag),
        ]

    @classmethod
    def from_fields(cls, fields: list[str]) -> "IMUSample":
        if len(fields) != 12:
            raise ValueError(f"Expected 12 fields, got {len(fields)}")
        try:
            return cls(
                accel_x=float(fields[0]),
                accel_y=float(fields[1]),
                accel_z=float(fields[2]),
                timestamp_accel=int(fields[3]),
                gyro_x=int(fields[4]),
                gyro_y=int(fields[5]),
                gyro_z=int(fields[6]),
                timestamp_gyro=int(fields[7]),
                mag_x=float(fields[8]),
                mag_y=float(fields[9]),
                mag_z=float(fields[10]),
                timestamp_mag=int(fields[11]),
            )
        except (ValueError, IndexError) as e:
            raise ValueError(f"Malformed IMU fields: {e}") from e

