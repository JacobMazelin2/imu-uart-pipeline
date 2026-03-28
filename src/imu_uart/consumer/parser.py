from imu_uart.protocol.models import IMUSample
from imu_uart.protocol.commands import CommandResponse, decode_response

def parse_payload(payload: str) -> IMUSample | CommandResponse:
    if ";" in payload:
        fields = payload.split(';')
        return IMUSample.from_fields(fields)
    else:
        return decode_response(payload)
    