import argparse
import logging

from imu_uart.consumer.history import History
from imu_uart.consumer.uart_io import UARTConsumer
from imu_uart.protocol.commands import Command


def main():
    parser = argparse.ArgumentParser(description="IMU data consumer over virtual UART")
    parser.add_argument("--port-path", type=str, default="/tmp/virtual1", help="serial port path")
    parser.add_argument("--baudrate", type=int, default=4096, help="UART baud rate")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="logging verbosity")

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level))

    history = History()

    try:
        consumer = UARTConsumer(args.port_path, args.baudrate, history)
    except Exception as e:
        logging.error("failed to open serial port: %s", e)
        return

    try:
        response = consumer.send_command(Command.START)
    except TimeoutError:
        logging.error("emulator did not respond, is it running?")
        return

    if not response.ok:
        logging.error("failed to start streaming: %s", response.status)
        return

    consumer.run()


if __name__ == "__main__":
    main()
