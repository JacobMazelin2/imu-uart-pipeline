import enum
from dataclasses import dataclass


class Command(enum.Enum):
    START = "0"
    STOP = "1"


@dataclass(frozen=True, slots=True)
class CommandResponse:
    command: Command
    status: str

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def encode(cmd: Command) -> str:
    return cmd.value


def decode_response(payload: str) -> CommandResponse:
    parts = payload.split(",", maxsplit=1)
    if len(parts) != 2:
        raise ValueError(f"Expected 'value,status', got: {payload!r}")
    cmd_value, status = parts
    try:
        command = Command(cmd_value)
    except ValueError:
        raise ValueError(f"Unknown command value: {cmd_value!r}")
    return CommandResponse(command=command, status=status)
