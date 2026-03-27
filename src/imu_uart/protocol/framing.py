FRAME_START = ord("$")
FRAME_END = ord("\n")


def encode_message(payload: str) -> bytes:
    return f"${payload}\n".encode("ascii")


def extract_messages(buffer: bytearray) -> tuple[list[str], bytearray]:
    messages = []

    while True:
        start = buffer.find(FRAME_START)
        if start == -1:
            buffer.clear()
            break

        if start > 0:
            # discard bytes before the first $
            buffer = buffer[start:]

        end = buffer.find(FRAME_END)
        if end == -1:
            break
        message = buffer[1:end]
        message = message.decode("ascii")
        messages.append(message)
        buffer = buffer[end + 1:]

    return messages, buffer
