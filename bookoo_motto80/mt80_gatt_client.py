#!/usr/bin/env python3
"""Minimal MT80 Custom GATT connection and handshake verifier."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import struct
import sys
import time
from collections.abc import Iterable
from typing import Any

try:
    from bleak import BleakClient, BleakScanner
except ImportError:  # Keep --help and the dependency error usable without Bleak.
    BleakClient = None  # type: ignore[assignment]
    BleakScanner = None  # type: ignore[assignment]


SERVICE_UUID = "4d543830-0001-4b80-8f00-424f4f4b4f4f"
RX_UUID = "4d543830-0002-4b80-8f00-424f4f4b4f4f"
TX_UUID = "4d543830-0003-4b80-8f00-424f4f4b4f4f"

FRAME_MAGIC = 0xA5
FRAME_VERSION = 0x01
FRAME_HEADER = struct.Struct("<BBHHH")
MESSAGE_MAX_LEN = 4096
REASSEMBLY_TIMEOUT_SECONDS = 2.0

# Twenty bytes is valid at the default ATT MTU (23) on both supported platforms.
SAFE_WRITE_PACKET_LEN = 20
SCAN_TIMEOUT_SECONDS = 10.0
HANDSHAKE_TIMEOUT_SECONDS = 5.0

HANDSHAKE_REQUEST = {
    "request": {
        "appHello": {
            "op": "handshake",
        }
    }
}

MAC_PATTERN = re.compile(r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")


class ClientError(RuntimeError):
    """A concise, user-facing client failure."""


class FrameError(ValueError):
    """A malformed or out-of-order Custom GATT frame."""


def parse_mac(value: str) -> str:
    """Validate and normalize a public BLE MAC address."""
    if not MAC_PATTERN.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "MAC must use XX:XX:XX:XX:XX:XX format"
        )
    return value.upper()


def encode_fragments(
    payload: bytes,
    *,
    sequence: int = 1,
    packet_len: int = SAFE_WRITE_PACKET_LEN,
) -> Iterable[bytes]:
    """Encode one logical JSON payload as ordered Custom GATT v1 frames."""
    if not 1 <= len(payload) <= MESSAGE_MAX_LEN:
        raise ValueError(f"payload length must be 1..{MESSAGE_MAX_LEN} bytes")
    if not 0 <= sequence <= 0xFFFF:
        raise ValueError("sequence must fit in uint16")
    if not FRAME_HEADER.size < packet_len <= 512:
        raise ValueError("packet_len must be 9..512 bytes")

    fragment_capacity = packet_len - FRAME_HEADER.size
    total_len = len(payload)
    for offset in range(0, total_len, fragment_capacity):
        fragment = payload[offset : offset + fragment_capacity]
        yield FRAME_HEADER.pack(
            FRAME_MAGIC,
            FRAME_VERSION,
            sequence,
            total_len,
            offset,
        ) + fragment


class FrameReassembler:
    """Reassemble ordered TX notifications into complete JSON byte strings."""

    def __init__(self) -> None:
        self._sequence: int | None = None
        self._total_len = 0
        self._payload = bytearray()
        self._last_fragment_at: float | None = None

    def reset(self) -> None:
        self._sequence = None
        self._total_len = 0
        self._payload.clear()
        self._last_fragment_at = None

    def feed(self, packet: bytes) -> bytes | None:
        now = time.monotonic()
        if (
            self._last_fragment_at is not None
            and now - self._last_fragment_at > REASSEMBLY_TIMEOUT_SECONDS
        ):
            self.reset()
        if len(packet) <= FRAME_HEADER.size:
            self.reset()
            raise FrameError("frame has no payload")

        magic, version, sequence, total_len, offset = FRAME_HEADER.unpack_from(packet)
        fragment = packet[FRAME_HEADER.size :]

        if magic != FRAME_MAGIC or version != FRAME_VERSION:
            self.reset()
            raise FrameError("unsupported frame magic or version")
        if not 1 <= total_len <= MESSAGE_MAX_LEN:
            self.reset()
            raise FrameError("invalid logical message length")
        if offset >= total_len or len(fragment) > total_len - offset:
            self.reset()
            raise FrameError("fragment exceeds logical message bounds")

        if offset == 0:
            # Firmware also treats offset zero as the start of a new message.
            self._sequence = sequence
            self._total_len = total_len
            self._payload = bytearray()
        elif (
            self._sequence is None
            or sequence != self._sequence
            or total_len != self._total_len
            or offset != len(self._payload)
        ):
            self.reset()
            raise FrameError("out-of-order or mismatched fragment")

        self._payload.extend(fragment)
        self._last_fragment_at = now
        if len(self._payload) != self._total_len:
            return None

        completed = bytes(self._payload)
        self.reset()
        return completed


def split_period_message(document: Any) -> tuple[Any | None, Any | None]:
    """Split a periodInfo envelope from any non-period content."""
    if not isinstance(document, dict):
        return None, document

    broadcast = document.get("broadcast")
    if not isinstance(broadcast, dict) or not isinstance(
        broadcast.get("periodInfo"), dict
    ):
        return None, document

    period_document = {
        "broadcast": {
            "periodInfo": broadcast["periodInfo"],
        }
    }

    remainder: dict[str, Any] = {}
    for key, value in document.items():
        if key != "broadcast":
            remainder[key] = value
            continue
        remaining_broadcast = {
            name: item for name, item in value.items() if name != "periodInfo"
        }
        if remaining_broadcast:
            remainder[key] = remaining_broadcast

    return period_document, remainder or None


def enable_terminal_cursor_control() -> bool:
    """Enable ANSI cursor control for an interactive Windows/Linux terminal."""
    if not sys.stdout.isatty():
        return False
    if sys.platform != "win32":
        return True

    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32
        kernel32.GetStdHandle.argtypes = [wintypes.DWORD]
        kernel32.GetStdHandle.restype = wintypes.HANDLE
        kernel32.GetConsoleMode.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(wintypes.DWORD),
        ]
        kernel32.GetConsoleMode.restype = wintypes.BOOL
        kernel32.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel32.SetConsoleMode.restype = wintypes.BOOL

        stdout_handle = kernel32.GetStdHandle(-11)
        console_mode = wintypes.DWORD()
        invalid_handle_value = ctypes.c_void_p(-1).value
        if stdout_handle in (None, invalid_handle_value):
            return False
        if not kernel32.GetConsoleMode(
            stdout_handle,
            ctypes.byref(console_mode),
        ):
            return False
        enable_virtual_terminal_processing = 0x0004
        return bool(
            kernel32.SetConsoleMode(
                stdout_handle,
                console_mode.value | enable_virtual_terminal_processing,
            )
        )
    except (AttributeError, OSError, ValueError):
        return False


class TerminalRenderer:
    """Print normal messages while refreshing periodInfo as one live block."""

    def __init__(self, *, cursor_control: bool | None = None) -> None:
        self._cursor_control = (
            sys.stdout.isatty() if cursor_control is None else cursor_control
        )
        self._period_lines: list[str] | None = None
        self._rendered_rows = 0

    def _move_to_live_block_start(self) -> None:
        if self._rendered_rows > 0:
            sys.stdout.write(f"\x1b[{self._rendered_rows}A")

    def _draw_live_block(self, lines: list[str]) -> None:
        rows = max(self._rendered_rows, len(lines))
        for index in range(rows):
            sys.stdout.write("\r\x1b[2K")
            if index < len(lines):
                sys.stdout.write(lines[index])
            sys.stdout.write("\n")
        sys.stdout.flush()
        self._period_lines = lines
        self._rendered_rows = rows

    def _remove_live_block(self) -> None:
        """Clear the live block and leave the cursor where the block began."""
        if not self._cursor_control or self._period_lines is None:
            return

        self._move_to_live_block_start()
        for index in range(self._rendered_rows):
            sys.stdout.write("\r\x1b[2K")
            if index < self._rendered_rows - 1:
                sys.stdout.write("\x1b[1B")
        if self._rendered_rows > 1:
            sys.stdout.write(f"\x1b[{self._rendered_rows - 1}A")
        sys.stdout.write("\r")
        sys.stdout.flush()

    def message(self, text: str, *, error: bool = False) -> None:
        saved_period_lines = self._period_lines
        self._remove_live_block()
        print(text, file=sys.stderr if error else sys.stdout, flush=True)
        if self._cursor_control and saved_period_lines is not None:
            self._draw_live_block(saved_period_lines)

    def pretty_json(self, document: Any) -> None:
        self.message(json.dumps(document, ensure_ascii=False, indent=2))

    def period_json(self, document: Any) -> None:
        lines = json.dumps(document, ensure_ascii=False, indent=2).splitlines()
        if self._cursor_control:
            if self._period_lines is not None:
                self._move_to_live_block_start()
            self._draw_live_block(lines)
        else:
            print("\n".join(lines), flush=True)

    def finish_live_line(self) -> None:
        self._period_lines = None
        self._rendered_rows = 0


def find_characteristic(service: Any, uuid: str) -> Any | None:
    """Find a characteristic without depending on service cache shortcuts."""
    uuid = uuid.lower()
    return next(
        (item for item in service.characteristics if item.uuid.lower() == uuid),
        None,
    )


async def wait_for_handshake_result(
    period_received: asyncio.Event,
    disconnected: asyncio.Event,
) -> None:
    period_task = asyncio.create_task(period_received.wait())
    disconnect_task = asyncio.create_task(disconnected.wait())
    try:
        done, _ = await asyncio.wait(
            {period_task, disconnect_task},
            timeout=HANDSHAKE_TIMEOUT_SECONDS,
            return_when=asyncio.FIRST_COMPLETED,
        )
        if disconnect_task in done:
            raise ClientError("device disconnected while waiting for periodInfo")
        if period_task not in done:
            raise ClientError(
                f"no periodInfo received within {HANDSHAKE_TIMEOUT_SECONDS:g} seconds"
            )
    finally:
        for task in (period_task, disconnect_task):
            if not task.done():
                task.cancel()
        await asyncio.gather(period_task, disconnect_task, return_exceptions=True)


async def run_client(mac: str) -> None:
    if sys.platform not in {"win32", "linux"}:
        raise ClientError("this MAC-address example supports Windows and Linux only")
    if BleakClient is None or BleakScanner is None:
        raise ClientError("Bleak is not installed; run: python -m pip install -r requirements.txt")

    renderer = TerminalRenderer(cursor_control=enable_terminal_cursor_control())
    reassembler = FrameReassembler()
    period_received = asyncio.Event()
    disconnected = asyncio.Event()

    def handle_disconnect(_client: Any) -> None:
        disconnected.set()

    def handle_notification(_characteristic: Any, data: bytearray) -> None:
        try:
            payload = reassembler.feed(bytes(data))
            if payload is None:
                return
            document = json.loads(payload.decode("utf-8"))
        except (FrameError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            renderer.message(f"Warning: ignored invalid notification: {exc}", error=True)
            return

        period_document, non_period_content = split_period_message(document)
        if non_period_content is not None:
            renderer.pretty_json(non_period_content)
        if period_document is not None:
            renderer.period_json(period_document)
            period_received.set()

    try:
        renderer.message(f"Scanning for {mac} ...")
        device = await BleakScanner.find_device_by_address(
            mac,
            timeout=SCAN_TIMEOUT_SECONDS,
        )
        if device is None:
            raise ClientError(
                f"device {mac} was not found within {SCAN_TIMEOUT_SECONDS:g} seconds"
            )

        renderer.message(f"Connecting to {device.name or mac} ...")
        client_options: dict[str, Any] = {}
        if sys.platform == "win32":
            client_options["winrt"] = {
                "address_type": "public",
                "use_cached_services": False,
            }

        async with BleakClient(
            device,
            disconnected_callback=handle_disconnect,
            **client_options,
        ) as client:
            service = client.services.get_service(SERVICE_UUID)
            if service is None:
                raise ClientError(f"Custom GATT service {SERVICE_UUID} was not found")

            rx_characteristic = find_characteristic(service, RX_UUID)
            tx_characteristic = find_characteristic(service, TX_UUID)
            if rx_characteristic is None or tx_characteristic is None:
                raise ClientError("Custom GATT RX or TX characteristic was not found")
            if not ({"write", "write-without-response"} & set(rx_characteristic.properties)):
                raise ClientError("RX characteristic is not writable")
            if "notify" not in tx_characteristic.properties:
                raise ClientError("TX characteristic does not support Notify")

            await client.start_notify(tx_characteristic, handle_notification)
            renderer.message("Connected; TX notifications enabled.")

            handshake_payload = json.dumps(
                HANDSHAKE_REQUEST,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
            for fragment in encode_fragments(handshake_payload):
                await client.write_gatt_char(
                    rx_characteristic,
                    fragment,
                    response=True,
                )

            renderer.message("Handshake sent; waiting for periodInfo ...")
            await wait_for_handshake_result(period_received, disconnected)
            renderer.message("Connection and handshake verified. Press Ctrl+C to exit.")

            await disconnected.wait()
            raise ClientError("device disconnected unexpectedly")
    finally:
        renderer.finish_live_line()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Connect to an MT80 Custom GATT server and verify its handshake."
    )
    parser.add_argument("mac", type=parse_mac, help="public BLE MAC (XX:XX:XX:XX:XX:XX)")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        asyncio.run(run_client(args.mac))
    except KeyboardInterrupt:
        print("Disconnected.")
        return 0
    except ClientError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # Bleak backend errors should stay concise by default.
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
