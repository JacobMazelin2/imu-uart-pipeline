# IMU UART Pipeline

This is a take-home project that simulates UART communication between an IMU sensor (emulator) and a host PC (consumer). The emulator generates fake IMU data and streams it over a virtual serial link. The consumer reads it, estimates orientation, and stores the results.

## Prerequisites

- Python 3.10+
- `socat` for virtual serial ports
  - Debian/Ubuntu: `sudo apt install socat`
  - macOS: `brew install socat`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running

Three terminals are needed:

```bash
# Terminal 1: create virtual serial pair
./scripts/setup_ports.sh

# Terminal 2: start the emulator
source .venv/bin/activate
emulator --port-path /tmp/virtual0 --baudrate 9600 --frequency 100 --log-level INFO

# Terminal 3: start the consumer
source .venv/bin/activate
consumer --port-path /tmp/virtual1 --baudrate 9600 --log-level DEBUG
```

The consumer automatically sends a START command on launch. Use Ctrl+C to stop
either process.

## Architecture

I split it into three packages. `protocol/` is shared so both sides agree on
how messages look on the wire without duplicating code.

- **`protocol/`** -- I put the data models, command definitions, and framing
  logic here. Both the emulator and consumer import from this package so
  neither side has to manually deal with `$...\n` formatting.
- **`emulator/`** -- I wrote this to generate fake but plausible IMU readings
  and stream them over UART. It sits idle until it gets a START command, then
  streams until it gets STOP.
- **`consumer/`** -- This is the host side. I have it reading from the serial
  port, figuring out if each message is IMU data or a command response, running
  the orientation filter, and storing results in a ring buffer.

## Assumptions and Trade-offs

- **Virtual port paths** default to `/tmp/` instead of `/dev/` because creating
  symlinks under `/dev/` usually requires root. Both paths are still
  configurable through CLI arguments.
- **Baudrate 4096** is the spec default, but it is non-standard and did not work
  reliably on macOS during development. I used 9600 for development, while
  keeping 4096 compatible with Linux.
- **Complementary filter** -- I used a complementary filter instead of a Kalman
  filter for orientation estimation. It is simpler, easier to reason about, and
  fits the scope of this project well. A Kalman filter would likely be better in
  a production system, but it felt like unnecessary complexity here.
- **Quaternion output** -- I store orientation as quaternions instead of Euler
  angles to avoid gimbal lock in the stored representation.
- **Timestamps** are stored as raw microseconds since epoch. They are large
  values, but that is standard for embedded-style sensor data and makes
  delta-time calculations straightforward.
- **Magnetometer is not used in the filter** -- Yaw is estimated through gyro
  integration only, so it will drift over time. I kept this trade-off
  intentionally to keep the filter simple. Adding magnetometer-based yaw
  correction would require handling magnetic distortion and calibration, which
  felt out of scope for this implementation.
- **No HTTP server** -- As per instructions, I prioritized the core pipeline for this version of the
  task: UART communication, parsing, orientation estimation, and history
  storage.

## Testing

```bash
pytest
```
