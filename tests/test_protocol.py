import pytest

from imu_uart.protocol.models import IMUSample
from imu_uart.protocol.commands import Command, CommandResponse, encode, decode_response
from imu_uart.protocol import framing


SAMPLE = IMUSample(
    accel_x=0.123, accel_y=0.456, accel_z=0.789,
    timestamp_accel=1624456789,
    gyro_x=12000, gyro_y=-13000, gyro_z=11000,
    timestamp_gyro=1624456790,
    mag_x=48.3, mag_y=50.1, mag_z=49.7,
    timestamp_mag=1624456791,
)


# --- Models ---

def test_imu_sample_round_trip():
    fields = SAMPLE.to_fields()
    rebuilt = IMUSample.from_fields(fields)
    assert rebuilt == SAMPLE


def test_imu_sample_wrong_field_count():
    with pytest.raises(ValueError):
        IMUSample.from_fields(["1", "2", "3"])


def test_imu_sample_bad_value():
    bad = ["abc"] + ["0"] * 11
    with pytest.raises(ValueError):
        IMUSample.from_fields(bad)


# --- Commands ---

def test_encode_start():
    assert encode(Command.START) == "0"


def test_encode_stop():
    assert encode(Command.STOP) == "1"


def test_decode_ok_response():
    resp = decode_response("0,ok")
    assert resp.command == Command.START
    assert resp.ok is True


def test_decode_error_response():
    resp = decode_response("1,invalid command")
    assert resp.command == Command.STOP
    assert resp.ok is False


def test_decode_garbage():
    with pytest.raises(ValueError):
        decode_response("garbage")


# --- framing ---

def test_encode_message():
    assert framing.encode_message("0,ok") == b"$0,ok\n"


def test_extract_single_message():
    buf = bytearray(b"$hello\n")
    msgs, leftover = framing.extract_messages(buf)
    assert msgs == ["hello"]
    assert leftover == bytearray()


def test_extract_partial_message():
    buf = bytearray(b"$hel")
    msgs, leftover = framing.extract_messages(buf)
    assert msgs == []
    assert leftover == bytearray(b"$hel")


def test_extract_two_messages():
    buf = bytearray(b"$first\n$second\n")
    msgs, leftover = framing.extract_messages(buf)
    assert msgs == ["first", "second"]
    assert leftover == bytearray()


def test_extract_garbage_before_frame():
    buf = bytearray(b"junk$hello\n")
    msgs, leftover = framing.extract_messages(buf)
    assert msgs == ["hello"]


def test_extract_trailing_partial():
    buf = bytearray(b"$first\n$sec")
    msgs, leftover = framing.extract_messages(buf)
    assert msgs == ["first"]
    assert leftover == bytearray(b"$sec")
