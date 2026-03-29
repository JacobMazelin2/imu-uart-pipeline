import logging
import time

import serial

from imu_uart.protocol import framing
from imu_uart.protocol.commands import Command, CommandResponse, decode_response
from imu_uart.protocol.models import IMUSample
from imu_uart.consumer.orientation import OrientationEstimator
from imu_uart.consumer.parser import parse_payload

log = logging.getLogger(__name__)

class UARTConsumer:

    def __init__(self, port, baudrate, history):
        self.port = serial.Serial(port, baudrate=baudrate, timeout=0.1)
        self.history = history
        self._buffer = bytearray()
        self._orientation = OrientationEstimator()
        
    def send_command(self, cmd: Command) -> CommandResponse:
        self.port.write(framing.encode_message(cmd.value))
        deadline = time.time() + 2.0
        while time.time() < deadline:
            data = self.port.read(1024)
            if not data:
                continue
            self._buffer.extend(data)
            messages, self._buffer = framing.extract_messages(self._buffer)
            for msg in messages:
                if ";" not in msg:
                    return decode_response(msg)
        raise TimeoutError("no response from device")

    def run(self):
        
        log.info("consumer listening")
        try:
            while True:
                data = self.port.read(1024)
                if not data:
                    continue
                self._buffer.extend(data)
                messages, self._buffer = framing.extract_messages(self._buffer)
                for msg in messages:
                    try:
                        result = parse_payload(msg)
                    except ValueError:
                        log.warning("skipping malformed message: %r", msg[:50])
                        continue
                    if isinstance(result, IMUSample):
                        self._process_sample(result)
                    elif isinstance(result, CommandResponse):
                        log.info("recieved response: %s", result)
        except KeyboardInterrupt:
            log.info("shutting down")
        finally:
            self.port.close()

    def _process_sample(self, sample: IMUSample):
        quaternion = self._orientation.update(sample)
        entry = {
            "timestamp": sample.timestamp_accel,
            "sample": quaternion,
        }
        self.history.append(entry)
        log.debug("orientation: [%.4f, %.4f, %.4f, %.4f]", *quaternion)
