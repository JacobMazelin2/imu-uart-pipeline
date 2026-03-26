#!/usr/bin/env bash
set -euo pipefail

# Creates a pair of virtual serial ports using socat.
# /dev/virtual0 <---> /dev/virtual1
# The emulator writes to one end, the consumer reads from the other.
# Requires: sudo apt install socat

PORTA="${1:-/tmp/virtual0}"
PORTB="${2:-/tmp/virtual1}"

echo "Creating virtual serial pair: $PORTA <-> $PORTB"
socat -d -d \
    pty,raw,echo=0,link="$PORTA" \
    pty,raw,echo=0,link="$PORTB"