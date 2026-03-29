import logging
import time

import serial

from imu_uart.protocol import framing, commands
from imu_uart.protocol.commands import Command
from imu_uart.emulator.imu_source import generate_sample

log = logging.getLogger(__name__)


class EmulatorDevice:
    def __init__(self, port: str, baudrate: int, frequency: int):
        if frequency <= 0:
            raise ValueError(f"frequency must be positive, got {frequency}")
        self.port = serial.Serial(port, baudrate=baudrate, timeout=0.01)
        self.frequency = frequency
        self.period = 1.0 / frequency
        self.streaming = False
        self._next_tick = 0.0
        self._buffer = bytearray()

    def run(self):
        """Main loop: listen for commands, stream data when active."""
        log.info("emulator ready, waiting for commands")
        try:
            while True:
                now = time.monotonic()
                if self.streaming and now >= self._next_tick:
                    self._send_sample()
                    self._next_tick += self.period

                wait = max(0, self._next_tick - time.monotonic()) if self.streaming else 0.1
                self.port.timeout = wait
                self._check_commands()
        except KeyboardInterrupt:
            log.info("shutting down")
        finally:
            self.port.close()
            
    def _check_commands(self):
        """Read any available bytes and handle complete commands."""
        data = self.port.read(1024)
        if not data:
            return
        self._buffer.extend(data)
        messages, self._buffer = framing.extract_messages(self._buffer)
        for payload in messages:
            self._handle_command(payload)

    def _handle_command(self, payload: str):
        """Parse a command payload and send the appropriate response."""
        try:
            cmd = Command(payload)
        except ValueError:
            response = f"{payload},invalid command"
            self.port.write(framing.encode_message(response))
            log.warning("unknown command: %r", payload)
            return

        if cmd == Command.START:
            self.streaming = True
            self._next_tick = time.monotonic()
            log.info("streaming started")
        elif cmd == Command.STOP:
            self.streaming = False
            log.info("streaming stopped")

        response = f"{cmd.value},ok"
        self.port.write(framing.encode_message(response))

    def _send_sample(self):
        """Generate one IMU sample and write it to the port."""
        sample = generate_sample()
        payload = ";".join(sample.to_fields())
        self.port.write(framing.encode_message(payload))
        log.debug("sent sample: %s", payload[:40])