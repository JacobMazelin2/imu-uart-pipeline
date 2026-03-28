import argparse
import logging

def main():
    parser = argparse.ArgumentParser(description="IMU sensor emulator over virtual UART")
    parser.add_argument("--port-path", type=str, default="/tmp/virtual0", help="serial port path")
    parser.add_argument("--baudrate", type=int, default=4096, help="UART baud rate")
    parser.add_argument("--frequency", type=int, default=100, help="samples per second")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="logging verbosity")

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level))

    logging.info("emulator starting on %s", args.port_path)

if __name__ == "__main__":
    main()