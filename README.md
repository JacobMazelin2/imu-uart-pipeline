# IMU UART Pipeline

UART-based IMU data pipeline consisting of a microcontroller emulator and a
host PC consumer. The emulator streams IMU sensor data over a virtual serial
connection; the consumer parses, processes, and stores the data.

## Prerequisites

- Python 3.10+
- `socat` (for virtual serial ports): `sudo apt install socat`

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Virtual Serial Ports

In a separate terminal:

```bash
./scripts/setup_ports.sh
```

This creates `/tmp/virtual0` and `/tmp/virtual1`. The emulator connects to one
end, the consumer to the other.

## Usage

```bash
# Terminal 1: start the emulator
emulator --port-path /tmp/virtual0

# Terminal 2: start the consumer
consumer --port-path /tmp/virtual1
```

## Architecture

The project is split into three packages:

- **`protocol/`** -- Shared message framing, command definitions, and data models
- **`emulator/`** -- IMU data generation and UART device emulation
- **`consumer/`** -- UART reader, parser, orientation estimation, history, and HTTP server

## Assumptions and Trade-offs

_To be documented as implementation progresses._

## Testing

```bash
pytest
```
