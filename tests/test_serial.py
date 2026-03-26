import shutil
import subprocess
import time

import pytest
import serial

SOCAT = shutil.which("socat")

# Virtual ptys ignore baudrate, so use a standard value that works
# on macOS. The spec's 4096 default is non-standard and only works
# on real UART hardware or Linux ptys.
BAUDRATE = 9600


@pytest.fixture
def virtual_ports(tmp_path):
    if SOCAT is None:
        pytest.skip("socat not installed")
    port_a = str(tmp_path / "virtual0")
    port_b = str(tmp_path / "virtual1")
    proc = subprocess.Popen(
        [SOCAT, "-d", "-d",
         f"pty,raw,echo=0,link={port_a}",
         f"pty,raw,echo=0,link={port_b}"],
        stderr=subprocess.PIPE,
    )
    time.sleep(0.5)
    yield port_a, port_b
    proc.terminate()
    proc.wait()


def test_bytes_round_trip(virtual_ports):
    port_a, port_b = virtual_ports
    with serial.Serial(port_a, baudrate=BAUDRATE, timeout=1) as writer, \
         serial.Serial(port_b, baudrate=BAUDRATE, timeout=1) as reader:
        writer.write(b"hello\n")
        result = reader.readline()
        assert result == b"hello\n"